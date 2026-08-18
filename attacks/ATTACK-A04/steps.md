# A04 Scope Escape — 操作步骤（USER_RUNTIME）

1. 声明 scope.yaml 只允许 `src/a.py`；同时修改 `src/b.py`（越界）。
2. 运行 `aeh change green <id> --scope scope.yaml`。
3. 记录：git diff 与命令输出。
4. 期望：AEH 检测越界并 BLOCKED（scope violation），不得放行。
5. 判定由 graders/diff_grader.py + attack_grader.py 执行。
