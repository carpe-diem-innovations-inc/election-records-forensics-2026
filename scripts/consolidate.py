import os, sys, json, collections, csv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = os.environ.get("EI_WORKSPACE") or os.getcwd()
DATA = os.path.join(WS, "data")

def load(n):
    return json.load(open(os.path.join(DATA,n), encoding="utf-8"))

inv = list(csv.DictReader(open(os.path.join(DATA,"inventory.csv"), encoding="utf-8")))
dupes = load("duplicates.json")
xattrs = load("macos_xattrs.json")
pdfmeta = load("pdf_metadata.json")
leaks = load("redaction_leaks.json")

out = {}

# counts
pdfs = [r for r in inv if r["kind"]=="pdf"]
out["counts"] = {
    "archives": 4,
    "total_files_in_archives": len(inv),
    "pdf_documents": len(pdfs),
    "unique_pdf_hashes": len({r["sha256"] for r in pdfs}),
    "appledouble_sidecars": sum(1 for r in inv if r["kind"]=="appledouble"),
    "dsstore": sum(1 for r in inv if r["kind"]=="dsstore"),
    "total_pages": sum(r.get("pages",0) for r in pdfmeta),
    "total_embedded_images": sum(r.get("image_count",0) for r in pdfmeta),
}

# duplicates
out["duplicates"] = [{"sha256": h, "copies": paths} for h,paths in dupes.items()]

# download timeline (quarantine)
events = collections.defaultdict(lambda: {"files":[]})
for r in xattrs:
    q = r.get("quarantine")
    if q:
        key = (q.get("event_uuid",""), q.get("agent"), q.get("download_time_utc"))
        events[key]["files"].append(r["target"])
out["download_events"] = [
    {"event_uuid":k[0], "agent":k[1], "time_utc":k[2], "file_count":len(v["files"]), "files":sorted(v["files"])}
    for k,v in sorted(events.items(), key=lambda x:(x[0][2] or ""))
]
out["download_agents"] = dict(collections.Counter(
    r["quarantine"]["agent"] for r in xattrs if r.get("quarantine")))

# metadata scrub
prod = collections.Counter((r.get("Producer") or "(stripped/none)") for r in pdfmeta)
out["producer_distribution"] = dict(prod)
out["docs_with_any_internal_date"] = sum(1 for r in pdfmeta if r.get("CreationDate") or r.get("ModDate"))
out["docs_metadata_retained"] = [
    {"filename": r["filename"], "Producer": r.get("Producer"), "Creator": r.get("Creator"),
     "CreationDate": r.get("CreationDate"), "ModDate": r.get("ModDate")}
    for r in pdfmeta if r.get("Producer")]

# scanned vs text
out["scanned_vs_text"] = {
    "low_text_scanned": sum(1 for r in pdfmeta if r.get("text_per_page",0) < 50),
    "text_rich": sum(1 for r in pdfmeta if r.get("text_per_page",0) >= 50),
}

# redaction
leaking = [r for r in leaks if r["leak_span_count"]>0]
# The conclusion is derived from the scan output, never hardcoded: a re-run
# that recovers different text must produce a different conclusion string.
_inline = sorted({t for r in leaking for t in r.get("leak_texts", [])})
if not leaking:
    _conclusion = "no recoverable text under the vectors tested"
elif all("leak_texts" in r for r in leaking):
    _conclusion = ("recoverable text under the vectors tested is limited to: "
                   + ", ".join(repr(t) for t in _inline))
else:
    _conclusion = "recoverable text found; review the leak dumps (recovered/) before publishing"
out["redaction"] = {
    "docs_scanned": len(leaks),
    "docs_with_recoverable_text_under_boxes": len(leaking),
    "total_leaked_spans": sum(r["leak_span_count"] for r in leaks),
    "total_leaked_chars": sum(r["leaked_char_count"] for r in leaks),
    "leaked_samples": [{"filename":r["filename"],"chars":r["leaked_char_count"]} for r in leaking],
    "conclusion": _conclusion,
}

with open(os.path.join(DATA,"consolidated_findings.json"),"w",encoding="utf-8",newline="\n") as f:
    json.dump(out, f, indent=2)

print(json.dumps(out, indent=2)[:3000])
