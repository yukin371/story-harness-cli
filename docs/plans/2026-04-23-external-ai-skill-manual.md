# 外部 AI Skill 手册统一

> 日期: 2026-04-23
> 状态: 已完成

## 目标模块

- `adapters/*`
- `docs/guides/quickstart.md`

## 现有 owner

- adapter source owner: `adapters/*`
- 快速上手 owner: `docs/guides/quickstart.md`

## 影响面

- 统一对外 AI 的操作手册与仓库真实流程
- 不修改 CLI 行为，不新增依赖

## 计划改动

1. 为 `adapters/` 增加模块文档
2. 把 Codex / Claude skill 从“命令提示”升级为“完整闭环手册”
3. 补充 fallback 运行方式、关键文件、评审与低分优化停止条件
4. 同步 quickstart，避免和 skill 口径分裂
5. 按新手册实际跑一遍样例流程

## 验证方式

- 读取 skill 文件确认包含完整闭环
- 按 skill 对 `demo-light-novel-short` 跑完整流程
- `python -m unittest tests.smoke.test_demo_light_novel_short_sample -v`

## 验证结果

- Codex / Claude 两套 `story-harness-writing` skill 已补齐完整闭环、fallback、停止条件、关键协议文件
- `demo-light-novel-short` 已按新 skill 跑通完整流程：
  - `chapter analyze`
  - `chapter suggest`
  - `review apply`
  - `projection apply`
  - `context refresh`
  - `review chapter`
  - `review scene`
  - `export`
- 在这次完整流程里，`chapter suggest` 生成了 `5` 条建议，`review apply` 接受了 `5` 条，`projection apply` 应用了 `5` 条
- 应用建议后，`chapter-001` 的 `review chapter` 总分达到 `93/100`，加权分达到 `94.9/100`
- `python -m unittest tests.smoke.test_demo_light_novel_short_sample -v` 通过
