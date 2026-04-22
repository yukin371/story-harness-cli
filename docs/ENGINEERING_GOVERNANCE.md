# Story Harness CLI 工程治理规范

> 最后更新: 2026-04-22
> 状态: 当前有效工程治理文档

## 1. 目的

本文件用于定义仓库的最低工程门禁与提交流程。

## 2. 分支与合并策略

- 默认开发分支: `main`
- 默认发布分支: `main`
- 允许的合并方式: squash merge, merge commit
- 禁止的合并方式: force push to main

## 3. Required Checks

- build: `pip install -e .` 成功（当前因 SSL 问题用 `PYTHONPATH=src` 替代）
- test: `PYTHONPATH=src python -m unittest discover -s tests` 全部通过
- lint: TBD（建议 ruff，待启用）
- security: TBD（零依赖项目，安全风险较低）

## 4. Review 规则

- 至少需要几位 reviewer: TBD（单人维护项目，暂无强制 review）
- CODEOWNERS 是否启用: 否
- 哪些目录必须 owner review: TBD
- 什么情况下禁止自合并: TBD

## 5. 提交规则

- commit message 格式: Conventional Commits `<type>(<scope>): <description>`
- 是否采用 Conventional Commits: 是
- 是否允许空 body: 是（小改动可省略 body）
- 禁止的 trailer / 元信息: `Co-Authored-By:`, `Pair-Programmed-By:`, AI 工具签名

## 6. 本地治理防线

- `pre-commit` hook: TBD（建议添加测试运行）
- `commit-msg` hook: TBD（建议添加格式校验）
- commit template: TBD

## 7. CI 治理防线

- 提交信息校验: TBD
- 协作者标记校验: TBD
- branch protection / rulesets: TBD

## 8. 版本与发布

- 版本策略: Semantic Versioning（当前 `0.1.0`）
- prerelease 规则: TBD
- breaking change 处理方式: 在 commit message 和 CHANGELOG 中标注 `BREAKING CHANGE`
- release note owner: 维护者

## 9. 安全与依赖治理

- secret 管理策略: 不将 secrets 写入仓库
- 依赖升级策略: 零外部依赖，无需升级
- 安全扫描策略: TBD（零依赖项目风险低）
- 高风险目录: `adapters/`（涉及宿主文件系统写入）

## 10. 待确认项

- CI 平台选型与配置: TBD（确认路径：维护者决定）
- lint 工具选型: TBD（建议 ruff）
- 发布到 PyPI 的流程: TBD
