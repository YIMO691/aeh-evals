# Phase 2 v1.7 four-run preflight result

- Date: 2026-08-25
- Evaluator: `ddb37a427cc9ce7c0064addd834f2b946389fdf1`
- Scope: first scheduled block only — `TASK-004`, repetition 1, order `G3 → G1 → G2 → G0`
- Machine verdict: `reports/phase2-preflight-v1.7-verdict.yaml` → **PREFLIGHT_FAILED_ENVIRONMENT_CONTRACT**
- Boundary: this result tests execution mechanics only and provides no AEH value conclusion.

## Result matrix

| Run | Group | Agent claim | Visible | Hidden | Scope | Secrecy | Task | Assurance | Seconds | Tokens |
|---|---|---|---|---|---|---|---|---|---:|---:|
| RUN-P201 | G3 | INCOMPLETE | FAIL | FAIL | OK | OK | FAIL | BLOCKED | 140 | 40,230 |
| RUN-P202 | G1 | INCOMPLETE | PASS | FAIL | OK | OK | FAIL | N/A | 144 | 59,464 |
| RUN-P203 | G2 | INCOMPLETE | PASS | FAIL | OK | OK | FAIL | N/A | 159 | 80,337 |
| RUN-P204 | G0 | INCOMPLETE | PASS | FAIL | OK | OK | FAIL | N/A | 173 | 99,269 |

All four run manifests are schema-valid, hidden-test secrecy is intact, every bundle is
self-sufficient, and all three adjacent cross-group comparisons report `FREEZE_IDENTICAL`.
No Agent changed production source, so hidden tests correctly failed in every group.

## Blocking findings

### P2-PF-001 — Codex execution policy was over-constrained

The preflight contract added `--ignore-rules` while selecting `workspace-write`. Codex then rejected
even read-only shell commands as blocked by policy in G0, G1, and G2. The CLI process exited zero
because the Agent honestly reported that it was blocked; the independent grader still recorded
`task_outcome: FAIL`.

This is an operator contract defect, not evidence about coding ability or AEH effectiveness.
The next candidate must remove `--ignore-rules`, retain a frozen explicit model/sandbox, and prove
the sandbox helper can read and write inside a disposable restored repository before consuming any
benchmark invocation.

### P2-PF-002 — G3 default bootstrap policy conflicts with headless execution

The v1.7 G3 runner calls `aeh bootstrap` without `--answers`. AEH 0.2.0 therefore installs fail-safe
defaults including `permissions.shell: ask` and `permissions.modify_source: ask`. In a headless
Agent run there is no interactive Owner approval path. RUN-P201 reached `VALID_RED`, captured the
trusted before-hash, and invoked Codex; Codex requested approval instead of editing source. The
Controller then observed `GREEN_FAILED`, so verify was not reached and assurance is `BLOCKED`.

The next protocol candidate needs a committed, schema-valid evaluation `answers.yaml` and must pass
it to bootstrap. For this isolated coding treatment, shell and source modification must be an
explicit Owner-authored `allow`; commit, push, and web access remain denied. This is treatment input
and must be hashed into the canonical input manifest.

## Evidence integrity

Raw runs remain local under `runs/RUN-P201` through `runs/RUN-P204`, per repository policy. Session
log SHA-256 digests are:

- RUN-P201: `baa9857193ed88325e76cef84b8cfed2e9f744b4de6ffa4f4ae0ff8ad8262d16`
- RUN-P202: `5911da8ac047fc18e440386055c8f1aeb84a1ddcacb7cc1e047d8770819041e0`
- RUN-P203: `d22bc25c0163e7f53a5602cac3a4afd239b40c829350dd15592b8624a9c76e2f`
- RUN-P204: `9455bdd39730e6894873784b53c7e194c9286b480033c568b8006d81cefdbc3e`

G3 evidence facts: AEH artifacts present; Agent did not invoke AEH CLI; validator replay did not run;
the Controller stopped at `GREEN_FAILED`. A pre-Agent PowerShell forwarding failure was retained
separately and does not count as an Agent invocation because `codex.exe` never started.

## Gate decision

`phase2_72_run.authorized` remains `false`. A01–A08 remain unauthorized. Per the preflight policy,
the four runs are not patched or selectively retried. The next eligible action is to create a new
protocol candidate with both fixes, validate it deterministically, and request separate Owner
authorization for a complete four-run rerun.

