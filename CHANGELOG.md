# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is date-based.

## [1.0.0] — 2026-07-19
### Added
- Initial public release: reproducible verification kit for the `whitehouse.gov/election-integrity`
  document archives (released 2026-07-16).
- Forensic scripts (`scripts/`): inventory + hashing, macOS/AppleDouble + `.DS_Store` decoding, PDF
  /Info + XMP metadata, redaction-integrity and revision-recovery tests, OCR, consolidation, state
  correlation, publish-scrub, manifest regeneration.
- `scripts/trust_but_verify.py`: one-command end-to-end verification — fetch, hash-check, re-run the
  pipeline, compare against the published dataset.
- Continuous verification: GitHub Actions workflow re-runs the full pipeline on push and weekly
  (canary for silent changes to the official source files); unit tests for the parsing primitives.
- Published dataset (`data/`): PII-free forensic metadata (incl. `dsstore.json` and XMP fields such as
  the Hewlett-Packard MFP scanner fingerprint) + scrubbed intelligence OCR.
- `manifest.json` anchoring reproducibility to the official source archives (URL + SHA-256) and listing
  the hash of every published file.
- Documentation: README, METHODOLOGY, FINDINGS (tiered, with full Sources list), LIMITATIONS, RED-TEAM,
  CONTRIBUTING.
- `docs/` visual dashboard + discoverability (JSON-LD, sitemap, robots).
- Claims lint (`scripts/claims_lint.py` + `tests/claims_map.json`, run by pytest in CI): every
  load-bearing number in README/FINDINGS/dashboard is asserted against the committed data, and the
  per-PDF metadata is checked for internal date/tool coherence — the prose cannot drift from the data.
- METHODOLOGY: chain-of-custody and standards-conformance section (acquisition record, pinned tooling,
  Berkeley Protocol / SWGDE mapping, scope + falsification statement for the provenance findings).
- README/CONTRIBUTING: explicit invitation for adversarial review and independent SHA-256 attestations
  of the source archives.
- Independent archive anchoring: `external_archives.json` (carried into `manifest.json` by
  `make_manifest.py`) records Internet Archive captures of the four source ZIPs + landing page; the raw
  archived bytes hash-match the `source_archives` SHA-256 values (verified 2026-07-18).
- OpenTimestamps proof `manifest.json.ots`: Bitcoin-anchored timestamp that the manifest (hashes,
  findings anchors, archive captures) existed by this date.
- Signed releases: tags signed with the project release key (fingerprint in README "Verifying releases").
### Notes
- Raw source PDFs and Michigan witness-interview OCR are intentionally not redistributed (see README /
  data/README.md).
