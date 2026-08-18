# runs/ — 实验记录规范

- 只有 `RUN-0000-template/` 入库；真实 `RUN-*` 是实验产物，默认被 .gitignore 忽略。
- 每个 run 一个目录：`run.yaml` + `evidence/`（原始输出不截断）。
- `run.yaml` 必须通过 `python -m graders.cli validate --run <path>`，否则 INVALID_RUN。
- outcome/metrics 由 grader/Owner 填写，执行 Agent 不填。
- 见 `environments/RUNBOOK.md` 的完整清单。
