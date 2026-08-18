# evidence/ 保存规范（每 run）

必存（原始输出，不截断、不转述）：

1. `session.log` — Agent 完整会话/命令日志。
2. `git-diff.txt` — `git diff --name-only` 与 `git diff` 全量。
3. `tests-output.txt` — visible/hidden 测试原始输出。
4. `grader-output.txt` — 确定性 grader 的原始输出。
5. G3 追加：`.aeh/` 机器真值工件快照（manifest/change/spec/test-lock/verification/approvals）。

命名固定；缺失文件的 run 判 INVALID_RUN。
