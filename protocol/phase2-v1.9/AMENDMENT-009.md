# AMENDMENT-009 — Codex global argv correction

- Protocol version: 1.9
- Date: 2026-08-25
- Basis: `reports/PHASE_2_PREFLIGHT_V1_8.md`
- Formal execution state: not started

The v1.8 deterministic gates verified the workspace sandbox and AEH headless policy, but its four
Codex processes exited before Agent sessions. The wrapper placed `--ask-for-approval` after `exec`,
where pinned Codex CLI 0.149.0 does not accept it.

v1.9 freezes argument ownership and order. Approval policy, model, sandbox and the native Windows
sandbox override precede `exec`; exec-only isolation/output args follow it. An exact-prefix `--help`
Gate proves parser acceptance without contacting a model. Historical v1.8 files and evidence remain
immutable.

All tasks, treatments, AEH inputs, schedule order, graders, hidden-test boundary and formal
authorization state otherwise remain unchanged.
