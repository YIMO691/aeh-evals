# Phase 1.1 Evidence Closure

- Closure date: 2026-08-19
- Protocol: v1.6 (unchanged; post-freeze amendments = 0)
- Evaluation commit before closure: `3267e8a`
- Verdict: `PHASE_1_1_FROZEN_AND_REPLAYED`
- Owner gate: G5 accepted for the Design & Evidence Baseline v0.2
- Commit gate: G6 completed at `3267e8a`; this closure is a new, non-amending commit
- Phase 2 / 72-run: `authorized=false`

## Closed findings

| Finding | Closure |
|---|---|
| FINDING-P11-001 | Runner now preserves positional targets for bootstrap/doctor and uses `--workdir` only for change subcommands; regression tests added. |
| FINDING-P11-002 | TASK-004 plan covers AC-002-01. |
| FINDING-P11-003 | RED signature matches observed unittest output. |
| FINDING-P11-004 | Replay exposes both execution `status` and acceptance `overall`; verdict prefers `overall`. |

## Evidence identity

Phase 1 v1.5 sources retain the `EVAL-P1-*` namespace. Phase 1.1 v1.6 sources use
`EVAL-P11-*`; the two generations of `RUN-D001..D004` are not interchangeable.

The committed result table reads metrics from `run.yaml` and therefore records tool-call counts
`5 / 4 / 4 / 22`. The full raw evidence remains internal; the public checksum manifest provides
stable file identities without publishing session logs.

## Claim boundary

This closure validates the frozen protocol and the minimum external-runner mechanism. It does not
establish product efficacy, attack resistance, economics, cross-domain validity, or authorization
to start the 72-run pilot.
