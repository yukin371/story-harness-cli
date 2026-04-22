# 当前路线图

> 最后更新: 2026-04-22
> 状态: 当前唯一执行入口

## 1. 当前版本目标

- v0.1: 完成 CLI 核心工作流命令（init → brainstorm → chapter → review → projection → export）
- 补齐查询/统计能力（entity list/show, context show, stats）
- 建立工程治理骨架

## 2. Active Tracks

### Track A: 核心工作流完善

- 目标: 补齐空壳功能（timeline, branch, causality）
- 当前状态: 查询命令已完成，timeline/branch 仍为 placeholder
- 下一步: 评估 timeline 管理的优先级

### Track B: 工程治理

- 目标: 按仓库治理模板建立完整骨架
- 当前状态: 正在创建治理文档
- 下一步: 完成 git hooks 和 CI 配置

## 3. 当前阻塞

- SSL 问题导致 `pip install -e .` 失败（镜像证书）:
  - 影响: 无法通过 `story-harness` 命令直接运行
  - 解除路径: 使用 `PYTHONPATH=src python -m story_harness_cli` 替代
- 无 CI/CD 配置:
  - 影响: 无法自动运行测试门禁
  - 解除路径: 维护者决定是否启用 GitHub Actions

## 4. 待验证项

- entity enricher 跨段落实体归属 bug 是否在真实场景中频繁触发
- adapters/ 目录的实际使用情况
- 发布到 PyPI 的可行性和流程

## 5. 最近进展

- 完成 consistency check、entity enrich/review、export 命令
- 完成 entity list/show、context show、stats 查询命令
- 54 个测试全部通过
- 建立仓库治理骨架

## 6. 下一步

1. 评估 timeline 管理命令的实现优先级
2. 建立 git hooks（commit-msg 校验）
3. 修复 entity enricher 的实体归属问题
