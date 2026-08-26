# aeh-evals — AEH Proof-of-Value 独立评估仓库

> **身份声明**：本仓库是 AEH 的**独立评估仓库**。考试题、评分器与实验结果
> **不受 AEH 仓库控制**；AEH 只作为被测对象出现，评估期间发现 AEH 的任何失败都
> 只记录、不现场修改 AEH。

## 做什么

回答一个问题：

> 在相同 Coding Agent、相同任务、相同仓库、相同工具条件下，引入 AEH 后，真实软件
> 变更的错误完成、越界修改、测试作弊与不可审计结果是否显著减少，且增加的成本可接受？

四组对照：G0 裸 Agent / G1 + AGENTS/CLAUDE + Project Skill / G2 + OpenSpec /
G3 + AEH（第二阶段加 G4 近邻方案）。试点规模 6 任务 × 4 组 × 3 次 = 72 runs。

## 开始前必读

1. `protocol/PROTOCOL.md` — 实验宪法（假设、纪律、Phase、结论）。
2. `protocol/decision-gates.yaml` — 实验前冻结的成功阈值。
3. `environments/RUNBOOK.md` — 72-run 执行手册（真实实验步骤均标 USER_RUNTIME）。

Phase 2 的正式结果见 `reports/PHASE_2_FORMAL_V1_10.md`。v0.2.1 的有界修复复测和
A01–A08 结果见 `reports/PHASE_2_REMEDIATION_V1_11.md`。

## 目录

| 目录 | 内容 |
|---|---|
| protocol/ | 冻结协议、指标、阈值、schema 与样例 |
| tasks/ | Benchmark A 任务（TASK-001..006 试点就绪；TASK-007..012 扩展占位） |
| attacks/ | Benchmark B 攻击用例 A01–A08 |
| environments/ | G0–G3 环境冻结规格与 runbook |
| runs/ | run 记录（仅模板入库，实验产物默认本地） |
| graders/ | 确定性判定器与本地单测 |
| reports/ | 证据矩阵与报告模板 |

## 运行边界

本仓库不替任何人跑 Agent。真实实验 = 你（Owner）在本机/CI 执行；每 run 提交
`run.yaml`（schema: `protocol/run-manifest.schema.json`）与原始证据，判定一律由
`graders/` 与独立 Reviewer 完成，执行 Agent 不得给自己的 run 打分。

## 当前证据状态

- Phase 1 v1.5：历史 dry-run，证据命名空间 `EVAL-P1-*`。
- Phase 1.1 v1.6：`PHASE_1_1_FROZEN_AND_REPLAYED`，证据命名空间 `EVAL-P11-*`。
- Phase 1.1 只验证冻结协议和 External Runner 最小机制，不证明 AEH 产品有效性。
- Phase 2 v1.10：正式 72-run 已完成，推荐结论为 `REPOSITION`。
- Phase 2 v1.11 remediation：三次修复复测阻断 3/3 机器真值直写；A01–A08 为
  8/8 BLOCKED、0 ESCAPED；v0.2.1 达到 Owner release review readiness。
- 总体产品有效性仍为 `NOT_YET_PROVEN`；上述结果不授权发布或改变选择性使用定位。

详见 `reports/PHASE_1_1_RESULT.md` 与 `reports/PHASE_1_1_CLOSURE.md`。
