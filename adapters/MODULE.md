# adapters 模块说明

> 最后更新: 2026-04-23
> 状态: 当前有效模块文档

## 1. 模块职责

- 维护 `story-harness-cli` 面向外部 AI 宿主的 adapter 源文件
- 把仓库内真实工作流翻译成宿主可执行的 skill / prompt / reference 文档
- 明确哪些协议文件要读、哪些命令要跑、何时算流程完成

## 2. Owns

- `adapters/README.md`
- `adapters/codex-skill/story-harness-writing/*`
- `adapters/claude-code/story-harness-writing/*`

## 3. 不变量

- adapter 必须保持“薄”，执行层仍是 `story-harness` CLI
- adapter 不得和仓库真实能力口径冲突
- adapter 必须说明 canonical workflow，而不是只罗列零散命令
- adapter 必须说明运行 fallback、关键协议文件、停止条件

## 4. 文档同步触发条件

- CLI 工作流变化
- 协议文件布局变化
- 新增章节/场景评审或回归步骤
- adapter 的默认 prompt 或 skill 触发规则变化
