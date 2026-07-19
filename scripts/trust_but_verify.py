#!/usr/bin/env python3
"""trust_but_verify.py — one command that re-derives this repository's published dataset.

What it does, end to end:
  1. verifies the four official source archives against the SHA-256 anchors in manifest.json
     (downloading them from whitehouse.gov if you don't already have them);
  2. re-runs the entire analysis pipeline in a temporary workspace;
  3. compares every produced file against the published data/ tree — byte for byte for
     metadata (with a structural-JSON fallback), and with a whitespace-normalized
     similarity threshold for OCR text (ONNX inference is not bit-for-bit across CPUs);
  4. re-checks the manifest hash of every published file;
  5. confirms the excluded private-citizen material is, in fact, absent.

Exit code 0 = everything reproduces. Anything else = investigate before trusting.

Usage:
    python scripts/trust_but_verify.py            # full run incl. OCR (~15 min)
    python scripts/trust_but_verify.py --fast     # skip OCR (~2 min): metadata pipeline only
    EI_CORPUS=/path/to/zips python scripts/trust_but_verify.py   # reuse already-downloaded zips
"""
import os, re, sys, json, difflib, hashlib, shutil, subprocess, tempfile, argparse

if sys.version_info < (3, 11):
    sys.exit("Python >= 3.11 required.")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(ROOT, "manifest.json")

METADATA_FILES = ["inventory.csv", "duplicates.json", "macos_xattrs.json", "dsstore.json",
                  "pdf_metadata.json", "redaction_leaks.json", "revision_recovery.json",
                  "consolidated_findings.json"]
# names that must never appear in published OCR (private-citizen Michigan material)
EXCLUDED_MARKERS = ["FBIMichigan", "Muskego", "RELEASE_MARKED", "Witness", "GBI_Strategies",
                    "Voter_Fraud_Spreadsheet", "PIN_"]

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def run_script(name, env):
    print(f"\n──── running {name} " + "─" * max(0, 48 - len(name)))
    r = subprocess.run([sys.executable, os.path.join(HERE, name)], env=env)
    if r.returncode != 0:
        sys.exit(f"FAIL: {name} exited with code {r.returncode}")

def norm_json(path):
    return json.load(open(path, encoding="utf-8"))

# ONNX inference is not bit-for-bit across CPUs, so OCR text can differ by a
# few characters between machines even with the exact pinned versions (see
# LIMITATIONS.md). OCR files therefore pass on whitespace-normalized equality
# or >= OCR_SIM_THRESHOLD character similarity; everything else stays strict.
OCR_SIM_THRESHOLD = 0.995

def ocr_similarity(a_text, b_text):
    na = re.sub(r"\s+", "", a_text)
    nb = re.sub(r"\s+", "", b_text)
    if na == nb:
        return 1.0
    return difflib.SequenceMatcher(None, na, nb, autojunk=False).ratio()

