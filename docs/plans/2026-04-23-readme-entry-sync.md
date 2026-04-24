# 首页入口真相同步

> 日期: 2026-04-23
> 状态: 已完成

## 目标模块

- 仓库根目录文档
- `docs/guides/*`
- `docs/plans/*`

## 现有 owner

- 首页入口 owner: `README.md`
- 使用指南 owner: `docs/guides/*`
- 计划记录 owner: `docs/plans/*`

## 影响面

- 首次进入仓库时的默认理解路径
- 作者与外部 AI 是否能尽快找到 canonical 闭环指南
- 不修改 CLI 行为，不新增依赖

## 计划改动

1. 为仓库根目录补模块文档
2. 在 `README.md` 增加完整创作闭环指南入口
3. 同步 README 中已过时的流程与能力说明
4. 保持“首页摘要，细节下沉到 guides”这一边界

## 验证方式

- 读取 `MODULE.md` 与 `README.md`
- 对照 `docs/roadmap.md` / `docs/PROJECT_PROFILE.md` 检查能力描述
- 运行 `git diff --check -- MODULE.md README.md docs/plans/2026-04-23-readme-entry-sync.md`

## 验证结果

- 仓库根模块文档已建立，明确首页职责与不变量
- `README.md` 已新增到 `docs/guides/creative-workflow.md` 的入口
- `README.md` 已补齐章节/一幕评审、scenePlans、timeline/search/causality、entity graph、positioning/story contract 等现有能力
- README 已收敛为“入口摘要 + canonical guide 链接”，不再并行维护另一套完整细节

## 残留风险

- README 的命令概览仍是摘要，不会覆盖所有子命令参数细节
- 若后续 `docs/guides/creative-workflow.md` 继续扩展，README 仍需最小同步入口与摘要
