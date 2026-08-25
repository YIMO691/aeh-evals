# AMENDMENT-008 — Headless execution contract correction

- Protocol version: 1.8
- Date: 2026-08-25
- Basis: `reports/PHASE_2_PREFLIGHT_V1_7.md`
- Formal execution state: not started

The v1.7 four-run preflight was evidence-complete but failed before any coding change. The common
Codex command included `--ignore-rules`, which blocked shell tools, while G3 called AEH bootstrap
without explicit answers and therefore compiled fail-safe `ask` permissions into a headless run.

v1.8 removes `--ignore-rules` from the frozen Agent command and adds an Owner-authored AEH answers
file as a hashed G3 treatment input. The G3 runner accepts `--answers` and forwards its absolute path
to bootstrap. Historical v1.7 files and failed-run evidence remain immutable.

All other treatment variables, the AEH 0.2.0 artifact, tasks, hidden tests, schedule order, grading
rules and formal authorization state are unchanged. A complete four-cell preflight rerun is required
before the formal experiment may be considered.

