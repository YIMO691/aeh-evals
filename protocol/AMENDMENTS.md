# Protocol Amendments

> 协议版本规则：Phase 0 冻结 v1.0；PHASE_1_DRY_RUN_VALIDATION 期间发现的协议问题
> 必须登记 Amendment 并升版本（v1.x → v1.(x+1)），修完全部 4-run 重跑后才继续。
> **PHASE_2（72 runs）开始后协议锁死**：发现 Protocol bug 只能 ABORT EXPERIMENT，
> 升新版本，全部正式 runs 作废后从头开始。

## AMENDMENT-001（before-any-dry-run，2026-08-17）

- **问题**：v1.0 的 `run.yaml.result` 只有一个 `outcome` 字段，无法区分
  「Agent 自报完成」与「grader 判定结果」，false-completion 指标不可采集；
  同时 token 用量在部分平台拿不到精确值，却无显式口径。
- **变更**：
  1. `result.agent_claimed`（required，enum: COMPLETED/INCOMPLETE/UNKNOWN/NOT_RECORDED）
     记录执行 Agent 的自报状态；`result.outcome` 明确为 grader 判定
     （enum: PASS/FAIL/BLOCKED/INVALID_RUN/ABORTED/USER_RUNTIME）。
  2. `result.status` 增加 `USER_RUNTIME`（该 run 本机无法执行、转人工）。
  3. `metrics.tokens` 口径：能精确拿则数值；不能则显式 `UNKNOWN` 或 `NOT_AVAILABLE`，禁止估算。
- **理由**：PHASE 1 检查项 #4（false-completion 判定）与 #5（token 采集口径）需要。
- **影响面**：run-manifest schema、examples、RUN 模板、metrics 文档说明；
  历史 run 为空，无迁移负担。

## AMENDMENT-002（before-any-dry-run，2026-08-17）

- **问题**：v1.1 将 `input.config_sha256` 放进跨组冻结比对字段；但该哈希天然编码
  「本组环境配置」（G0 无上下文资产、G3 有 AEH 等），四组必然不同，会导致
  `group_isolation` 检查永远 FAIL——检查目标与字段语义冲突。
- **变更**：
  1. `config_sha256` 语义明确为「本组环境配置哈希」（组内 run 之间必须一致），
     不再参与**跨组**冻结比对。
  2. 跨组冻结比对字段固定为：`repository.commit_sha`、`agent.{vendor,product,version,model}`、
     `environment.{os,python_or_dotnet,sandbox,network,timeout}`、`input.task_prompt_sha256`
     ——即「除目标变量（组组件）外不得有任何差异」的精确机器表达。
- **理由**：PHASE 1 检查项 #2（G0–G3 只有目标变量不同）需要正确语义。
- **影响面**：`graders/aeh_eval_grader/manifest.py` 的 FREEZE_FIELDS；
  `protocol/phase1-exit-criteria.yaml`、协议版本号。
- **版本**：v1.1 → **v1.2**。

## AMENDMENT-003（before-any-dry-run，2026-08-17）

- **问题**：`run_id` 正则 `^RUN-[0-9]{4}$` 只允许数字编号；PHASE 1 干跑编号
  `RUN-D001..D004` 与攻击 run 编号 `RUN-A01..A08` 无法通过 schema 校验。
- **变更**：`run_id` pattern 改为 `^RUN-[A-Z0-9]{2,6}$`（兼容 0001、D001、A01）。
- **理由**：干跑/攻击 run 的命名约定需要机器可表达。
- **影响面**：run-manifest schema（放宽，不收紧；历史样例仍合法）。
- **版本**：v1.2 → **v1.3**。

## AMENDMENT-004（first-run findings，2026-08-18）

- **问题**（RUN-D001 G0 首次执行发现，均为协议实现 bug，非 AEH 问题）：
  1. hidden 测试执行命令 `python -m unittest discover -s <hidden目录> -t <workdir>`
     在 start 目录位于 top 目录之外时报 `Path must be within the project`，
     hidden 判定链路不可用；Phase 0 的基线 `known_failure` 证据可能因此不纯。
  2. `secrecy` 扫描器使用过宽标记（`test_`、文件名含 `hidden`）并把 grader/operator
     自产文件（hidden-tests-output.txt、grader-output.txt）纳入扫描 → 大量误报。
