# reports/ — 聚合报告

由 `python -m graders.cli matrix --out reports/evidence-matrix.csv` 生成。
最终裁决对照 `protocol/decision-gates.yaml`，结论只落五档之一：
CONTINUE / CONTINUE_BUT_NARROW / INTEGRATE / REPOSITION / STOP。

## 证据权威顺序

Phase 1.1 的冲突消解顺序固定为：原始 run evidence → `run.yaml` → machine verdict YAML
→ Markdown narrative。旧 Phase 1 使用 `EVAL-P1-*` 证据标识；v1.6 Phase 1.1 使用
`EVAL-P11-*`，两期同名 `RUN-D004` 不得视为同一次运行。

完整 session/run 原始证据保存在内部证据包。公开仓库提交脱敏报告、机器判定与
`phase1-1-evidence-manifest.sha256`，不把被忽略的本地 run 目录伪装成公开可复现资产。

Phase 2 v1.7 的四次执行机制预检记录在 `PHASE_2_PREFLIGHT_V1_7.md` 与
`phase2-preflight-v1.7-verdict.yaml`。该预检因环境契约失败，不产生价值结论，正式执行仍未授权。

Phase 2 v1.8 的四单元预检记录在 `PHASE_2_PREFLIGHT_V1_8.md` 与
`phase2-preflight-v1.8-verdict.yaml`。该预检因 Codex CLI 参数契约失败，不产生价值结论，
正式 72-run 与 A01–A08 仍未授权。

Phase 2 v1.9 的四单元预检记录在 `PHASE_2_PREFLIGHT_V1_9.md` 与
`phase2-preflight-v1.9-verdict.yaml`。四组功能均通过且 G3 达到 `MERGE_READY`，但 G3 stdout
存在 Windows GBK/UTF-8 捕获警告；正式执行前需修复采集器，72-run 与 A01–A08 仍未授权。

Phase 2 v1.10 的正式 72-run 记录在 `PHASE_2_FORMAL_V1_10.md` 与
`phase2-formal-v1.10-verdict.yaml`。72/72 精确终态、捕获完整，正式结论为 `REPOSITION`：
G1 18/18、G2 17/18，而 G3 仅 4/18 达到完整可信成功，并观察到一次 Agent 机器真值直写被
verifier 错误接受。A01–A08 未执行，攻击 Gate 仍不可判定。
