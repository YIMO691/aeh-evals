# 72-Run Proof-of-Value Pilot — RUNBOOK

> 所有标 `USER_RUNTIME` 的步骤由 Owner 在本机/CI 执行。本仓库不替任何人跑 Agent。
> 判定一律由 `graders/` 与独立 Reviewer 完成；执行 Agent 不得给自己的 run 打分。

## 1. 冻结先于执行

开始前计算并冻结（跨 72 runs 不变）：

```text
task_prompt_sha256 = sha256(each task.yaml request.original_prompt, UTF-8, no trailing newline)
config_sha256       = sha256(task.yaml + environment yaml, canonical bytes)
```

- 同一 task 的所有组用同一 `task_prompt_sha256`；同一组内配置不变。
- 每个任务仓库的 `repository.commit_sha` 必须等于 task.yaml 里的冻结值（TASK-001..006）。

## 2. 执行顺序（72 runs）

组优先：先跑完一组再换组，避免组间互相污染。

```text
for group in G0, G1, G2, G3:          # 4 groups
  for task in TASK-001 .. TASK-006:   # 6 tasks
    for rep in 1, 2, 3:               # 3 repetitions
      run_id = RUN-<序列号 0001..0072>
```

- G0/G1/G2 只有 Benchmark A；Benchmark B 的 A01–A08 对这三个组记 `NOT_APPLICABLE`。
- G3 每组任务完成后，再按 `attacks/ATTACK-A01..A08/steps.md` 单独执行 8 个攻击 run
  （不计入 72；单独编号 `RUN-A01..A08`，run.yaml 的 task_id 写 `ATTACK-Axx`）。

## 3. 每个 run 的操作清单（USER_RUNTIME）

1. 从 `tasks/<task>/repo-src.bundle` 恢复干净副本（bundle 内含冻结 SHA 的完整历史）：
   `git clone tasks/<task>/repo-src.bundle <workdir>`，然后 `git checkout <task.yaml 冻结 SHA>`，工作树 dirty=false。
2. 按 `environments/<group>.yaml` 准备环境；G3 必须 `aeh bootstrap` 且 doctor READY。
3. 计算并填写 `runs/RUN-XXXX/run.yaml`（模板：`runs/RUN-0000-template/run.yaml`）。
4. 用同一 Agent 产品/版本/模型执行 `task.yaml` 的 `request.original_prompt`。
5. 保存原始证据到 `runs/RUN-XXXX/evidence/`：
   - 完整对话/命令日志、git diff、测试输出、AEH 产物（G3）。
6. 由 Owner（不是执行 Agent）运行确定性 grader：

```text
python -m graders.cli validate --run runs/RUN-XXXX/run.yaml     # 必须 VALID
python -m graders.cli diff --changed <git diff --name-only 逗号串> --scope-file tasks/<task>/task.yaml
python -m unittest discover -s <hidden-tests 目录> -t <repo>     # PYTHONPATH=<repo>/src
# G3 追加：
python -m graders.cli attack --attack A01 --signals <输出中观察到的信号> --group G3
```

7. 填写 `run.yaml.result.agent_claimed`（执行 Agent 自报的转录）与 `run.yaml.result.outcome`
   （grader 结论，非 Agent 自述）与 `metrics`；tokens 拿不到精确值就写
   `UNKNOWN` / `NOT_AVAILABLE`，禁止估算（AMENDMENT-001）。
8. `git diff --name-only` 结果同时交给 Blind Reviewer（reviewer 不知道 run 来自哪一组）。

## 4. 有效性规则

- `validate` 输出非 `VALID` → run 判 `INVALID_RUN`，不进入统计。
- 同 task 四组的冻结字段不一致 → 该 task 全部作废并重跑。
- `status: ABORTED` 的 run 保留记录但不进入统计。
- hidden-tests 文件不得出现在 repo-src；发现泄露 → 该 task 所有 run 作废。

## 5. 攻击 run（G3，A01–A08）

- 每个攻击用独立的干净副本 + 独立 `.aeh`；按 steps.md 操作。
- 观察输出中是否出现 attack.yaml 的 expected signals → `attack_grader` 判 BLOCKED/ESCAPED。
- **发现 AEH 失败：只记录 `AEH v0.1 A0x = FAIL`，不现场修 AEH。** 整轮结束后统一裁决。

## 6. 产出

```text
runs/RUN-0001..RUN-0072/run.yaml + evidence/
runs/RUN-A01..RUN-A08/run.yaml + evidence/
reports/evidence-matrix.csv      # 由 graders/report.py 聚合
reports/metrics.csv              # 聚合 10 指标
```

最终结论只能落在 CONTINUE / CONTINUE_BUT_NARROW / INTEGRATE / REPOSITION / STOP 之一，
并对照 `protocol/decision-gates.yaml` 的 AEH_VALUE_GATE 逐项裁决。


## 7. PHASE_2（72 runs）开始后的锁定政策

- **分层随机化**：每个 Task 内随机 G0–G3 顺序（随机表先冻结并入库），不做
  「先全部 G0 再全部 G1」。每次运行必须新工作目录、新会话，禁止跨 run context 污染。
- **报告分离**：`BENCHMARK_RESULT`（正常开发任务价值）与 `ADVERSARIAL_RESULT`
  （A01–A08 Trust Boundary）分开报告；攻击用例不计入普通 Task Success Rate。
- **全锁**：PHASE_2 开始后协议/Task/Grader/AEH Version 全部锁死。
  - 发现 AEH bug → 只 `record FAIL`，整轮后统一裁决。
  - 发现 Protocol bug → `ABORT EXPERIMENT` → 协议升新版本 → 全部正式 runs 作废 → 从头开始。
- **结论边界**：72-run Pilot 当前任务分布为 Python slice；结论只能表述为
  「AEH 在当前冻结的 Python Pilot task distribution 上……」，
  不得宣称对大型软件工程/Unity brownfield 有效。Unity/C# 补齐属后续 Cross-domain Validation。
