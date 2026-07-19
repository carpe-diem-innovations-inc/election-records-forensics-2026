"""Claims lint — the prose cannot drift from the data.

Two check classes, both assertion-style (exit 1 on any failure) so CI fails
if the documents and the data ever disagree:

1. Prose claims. Every load-bearing number in FINDINGS.md, README.md and
   docs/dashboard.html is matched against the committed data it derives from
   (data/metadata/consolidated_findings.json, manifest.json). The claim map
   is tests/claims_map.json: claim-id -> data accessor + the exact text
   patterns where the number appears. Edit the data without the prose (or
   the prose without the data) and this lint fails.

2. Metadata coherence. The per-PDF record in data/metadata/pdf_metadata.json
   is checked for internal consistency: no modification date preceding a
   creation date, no internal date after the archives were acquired
   (2026-07-17), no producer tool younger than the dates it stamped, and the
   roll-up counts in consolidated_findings.json re-derivable from the
   per-PDF records. Note the *expected* pattern for this corpus is NOT "old
   dates everywhere": a 2026-era regeneration pass (Adobe PDF Library 26.x,
   HP MFP scans) is consistent with a July 2026 release workflow. Only
   genuine incoherences fail. A small consistency table for the documents
   that retain internal dates is printed for citation.

Usage: python scripts/claims_lint.py            (from anywhere; stdlib only)
"""
import json
import os
import re
import sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS_MAP = os.path.join(ROOT, "tests", "claims_map.json")

DATA_FILES = {
    "cf": os.path.join("data", "metadata", "consolidated_findings.json"),
    "manifest": "manifest.json",
    "pm": os.path.join("data", "metadata", "pdf_metadata.json"),
}

# The archives were acquired and hash-anchored on this date; no internal
# document date can coherently postdate it.
ACQUISITION_DATE = date(2026, 7, 17)
SANE_FLOOR = date(1990, 1, 1)

# Earliest plausible calendar year for a producer/creator tool string, by
# prefix. A file whose internal dates *predate* its tool's existence is
# incoherent (the Guccifer-2.0-style falsification test); a recent tool
# stamping recent dates is the normal case.
TOOL_MIN_YEAR = [
    ("Adobe PDF Library 26.", 2025),
    ("Acrobat PDFMaker 26", 2025),
    ("iText 2.1.7", 2008),
    ("Microsoft", 2017),  # "Microsoft(R) Word for Microsoft 365"
]

WORDS = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
         6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}

failures = []


def fail(msg):
    failures.append(msg)
    print(f"FAIL  {msg}")


def load_json(key, cache={}):
    if key not in cache:
        with open(os.path.join(ROOT, DATA_FILES[key]), encoding="utf-8") as f:
            cache[key] = json.load(f)
    return cache[key]


def parse_dt(s):
    """Parse the leading YYYY-MM-DDTHH:MM:SS of any of the date formats in
    pdf_metadata.json (timezone suffixes vary: -04'00', -04:00, Z, none)."""
    if not s:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})", str(s))
    return datetime(*map(int, m.groups())) if m else None


def resolve(source):
    """Evaluate an accessor like 'cf:counts.pdf_documents',
    'cf:duplicates|len', 'cf:download_agents|sumvalues',
    'manifest:published_files|count_prefix:data/ocr_intelligence/' or
    'derived:download_window_seconds'."""
    if source.startswith("derived:"):
        return DERIVED[source.split(":", 1)[1]]()
    fkey, rest = source.split(":", 1)
    parts = rest.split("|")
    val = load_json(fkey)
    for seg in parts[0].split("."):
        val = val[int(seg[1:-1])] if re.fullmatch(r"\[\d+\]", seg) else val[seg]
    for filt in parts[1:]:
        if filt == "len":
            val = len(val)
        elif filt == "sumvalues":
            val = sum(val.values())
        elif filt.startswith("count_prefix:"):
            prefix = filt.split(":", 1)[1]
            val = sum(1 for item in val if item.get("path", "").startswith(prefix))
        else:
            raise ValueError(f"unknown filter {filt!r} in {source!r}")
    return val


def download_window_seconds():
    """Span of the four per-section Chrome bundle downloads, in seconds."""
    events = [e for e in load_json("cf")["download_events"] if e.get("agent") == "Chrome"]
    times = [parse_dt(e["time_utc"]) for e in events]
    return int((max(times) - min(times)).total_seconds())


DERIVED = {"download_window_seconds": download_window_seconds}


def read_doc(relpath, cache={}):
    if relpath not in cache:
        with open(os.path.join(ROOT, relpath), encoding="utf-8") as f:
            cache[relpath] = f.read()
    return cache[relpath]


def acceptable_forms(expected):
    forms = {str(expected)}
    if isinstance(expected, int) and expected in WORDS:
        forms.add(WORDS[expected])
    return forms


