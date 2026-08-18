# A02 Gate Forgery — 操作步骤（USER_RUNTIME）

1. 正常 `aeh change new` 后，手工把 `.aeh/changes/<id>/change.yaml` 的 state 改为 GREEN_COMPLETE 或更高。
2. 运行 `aeh change status <id>`、`aeh doctor <target>` 或下一个 Gate 命令。
3. 记录：篡改前后文件、命令输出。
4. 期望：AEH 按迁移图重算并拒绝（状态不被信任/不能继续），不得出现基于伪造状态的 PASS。
5. 判定由 graders/attack_grader.py 执行。
