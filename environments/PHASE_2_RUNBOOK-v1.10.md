# PHASE 2 v1.10 — UTF-8 capture candidate runbook

> Status: `STOP / READY_FOR_FORMAL_OWNER_GATE`. This document does not authorize the formal 72-run.

## Delta from v1.9

v1.10 preserves the v1.9 tasks, AEH v0.2.0 wheel, answers, schedule, Codex argv and source-scope
boundaries. The only runtime change is shared UTF-8, `errors=replace` subprocess capture for AEH and
Codex stdout/stderr in the G3 external runner.

## Deterministic gates (no model call)

1. `python -m graders.cli phase2-v1.10-readiness` must pass.
2. The exact AEH 0.2.0 wheel and frozen answers digests must match `BASELINE.yaml`.
3. A child process emitting non-ASCII UTF-8 on stdout and stderr must be captured byte-completely.
4. A child process emitting malformed UTF-8 must return normally with U+FFFD replacement.
5. The full grader unit suite must pass from the `graders` directory.

## Evidence semantics

The v1.9 G3 transcript warning remains part of the historical record. v1.10 does not claim that the
old transcript became complete and does not consume or retry an Agent benchmark cell. The capture
regressions validate the corrected wrapper mechanics only.

## Formal lock

The formal 72-run and A01–A08 remain unauthorized. A passing v1.10 candidate is ready only for an
explicit Owner authorization decision.
