# Findings

Findings are separated by **evidentiary tier**. Read the tier before the claim.

- **Tier 1 — Reproducible fact.** Re-derivable from the source files with the scripts here. If you run the
  method, you get the same result.
- **Tier 2 — Sourced fact-check.** Comparison of the documents' claims against the public record; depends
  on cited third-party sources being accurate.
- **Tier 3 — Interpretation.** Reasoned inference. Presented with a steelman and a falsification test.
  Not asserted as fact.

An adversarial review of every item is in [RED-TEAM.md](RED-TEAM.md); its wording corrections are applied
below.

---

## Tier 1 — Reproducible facts

> *Re-derivability note:* T1.1–T1.4 are checkable against the committed `data/metadata/` alone. T1.5
> quotes the committed OCR in `data/ocr_intelligence/` (verify quotes against the page images — OCR can
> drop small print). T1.6 quotes Michigan documents whose OCR is deliberately **not** committed; re-derive
> it from the source archives with `scripts/ocr_michigan_all.py` (see `data/README.md`).

**T1.1 — The package was assembled on one macOS machine, and the assembly is timestamped.**
The archives retained macOS filesystem residue. The `com.apple.quarantine` attributes decode to **four
download events, one per section, within ~38 seconds** on 2026-07-16 (16:02:35–16:03:13 UTC), each sharing
one per-section event ID (the signature of a bundle download whose quarantine propagated to its contents).
Two narrative "FINAL" documents were added separately minutes later — one saved via **Adobe Acrobat**, one
received via **Mattermost** (a team-chat platform). Exactly two files carry an opened-on-the-machine
residue (`com.apple.lastuseddate`): the Mattermost-received statement and — notably — one Chrome-bundled
evidence PDF (the NICM "Vulnerabilities in US 2020 Election Infrastructure" memo). The Acrobat-saved
report carries no open-residue attribute; its arrival stamped by Acrobat implies it passed through that
application, but the data records the *agent*, not an "open." The Michigan folder's `.DS_Store` retains a working-folder name not shipped in the package:
"NEW ADDED FOR UPLOAD 7.15.26" (decoded to `data/metadata/dsstore.json` by `macos_forensics.py`).

**T1.2 — Authoring metadata was stripped from the evidence but not the narrative.**
55 of 58 PDFs carry no Author/Creator/Producer. Only 6 retain any internal `/Info` dates: the 3 toolchain
exceptions — two narrative "FINAL" documents authored in **Microsoft Word / Acrobat** (one with a creation
date ~3 weeks before release) and one 2025-era FBI document processed by a different toolchain (`iText`) —
plus the Venezuela note and the (duplicated) CIA Wire Memo, whose 2026-07-14 processing timestamps
survived. XMP residue adds a hardware fingerprint: four scanned memos retain
`xmp:CreatorTool = "Hewlett-Packard MFP"` — the three "Summary" framing memos were scanned on the same
scanner model, consecutively, on **2026-07-14, 22 and 12 seconds apart** (15:27:30 → 15:28:04 ET, a
34-second span), two days before release. (Identical model string + sequential timing; the XMP carries no
device serial, so "same physical device" is the natural reading, not a recorded fact.) All surviving
`/Info`/XMP creation-modification dates fall in **2026-07-11 → 07-16** (plus the 06-24 Word draft and the
2025 FBI document; a 2024-11-19 Microsoft sensitivity-label `SetDate` also survives inside the CISA
report).

**T1.3 — Three documents are byte-identical duplicates re-filed under two sections** (confirmed by
SHA-256), alongside filename typos and inconsistent redaction-suffix conventions — consistent with manual
assembly.

**T1.4 — Redactions held under the vectors tested.**
No meaningful text was recoverable beneath redaction marks (the only extractable item corpus-wide was the
form label "Dated:"). Born-digital text was genuinely removed; scanned redactions are single flattened
images. The multiple `%%EOF` markers were **linearization** ("Fast Web View"), not recoverable prior
revisions. *Scope:* this tests the standard recovery vectors (text under marks, un-flattened image layers,
incremental-revision recovery); burned-in raster redaction is unrecoverable by definition and is confirmed
single-image, not audited further.

**T1.5 — What the intelligence memos say (from OCR of the scanned documents).**
Every substantive memo describes **collection of voter-registration/PII data** and **social-media influence
operations**; none states that voter rolls, ballots, or tabulation were altered. Specifics from the text:
- The "200M Voter Records" memo itself describes a **2016 dataset of 204,822,241 records** on a PRC-held
  list of "likely leaked, compromised data" on which "most of the entries were targets in other countries."
- The "18 States" memo describes obtaining voter data for "U.S. person matching and public opinion
  analysis."
- The most forward-leaning China memo is stamped **"ALTERNATIVE ANALYSIS"** and carries the Intelligence
  Community mainline judgment verbatim: "Beijing has **not** deployed influence efforts intended to change
  the outcome"; its dissent describes only "low-level, exploratory steps" at "low-to-medium confidence."
