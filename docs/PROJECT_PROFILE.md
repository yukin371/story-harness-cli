# Story Harness CLI 项目画像

> 最后更新: 2026-04-22
> 事实来源: `README.md`、`pyproject.toml`、入口代码、测试目录
> 说明: 只记录高置信度事实；未确认项标记为 `TBD`

## 1. 项目类型

- 主语言: Python 3.10+
- 仓库类型: CLI 工具（单包）
- 当前主线: `main`
- 主模块: `src/story_harness_cli/`

## 2. 当前定位

Agent-native 小说创作工作流 CLI。将长篇小说的创作状态拆分为结构化文件层（proposals / reviews / projections / context），让 AI agent 和作者在明确的约束下协作，减少设定漂移和状态丢失。当前处于早期功能积累阶段。

## 3. 运行与构建入口

- 主程序入口: `src/story_harness_cli/main.py` → `story_harness_cli.cli:main`
- 构建系统: hatchling (`pyproject.toml`)
- 本地运行方式: `PYTHONPATH=src python -m story_harness_cli <command>` 或 `pip install -e .` 后 `story-harness <command>`
- 关键命令矩阵:

| 命令 | 子命令 | 用途 |
|------|--------|------|
| `init` | — | 初始化项目 |
| `brainstorm` | `character` / `world` / `outline` | 灵感生成 |
| `outline` | `propose` / `promote` | 大纲管理 |
| `chapter` | `analyze` / `suggest` | 章节分析 |
| `review` | `apply` | 审核变更请求 |
| `projection` | `apply` | 应用投影 |
| `context` | `refresh` / `show` | 写作上下文 |
| `entity` | `enrich` / `review` / `list` / `show` | 角色管理 |
| `consistency` | `check` | 一致性校验 |
| `stats` | — | 项目统计 |
| `export` | — | 导出纯文本 |
| `doctor` | — | 项目校验 |

## 4. 技术栈

- 运行时: Python 3.10+（stdlib only，零外部依赖）
- 框架: argparse（子命令路由）
- 持久化: JSON-compatible YAML 文件（`.yaml` 后缀，内容为合法 JSON）
- 测试框架: unittest（stdlib）
- CI 平台: TBD

## 5. 当前验证基线

- Lint: TBD（无 linter 配置）
- Test: `PYTHONPATH=src python -m unittest discover -s tests`（54 个测试）
- Build: `pip install -e .`（需 hatchling）
- Security: TBD
- Release: TBD

## 6. 仓库拓扑

- `src/story_harness_cli/commands/`: CLI 子命令实现（每个命令一个模块）
- `src/story_harness_cli/services/`: 业务逻辑层（分析、投影、一致性等）
- `src/story_harness_cli/protocol/`: 状态加载/保存、文件路径、schema 默认值
- `src/story_harness_cli/utils/`: 通用工具（哈希、时间、文本处理）
- `src/story_harness_cli/data/`: 创作数据表（角色原型、世界元素、中文姓名等）
- `tests/smoke/`: 冒烟测试
- `tests/fixtures/minimal_project/`: 最小测试 fixture
- `docs/`: 文档与模板
- `adapters/`: 宿主适配器（Codex、Claude Code 等）
- `scripts/`: 安装脚本

## 7. 现有治理骨架

- 当前执行入口: 本文档创建前无（本文件为首次建立）
- 架构护栏: 无（本文件为首次建立）
- 模块文档规范: 无
- 报告 / issue / archive 入口: 无
- hooks / commit policy / CI governance: 无

## 8. 已知高风险区域

- `protocol/state.py` 的 `_sync_outline()`: volumes 与 flat chapters 的同步逻辑，直接影响大纲一致性
- `services/analyzer.py`: 实体识别逻辑（`@{名称}` vs `@名称`），影响后续所有分析
- `utils/text.py`: 关键词表（STATE_KEYWORDS / APPEARANCE_KEYWORDS / ABILITY_KEYWORDS），硬编码中文关键词
- `services/entity_enricher.py`: 跨段落实体归属问题（已知 bug：多实体同段落时属性可能错配）

## 9. 缺失或待确认项

- CI/CD 配置: TBD（确认路径：maintainer 决定是否使用 GitHub Actions）
- lint 工具: TBD（确认路径：ruff / flake8 选型）
- 发布流程: TBD（确认路径：PyPI 发布 + 版本策略）
- 适配器安装脚本的实际使用情况: TBD
