# Phase 2 v1.8 four-cell preflight result

- Date: 2026-08-25
- Evaluated candidate: commit `7145ba8046a725f1c4e525b28bac7eb32bb3cbcb`, tree
  `6e338aaa4d5214d7c43d03a35e90d8bf919d19b3`
- Scope: first scheduled block only — `TASK-004`, repetition 1, order `G3 → G1 → G2 → G0`
- Machine verdict: `reports/phase2-preflight-v1.8-verdict.yaml` →
  **PREFLIGHT_FAILED_CODEX_CLI_CONTRACT**
- Boundary: this result tests execution mechanics only and provides no AEH value conclusion.

## Result matrix

| Run | Group | Codex exit | Agent session | Task | Assurance | Scope | Secrecy | Bundle |
|---|---|---:|---|---|---|---|---|---|
| RUN-P281 | G3 | 2 | not started | ABORTED | NOT_EXECUTED | OK | OK | SELF_SUFFICIENT |
| RUN-P282 | G1 | 2 | not started | ABORTED | N/A | OK | OK | SELF_SUFFICIENT |
| RUN-P283 | G2 | 2 | not started | ABORTED | N/A | OK | OK | SELF_SUFFICIENT |
| RUN-P284 | G0 | 2 | not started | ABORTED | N/A | OK | OK | SELF_SUFFICIENT |

All four manifests are schema-valid. Hidden-test secrecy is intact, every bundle is self-sufficient,
and all three adjacent cross-group comparisons report `FREEZE_IDENTICAL`. No model session started,
no model tokens were consumed, and no Agent changed product source or AEH machine truth.

## What v1.8 fixed successfully

Before the four cells, the native Codex workspace permission profile passed a no-model read/write
smoke test. The exact AEH 0.2.0 wheel also bootstrapped a fresh TASK-004 restoration using the
Owner-authored answers file. Its managed policy correctly allowed shell/source modification while
denying commit, push, and web access. These checks close the two defects recorded by v1.7.

## Blocking finding P2-PF-003

v1.8 added `--ask-for-approval never` to the arguments placed after `codex exec`. Codex CLI 0.149.0
rejected that option at argument parsing with exit code 2 before starting an Agent session. The
identical failure occurred in G3, G1, G2, and G0. The preflight contract prohibits changing flags
between groups or selectively retrying, so the four-cell block was completed without mutation.

This is an operator CLI-contract defect, not evidence about coding ability or AEH effectiveness.
A subsequent candidate must use argv accepted by the pinned CLI—for example, by expressing approval
policy in a supported global/config position—and prove exact argv parsing before any benchmark cell.

## Evidence integrity

Raw run evidence remains local under `runs/RUN-P281` through `runs/RUN-P284`. Session SHA-256:

- RUN-P281: `06cc272d919a94b7441f41e57362271ee52af163b0a7f0cdc737df492a95df82`
- RUN-P282: `c206a405769cb087010d604fab55fd38b0612d2dfc6435797cfba6df5240b7e7`
- RUN-P283: `c206a405769cb087010d604fab55fd38b0612d2dfc6435797cfba6df5240b7e7`
- RUN-P284: `c206a405769cb087010d604fab55fd38b0612d2dfc6435797cfba6df5240b7e7`

G3 reached `VALID_RED`; AEH artifacts are present; the Agent did not invoke AEH; GREEN and validator
replay were not executed. Therefore G3 assurance is `NOT_EXECUTED`, not `BLOCKED` or `MERGE_READY`.

## Gate decision

`phase2_72_run.authorized` remains `false`. A01–A08 remain unauthorized. No additional Agent run is
authorized. The next eligible action is a new protocol correction plus a separate Owner gate.