- The Venezuela note, in the CIA's own words, "did not definitively confirm that large-scale electronic
  fraud was successfully executed in specific Venezuelan elections" and "was **not** coordinated within the
  Intelligence Community." (The second quote is a small-print page-2 footer line — "This product reflects a
  CIA perspective and was not coordinated within the Intelligence Community" — which the committed OCR text
  missed; verify it against the page image.)
- *Caveat:* proper names in these documents are **OCR-read** and should be verified against the official
  record before being asserted. The release authority stamp pattern ("Counsel to the President," dated
  10 July 2026) is consistent across dozens of pages.

**T1.6 — Michigan: a paid-canvasser registration-fraud case, caught then declined.**
The FBI documents reconstruct the arc: the **Muskegon City Clerk detected** fraudulent applications
(non-existent addresses, invalid phones, identical handwriting) and referred them (Oct 2020); canvassers
were **paid per registration** with quotas, incentivizing padding; database checks on the **107** flagged
applications found **91** listing individuals with **no database trace** (and of the 16 real individuals,
only 4 signatures matched); federal prosecutors ultimately **declined** ("not seeking further …
prosecutive action"). This is *application* fraud caught before processing — not fraudulent ballots or
altered votes.

---

## Tier 2 — Sourced fact-check

> *"Extraordinary claims require extraordinary evidence."* — Carl Sagan

Each verdict compares a claim associated with the release to the public record. Full source links are in
[Sources](#sources) below.

| Claim | Verdict | Basis |
|---|---|---|
| China "compromised" 200–220M voter records | **Misleading framing** | Commercial voter files — compiled largely from public state records and sold openly (32 states + DC) — are marketed as covering nearly every U.S. adult (full files ≈200M records, Pew); acquisition ≠ altering votes. |
| ≥18 states' rolls "compromised" by the PRC | **Disputed / conflated** | Foreign probing is documented (2016 activity mainly attributed to Russia); "compromised" blends acquisition, probing, breach. |
| China changed the 2020 outcome (implied) | **Disputed** | 2021 declassified ICA: China "considered but did not deploy" outcome-changing influence efforts; the minority view + DNI dissent contest whether influence was *attempted* — no IC view, majority or minority, asserted the outcome was changed; material largely already known. |
| Michigan "fake voter" scheme (GBI Strategies) | **Real case; theft framing unsupported** | Applications caught pre-processing; no fraudulent ballots; no charges (corroborated by the package's own declination memos). |
| 250k+ noncitizens registered in 4 states | **Unverified / likely overstated** | State SAVE checks flag ~0.01–0.02% of registrants, and a large share of investigated flags turn out to be citizens; completed audits confirm far fewer. The tool has documented false positives and was court-limited (June 2026). |
| CIA "Venezuela machines" (implied 2020 impact) | **Debunked** | Dominion founded in Canada (2002); Smartmatic not used in 2020 swing states; $787.5M Dominion settlement. |
| CISA found election-software vulnerabilities (2019–24) | **Established / credible** | Real cooperative CISA/INL testing; the report documents vulnerabilities needing remediation, explicitly not exploited attacks. |

Sources named here are linked in full in [Sources](#sources).

---

## Tier 3 — Interpretation (fenced; not asserted as fact)

**T3.1 — The public framing invites an inference the intelligence does not state.**
"Compromised voter records" is literally true (data was acquired), but the release's presentation invites
the stronger inference that elections were *altered* — which the underlying memos' own text does not
support and, in the mainline judgment, contradicts. *Falsification:* if any memo asserted altered
rolls/ballots/tabulation, this collapses. None checked does.

**T3.2 — One reading: an inward-facing effort using real intelligence as a credibility carrier.**
The release couples genuinely-declassified espionage/influence material with narrative documents that
supply framing the raw files don't establish; it lands amid live litigation over the administration's
voter-data and citizenship-verification initiatives, shortly before the pre-election "quiet period."
*Steelman (competing reading):* a good-faith effort to warn states and harden systems — supported by the
sober CISA report and the footnoted threat overview. *Falsification tests:* (a) had the release omitted the
court-rejected Venezuela theory and partisan phrasing, the good-faith reading would dominate; (b) had it
led with the IC mainline rather than the minority view, a "suppression" framing would be unsupported;
(c) if the timing were unrelated to the litigation/quiet-period calendar, the "calibrated" reading weakens.

**T3.3 — Sequencing.** At least one framing document carries a creation date ~3 weeks before the evidence
bundle was assembled — consistent with narrative preceding final assembly. *Steelman:* a single document's
creation date is weak evidence — templates carry old dates, and drafting a summary before assembling its
attachments is normal staff work. *Falsification:* if the 06-24 date is shown to be a template artifact
(e.g., other unrelated documents from the same office share it), the sequencing inference collapses.

**T3.4 — The named states are intelligence-derived, not a curated target list.**
The states named publicly appear in the underlying PRC memo's own text (primary-verified), and split as a
near-even partisan mirror rather than a one-sided list. *Steelman:* even an intelligence-derived list can
be deployed selectively — provenance does not preclude political use. *Caveat:* the DOJ-posture
classification used to test this came from **secondary reporting, not primary court dockets**, and had at
least one conflict (Oklahoma appeared in two lists); the surviving conclusion is only that the list is
**not** cherry-picked. *Falsification:* if any named state does not appear in the underlying memos' own
text (check the source images — the committed OCR does not capture every state list), the
"intelligence-derived" conclusion fails for that state.

---

## Sources

Tier-2 verdicts rest on the following (public record as of July 2026); the package's own primary text
corroborates several (see Tier 1).

- Pew Research Center — [Commercial voter files and the study of U.S. politics](https://www.pewresearch.org/methods/2018/02/15/commercial-voter-files-and-the-study-of-u-s-politics/)
- Ballotpedia — [Availability of state voter files](https://ballotpedia.org/Availability_of_state_voter_files)
- Senate Select Committee on Intelligence — [Russian Active Measures, Vol. 1: Russian Efforts Against Election Infrastructure](https://www.intelligence.senate.gov/sites/default/files/documents/Report_Volume1.pdf) (2016 state-targeting attribution)
- Nextgov/FCW — [Trump stretches declassified China intelligence into broader 2020 election claims](https://www.nextgov.com/cybersecurity/2026/07/trump-stretches-declassified-china-intelligence-broader-2020-election-claims/414837/) (also links the two prior primary IC source PDFs on dni.gov — the 2020 NICM assessment and the 2021 ICA — for direct comparison)
- Washington Examiner — [Minority view in intelligence assessment argues China meddled in 2020 to hurt Trump](https://www.washingtonexaminer.com/news/minority-view-intelligence-assessment-argues-china-2020-hurt-trump) (Mar 18, 2021)
- Bridge Michigan — [Muskegon fake voter applications probed in 2020, referred to FBI](https://bridgemi.com/michigan-government/muskegon-fake-voter-applications-probed-2020-referred-fbi-nessel-says/)
- Newsweek — [Fact check: Did Michigan police uncover a 2020 Democratic election plot?](https://www.newsweek.com/fact-check-did-michigan-police-uncover-2020-democratic-election-plot-1820154)
- FactCheck.org — [Flaws in government tool to ID noncitizen voters](https://www.factcheck.org/2026/03/flaws-in-government-tool-to-id-noncitizen-voters/)
- Brennan Center — [Watch out for false voter-fraud claims fueled by the SAVE program](https://www.brennancenter.org/our-work/research-reports/watch-out-false-voter-fraud-claims-fueled-save-program)
- Votebeat — [Judge blocks Trump administration's overhaul of SAVE database](https://www.votebeat.org/national/2026/06/22/judge-rules-against-trump-overhaul-save-database-noncitizen-voters/) (D.D.C., June 22, 2026)
- Cato Institute (commentary) — [Voting-machine conspiracy theories harm U.S. cybersecurity](https://www.cato.org/blog/voting-machine-conspiracy-theories-harm-us-cybersecurity)
- Lawfare (analysis) — [Five foreign election conspiracy theories making the rounds again](https://www.lawfaremedia.org/article/five-foreign-election-conspiracy-theories-making-the-rounds-again)
- Delaware Superior Court — *US Dominion, Inc. v. Fox News Network*: summary judgment finding the statements about Dominion false (Judge Eric M. Davis, Mar 31, 2023) and $787.5M settlement (Apr 18, 2023; widely reported)
- CISA — [Election security topic page](https://www.cisa.gov/topics/election-security) (cooperative election-technology testing with Idaho National Laboratory; supports the CISA-report verdict row)
- 2021 declassified Intelligence Community Assessment — [*Foreign Threats to the 2020 US Federal Elections* (ICA 2021-00078D)](https://www.dni.gov/files/ODNI/documents/assessments/ICA-declass-16MAR21.pdf)

**Independent analyses of this release** (secondary; content-focused coverage of the same corpus,
complementary to the file-level approach here):

- GlobalSecurity.org — [The July 2026 Election Documents Release: What It Amounts To](https://www.globalsecurity.org/intell/library/reports/2026/0717/analysis.html) (2026-07-17; the only other long-form treatment — a full documentary/content analysis of all four collections, with per-collection analyses and OCR transcripts)
- FactCheck.org — [FactChecking Trump's Election Security Speech](https://www.factcheck.org/2026/07/factchecking-trumps-election-security-speech/) (2026-07-17)
- BBC Verify — [Do declassified files support Trump's election security claims?](https://www.bbc.com/news/articles/cz64wx8yjjdo) (notes the heavy redaction; flags the DHS one-pager's noncitizen-registration figure as unverifiable — no underlying data or methodology published)
- CBC News — [Fact-checking Donald Trump's national address on U.S. election integrity](https://www.cbc.ca/news/world/donald-trump-speech-election-integrity-fact-check-9.7273535) (line-by-line comparison of the two cited CIA documents against the spoken claims)
- NPR — [In primetime speech, Trump doesn't provide evidence for illegal voting](https://www.npr.org/2026/07/16/nx-s1-5896448/trump-election-address)
- CBS News — fact-check rating the 220M-records claim "Misleading," citing the 2020 CISA/FBI joint bulletin on the availability of U.S. voter data (published via CBS News' social channels, 2026-07-17)
