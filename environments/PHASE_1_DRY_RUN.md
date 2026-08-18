# PHASE_1_DRY_RUN_VALIDATION — 4-run 干跑手册

> 目的：**不产生 AEH 价值结论**。只回答「这套实验协议本身能不能正确运行」。
> 退出条件：`protocol/phase1-exit-criteria.yaml`。任一 FAIL → `DRY_RUN_NOT_VALIDATED`，
> 修协议（Amendment）后**重跑全部 4 runs**，直到 4/4 VALID。

## 1. 规模

| 项目 | 值 |
|---|---|
| 任务 | TASK-004（top-service: config limit 被忽略；CROSS_MODULE / STANDARD） |
| Run | RUN-D001(G0) / RUN-D002(G1) / RUN-D003(G2) / RUN-D004(G3) |
| 重复 | 1 次/组 |
| 执行 Agent | Codex CLI（headless，版本/模型写入 run.yaml 冻结） |
| 超时 | 1800 s/run；超时 → status=ABORTED |

## 2. 8 项目标与检查命令

| # | 目标 | 检查命令（operator 执行，非执行 Agent） |
|---|---|---|
| 1 | Repo restoration 确定性 | `python -m graders.cli restore-check --task tasks/TASK-004 --workdir runs/RUN-D00X/work` → 必须 `RESTORE_OK`；再 `restore-verify` 复验 |
| 2 | G0–G3 只有目标变量不同 | `python -m graders.cli freeze-compare --run-a runs/RUN-D001/run.yaml --run-b runs/RUN-D002/run.yaml`（并逐对比较）→ 必须 `FREEZE_IDENTICAL` |
| 3 | Hidden tests 真的 hidden | `python -m graders.cli secrecy --run-dir runs/RUN-D00X` → 必须 `SECRECY_OK` |
| 4 | Grader 独立判错（false completion） | `python -m graders.cli outcome --agent-claimed <转录> --hidden-pass <true/false> --visible-pass <...> --scope-ok <...>` |
| 5 | 时间/Token/Tool-call 采集 | run.yaml.metrics 三字段齐全；tokens 拿不到必须 `UNKNOWN`/`NOT_AVAILABLE`，禁止估算 |
| 6 | G3 真的运行了 AEH | `python -m graders.cli aeh-evidence --workdir runs/RUN-D004/work --session-log runs/RUN-D004/evidence/session.log --replay runs/RUN-D004/evidence/aeh-replay-verify.txt`（AMENDMENT-005：Agent 调用 aeh CLI **或** operator 用真实 AEH 验证器回放并记录裁决） |
| 7 | INVALID_RUN 可用 | `restore-verify`（wrong SHA / dirty）+ `validate`（缺字段）→ 必须 `INVALID_RUN` |
| 8 | Run artifact 自足 | `python -m graders.cli sufficiency --run-dir runs/RUN-D00X` → 必须 `SELF_SUFFICIENT` |

## 3. 每个 run 的操作清单（operator = 本会话或用户；执行 Agent = codex.exe）

1. **restore**：`restore-check` 恢复干净副本到 `runs/RUN-D00X/work`（HEAD==冻结 SHA，clean）。
2. **环境**：
   - G0：什么都不加（bare）。
   - G1/G2/G3：复制 `environments/G1-assets/{AGENTS.md,context/}` 进 workdir（冻结资产）。
   - G2：在 G1 基础上按 OpenSpec 流程初始化。
   - G3：在 G1 基础上用冻结 AEH 源 `aeh bootstrap .`，`aeh doctor .` 必须 READY/READY_WITH_WARNINGS；
     执行后 operator 必须用真实 AEH 验证器回放：`aeh change verify <id>` + `aeh doctor .`，
     原始输出落 `evidence/aeh-replay-*.txt`（AMENDMENT-005）。
3. **run.yaml**：填 group/repository/agent/harness/environment/input（prompt sha256 实算），
   `result.agent_claimed=NOT_RECORDED`（跑完再转录），校验 `VALID`。
4. **执行**：`codex exec "<TASK-004 original_prompt>"`，cwd=workdir，后台执行，
   输出原始落 `evidence/session.log`；记录 started_at/finished_at。
5. **收证据**：`git diff --name-only` + `git diff` → `evidence/git-diff.txt`；
   visible tests → `evidence/tests-output.txt`（hidden tests 由 operator 在 run 外另跑，不得进 workdir）。
6. **判定**：hidden tests 结果 → `outcome` CLI → 转录 agent_claimed → 填 run.yaml → `validate` 再验。
7. **比对**：`freeze-compare` 与其它组两两比对（组字段之外的 frozen 字段必须一致）。
8. **自足性**：`sufficiency` 确认 5 文件齐全。

## 4. 环境冻结（本阶段）

- Agent：`codex-cli 0.147.0`（本机实测版本）；model 以 CLI 默认值写入 run.yaml（若不可查则 `UNKNOWN`）。
- Sandbox：本机 Codex `workspace-write` 沙箱缺 helper（`codex-windows-sandbox-setup.exe`），
  Owner 授权四组统一 `--dangerously-bypass-approvals-and-sandbox`，run.yaml 记录
  `environment.sandbox: bypass`；四组同值，组间隔离成立（环境差异已如实记录）。
- `input.config_sha256`：本组环境配置哈希（组内一致即可）；**不参与跨组冻结比对**（AMENDMENT-002，协议 v1.2）。
- repository.commit_sha：`tasks/TASK-004/task.yaml` 冻结值（3374f3…）。
- prompt：`tasks/TASK-004/task.yaml` 的 `request.original_prompt`，UTF-8 无尾换行 sha256。
- G1 资产：`environments/G1-assets/`（构造后 sha256 冻结）。
- G3 AEH 源：本地 AEH 仓库 main@6513102（零改动，editable 安装到 `.venv-aeh`）。

## 5. 发现协议问题的处理（干跑期唯一允许）

```text
发现 → 记录 Amendment（AMENDMENTS.md）→ 修 aeh-evals → 协议版本 v1.x → v1.(x+1)
→ 重跑全部 4-run → 直到 4/4 VALID → 重新 Freeze。
```

正式 72 runs 开始后此路径关闭：Protocol bug = ABORT EXPERIMENT + 全部重来。

## 6. 报告

- `reports/PHASE_1_RESULT.md`：8 项逐条 PASS/FAIL + 证据路径 + 发现。
- `reports/phase1-verdict.yaml`：机器断言 exit-criteria；`next_phase_started` 必须 false
  （下一阶段启动必须由 Owner 显式批准）。
