import os, sys, json, re, collections
import pikepdf
import fitz  # PyMuPDF

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# pikepdf returns XMP keys in Clark notation ("{namespace-uri}LocalName");
# map the URIs back to the conventional prefixes so keys read as "xmp:CreateDate".
XMP_NS = {
    "http://ns.adobe.com/xap/1.0/": "xmp",
    "http://ns.adobe.com/xap/1.0/mm/": "xmpMM",
    "http://ns.adobe.com/xap/1.0/rights/": "xmpRights",
    "http://ns.adobe.com/pdf/1.3/": "pdf",
    "http://ns.adobe.com/pdfx/1.3/": "pdfx",
    "http://purl.org/dc/elements/1.1/": "dc",
}

def xmp_prefixed(key):
    m = re.match(r"\{(.+)\}(.+)$", key)
    if not m:
        return key
    uri, local = m.groups()
    return f"{XMP_NS.get(uri, uri)}:{local}"

WS = os.environ.get("EI_WORKSPACE") or os.getcwd()
EXTRACT = os.path.join(WS, "extracted")
DATA = os.path.join(WS, "data")

def pdf_dates(s):
    # D:YYYYMMDDHHmmSS...  -> iso-ish
    if not s: return None
    m = re.match(r"D?:?(\d{4})(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\d{2})?", str(s))
    if not m: return str(s)
    y,mo,da,h,mi,se = [g or "01" for g in m.groups()]
    tzmatch = re.search(r"([+\-Z]\d{0,2}'?\d{0,2}'?)$", str(s))
    tz = tzmatch.group(1) if tzmatch else ""
    return f"{y}-{mo}-{da}T{h}:{mi}:{se}{tz}"

records = []
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
        # ---- pikepdf: docinfo, xmp, versions, xref/incremental ----
        try:
            pdf = pikepdf.open(full)
            rec["pdf_version"] = str(pdf.pdf_version)
            docinfo = {}
            if pdf.docinfo:
                for k,v in pdf.docinfo.items():
                    docinfo[str(k)] = str(v)
            rec["docinfo"] = docinfo
            rec["Author"] = docinfo.get("/Author")
            rec["Creator"] = docinfo.get("/Creator")
            rec["Producer"] = docinfo.get("/Producer")
            rec["CreationDate"] = pdf_dates(docinfo.get("/CreationDate"))
            rec["ModDate"] = pdf_dates(docinfo.get("/ModDate"))
            # XMP
            try:
                with pdf.open_metadata() as meta:
                    xmp = {xmp_prefixed(k): str(v) for k,v in dict(meta).items()}
                rec["xmp_keys"] = sorted(xmp.keys())
                for kk in ("xmp:CreatorTool","pdf:Producer","dc:creator","xmp:CreateDate",
                           "xmp:ModifyDate","xmp:MetadataDate","xmpMM:DocumentID","xmpMM:InstanceID",
                           "xmpMM:History"):
                    if kk in xmp:
                        rec["xmp_"+kk.replace(":","_")] = xmp[kk][:500]
            except Exception as e:
                rec["xmp_error"] = str(e)
            pdf.close()
        except Exception as e:
            rec["pikepdf_error"] = str(e)

        # ---- raw scan: count EOF markers / startxref (incremental updates) ----
        try:
            with open(full,"rb") as f:
                raw = f.read()
            rec["eof_markers"] = raw.count(b"%%EOF")
            rec["startxref_count"] = raw.count(b"startxref")
            rec["has_xref_streams"] = b"/XRef" in raw
            rec["obj_count_est"] = len(re.findall(rb"\d+ \d+ obj", raw))
        except Exception as e:
            rec["raw_error"] = str(e)

        # ---- fitz: page count, is it scanned images or text? ----
        try:
            doc = fitz.open(full)
            rec["pages"] = doc.page_count
            txt_chars = 0
            img_count = 0
            for pg in doc:
                txt_chars += len(pg.get_text("text"))
                img_count += len(pg.get_images(full=True))
            rec["text_chars"] = txt_chars
            rec["image_count"] = img_count
            rec["text_per_page"] = round(txt_chars/max(doc.page_count,1),1)
            doc.close()
        except Exception as e:
            rec["fitz_error"] = str(e)

        records.append(rec)

with open(os.path.join(DATA,"pdf_metadata.json"),"w",encoding="utf-8",newline="\n") as f:
    json.dump(records, f, indent=2, default=str)

# ------- summaries -------
def norm(x): return (x or "(none)").strip()
print(f"PDF documents analyzed: {len(records)}\n")

print("=== PRODUCER clustering ===")
prod = collections.Counter(norm(r.get("Producer")) for r in records)
for p,c in prod.most_common():
    print(f"  x{c:2d}  {p}")

print("\n=== CREATOR clustering ===")
crea = collections.Counter(norm(r.get("Creator")) for r in records)
for p,c in crea.most_common():
    print(f"  x{c:2d}  {p}")

print("\n=== AUTHOR values ===")
auth = collections.Counter(norm(r.get("Author")) for r in records)
for p,c in auth.most_common():
    print(f"  x{c:2d}  {p}")

print("\n=== xmp CreatorTool ===")
ct = collections.Counter(norm(r.get("xmp_xmp_CreatorTool")) for r in records)
for p,c in ct.most_common():
    print(f"  x{c:2d}  {p}")

print("\n=== incremental updates (eof_markers > 1) ===")
for r in sorted(records, key=lambda r:-r.get("eof_markers",0)):
    if r.get("eof_markers",0) > 1:
        print(f"  EOFx{r['eof_markers']} startxrefx{r.get('startxref_count')}  {r['filename']}")
