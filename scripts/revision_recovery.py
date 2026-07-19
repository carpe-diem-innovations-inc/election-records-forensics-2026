import os, sys, json, re
import fitz

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = os.environ.get("EI_WORKSPACE") or os.getcwd()
EXTRACT = os.path.join(WS, "extracted")
DATA = os.path.join(WS, "data")
REC = os.path.join(WS, "recovered")
os.makedirs(REC, exist_ok=True)

def revisions(raw):
    """Return byte offsets right after each %%EOF (end of each revision)."""
    offs = []
    for m in re.finditer(rb"%%EOF", raw):
        offs.append(m.end())
    return offs

def text_of_bytes(b):
    try:
        d = fitz.open(stream=b, filetype="pdf")
        t = "\n".join(p.get_text("text") for p in d)
        n = d.page_count
        d.close()
        return t, n
    except Exception as e:
        return None, f"err:{e}"

results = []
for root, dirs, files in os.walk(EXTRACT):
    dirs.sort(); files.sort()  # deterministic traversal: NTFS returns sorted entries, ext4 does not
    if "__MACOSX" in root:
        continue
    for fn in files:
        if not fn.lower().endswith(".pdf"):
            continue
        full = os.path.join(root, fn)
        rel = os.path.relpath(full, EXTRACT).replace("\\","/")
        raw = open(full,"rb").read()
        offs = revisions(raw)
        if len(offs) < 2:
            continue
        # revision 1 = bytes up to and including first %%EOF
        rev1 = raw[:offs[0]]
        t1, n1 = text_of_bytes(rev1)
        # final
        tf, nf = text_of_bytes(raw)
        rec = {"filename": fn, "section": rel.split("/")[0],
               "num_revisions": len(offs),
               "rev1_pages": n1, "final_pages": nf,
               "rev1_chars": len(t1) if isinstance(t1,str) else None,
               "final_chars": len(tf) if isinstance(tf,str) else None}
        # content that exists in rev1 but not in final (candidate pre-redaction text)
        if isinstance(t1,str) and isinstance(tf,str):
            final_norm = re.sub(r"\s+"," ", tf)
            extra_lines = []
            for line in t1.splitlines():
                s = line.strip()
                if len(re.sub(r"\s","",s)) >= 4 and s not in final_norm and re.sub(r"\s+"," ",s) not in final_norm:
                    extra_lines.append(s)
            rec["rev1_only_line_count"] = len(extra_lines)
            rec["rev1_extra_sample"] = extra_lines[:8]
            if extra_lines:
                outp = os.path.join(REC, re.sub(r'[^\w.-]','_', fn) + ".rev1_only.txt")
                with open(outp,"w",encoding="utf-8",newline="\n") as f:
                    f.write("\n".join(extra_lines))
                rec["rev1_dump"] = os.path.relpath(outp, WS).replace("\\","/")
        results.append(rec)

with open(os.path.join(DATA,"revision_recovery.json"),"w",encoding="utf-8",newline="\n") as f:
    json.dump(results, f, indent=2, default=str)

print(f"multi-revision docs analyzed: {len(results)}")
changed = [r for r in results if r.get("rev1_only_line_count",0) > 0]
print(f"docs where revision 1 contains text absent from final: {len(changed)}")
print()
for r in sorted(results, key=lambda r:-(r.get('rev1_only_line_count') or 0))[:25]:
    print(f"  rev1_only_lines={r.get('rev1_only_line_count'):>4}  rev1={r.get('rev1_chars')} final={r.get('final_chars')} p+{r.get('rev1_pages')}/{r.get('final_pages')}  {r['filename'][:52]}")
