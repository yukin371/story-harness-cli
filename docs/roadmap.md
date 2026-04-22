# 当前路线图

> 最后更新: 2026-04-22
> 状态: 当前唯一执行入口

## 1. 当前版本目标

- v0.2: 修复已知缺陷 + 补齐空壳功能 + 工程质量提升

## 2. Active Tracks

### Track P0: 修复 entity enricher 实体归属

- 目标: 同段落多实体时，外貌/能力属性错配给后出现的实体
- 当前状态: **已完成** — 按句子粒度归属标签
- 下一步: 无

### Track P1: 补齐空壳功能

- 目标: timeline 管理、causality 追踪、search 跨章节搜索
- 当前状态: timeline (add/list/check) 和 search 已完成，causality 待实施
- 下一步: causality 追踪（或跳过，优先 P2）

### Track P2: 工程质量

- 目标: CI/CD (GitHub Actions)、lint (ruff)、entity 注册自动化
- 当前状态: **已完成** — CI workflow、ruff 配置、entity 自动注册均已落地
- 下一步: 无

### Track P3: 体验优化

- 目标: 导出格式扩展、relationship graph、beat 追踪、配置化关键词表
- 当前状态: 待评估
- 下一步: 等 P0-P2 稳定后推进

## 3. 当前阻塞

- SSL 问题导致 `pip install -e .` 失败（镜像证书）:
  - 影响: 无法通过 `story-harness` 命令直接运行
  - 解除路径: 使用 `PYTHONPATH=src python -m story_harness_cli` 替代

## 4. 待验证项

- entity enricher 修复后的真实场景验证
- adapters/ 目录的实际使用情况

## 5. 最近进展

- 修复 entity enricher 跨实体属性错配（P0）
- 新增 timeline add/list/check 命令（P1）
- 新增 search 跨章节搜索命令（P1）
- GitHub Actions CI workflow (test/lint/commit-governance)（P2）
- ruff lint/format 配置（P2）
- chapter analyze 自动注册 inferred entities（P2）
- 65 个测试全部通过

## 6. 下一步

1. causality 追踪（P1 遗留）
2. 导出格式扩展（P3）
3. relationship graph 可视化（P3）
4. beat 追踪（P3）
