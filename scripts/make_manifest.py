#!/usr/bin/env python3
"""Regenerate manifest.json's published_files block from the repo's data/ tree.

The source_archives block (official URLs + SHA-256 of the whitehouse.gov zips) is
preserved verbatim — those hashes anchor the whole kit and must never be derived
from local state. Everything under data/ (including data/README.md) is listed with
its SHA-256 and size so third parties can verify the published dataset file-by-file.

If external_archives.json exists at the repo root (independent archive captures of
the official source URLs, hash-verified against source_archives), its content is
carried into the manifest as an external_archives block, verbatim — the input file
is checked in, so the output stays deterministic.
"""
import os, sys, json, hashlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(ROOT, "manifest.json")
EXTERNAL = os.path.join(ROOT, "external_archives.json")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    man = json.load(open(MANIFEST, encoding="utf-8"))
    published = []
    data_dir = os.path.join(ROOT, "data")
    for root, dirs, files in os.walk(data_dir):
        dirs.sort()
        for fn in sorted(files):
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            published.append({"path": rel, "sha256": sha256(full), "bytes": os.path.getsize(full)})
    published.sort(key=lambda r: r["path"])
    man["published_files"] = published
    n_ext = 0
    if os.path.exists(EXTERNAL):
        ext = json.load(open(EXTERNAL, encoding="utf-8"))
        n_ext = len(ext.get("captures", []))
        ordered = {}
        for k, v in man.items():
            if k == "external_archives":
                continue
            ordered[k] = v
            if k == "source_archives":
                ordered["external_archives"] = ext
        ordered.setdefault("external_archives", ext)
        man = ordered
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, indent=2)
        f.write("\n")
    print(f"manifest.json updated: {len(published)} published files, "
          f"{len(man['source_archives'])} source archives (unchanged), "
          f"{n_ext} external archive captures")

if __name__ == "__main__":
    main()
