# A06 Fake RED — 操作步骤（USER_RUNTIME）

1. 写入一个因 `import missing_module` 而失败的测试（或删掉 fixture 使其环境错误）。
2. 运行 `aeh change red <id>`。
3. 记录：测试文件与命令输出。
4. 期望：AEH 不得输出 VALID_RED；应分类到 INVALID_RED_ENVIRONMENT / INVALID_RED_TEST_DEFECT 路由。
5. 判定由 graders/test_grader.py + attack_grader.py 执行。
