# Data dictionary & provenance

All data here is **derived** from the four official source archives (public-domain U.S. Government works).
The source archives themselves are **not** redistributed — retrieve them from the URLs in
[`../manifest.json`](../manifest.json) and verify the SHA-256.

## `metadata/` — forensic outputs (no personal data)

| File | Contents |
|---|---|
| `inventory.csv` | Every file in the archives: section, filename, kind, size, SHA-256. |
| `duplicates.json` | Byte-identical files appearing under more than one name/section. |
| `macos_xattrs.json` | Decoded macOS AppleDouble extended attributes: quarantine agent, per-download event UUID, UTC download time. (No personal names; UUIDs are download-event IDs.) |
| `dsstore.json` | Decoded `.DS_Store` (Finder folder-state) entry names — can retain names of working folders not shipped in the package. |
| `pdf_metadata.json` | Per-PDF `/Info` + XMP (Author/Creator/Producer/dates), version, EOF/startxref counts, page/text/image stats. |
| `redaction_leaks.json` | Redaction-integrity scan results (recoverable-text test). |
| `revision_recovery.json` | Incremental-revision recovery test (multiple `%%EOF`). |
| `consolidated_findings.json` | Roll-up of the above into headline counts. |

## `ocr_intelligence/` — scrubbed OCR text

OCR of the scanned **intelligence** memos (China / Venezuela / IC-process). Residual structured
identifiers were scrubbed by `scripts/scrub_and_pack.py`; the source documents had already redacted
personal identifiers. Names of **public officials acting in official capacity** are retained. OCR is
imperfect — verify quotes against the source image.

One borderline case was reviewed and deliberately retained:
`EMAIL_ICA.CommentsReMinorityView_30DEC2020_DECLASS_REDACTED.pdf.ocr.txt` contains the first name
(no surname, rank, or role) of an FBI team member mentioned in passing as an office contact. The
name appears as-is in the officially released document; masking it here would make the committed
OCR diverge from what OCR of the release actually produces, so it is published as released.

## `SCRUB_LOG.json`

Record of what the publish-scrub masked (empty/near-empty because the source was already redacted).

## Intentionally excluded

- **Raw source PDFs** — fetch from `manifest.json` (avoids re-hosting third-party PII and keeps this repo
  small; reproducibility is anchored to the hashes).
- **Verbatim OCR of the Michigan FBI witness interviews** — these concern **private individuals**.
  Republishing their interview text is not necessary for reproducibility (re-derive it from the source
  PDFs if needed) and not responsible. The forensic *metadata* for those files is included above.

## Licensing

Derived data: CC-BY-4.0. Source documents: U.S. Government (public domain).
