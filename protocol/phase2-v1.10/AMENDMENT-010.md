# AMENDMENT-010 — UTF-8 transcript capture correction

- Protocol version: 1.10
- Date: 2026-08-25
- Basis: `reports/PHASE_2_PREFLIGHT_V1_9.md`
- Formal execution state: not started

The v1.9 four-cell preflight completed all Agent sessions and functional checks, but the G3 wrapper
decoded UTF-8 Codex JSONL through the Windows ANSI code page. A non-ASCII byte terminated the
capture reader and truncated `session.log`.

v1.10 routes both AEH and Codex captured stdout/stderr through one explicit UTF-8,
replacement-safe helper. Deterministic no-model regressions prove that non-ASCII UTF-8 is retained
and malformed bytes are replaced without losing the subprocess result.

Tasks, treatments, argv, AEH inputs, schedule, hidden-test boundary and authorization state remain
unchanged. No Agent benchmark run is consumed by this correction. Historical v1.6-v1.9 evidence
remains immutable, and the formal 72-run and A01-A08 remain separately Owner-gated.
