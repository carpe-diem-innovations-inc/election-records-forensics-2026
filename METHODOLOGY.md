# Methodology — do it yourself

This is the "how," step by step, so you can reproduce every result or run the same method on a different
document release. It assumes basic comfort with a terminal and Python (≥ 3.11). It does **not** define
every acronym — where a term is domain-specific (e.g., *AppleDouble*, *ICA*, *xref*), a one-line gloss is
given and you can search the rest.

**Shortcut:** `python scripts/trust_but_verify.py` runs steps 0–6 end to end in a temporary workspace and
compares every output against the published `data/` (add `--fast` to skip OCR). The steps below are the
same pipeline, unbundled so you can inspect each stage. The metadata outputs reproduce byte-identically
across machines; OCR text can differ by a few characters between CPUs even with the pinned versions, so
the verifier compares OCR with a whitespace-normalized similarity check (see LIMITATIONS). A weekly CI
run repeats the whole thing on Linux.

## 0. Setup

```bash
pip install -r requirements.txt        # pikepdf, PyMuPDF, pdfminer.six, rapidocr-onnxruntime, ds-store
python scripts/fetch_sources.py        # downloads the 4 official ZIPs into ./corpus, verifies SHA-256
export EI_CORPUS=./corpus              # where the source ZIPs live
export EI_WORKSPACE=./work             # where extracted files + outputs go
```

`fetch_sources.py` checks each download against the hashes in `manifest.json`. If a hash doesn't match,
the official file changed — stop and note it; you are no longer analyzing the same bytes we did.

## 1. Extract & inventory — `inventory.py`

Unzips all four archives (preserving the macOS residue), then records for every file: section, name,
size, SHA-256. Duplicate detection flags any files that are byte-identical across archives.

*What to look for:* identical hashes under different names = the same document filed twice (a sign of
manual assembly).

## 2. Container / macOS forensics — `macos_forensics.py`

macOS writes hidden sidecar files (`._name`, "AppleDouble") into ZIPs; they carry **extended
attributes**. The important one is `com.apple.quarantine`, which records *which app downloaded the file,
a per-download event ID, and a UTC timestamp*. The script decodes these and reconstructs the download
timeline. It also decodes every `.DS_Store` (a Finder folder-state file, which can retain names of
folders no longer present) into `dsstore.json`.

*What to look for:* clustering of timestamps and shared event IDs (bulk vs. individual downloads);
which application downloaded each file; any working-folder names left behind.

## 3. PDF-level forensics — `pdf_forensics.py`

For each PDF: the `/Info` dictionary and XMP metadata (Author / Creator / Producer / dates), the software
fingerprint, and structural signals — number of `%%EOF` markers and `startxref` entries (multiple can mean
either an *incremental update* or *linearization* / "Fast Web View").

*What to look for:* stripped vs. retained metadata (who sanitized what), which authoring tools were used,
and any documents that stand apart from the rest.

## 4. Redaction integrity — `redaction.py` + `revision_recovery.py`

Two independent tests of whether "redacted" content is actually gone:

- `redaction.py` — finds dark filled rectangles and checks whether selectable text still sits *under*
  them, and whether image redactions are separate overlays over a recoverable base image.
- `revision_recovery.py` — for files with multiple `%%EOF` markers, tries to open the earlier revision
  (which, for a true incremental update, could contain pre-redaction content).

*What to look for:* any recoverable text or prior revision. (In this corpus, essentially none — the
redactions held under these vectors; the multiple `%%EOF`s were linearization, not recoverable revisions.)

## 5. OCR the scanned documents — `ocr.py`, `ocr_michigan_all.py`

Many pages are scanned images with no text layer. These scripts render each page and run OCR
(`rapidocr-onnxruntime`) so the *content* can be read and quoted. OCR is imperfect — verify any quote
against the source image before relying on it.

## 6. Roll-up & correlation — `consolidate.py`, `correlation.py`

