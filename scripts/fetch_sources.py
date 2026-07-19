#!/usr/bin/env python3
"""Download the official source archives and verify their SHA-256 against manifest.json.

Reproducibility anchor: this repo does NOT redistribute the source PDFs. This script fetches them
from the official whitehouse.gov URLs and checks the exact bytes. If a hash does not match, the
official file has changed since analysis — stop and note it.

Usage:
    python scripts/fetch_sources.py            # -> ./corpus (or $EI_CORPUS)
"""
import os, sys, json, hashlib, urllib.request, zipfile

if sys.version_info < (3, 11):
    sys.exit("Python >= 3.11 required (zip entry names are decoded as UTF-8 via metadata_encoding).")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORPUS = os.environ.get("EI_CORPUS") or os.path.join(os.getcwd(), "corpus")
WORKSPACE = os.environ.get("EI_WORKSPACE") or os.getcwd()
EXTRACT = os.path.join(WORKSPACE, "extracted")
MANIFEST = os.path.join(ROOT, "manifest.json")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    man = json.load(open(MANIFEST, encoding="utf-8"))
    os.makedirs(CORPUS, exist_ok=True)
    ok = True
    for a in man["source_archives"]:
        dest = os.path.join(CORPUS, a["filename"])
        if not os.path.exists(dest) or sha256(dest) != a["sha256"]:
            print(f"downloading {a['filename']} ...", flush=True)
            urllib.request.urlretrieve(a["url"], dest)
        got = sha256(dest)
        size = os.path.getsize(dest)
        match = (got == a["sha256"]) and (size == a["bytes"])
        ok = ok and match
        print(f"  {'OK ' if match else 'MISMATCH'}  {a['filename']}")
        if not match:
            print(f"     expected {a['sha256']} ({a['bytes']} bytes)\n     got      {got} ({size} bytes)")
    if not ok:
        print("\nWARNING: one or more hashes did not match — NOT extracting.")
        sys.exit(1)
    print("\nAll archives verified. Extracting (preserving macOS residue) ...")
    os.makedirs(EXTRACT, exist_ok=True)
    for a in man["source_archives"]:
        # metadata_encoding: some entries lack the zip UTF-8 flag; without this, Python
        # decodes their names as cp437 and "China's" becomes mojibake in every output path.
        with zipfile.ZipFile(os.path.join(CORPUS, a["filename"]), metadata_encoding="utf-8") as zf:
            try:
                zf.extractall(EXTRACT)
            except (FileNotFoundError, OSError):
                # The archives contain ~70-char folder names + ~80-char filenames; on
                # Windows a deep EI_WORKSPACE overflows MAX_PATH (260) and extraction
                # dies with a misleading FileNotFoundError.
                if os.name == "nt" and len(os.path.abspath(EXTRACT)) > 100:
                    sys.exit(f"Extraction failed — the workspace path is likely too deep for "
                             f"Windows MAX_PATH (extracted paths exceed 260 chars).\n"
                             f"Use a shorter EI_WORKSPACE (e.g. C:\\ei) or enable Windows "
                             f"long paths, then re-run.\nWorkspace: {EXTRACT}")
                raise
    print(f"Extracted to {EXTRACT}\nNext: set EI_WORKSPACE={WORKSPACE} and run the analysis scripts.")
    sys.exit(0)

if __name__ == "__main__":
    main()
