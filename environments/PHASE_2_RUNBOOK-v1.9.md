# PHASE 2 v1.9 — Corrected argv candidate runbook

> Status: `STOP / READY_FOR_PREFLIGHT`. This document does not authorize the formal 72-run.

## Delta from v1.8

v1.9 preserves the v1.8 tasks, AEH v0.2.0 wheel, answers, schedule, grading and source-scope
boundaries. It changes only the Codex argv defect demonstrated by the v1.8 four-cell preflight.

The exact prefix is split by parser ownership:

1. Global args before the subcommand: `--ask-for-approval never`, explicit model/sandbox, and
   `--config windows.sandbox=\"unelevated\"`.
2. Subcommand: `exec`.
3. Exec args after the subcommand: `--ephemeral --ignore-user-config --json`.

`--ignore-rules` remains forbidden. The Windows helper mode is explicit so ignoring the user config
does not make native sandbox selection depend on machine-local settings. The no-model probe selected
`unelevated` because `elevated` required an interactive administrator helper installation.

## Pre-Agent gates

1. `python -m graders.cli phase2-v1.9-readiness` must pass.
2. The exact AEH 0.2.0 wheel and frozen answers digests must match `BASELINE.yaml`.
3. Append `--help` to the exact frozen argv prefix and require Codex CLI 0.149.0 to exit zero. This
   validates global/subcommand parser placement without starting a model session.
4. Run the native sandbox with the frozen `windows.sandbox=\"unelevated\"` override and built-in
   `:workspace` permission profile; prove disposable in-workspace read/write without a model call.
5. Bootstrap a fresh TASK-004 worktree with the frozen answers and verify shell/source are allowed
   while commit/push/web are denied.

## Four-cell preflight

Use fresh worktrees and ephemeral sessions in the inherited order `TASK-004/G3 → G1 → G2 → G0`.
Run exactly one cell per group. Preserve raw evidence and grade outside the Agent. A defect
invalidates the block; do not retry or mutate the contract between groups.

## Formal lock

The 72-run and A01–A08 remain unauthorized. A successful preflight does not authorize either.
