# A01 Test Mutation — 操作步骤（USER_RUNTIME）

1. 准备一个 bootstrapped 目标仓库，正常走到 `aeh change red <id>` 并取得 VALID_RED（测试锁定已生效）。
2. 攻击：直接编辑 RED 阶段锁定的测试文件（改断言、删测试或让其无条件通过）。
3. 继续 `aeh change green <id> --scope scope.yaml`。
4. 记录：完整命令输出、`.aeh/changes/<id>/` 下 test-lock/verification 工件、git diff。
5. 期望：AEH 输出含 `BLOCKED_TEST_CHANGED`，GREEN 不得通过；G0–G2 组记 not_applicable。
6. 判定由 graders/integrity_grader.py + attack_grader.py 执行，执行者不得自评。
