# AI Repo Init Prompt

> 用途: 给任意 AI 一段可以直接复制粘贴的仓库初始化指令
> 适用场景: 新仓库接手、存量仓库补治理、`/init` 或类似初始化命令
> 配套文件:
> - `docs/AI_REPO_BOOTSTRAP_PLAYBOOK.md`
> - `docs/templates/README.md`

## 1. 最推荐用法

如果目标 AI 支持先读仓库文件再执行初始化，把下面这段直接贴给它即可:

```text
你正在接手一个仓库。你的第一目标不是直接修改业务代码，而是先完成仓库初始化治理。

请严格按以下文件执行：
1. `docs/AI_REPO_BOOTSTRAP_PLAYBOOK.md`
2. `docs/templates/README.md`

初始化要求：
- 先建立项目画像
- 建立根目录 AGENTS.md
- 建立唯一当前执行入口，只能二选一：
  - `docs/roadmap.md`
  - `docs/plans/current-execution-control.md`
- 建立 `docs/ARCHITECTURE_GUARDRAILS.md`
- 为 1 到 3 个关键模块建立模块文档
- 建立工程治理文档与自动化防线：
  - 提交规则
  - git hooks
  - CI governance
  - 文档生命周期
  - release checklist

初始化过程必须遵守：
- 不编造事实，未知项写 `TBD`
- 不得并行创建多个“当前计划”文档
- 新增 shared helper / adapter / service 前必须先搜索现有实现
- 不得擅自添加 `Co-Authored-By`、`Pair-Programmed-By` 或 AI 工具签名
- 每个非平凡改动前，先输出：
  目标模块、现有 owner、影响面、计划改动、验证方式、需要同步的文档
- 完成后必须输出：
  已完成改动、验证结果、未验证区域、同步文档、残留风险

初始化完成的最低交付物：
- `docs/PROJECT_PROFILE.md`
- `AGENTS.md`
- 一个且仅一个当前执行入口
- `docs/ARCHITECTURE_GUARDRAILS.md`
- 关键模块文档
- `docs/plans/` 与 `docs/adr/` 最小入口
- 提交规则 / hooks / CI governance 资产

如果仓库里已有同类文档，优先复用与补全，不要平行新建重复入口。
```

## 2. `/init` 风格用法

如果目标 AI 支持 `/init`、`init` 或类似命令，推荐这样下指令:

```text
/init
按 `docs/AI_REPO_BOOTSTRAP_PLAYBOOK.md` 和 `docs/templates/README.md` 初始化本仓库。
要求：
- 复用现有文档，不重复造入口
- 建立唯一当前执行入口
- 补齐项目画像、架构护栏、关键模块文档
- 补齐提交规则、hooks、CI governance
- 禁止添加 `Co-Authored-By` 或 AI 工具签名
- 完成后汇报：已完成改动 / 验证结果 / 同步文档 / 残留风险
```

## 3. 最小精简版

如果你只想给 AI 一个非常短的启动指令，复制这段:

```text
请不要直接改业务代码，先按 `docs/AI_REPO_BOOTSTRAP_PLAYBOOK.md` 初始化本仓库治理骨架，并优先使用 `docs/templates/README.md` 中的模板。
要求补齐：
- `docs/PROJECT_PROFILE.md`
- `AGENTS.md`
- 唯一当前执行入口
- `docs/ARCHITECTURE_GUARDRAILS.md`
- 关键模块文档
- 提交规则、git hooks、CI governance

禁止：
- 编造事实
- 创建多个当前计划入口
- 擅自添加 `Co-Authored-By` 或 AI 工具签名
```

## 4. 给你自己的建议

如果你要把这套东西复制到别的仓库，最实用的带法是:

1. 复制 `docs/AI_REPO_BOOTSTRAP_PLAYBOOK.md`
2. 复制整个 `docs/templates/`
3. 复制本文件 `docs/AI_REPO_INIT_PROMPT.md`

这样你有三层入口:

- `AI_REPO_BOOTSTRAP_PLAYBOOK.md`: 总规则
- `docs/templates/`: 具体模板
- `AI_REPO_INIT_PROMPT.md`: 直接贴给 AI 的启动指令