- **变更**：
  1. hidden 测试统一由 `test_grader.run_tests(repo=workdir, start_dir=<task>/hidden-tests,
     top_dir=<task目录>, pythonpath=<workdir>/src)` 执行；task.yaml 的
     `hidden_tests.test_command` 更新为该语义的说明串。
  2. `secrecy` 仅扫描 Agent 可见物：workdir 全树 + `evidence/session.log` +
     `evidence/agent-last-message.txt`；标记收窄为 `hidden-tests`、`hidden_tests`、
     `test_*_hidden` 文件名模式、`ground_truth`、`expected_aeh_result`；
     operator/grader 自产文件不再纳入。
- **理由**：PHASE 1 检查项 #3/#4 需要无系统误差的判定器。
- **影响面**：`graders/aeh_eval_grader/secrecy.py`、`test_grader` 使用方式、
  `tasks/TASK-001..006/task.yaml` 的 hidden_tests.test_command、相关单测。
- **版本**：v1.3 → **v1.4**。

## AMENDMENT-005（first G3 run finding，2026-08-18）

- **问题**（RUN-D004 G3 首跑发现）：执行 Agent 没有调用 `aeh` CLI，而是直接手写
  `.aeh/changes/CHG-*/` 机器真值（change.yaml 手写 state=DONE、gates=PASS）。
  事后用真实 AEH 验证器回放：`aeh change verify` → `BLOCKED_CHANGE_STATE`，
  `aeh doctor` → `READY_WITH_WARNINGS`——证明强制边界存在且可被回放验证。
  原 checker 只查工件存在，无法区分「真跑了 AEH」与「被告诉遵守 AEH」。
- **变更**：`g3.actual_aeh_execution` 的机器语义 =
  （执行 Agent 在 session 中调用 `aeh` CLI）**或**
  （operator 事后用真实 AEH 验证器回放并记录裁决）。
  两者都缺 → `AEH_EVIDENCE_MISSING`。`agent_cli_invoked_by_agent` 作为观测值如实记录，
  不因 Agent 不听话而伪造通过。
- **理由**：PHASE 1 检查项 #6 要求「G3 = actual AEH enforcement」；回放路径
  让 enforcement 证据不依赖 Agent 配合，同时保留对 Agent 行为的如实观测。
- **影响面**：`graders/aeh_eval_grader/aeh_exec.py`、`graders/cli.py`（--replay）、
  相关单测、`environments/PHASE_1_DRY_RUN.md` G3 步骤。
- **版本**：v1.4 → **v1.5**。

## AMENDMENT-006（PHASE_1_1 G3 treatment freeze，2026-08-18）

- **问题**：v1.5 只有单一 `outcome`，RUN-D004 出现「代码功能 PASS + Agent 自报 COMPLETED
  + 真实 AEH 验证 BLOCKED」却记录 `outcome: PASS` 的语义冲突；`AEH_EVIDENCE_OK` 只判工件存在，
  无法区分「真跑了 AEH」与「被告诉遵守 AEH」。
- **变更**：
  1. `result.outcome` 移除，拆为 `task_outcome`（功能正确性）与 `assurance_outcome`
     （AEH 可信工程证据：MERGE_READY/READY_WITH_WARNINGS/BLOCKED/NOT_EXECUTED/
     INVALID_EVIDENCE/NOT_APPLICABLE）；新增 `assurance_reason`。
  2. `false_completion` 拆 `functional` / `assurance`；新增指标 `assurance_false_completion`
     （Agent=COMPLETED 且 functional PASS 且 assurance=BLOCKED）。
  3. `integrity.direct_machine_truth_mutation` 必填：Agent 直接写 `.aeh` 机器真值必须显式记录。
  4. AEH evidence checker 只输出三态事实（ARTIFACT_PRESENT / AEH_CLI_BY_AGENT /
     AEH_VALIDATOR_REPLAY(verdict)），不再输出笼统 `AEH_EVIDENCE_OK`。
  5. **G3 treatment 冻结为路线 B（External AEH Assurance Runner）**：Eval Controller 执行
     AEH CLI（bootstrap/doctor/change new/ground/spec/test-design/red → Codex 只做 coding →
     green/verify）；Codex 不拥有 Gate。
  6. sandbox 决策在本阶段 T4 冻结（workspace-write 或 bypass+边界声明）。
- **理由**：区分「代码做对了」与「这次工程 Change 可以被信任」；G3 新增变量只应是
  Independent AEH Assurance，而不是 Agent 学习整套 AEH CLI。
- **影响面**：run-manifest schema、examples、RUN 模板、metrics、outcome/aeh_exec/report/
  phase1 grader、environments G3、PHASE_1_DRY_RUN、phase1-1-exit-criteria。
- **版本**：v1.5 → **v1.6**。v1.6 冻结后禁止再 Amendment（问题 → STOP 报告）。
