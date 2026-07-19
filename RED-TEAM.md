# Adversarial Red-Team Review

> *"The first principle is that you must not fool yourself — and you are the easiest person to fool."*
> — Richard Feynman

Purpose: try to *break* every finding before publication. Each item states the claim, the strongest
refutation attempt, a verdict (**HOLDS** / **TIGHTEN** / **CUT**), and — for interpretive claims — a
falsification test (what evidence would overturn it). Tiers: **T1** reproducible fact · **T2** sourced
fact-check · **T3** interpretation.

## Tier 1 — reproducible facts

**1. macOS curation on one machine (T1).**
Refutation: could the AppleDouble/quarantine attributes be artifacts of *our* extraction, not the
original curator's Mac? No — the `._*` sidecars and `__MACOSX/` were stored *inside* the delivered ZIPs;
they were written by the machine that zipped them. Quarantine strings decode cleanly (valid agents,
epoch times, UUIDs), confirming correct parsing. **HOLDS.** Falsification: a non-Mac origin would leave
no AppleDouble — but they are present in all four archives.

**2. Four Chrome bundle-downloads, 38-second window (T1).**
Refutation: do identical per-section quarantine **event UUIDs** really prove *bundle* downloads vs. 60
coincidental same-second events? Same-UUID across a whole section is the documented signature of one
download event whose quarantine propagated to extracted contents. **HOLDS.** (Wording: say "four download
events, one per section," not "four ZIPs" — the container form is inferred.)

**3. Metadata stripped from 55/58; 3 retain producer (T1).** Directly re-derivable from `/Info`+XMP.
**HOLDS.**

**4. Three byte-identical duplicates (T1).** SHA-256 match. **HOLDS.**

**5. Redaction integrity (T1).**
Refutation: "technically sound" overclaims — we tested vector-box-over-text, multi-image overlays, and
incremental-revision recovery, but **not** exhaustively (e.g., orphaned objects, embedded thumbnails, and
burned-in raster text is unrecoverable *by definition* so "sound" there is untestable, not proven).
**TIGHTEN** → "No recoverable text was found beneath redactions via the standard vectors tested; scanned
redactions appear flattened (burned-in), which we can confirm as single-image but not audit further."

**6. "200M records" = a 2016 dataset (T1/T2).**
Refutation: are we sure the WHTF statement's "200 million" is the *same* number as the memo's
204,822,241? We are linking a public figure to the "200M Voter Records" memo's own text. Strong but not
certain. **TIGHTEN** → attribute precisely: "the '200M Voter Records' memo itself describes a **2016
dataset of 204,822,241 records** on a PRC-held list on which 'most of the entries were targets in other
countries.'"

**7. Declassification-by-Counsel stamps (T1).**
Refutation: names are **OCR-derived** ("WARRINGTON," "Ratcliffe") and may be misread. The *pattern*
(release authority = Counsel to the President, dated 10 Jul 2026) is consistent across dozens of pages.
**TIGHTEN** → flag that proper names are OCR-read and should be verified against the official record before
being asserted; the authority-and-date pattern is robust.

**8. Michigan case arc + declinations (T1).** Re-derivable from the OCR'd timeline + declination emails;
corroborated by independent reporting. **HOLDS.**

## Tier 2 — sourced fact-check

**9. All seven claim verdicts (T2).**
Refutation: these depend on external sources being correct and current. They are well-supported by
multiple reputable outlets, court records, and nonpartisan research bodies, **and** several are
corroborated by the package's own primary text (e.g., the FBI declination; the "ALTERNATIVE ANALYSIS"
stamp). The seventh (CISA) row's corroboration is primarily the package's own primary document plus
CISA's public program documentation. **HOLDS**, with the standing caveat that T2 rests on cited
third-party sources.

**10. State correlation classifications (T2).**
Refutation: the sued/complied lists came from a **secondary news summary**, and at least one state
(Oklahoma) appeared in *both* lists — a real data conflict. **TIGHTEN** → label the DOJ-posture columns as
"per secondary reporting, not primary court dockets," flag the Oklahoma conflict, and keep only the
conclusion that survives it: the named states are drawn from the intelligence memo itself (primary-verified)
and are **not** a curated political target list.

## Tier 3 — interpretation (must stay fenced)

**11. "Framing invites an inference the intelligence doesn't state."**
Refutation / steelman: "compromised voter records" is *literally* true (data was acquired), so is this
unfair? The gap is between the true narrow claim and the *implied* conclusion of altered elections. Because
the underlying memos' own text describes collection + influence and **explicitly** carries the IC mainline
("not deployed influence efforts intended to change the outcome"), the gap is documentable from primary
text, not opinion. **HOLDS** as the strongest interpretive claim — but phrase as "invites an inference,"
never "they lied." Falsification: if any memo asserted altered rolls/ballots/tabulation, this collapses —
none does (checked across all OCR'd memos).

**12. "Influence effort aimed inward / timed to the legal window / to advance the SAVE agenda."**
Refutation / steelman: a good-faith reading — the administration genuinely believes foreign threats are
underappreciated and wants states to harden systems — is supported by the sober CISA report and the
footnoted Database-Threats overview. My motive-attribution is inference from timing + framing + the
inclusion of the court-rejected Venezuela theory + partisan language in one document. **TIGHTEN** → present
as *one reading* alongside the good-faith reading; do not state motive as fact. Falsification tests to
publish alongside it: (a) had the release omitted the Venezuela theory and partisan phrasing, the
sincere-hardening reading would dominate; (b) had it led with the IC mainline judgment rather than the
minority view, "suppression" framing would be unsupported; (c) if the timing were unrelated to the
quiet-period/litigation calendar, the "calibrated" claim weakens.

**13. "Conclusion preceded the evidence" (June 24 draft).**
Refutation: the 24 Jun date is one document's CreationDate (which can reflect a reused template), and it's
the noncitizen wrapper — not proof the *whole* package's conclusion predated *all* evidence. **TIGHTEN** →
"at least one framing document carries a creation date ~3 weeks before the evidence bundle was assembled."

**14. "Mattermost ⇒ security-conscious/self-hosted shop."**
Refutation: the quarantine agent only shows the file arrived via the Mattermost desktop app; the
"security-conscious/self-hosted" gloss is speculation. **CUT** the gloss → state only "one framing document
was received via Mattermost (a team-chat platform), separate from the bulk download."

## Net actions applied before publication
- TIGHTEN wording on: redaction scope (#5), the 200M attribution (#6), OCR-name caveat (#7), state-posture
  sourcing + Oklahoma conflict (#10), framing phrasing (#11), motive-as-one-reading + falsification tests
  (#12), the June-24 claim (#13).
- CUT the Mattermost editorializing (#14).
- Everything in T1/T2 that HOLDS is retained; every T3 item is explicitly labeled interpretation with a
  falsification test and a steelman.
