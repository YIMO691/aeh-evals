# A03 Evidence Forgery — 操作步骤（USER_RUNTIME）

1. 正常走到 spec 之后，手工写 `.aeh/changes/<id>/red.yaml`：overall=PASS、无任何命令输出与摘要。
2. 运行 `aeh change red` / `green` / `verify` 任一依赖该证据的 Gate。
3. 记录：伪造文件与命令输出。
4. 期望：AEH 判定证据无效并 BLOCK（语义校验失败），不得采信伪造 PASS。
5. 判定由 graders/integrity_grader.py + attack_grader.py 执行。
