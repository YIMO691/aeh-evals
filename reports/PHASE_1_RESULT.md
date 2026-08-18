# PHASE_1_DRY_RUN_VALIDATION — 结果报告

- 日期：2026-08-18
- 协议版本：v1.5（Phase 0 v1.0 + AMENDMENT-001..005）
- 机器判定：`reports/phase1-verdict.yaml` → **VERDICT=DRY_RUN_VALIDATED**
- 结论声明：本报告只回答「实验协议本身能否正确运行」；**不产生任何 AEH 价值结论**；
  `next_phase_started: false`（72 runs 必须由 Owner 显式批准后才启动）。

## 1. 4-run 概览（TASK-004，Codex gpt-5.6-terra，sandbox=bypass）

| Run | 组 | Agent 自报 | Grader outcome | hidden | visible | scope | 墙钟(s) | tokens | tool_calls(transcript) |
|---|---|---|---|---|---|---|---|---|---|
| RUN-D001 | G0 | COMPLETED | PASS | 2/2 | 4/4 | OK | 179 | 13577 | 5 |
| RUN-D002 | G1 | COMPLETED | PASS | 2/2 | 4/4 | OK | 175 | 28572 | 3 |
| RUN-D003 | G2 | COMPLETED | PASS | 2/2 | 4/4 | OK | 173 | 11178 | 3 |
| RUN-D004 | G3 | COMPLETED | PASS | 2/2 | 4/4 | OK | 269 | 31665 | 10 |

四组全部：`validate=VALID`、`secrecy=SECRECY_OK`、`sufficiency=SELF_SUFFICIENT`；
四组两两 `freeze-compare=FREEZE_IDENTICAL`（6 对 0 差异）。

## 2. 8 项目标判定

| # | 目标 | 判定 | 证据 |
|---|---|---|---|
| 1 | Repo restoration 确定性 | PASS | 4×`restore-check.txt` RESTORE_OK；本次复跑 fresh restore HEAD==frozen SHA、clean |
| 2 | G0–G3 只有目标变量不同 | PASS | 6 对 freeze-compare 0 mismatches |
| 3 | Hidden tests 真的 hidden | PASS | 4×SECRECY_OK，hits=[] |
| 4 | Grader 独立判错 | PASS | false_completion 判定器正反两例；伪造 run→INVALID_RUN；dirty/wrong-SHA→INVALID_RUN |
| 5 | 时间/Token/Tool-call 采集 | PASS | wall_time 4/4；tokens 4/4 精确；tool_calls=transcript exec/patch 计数（口径冻结）；human_interventions=0 |
| 6 | G3 真的运行了 AEH | PASS | `.aeh` 工件齐全；**agent 未调用 CLI**（`aeh_cli_invoked_by_agent=false`），operator 回放 `aeh change verify`→`BLOCKED_CHANGE_STATE`、`aeh doctor`→READY_WITH_WARNINGS（AMENDMENT-005 回放路径） |
| 7 | INVALID_RUN 可用 | PASS | wrong SHA / dirty 两例均 INVALID_RUN |
| 8 | Run artifact 自足 | PASS | 4×SELF_SUFFICIENT（run.yaml + 5 类证据） |

## 3. 干跑发现（已按干跑期流程修订）

1. **AMENDMENT-002**：config_sha256 语义与跨组冻结比对冲突 → 退出冻结字段，协议 v1.2。
2. **AMENDMENT-003**：run_id 正则不支持 RUN-Dxxx → 放宽，v1.3。
3. **AMENDMENT-004**：hidden 测试执行器 start-dir 越界错误 + secrecy 扫描器误报 → 修复并基线复验，v1.4。
4. **AMENDMENT-005**：G3 执行 Agent 手写 `.aeh` 机器真值而不调用 CLI；真实验证器回放拒绝
   （BLOCKED_CHANGE_STATE）→ `actual_aeh_execution` 采用「Agent CLI 或 operator 回放」双路径，v1.5。
5. **环境发现（非协议）**：本机 Codex workspace-write 沙箱缺 helper；Owner 授权四组统一
   `--dangerously-bypass-approvals-and-sandbox`，run.yaml 记录 `sandbox: bypass`。
6. **运行环境发现**：Codex 网络 WebSocket 不稳（每次回退 HTTPS 后继续），四组一致记录在 session.log。

## 4. 诚实记录

- G3 的 `agent_cli_invoked_by_agent=false`：执行 Agent 直接写机器真值、自报 DONE；
  AEH 验证器回放拒绝该状态。这是干跑最有价值的发现之一——G3 ≠「prompt 说用 AEH」，
  回放路径让 enforcement 证据不依赖 Agent 配合。
- AMENDMENT-005 属 post-run checker 变更；RUN-D004 的回放已补跑，D001–D003 不受影响。
  D001 在 AMENDMENT-004 后已整轮重跑；D002/D003 执行时运行条件未变。
  若 Owner 要求最严格口径「每次 Amendment 后全部 4-run 重跑」，请指示，我会重跑全部 4-run。
- 结论边界：本干跑只覆盖 Python slice（TASK-004）；任何价值推断都必须等 72-run 完成。

## 5. 下一阶段

- 等待 Owner 批准：`next_phase_started=false` 保持，直到明确指令启动 PHASE_2
  （72-run Pilot，分层随机化 + 全锁纪律见 RUNBOOK §7）。