def compare(label, committed, produced, results):
    if not os.path.exists(produced):
        results.append((label, "FAIL", "not produced")); return
    if not os.path.exists(committed):
        results.append((label, "FAIL", "not in repo")); return
    if sha256(committed) == sha256(produced):
        results.append((label, "PASS", "byte-identical")); return
    if committed.endswith(".json"):
        try:
            if norm_json(committed) == norm_json(produced):
                results.append((label, "PASS", "structurally identical (bytes differ)")); return
        except Exception:
            pass
    if committed.endswith(".ocr.txt"):
        a = open(committed, encoding="utf-8").read()
        b = open(produced, encoding="utf-8").read()
        sim = ocr_similarity(a, b)
        if sim >= OCR_SIM_THRESHOLD:
            results.append((label, "PASS",
                            f"{sim:.2%} char similarity (OCR nondeterminism; threshold {OCR_SIM_THRESHOLD:.1%})"))
            return
        results.append((label, "FAIL", f"only {sim:.2%} char similarity")); return
    results.append((label, "FAIL", "content differs"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="skip OCR (metadata pipeline only)")
    ap.add_argument("--keep", action="store_true", help="keep the temporary workspace")
    args = ap.parse_args()

    results = []
    ws = tempfile.mkdtemp(prefix="ei_verify_")
    corpus = os.environ.get("EI_CORPUS") or os.path.join(ws, "corpus")
    env = dict(os.environ, EI_CORPUS=corpus, EI_WORKSPACE=ws, PYTHONIOENCODING="utf-8")
    print(f"workspace: {ws}\ncorpus:    {corpus}")

    # 1) sources: fetch_sources.py downloads if needed and verifies SHA-256 (exits non-zero on mismatch)
    run_script("fetch_sources.py", env)
    results.append(("source archives (4)", "PASS", "SHA-256 match manifest.json"))

    # 2) pipeline
    stages = ["inventory.py", "macos_forensics.py", "pdf_forensics.py",
              "redaction.py", "revision_recovery.py"]
    if not args.fast:
        stages.append("ocr.py")
    stages.append("consolidate.py")
    for s in stages:
        run_script(s, env)
    if not args.fast:
        run_script("scrub_and_pack.py", env)

    print("\n──── comparing outputs against published data/ ────")
    # 3) metadata outputs
    for fn in METADATA_FILES:
        compare(f"data/metadata/{fn}",
                os.path.join(ROOT, "data", "metadata", fn),
                os.path.join(ws, "data", fn), results)
    # OCR + scrub outputs (full mode only)
    if not args.fast:
        pub = os.path.join(ws, "data_public")
        committed_ocr = sorted(os.listdir(os.path.join(ROOT, "data", "ocr_intelligence")))
        produced_ocr = sorted(os.listdir(os.path.join(pub, "ocr_intelligence")))
        if committed_ocr != produced_ocr:
            results.append(("ocr_intelligence file set", "FAIL",
                            f"{len(committed_ocr)} committed vs {len(produced_ocr)} produced"))
        else:
            results.append(("ocr_intelligence file set", "PASS", f"{len(committed_ocr)} files"))
        for fn in committed_ocr:
            compare(f"data/ocr_intelligence/{fn}",
                    os.path.join(ROOT, "data", "ocr_intelligence", fn),
                    os.path.join(pub, "ocr_intelligence", fn), results)
        compare("data/SCRUB_LOG.json",
                os.path.join(ROOT, "data", "SCRUB_LOG.json"),
                os.path.join(pub, "SCRUB_LOG.json"), results)

    # 4) manifest hash of every published file
    man = json.load(open(MANIFEST, encoding="utf-8"))
    bad = []
    for f in man["published_files"]:
        p = os.path.join(ROOT, *f["path"].split("/"))
        if not os.path.exists(p) or sha256(p) != f["sha256"] or os.path.getsize(p) != f["bytes"]:
            bad.append(f["path"])
    results.append((f"manifest.json published_files ({len(man['published_files'])})",
                    "FAIL" if bad else "PASS",
                    ("mismatch: " + ", ".join(bad)) if bad else "all hashes + sizes match"))

    # 5) excluded private-citizen material must be absent from the published tree
    leaked = [fn for fn in os.listdir(os.path.join(ROOT, "data", "ocr_intelligence"))
              if any(m in fn for m in EXCLUDED_MARKERS)]
    results.append(("private-citizen OCR excluded", "FAIL" if leaked else "PASS",
                    ("present: " + ", ".join(leaked)) if leaked else "none present"))

    # report
    width = max(len(r[0]) for r in results)
    print("\n" + "=" * (width + 40))
    fails = 0
    for label, status, note in results:
        if status == "FAIL":
            fails += 1
        print(f"  {status:4s}  {label.ljust(width)}  {note}")
    print("=" * (width + 40))
    mode = "FAST (OCR skipped)" if args.fast else "FULL"
    if fails:
        print(f"\n{mode}: {fails} check(s) FAILED — do not trust until explained.")
    else:
        print(f"\n{mode}: everything reproduces. Nullius in verba — and now you didn't have to.")
    if not args.keep:
        shutil.rmtree(ws, ignore_errors=True)
    else:
        print(f"workspace kept: {ws}")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
