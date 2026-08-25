# Phase 2 v1.9 four-cell preflight result

- Date: 2026-08-25
- Evaluated candidate: commit `07de77e213ac115b648abd54f80271dd01965def`, tree
  `0f5f1970719dd540298bc3d34910b7290182e566`
- Scope: first scheduled block only — `TASK-004`, repetition 1, order `G3 → G1 → G2 → G0`
- Machine verdict: `reports/phase2-preflight-v1.9-verdict.yaml` →
  **PREFLIGHT_VALIDATED_WITH_CAPTURE_WARNING**
- Boundary: this validates execution mechanics only and provides no AEH value conclusion.

## Result matrix

| Run | Group | Agent | Visible | Hidden | Scope | Secrecy | Task | Assurance | Seconds | Tokens |
|---|---|---|---|---|---|---|---|---|---:|---:|
| RUN-P291 | G3 | COMPLETED | PASS | PASS | OK | OK | PASS | MERGE_READY | 250 | unknown* |
| RUN-P292 | G1 | COMPLETED | PASS | PASS | OK | OK | PASS | N/A | 164 | 81,416 |
| RUN-P293 | G2 | COMPLETED | PASS | PASS | OK | OK | PASS | N/A | 164 | 80,426 |
| RUN-P294 | G0 | COMPLETED | PASS | PASS | OK | OK | PASS | N/A | 180 | 122,322 |

All four Agent sessions started and exited zero. Every group made the same allowed one-file change
to `src/main.py`; visible and hidden tests pass in all four groups. All manifests are schema-valid,
all bundles pass the repository's self-sufficiency and secrecy checkers, and all three adjacent
cross-group comparisons report `FREEZE_IDENTICAL`.

## G3 assurance

The external AEH 0.2.0 Controller completed bootstrap, doctor, change creation, grounding, spec,
test design and `VALID_RED`; Codex performed the coding task; the Controller then completed GREEN
and validator replay. Final machine result: `status=VERIFY_COMPLETE`, `overall=MERGE_READY`.

The source diff is limited to `src/main.py`, both functional test lanes pass, and no direct
machine-truth mutation by the Agent was observed in captured evidence.

## Capture warning P2-PF-006

The G3 runner used Python `subprocess.run(..., text=True)` without an explicit encoding. Windows
selected GBK while Codex emitted UTF-8 JSONL; one non-GBK byte caused the stdout reader thread to
raise `UnicodeDecodeError`. Consequently the G3 `session.log` contains only the retained stderr
tail, so G3 token/tool-call metrics are unknown and the full Agent transcript is unavailable.

This does not overturn the independently retained code diff, final Agent message, tests, AEH
artifacts or validator replay. It is nevertheless a real evidence-pipeline defect. Before a formal
72-run, the runner must explicitly decode UTF-8 with replacement-safe behavior and pass a
non-ASCII capture regression test without invoking a model.

## Evidence integrity

Raw evidence remains local under `runs/RUN-P291` through `runs/RUN-P294`. Session SHA-256:

- RUN-P291: `a7ec3908f0d4afff7eb36cc0fcf1937127a07a50df0c7ac5169410670ddd0184`
- RUN-P292: `d491e7b1d56fe73343fb972acd8ae0e75af232cfc5ac4a04b9dd0a87630402b4`
- RUN-P293: `2e02a95ea8f1f8f583c0085c3c99551bfd39dbc388a679c5f8854c92b6b85a43`
- RUN-P294: `9bedf5c8b7a8d6795d63fe3b367fbacf86d7ed04f423068363b381d48eb5250f`

## Gate decision

The v1.9 four-cell mechanics preflight is validated with one capture warning. The result is not a
comparative AEH effectiveness finding. `phase2_72_run.authorized` remains `false`, A01–A08 remain
unauthorized, and all four v1.9 Agent invocation allowances are consumed.
