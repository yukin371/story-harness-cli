# 创作闭环指南落地

> 日期: 2026-04-23
> 状态: 已完成

## 目标模块

- `docs/guides/*`
- `docs/plans/*`

## 现有 owner

- 指南 owner: `docs/guides/*`
- 计划记录 owner: `docs/plans/*`

## 影响面

- 为作者和外部 AI 提供统一的完整创作闭环
- 提升评审、改稿、复评和导出的可执行性
- 不修改 CLI 行为，不新增依赖

## 计划改动

1. 为 `docs/guides/` 补充模块文档，明确职责与不变量
2. 新增一份以 Mermaid 呈现的创作闭环指南
3. 在 `quickstart` 中增加到闭环指南的入口
4. 明确作者口径、外部 AI 口径、停止条件与 fallback 命令

## 验证方式

- 读取 `docs/guides/creative-workflow.md`，确认闭环步骤、Mermaid 图和停止条件齐全
- 读取 `docs/guides/quickstart.md`，确认存在到闭环指南的入口与复评步骤
- 运行 `git diff --check -- docs/guides/MODULE.md docs/guides/creative-workflow.md docs/guides/quickstart.md docs/plans/2026-04-23-creative-workflow-guide.md`

## 验证结果

- `docs/guides/MODULE.md` 已建立，明确了 guides 模块职责、owns 与不变量
- `docs/guides/creative-workflow.md` 已补齐完整创作闭环、作者清单、外部 AI 清单、停止条件与 fallback
- `docs/guides/quickstart.md` 已新增到闭环指南的入口，并补充 `review chapter`、`review scene` 与低分复评流程
- `git diff --check` 通过，未出现空白符错误；当前仅存在 Git 对工作区 `LF/CRLF` 的转换提示

## 残留风险

- Mermaid 图只做了文本级校对，尚未经过渲染器预览
- 顶层 `README.md` 仍以简化流程为主，读者若只看仓库首页，仍可能先看到短版流程
