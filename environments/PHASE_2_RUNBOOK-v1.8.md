# PHASE 2 v1.8 — Corrected candidate runbook

> Status: `STOP / READY_FOR_PREFLIGHT`. This document does not authorize the formal 72-run.

## Delta from v1.7

v1.8 preserves the v1.7 task set, AEH v0.2.0 wheel, schedule order, grading boundaries and source
scope rules. It changes only the two execution-contract defects established by the v1.7 preflight:

1. Codex runs must not use `--ignore-rules`. The frozen invocation uses an explicit model,
   `--sandbox workspace-write`, `--ask-for-approval never`, `--ephemeral`,
   `--ignore-user-config` and `--json`.
2. G3 bootstrap must receive `environments/G3-assets/answers-v1.8.yaml`. The Owner-authored policy
   allows shell and source modification for the isolated task worktree while denying commit, push
   and web access.

## Pre-Agent gates

1. `python -m graders.cli phase2-v1.8-readiness` must pass.
2. The exact AEH 0.2.0 wheel digest must match `BASELINE.yaml` before installation.
3. Run `codex sandbox -P :workspace` against a disposable directory and prove that a file can be
   read and a new file can be written under the built-in workspace permission profile, without
   invoking a model.
4. Bootstrap a disposable restored TASK-004 worktree with the frozen answers and verify the managed
   Agent section says `shell: allow`, `modify_source: allow`, and commit/push/web are denied.

## Four-run preflight

Use fresh worktrees and fresh ephemeral sessions in the inherited first-block order
`TASK-004/G3 → G1 → G2 → G0`. Run exactly one cell per group. Preserve raw local evidence and grade
visible tests, hidden tests, source scope, secrecy, functional outcome and AEH assurance outside the
Agent session. A defect invalidates the preflight; do not selectively retry or change the contract
between groups.

## Formal lock

The 72-run and A01–A08 remain unauthorized. A successful preflight is necessary but does not itself
authorize either experiment.