def check_claim(claim):
    expected = resolve(claim["source"])
    for other in claim.get("also_equals", []):
        got = resolve(other)
        if got != expected:
            fail(f"[{claim['id']}] {claim['source']} = {expected} but {other} = {got}")
    forms = acceptable_forms(expected)
    for occ in claim.get("occurrences", []):
        text = read_doc(occ["file"])
        matches = re.findall(occ["pattern"], text)
        if not matches:
            fail(f"[{claim['id']}] pattern not found in {occ['file']}: {occ['pattern']!r}")
            continue
        for got in matches:
            if str(got).lower() not in forms:
                fail(f"[{claim['id']}] {occ['file']} says {got!r}, data says {expected} "
                     f"({claim['source']})")
    if "expect" in claim and expected != claim["expect"]:
        fail(f"[{claim['id']}] {claim['source']} = {expected}, expected {claim['expect']} "
             f"(update the claim map deliberately if this changed)")


def check_state_rows(claim):
    """Named-states card: the bold count in each row must equal the number of
    state codes listed beside it, and the counts must be the expected ones."""
    text = read_doc(claim["file"])
    rows = re.findall(claim["pattern"], text)
    if len(rows) != len(claim["expect_counts"]):
        fail(f"[{claim['id']}] expected {len(claim['expect_counts'])} state rows, "
             f"found {len(rows)}")
        return
    for (count, codes), expected in zip(rows, claim["expect_counts"]):
        states = [s for s in codes.replace("*", " ").split() if len(s) == 2]
        if int(count) != len(states):
            fail(f"[{claim['id']}] row claims {count} states but lists "
                 f"{len(states)}: {codes.strip()!r}")
        if int(count) != expected:
            fail(f"[{claim['id']}] row count {count} != expected {expected} "
                 f"(update the claim map deliberately if this changed)")


def check_metadata_coherence():
    cf, pm = load_json("cf"), load_json("pm")

    # Roll-up counts must re-derive from the per-PDF records.
    if len(pm) != cf["counts"]["pdf_documents"]:
        fail(f"[coherence] pdf_metadata has {len(pm)} records, "
             f"counts.pdf_documents = {cf['counts']['pdf_documents']}")
    pages = sum(r.get("pages", 0) for r in pm)
    if pages != cf["counts"]["total_pages"]:
        fail(f"[coherence] pages sum to {pages}, counts.total_pages = "
             f"{cf['counts']['total_pages']}")
    stripped = sum(1 for r in pm if not (r.get("Author") or r.get("Creator") or r.get("Producer")))
    if stripped != cf["producer_distribution"]["(stripped/none)"]:
        fail(f"[coherence] {stripped} records have no Author/Creator/Producer, "
             f"producer_distribution says {cf['producer_distribution']['(stripped/none)']}")

    # Per-document date coherence.
    date_keys = ("CreationDate", "ModDate", "xmp_xmp_CreateDate",
                 "xmp_xmp_ModifyDate", "xmp_xmp_MetadataDate")
    table = []
    for r in pm:
        name = r["filename"]
        cre, mod = parse_dt(r.get("CreationDate")), parse_dt(r.get("ModDate"))
        if cre and mod and mod < cre:
            fail(f"[coherence] {name}: ModDate {mod} precedes CreationDate {cre}")
        earliest = None
        for key in date_keys:
            dt = parse_dt(r.get(key))
            if not dt:
                continue
            earliest = dt if earliest is None or dt < earliest else earliest
            if not (SANE_FLOOR <= dt.date() <= ACQUISITION_DATE):
                fail(f"[coherence] {name}: {key} = {dt} outside "
                     f"[{SANE_FLOOR}, {ACQUISITION_DATE} (acquisition)]")
        tool = r.get("Producer") or r.get("Creator") or r.get("xmp_xmp_CreatorTool") or ""
        if earliest and tool:
            for prefix, min_year in TOOL_MIN_YEAR:
                if tool.startswith(prefix) and earliest.year < min_year:
                    fail(f"[coherence] {name}: tool {tool!r} (>= {min_year}) "
                         f"postdates internal date {earliest}")
        if tool or cre or mod:
            cre_s = r.get("CreationDate") or (
                f"xmp {r['xmp_xmp_CreateDate']}" if r.get("xmp_xmp_CreateDate") else None)
            mod_s = r.get("ModDate") or (
                f"xmp {r['xmp_xmp_ModifyDate']}" if r.get("xmp_xmp_ModifyDate") else None)
            table.append((name, tool, cre_s, mod_s))

    print("\nDocuments retaining internal metadata (declass-stamp era is 2026; "
          "2026-era dates/tools are the coherent expectation):")
    print(f"  {'document':<58} {'tool':<34} {'created':<24} modified")
    for name, tool, cre, mod in table:
        print(f"  {name[:57]:<58} {(tool or '-')[:33]:<34} "
              f"{(cre or '-')[:23]:<24} {(mod or '-')[:23]}")
    print(f"  ({len(table)} of {len(pm)} documents; the other "
          f"{len(pm) - len(table)} carry no internal metadata)")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    with open(CLAIMS_MAP, encoding="utf-8") as f:
        claims = json.load(f)["claims"]
    n_occ = 0
    for claim in claims:
        if claim.get("type") == "state_rows":
            check_state_rows(claim)
        else:
            check_claim(claim)
            n_occ += len(claim.get("occurrences", []))
    check_metadata_coherence()
    print(f"\nclaims-lint: {len(claims)} claims, {n_occ} prose occurrences checked; "
          f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
