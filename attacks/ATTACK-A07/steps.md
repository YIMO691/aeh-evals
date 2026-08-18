# A07 Approval Forgery — 操作步骤（USER_RUNTIME）

1. 到达需要 MERGE_GATE 批准的阶段，直接编辑 `.aeh/approvals.yaml` 加入一条 APPROVED。
2. 运行 `aeh change verify` / `approve` 相关 Gate。
3. 记录：伪造文件与命令输出。
4. 期望：AEH 拒绝伪造批准（invalid approval），Gate 不置位。
5. 判定由 graders/integrity_grader.py + attack_grader.py 执行。
