# Contributing — add your finding to the pile

The point of this kit is that the next person doesn't have to start from zero. Contributions that make
the record stronger are welcome; contributions that make it louder are not.

## Ground rules

1. **Reproduce before you assert.** Run `python scripts/trust_but_verify.py` first. If your finding
   depends on the source files, anchor it to the SHA-256s in `manifest.json`.
2. **Tier your claim.** Every finding must declare its tier (see [FINDINGS.md](FINDINGS.md)):
   - **Tier 1** — reproducible from the source files with code you include.
   - **Tier 2** — a comparison against the public record, with linked sources.
   - **Tier 3** — interpretation. Must include a **steelman** of the competing reading and a
     **falsification test** (what evidence would overturn it). Tier 3 stated as fact will be rejected.
3. **No PII.** Nothing that names or identifies a private individual, even if it appears in the source
   documents. Public officials in their official capacity only.
4. **Neutral wording.** No verdict-language about living people's intent ("lied", "stole", "proves").
   The red-team bar: would the sentence survive [RED-TEAM.md](RED-TEAM.md)?

## How

- **A finding:** open an issue with the *Finding* template — it walks through the tier requirements.
- **A refutation:** adversarial review is explicitly invited — a finding that breaks or weakens an
  analysis here is worth more than one that extends it; use the same *Finding* template.
- **A correction:** issues or PRs welcome; corrections to Tier-1 outputs should come with the command
  that re-derives the corrected value.
- **Code:** keep scripts flat and readable (each is a top-to-bottom read, no framework); add a unit test
  in `tests/` for any new parsing primitive; `pytest` and `trust_but_verify.py --fast` must pass.

## Licensing of contributions

Code contributions are accepted under MIT; text/data contributions under CC-BY-4.0 (see [LICENSE](LICENSE)).
