# A08 Contract Tamper — 操作步骤（USER_RUNTIME）

1. `aeh bootstrap` 后，修改 `.aeh/runtime/core/workflow.yaml` 或任一 schema 文件。
2. 运行 `aeh doctor <target>` 或任一 Gate。
3. 记录：篡改前后文件与命令输出。
4. 期望：doctor/Gate 输出 BLOCKED_RUNTIME_INTEGRITY，不得基于被篡改的裁判规则继续判 PASS。
5. 判定由 graders/integrity_grader.py + attack_grader.py 执行。
