# CLAUDE.md
version: 1.0
role: code-surface project layer — election-records-forensics-2026
deploy: auto-loaded (Code walks cwd upward)
status: active

Inherits the account-level canon (auto-composed). Adds repo specifics only.

- **Owner:** carpe-diem-innovations-inc (admin). **Surface:** code. **Visibility:** public.
- **Role:** reproducible forensic analysis of an election-records release. Public repo — every
  claim must be reproducible and sourced (README, METHODOLOGY.md, LIMITATIONS.md, RED-TEAM.md
  set the bar). No chat slug.
- **Stack:** Python — `requirements.txt` / `requirements-dev.txt`; pipeline in `scripts\`,
  tests in `tests\`, inputs in `data\`, site in `docs\` (GitHub Pages dashboard).
- **Guardrail:** provenance-critical record. Tie every material claim to its source; stop and
  flag gaps rather than infer. Do not weaken reproducibility (CITATION.cff, manifest, verify
  workflow) without saying so.
