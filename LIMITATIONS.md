# Limitations & sources of error

Read this before citing anything here.

- **"Document forensics" here is not statistical "election forensics."** This kit examines files, metadata,
  and sourced claims; it is unrelated to the statistical analysis of vote counts (Mebane-style "election
  forensics") and makes no statistical claim about any election result.
- **Timestamps reflect the assembling machine, not authorship.** `com.apple.quarantine` records when a file
  was downloaded onto the machine that built the package — not when a document was originally created.
- **OCR is imperfect.** Scanned pages were read by OCR; character errors occur, especially in proper names.
  Verify any quote against the source image before relying on it. Proper names in the intelligence memos are
  OCR-read and should be confirmed against the official record.
- **Redaction conclusions are scoped.** "Redactions held" means *no recoverable content under the standard
  vectors tested* (selectable text under marks, un-flattened image layers, incremental-revision recovery).
  Burned-in raster redaction is unrecoverable by definition; we confirm it is single-image but do not audit
  beyond that.
- **Tier 2 depends on third parties.** Fact-check verdicts rest on cited external reporting, court records,
  and research organizations current as of July 2026. If those sources are wrong or updated, revisit.
- **Zip entry names are decoded as UTF-8.** Some entries in the official archives lack the zip UTF-8 flag;
  the scripts pass `metadata_encoding="utf-8"` (Python ≥ 3.11) so names like "China's" decode correctly.
  Tools that default to cp437 will show mojibake in paths — the file *contents* and hashes are unaffected.
- **OCR text is not bit-for-bit reproducible across machines.** `rapidocr-onnxruntime`/`onnxruntime` are
  pinned in `requirements.txt`, but ONNX inference varies slightly by CPU: an independent machine with the
  exact pins reproduced 14 of 16 OCR files byte-identically and 2 with whitespace-level differences plus a
  single character flip. `trust_but_verify.py` therefore compares OCR output using a whitespace-normalized
  similarity threshold (≥ 99.5%) rather than raw bytes; the metadata outputs are compared byte-for-byte.
- **The state-correlation posture data is secondary.** DOJ litigation "posture" per state came from news
  summaries, not primary court dockets, and contained at least one conflict (Oklahoma). Treat that column as
  indicative only; the primary-verified point is that the named states come from the intelligence memo.
- **Tier 3 is interpretation.** Motive and intent are not established facts. Each Tier-3 item ships with a
  steelman and a falsification test; weigh them yourself.
- **Not published here:** raw source PDFs (re-fetch from `manifest.json` URLs) and verbatim Michigan
  witness-interview OCR (private individuals). Their absence limits one-click verification of the Michigan
  *quotes*; reproduce them from the source if you need to.
- **AI-assisted.** Parsing, OCR, and drafting were AI-assisted. The design goal is that every step is
  independently checkable; that does not eliminate the possibility of error in judgment or code. Check it.