`consolidate.py` merges the per-stage outputs into `consolidated_findings.json`. `correlation.py` compares
the states named in the release against (a) states in DOJ voter-data litigation and (b) 2026 battleground
maps — a test of whether the named list looks politically curated. (It doesn't; see FINDINGS Tier 3 / #11.)

## 7. Publish-safety — `scrub_and_pack.py`

Assembles the publication dataset: copies the PII-free forensic metadata, scrubs residual structured
identifiers from the intelligence OCR, and **excludes** the private-citizen Michigan witness interviews.
Run this before publishing any derived text.

## Chain of custody and standards conformance

**Acquisition record.** The four official ZIP archives were downloaded from
`whitehouse.gov/election-integrity` over TLS on **2026-07-17**. SHA-256 digests were computed at intake;
those digests are the values published in `manifest.json` (`165d85c4…`, `a823364d…`, `b73c4dee…`,
`3291004b…`). An independent re-download on 2026-07-17 matched all four digests exactly. Every analysis
step derives from hash-verified copies: `fetch_sources.py` verifies each archive against the manifest and
stops if any digest differs.

**Tooling.** All analysis dependencies are version-pinned (`requirements.txt`), including the transitive
packages that affect output. Directory traversal is explicitly sorted and every writer emits LF newlines,
so the metadata outputs are byte-identical across operating systems and filesystems. A weekly CI run
re-derives the entire published dataset from the source archives on a GitHub-hosted Linux runner (pinned
Python 3.14, pinned dependencies) and compares byte-for-byte.

**Standards mapping.** For readers who evaluate open-source evidence against published standards, the
pipeline maps onto the phases of the Berkeley Protocol on Digital Open Source Investigations, and onto
SWGDE-style digital-evidence practice (hashing at acquisition with a NIST-approved algorithm, documented
tool versions, repeatability), as follows:

| Phase | Practice here |
|---|---|
| Collection | Official source URLs, sizes, and download date recorded in `manifest.json`; acquisition over TLS |
| Preservation | SHA-256 at intake; archives re-fetchable and hash-checked by `fetch_sources.py`; hashes of every published output in the manifest |
| Verification | Byte-identical re-derivation of every published output on an independent machine (`trust_but_verify.py`; weekly CI) |
| Analysis | Findings separated by evidentiary tier; interpretation fenced with steelman + falsification tests; adversarial [RED-TEAM.md](RED-TEAM.md) pass |

**Scope of the provenance findings — and what would overturn them.** The macOS artifacts (quarantine
attributes, `.DS_Store` entries, AppleDouble sidecars) establish facts about the *assembly workflow*:
which operating system, which downloading applications, and what timing packaged the archives. They
establish nothing about the authenticity or integrity of the documents' *contents*, and nothing about who
authored the documents, where, or why. That scope limit is the standing lesson of the Guccifer 2.0
episode: document metadata reliably shows *that* certain software touched certain files, and *with what
tooling* — the findings that survived were exactly those; the widely criticized 2017 "transfer-speed"
counter-analysis, which stretched file metadata into claims about *where* copying physically occurred, is
the canonical over-reading failure. The readings here are falsifiable: the quarantine timeline would be
overturned if the decoded `com.apple.quarantine` fields were shown to be mis-parsed (the raw bytes are in
the source archives; re-decode them with `macos_forensics.py`) or if the same attribute pattern were shown
to be producible by a non-macOS packaging workflow; the working-folder reading would be overturned if the
"NEW ADDED FOR UPLOAD 7.15.26" entry in the Michigan `.DS_Store` were shown to be a decoding artifact
rather than a stored folder name (compare `data/metadata/dsstore.json` against the raw `.DS_Store` bytes).

## Applying this to a different release

Point `EI_CORPUS` at any archive of documents and run steps 1–6. The method is document-agnostic; only the
findings are specific to this corpus.
