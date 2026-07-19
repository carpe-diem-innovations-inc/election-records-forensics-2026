import os, sys, json, re
import fitz

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = os.environ.get("EI_WORKSPACE") or os.getcwd()
EXTRACT = os.path.join(WS, "extracted")
DATA = os.path.join(WS, "data")
REC = os.path.join(WS, "recovered")
os.makedirs(REC, exist_ok=True)

def is_dark(fill):
    if fill is None:
        return False
    try:
        return all(c <= 0.25 for c in fill[:3])
    except Exception:
        return False

def pii_scan(text):
    flags = {}
    flags["ssn"] = len(re.findall(r"\b\d{3}-\d{2}-\d{4}\b", text))
    flags["phone"] = len(re.findall(r"\b\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b", text))
    flags["dob"] = len(re.findall(r"\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)\d\d\b", text))
    flags["email"] = len(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))
    return {k:v for k,v in flags.items() if v}

summary = []
for root, dirs, files in os.walk(EXTRACT):
    dirs.sort(); files.sort()  # deterministic traversal: NTFS returns sorted entries, ext4 does not
    if "__MACOSX" in root:
        continue
    for fn in files:
        if not fn.lower().endswith(".pdf"):
            continue
        full = os.path.join(root, fn)
        rel = os.path.relpath(full, EXTRACT).replace("\\","/")
        rec = {"relpath": rel, "filename": fn, "section": rel.split("/")[0]}
        leaks = []          # text recovered from under black boxes
        try:
            doc = fitz.open(full)
            for pno, page in enumerate(doc):
                # collect dark filled rectangles from vector drawings
                boxes = []
                for dr in page.get_drawings():
                    fill = dr.get("fill")
                    if is_dark(fill):
                        r = dr.get("rect")
                        if r and r.width > 6 and r.height > 4:
                            boxes.append(fitz.Rect(r))
                # also redaction/square annotations
                try:
                    a = page.first_annot
                    while a:
                        if a.type[0] in (12, 4, 2):  # Square, Redact-ish
                            boxes.append(fitz.Rect(a.rect))
                        a = a.next
                except Exception:
                    pass
                # for each box, is there selectable text under it?
                for b in boxes:
                    # shrink slightly to avoid catching adjacent text
                    q = fitz.Rect(b.x0+1, b.y0+1, b.x1-1, b.y1-1)
                    if q.is_empty or q.width<=0 or q.height<=0:
                        continue
                    t = page.get_textbox(q).strip()
                    # meaningful (letters/digits, not just a stray char)
                    if t and len(re.sub(r"\s","",t)) >= 3 and re.search(r"[A-Za-z0-9]", t):
                        leaks.append({"page": pno+1, "rect": [round(v,1) for v in b],
                                      "text": t})
            rec["page_count"] = doc.page_count
            doc.close()
        except Exception as e:
            rec["error"] = str(e)
        rec["leak_span_count"] = len(leaks)
        alltext = "\n".join(l["text"] for l in leaks)
        rec["leaked_char_count"] = sum(len(l["text"]) for l in leaks)
        rec["pii"] = pii_scan(alltext)
        # Inline the recovered text only when it is tiny and PII-clean, so the
        # published JSON is self-verifying; anything larger or flagged stays in
        # the local dump (recovered/) for manual review before any publication.
        if leaks and not rec["pii"] and rec["leaked_char_count"] <= 200:
            rec["leak_texts"] = [l["text"] for l in leaks]
        # write full recovered leaks to disk (handled with care)
        if leaks:
            outp = os.path.join(REC, re.sub(r'[^\w.-]','_', fn) + ".leaks.txt")
            with open(outp, "w", encoding="utf-8", newline="\n") as f:
                for l in leaks:
                    f.write(f"[p{l['page']} @ {l['rect']}]\n{l['text']}\n{'-'*40}\n")
            rec["leak_dump"] = os.path.relpath(outp, WS).replace("\\","/")
        summary.append(rec)

with open(os.path.join(DATA,"redaction_leaks.json"),"w",encoding="utf-8",newline="\n") as f:
    json.dump(summary, f, indent=2, default=str)

leaking = [r for r in summary if r["leak_span_count"]>0]
print(f"Documents scanned: {len(summary)}")
print(f"Documents with recoverable text under black boxes: {len(leaking)}")
print(f"Total leaked spans: {sum(r['leak_span_count'] for r in summary)}")
print(f"Total leaked chars: {sum(r['leaked_char_count'] for r in summary)}")
print()
print("=== per-document leak scoreboard (leaking only) ===")
for r in sorted(leaking, key=lambda r:-r["leak_span_count"]):
    pii = r["pii"]
    piis = (" PII:"+",".join(f"{k}x{v}" for k,v in pii.items())) if pii else ""
    print(f"  spans={r['leak_span_count']:4d} chars={r['leaked_char_count']:6d}{piis}  {r['filename'][:60]}")
