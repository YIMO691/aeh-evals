# PROTOCOL v1.7 DELTA — PHASE 2 READINESS

Status: `READY_FOR_PREFLIGHT`; Phase 2 execution remains unauthorized.

This delta creates a new protocol version. It does not edit or supersede the immutable Phase 1.1
v1.6 evidence record.

## Problems corrected

1. The historical RUNBOOK first prescribed group-first execution and later prescribed per-task
   stratified randomization. Both rules cannot govern the same 72-run experiment.
2. The G3 treatment named a fixed AEH commit but did not pin the released artifact that formal
   Phase 2 should evaluate.
3. The Phase 1.1 G3 runner and AEH inputs covered only TASK-004, so they were not a valid execution
   surface for the six-task pilot.

## v1.7 decisions

- Canonical ordering is the committed block schedule in `SCHEDULE.yaml`: each task/repetition block
  contains G0–G3 exactly once in a deterministic hash-derived order.
- AEH is pinned to the public v0.2.0 release, exact commit and exact wheel digest recorded in
  `BASELINE.yaml`.
- Every pilot task must have its own `aeh-inputs` and the G3 runner must derive scope hashes from
  the task-specific scope template without hard-coded source paths.
- The historical `protocol/FREEZE-v1.6.md`, `protocol/PROTOCOL.md`, Phase 1.1 reports and verdict are
  not rewritten.

## Authorization boundary

This delta authorizes deterministic readiness validation only. A new Owner decision is required
before a four-run preflight, any of the 72 formal runs, or A01–A08.
