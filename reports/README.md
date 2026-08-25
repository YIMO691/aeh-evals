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
