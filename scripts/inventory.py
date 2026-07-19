import os, sys, hashlib, csv, json, collections

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = os.environ.get("EI_WORKSPACE") or os.getcwd()
EXTRACT = os.path.join(WS, "extracted")
DATA = os.path.join(WS, "data")
os.makedirs(DATA, exist_ok=True)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

rows = []
for root, dirs, files in os.walk(EXTRACT):
    dirs.sort(); files.sort()  # deterministic traversal: NTFS returns sorted entries, ext4 does not
    for fn in files:
        full = os.path.join(root, fn)
        rel = os.path.relpath(full, EXTRACT).replace("\\", "/")
        is_appledouble = "__MACOSX" in rel or fn.startswith("._")
        is_dsstore = fn == ".DS_Store"
        section = rel.split("/")[0]
        kind = "appledouble" if is_appledouble else ("dsstore" if is_dsstore else ("pdf" if fn.lower().endswith(".pdf") else "other"))
        size = os.path.getsize(full)
        digest = sha256(full)
        rows.append({
            "section": section,
            "relpath": rel,
            "filename": fn,
            "kind": kind,
            "size": size,
            "sha256": digest,
        })

# duplicate detection among real PDFs
pdfs = [r for r in rows if r["kind"] == "pdf"]
by_hash = collections.defaultdict(list)
for r in pdfs:
    by_hash[r["sha256"]].append(r["relpath"])
dupes = {h: paths for h, paths in by_hash.items() if len(paths) > 1}

with open(os.path.join(DATA, "inventory.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["section","filename","kind","size","sha256","relpath"],
                       lineterminator="\n")
    w.writeheader()
    # relpath tiebreaker: (section, kind, filename) is not unique (e.g. __MACOSX ._.DS_Store x2)
    for r in sorted(rows, key=lambda r: (r["section"], r["kind"], r["filename"], r["relpath"])):
        w.writerow(r)

with open(os.path.join(DATA, "duplicates.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(dupes, f, indent=2)

print(f"total files: {len(rows)}")
for k in ("pdf","appledouble","dsstore","other"):
    print(f"  {k}: {sum(1 for r in rows if r['kind']==k)}")
print(f"\nunique PDF hashes: {len(by_hash)}  (of {len(pdfs)} PDFs)")
print(f"duplicate hash groups: {len(dupes)}")
for h, paths in dupes.items():
    print(f"\n  [{h[:12]}]  x{len(paths)}")
    for p in paths:
        print(f"     {p}")
