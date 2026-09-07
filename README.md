# Election Records Forensics 2026

**Examine the files, cross-check the claims — then reproduce every step yourself.**

[![Reproducibility](https://github.com/carpe-diem-innovations-inc/election-records-forensics-2026/actions/workflows/verify.yml/badge.svg)](https://github.com/carpe-diem-innovations-inc/election-records-forensics-2026/actions/workflows/verify.yml)
[![Code: MIT](https://img.shields.io/badge/code-MIT-2f7d4f.svg)](LICENSE)
[![Data & text: CC BY 4.0](https://img.shields.io/badge/data%20%26%20text-CC%20BY%204.0-2f7d4f.svg)](LICENSE)

**[Visual dashboard](https://carpe-diem-innovations-inc.github.io/election-records-forensics-2026/dashboard.html)** ·
**[Findings](FINDINGS.md)** · **[Reproduce it](METHODOLOGY.md)** · **[Data dictionary](data/README.md)** ·
**[Apply it to another release](#apply-this-method-to-any-document-release)**

A **reproducible verification kit** for the four document archives published at
`whitehouse.gov/election-integrity` on **16 July 2026**. It examines the *files* — their metadata,
structure, redactions, and text — and cross-checks the *claims* against the public record. The method is
general — point it at any document release; this release is the worked example.

> **Don't trust this repo. Test your own reality.** Every finding is re-derivable from the official
> source files using the scripts here. The point is not to tell you what to think — it's to lower the
> effort for the next person to check, and to add their own findings to the pile.

## What this is (and isn't)

- **Is:** an open method + dataset for document forensics, applied once as a worked example. Neutral in
  tone, non-partisan, source-anchored.
- **Isn't:** an accusation, an exposé, or a claim that any election was altered. Where the evidence only
  supports an *interpretation*, it is labeled as interpretation (see [FINDINGS.md](FINDINGS.md), Tier 3).

## 60-second summary

- **58 PDFs** (55 unique), assembled and zipped on a **macOS** machine; the archive still carried its
  filesystem residue (`__MACOSX/`, `.DS_Store`, `._` AppleDouble sidecars).
- The macOS `com.apple.quarantine` attributes timestamp the assembly: the evidentiary files arrived in
  **four download events, one per section, inside a ~38-second window** on 2026-07-16; two narrative
  "FINAL" documents were handled separately (one via Adobe Acrobat, one via a team-chat app).
- **55 of 58** documents have their authoring metadata stripped; the 3 that don't: two narrative "FINAL"
  documents authored in Microsoft Word / Acrobat, and one 2025 FBI document processed with iText. Only 6
  files (5 unique documents — the duplicated CIA Wire Memo counts twice) retain internal `/Info` dates;
  four scanned memos still carry a **"Hewlett-Packard MFP"** scanner fingerprint (and scan timestamps)
  in XMP.
- **Redactions held** under the vectors tested — no meaningful hidden text was recoverable.
- Reading the underlying intelligence memos (OCR included): they describe **data collection and
  social-media influence**; none states that voter rolls, ballots, or vote tabulation were altered.
- The Michigan documents describe a real **paid-canvasser registration-fraud** case that was **caught by
  the county clerk** and **declined by federal prosecutors** — no fraudulent ballots, no charges.

Full detail with tiered confidence: **[FINDINGS.md](FINDINGS.md)**. How to reproduce it yourself:
**[METHODOLOGY.md](METHODOLOGY.md)**. What could be wrong: **[LIMITATIONS.md](LIMITATIONS.md)** and the
adversarial **[RED-TEAM.md](RED-TEAM.md)**.

## Trust, but verify — in one command

```bash
pip install -r requirements.txt
python scripts/trust_but_verify.py       # fetch → hash-check → re-run pipeline → compare to data/
```

It downloads the official archives, verifies their SHA-256 against `manifest.json`, re-runs the entire
analysis in a temporary workspace, and compares every output against the published `data/` — then prints
a PASS/FAIL table. `--fast` skips OCR (~2 min instead of ~15). A weekly CI run does the same thing in
public, so this repo also acts as a **canary**: if the official source files are ever modified or removed,
the badge above goes red.

### Where it has been reproduced

Reproduction is only worth as much as the number of places it has happened, so here is the
record rather than a claim:

| platform | CPU | what ran | result |
|---|---|---|---|
| GitHub Actions, `ubuntu-latest` | runner-assigned | full pipeline incl. OCR, every push | metadata byte-identical; OCR at the ≥ 99.5% similarity threshold |
| `windows-26100.9168` | Zen 5, 2024 | full pipeline incl. OCR + 12 unit tests | 29/29 — **16 of 16** OCR files byte-identical |
| `windows-19044.7663` | Ivy Bridge, 2012 | full pipeline incl. OCR + 12 unit tests, from a **fresh clone of this repo** | 29/29 — **14 of 16** byte-identical, 2 on similarity (99.97% and 100.00%) |

**The two rows differ, and the difference is the interesting part.**

The 2024 machine reproduced all 16 OCR files byte-for-byte. The 2012 machine reproduced 14
byte-for-byte and two only after whitespace normalisation —
`EMAIL_ICA.CommentsReMinorityView…` at 99.97% and
`NICM_ChinaStepsToInfluenceElection…` at 100.00% character similarity.

That is **exactly** what [LIMITATIONS](LIMITATIONS.md) predicts: ONNX inference is not
bit-for-bit across CPUs, and an independent machine was recorded as reproducing 14 of 16
byte-identically with two whitespace-level differences. An independent run twelve years of
microarchitecture away landed on the same figure. **So the caveat in LIMITATIONS is not a
hedge — it is a measured, reproduced property**, and the similarity threshold exists because
it has to.

It also means the 16-of-16 row is the **weaker** of the two as evidence: getting a perfect
byte match is consistent with that being the machine the published data was produced on, so it
demonstrates the pipeline has not drifted rather than that it is machine-independent.

‼ **One limit on both Windows rows, stated because a reader would otherwise assume more than
is there: both are LTSC installations** — the same stripped-down Windows servicing lineage,
neither a stock consumer image. Two Windows results here are less independent than "two
Windows machines" sounds. They differ in OS generation and CPU, not in OS lineage.

**The genuinely uncontrolled platform is the CI row**, on hardware and an operating system this
project does not own. And none of these rows replaces the thing worth most: someone with no
stake in the conclusions running it. See below.

### The timestamp, checked against a node rather than a service

`manifest.json.ots` is an [OpenTimestamps](https://opentimestamps.org) proof anchoring the
manifest into the Bitcoin blockchain. On 2026-09-07 it was verified against a **self-hosted
Bitcoin Core node** rather than a third-party calendar or block explorer:

```
Got digest 333df3c8dc40c01e1dace57e2b7d76be9a0c8da21f82ef6d583af34c1e045047
Attestation block hash: 000000000000000000022958df14a8b588a2fb9745ce4e11e1d376ff7c55214d
Success! Bitcoin block 958631 attests existence as of 2026-07-18
```

So `manifest.json` — and through it the SHA-256 of every published file — provably existed in
its current form before that block was mined. **You do not have to take our word for the
timestamp, and you do not have to trust a calendar server either:** `ots verify manifest.json.ots`
against your own node reaches the same block independently.

## Independent verification invited

**Try to break these findings.** The strongest check on this work is adversarial technical review by
people with no stake in its conclusions. Re-run the one-command reproduction above, attack the method,
and file what you find with the [Finding issue template](.github/ISSUE_TEMPLATE/finding.yml) —
refutations and corrections carry at least as much weight here as confirmations.

Independently valuable even without reviewing anything: **publish your own SHA-256 attestation of the
four source archives.** Download them from the official URLs in `manifest.json`, hash them, and post the
digests somewhere public and datestamped (an issue here, a gist, your own site). Independent downloads by
unaffiliated parties at different times are the strongest form of source anchoring — they turn one
project's hash manifest into a distributed public record that the released bytes have not changed.

## Reproduce it step by step

```bash
pip install -r requirements.txt
python scripts/fetch_sources.py          # downloads the 4 official ZIPs, verifies SHA-256
export EI_CORPUS=./corpus EI_WORKSPACE=./work   # Windows: keep EI_WORKSPACE short (long archive
                                                #   filenames can exceed MAX_PATH on deep paths)
python scripts/inventory.py              # inventory + hashes + duplicate detection
python scripts/macos_forensics.py        # decode AppleDouble / quarantine timeline + .DS_Store
python scripts/pdf_forensics.py          # /Info + XMP, software fingerprint, revisions
python scripts/redaction.py              # redaction-integrity test
python scripts/revision_recovery.py      # incremental-revision recovery test
# OCR (optional, heavier): scripts/ocr.py, scripts/ocr_michigan_all.py
python scripts/consolidate.py            # roll up
python scripts/correlation.py            # named-states correlation
```

The `manifest.json` lists every official source archive with its URL and SHA-256, and every published
file with its hash. If your re-download hash-matches the manifest, you are analyzing the exact same bytes.

The source archives are also **archived independently of this project**: the `external_archives` block in
`manifest.json` records Internet Archive captures of all four ZIPs (plus the landing page), and the raw
archived bytes (the `id_` capture URLs) hash-match the `source_archives` SHA-256 values. The anchors are
therefore not self-referential — if the official URLs are ever changed or removed, the archived copies
still reproduce the exact bytes analyzed here, and anyone can re-check that claim by hashing the captures
themselves.

## Apply this method to any document release

Nothing here is specific to this corpus except the findings. Point `EI_CORPUS` at any archive of
documents and the same pipeline produces the same artifacts: hash inventory, container forensics,
metadata clustering, redaction-integrity tests, OCR, and a manifest others can verify against. The kit
is the capability; this release is the worked example. Fork it.

## What's published here

- `data/metadata/` — inventory, SHA-256s, decoded macOS attributes, PDF metadata, redaction/revision
  results (no personal data).
- `data/ocr_intelligence/` — OCR text of the intelligence memos (China/Venezuela/IC-process), scrubbed.
- `docs/dashboard.html` — a visual summary.
- `scripts/` — the full method.

**Deliberately not published:** the raw source PDFs (re-fetch them from the official URLs in
`manifest.json`) and the verbatim OCR of the Michigan FBI witness interviews — those concern **private
individuals**, and republishing their details is neither necessary for reproducibility nor responsible.
See [data/README.md](data/README.md).

## Provenance & method note

This analysis was **AI-assisted** (metadata parsing, OCR, drafting) and is **human-checkable end to end** —
that is the entire design. Source documents are U.S. Government works (public domain). See
[CITATION.cff](CITATION.cff) to cite this work.

## Verifying releases

Release tags are signed with the project's release key:

```
iridex-ai <iridex@carpedieminnovationsinc.com>
ed25519, sign-only · fingerprint: BA44 9C4B 93EE 08C3 C8C6  BB66 19B8 C479 4FA5 E399
```

Fetch the key (`gpg --keyserver hkps://keys.openpgp.org --recv-keys
BA449C4B93EE08C3C8C6BB6619B8C4794FA5E399`), check that its fingerprint matches the one printed above,
then run `git tag -v v1.0.0`. The GitHub web UI may label signed tags "Unverified" — that badge only
reflects keys uploaded to a GitHub account profile; the signature itself verifies with the key and
fingerprint above, independent of GitHub.

## License

Code: MIT. Derived data & text: CC-BY-4.0. Source documents: U.S. Government (public domain). See
[LICENSE](LICENSE).
