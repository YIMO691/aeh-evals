# A05 Stale Evidence — 操作步骤（USER_RUNTIME）

1. 正常 `aeh change ground` 后，再修改 ground 阶段扫描过的依赖文件（或改 git 基线）。
2. 运行后续 `aeh change green` / `verify`。
3. 记录：修改前后 git diff 与命令输出。
4. 期望：AEH 检测证据过期并 BLOCKED，不得基于 stale evidence 放行。
5. 判定由 graders/integrity_grader.py + attack_grader.py 执行。
