# Commands 模块说明

> 最后更新: 2026-04-23
> 状态: 当前有效模块文档

## 1. 模块职责

- 定义所有 CLI 子命令的参数解析和处理逻辑
- 每个命令一个文件，通过 `register_xxx_commands(subparsers)` 注册
- 命令函数 `command_xxx_action(args) -> int` 负责串联 protocol → service → output

## 2. Owns

- argparse 子命令注册（`__init__.py` 导出 + `cli.py` 注册）
- 命令参数定义（--root, --chapter-id, --output 等）
- JSON 输出格式化（`print(json.dumps(...))`）
- 文件 I/O 时机控制（何时 save_state）
- workflow 命令编排（如 `review apply`、`review chapter`、`review scene` 的不同评审路径，以及 `review scene --list-scenes` 的场景枚举）
- `outline scene-add` / `outline scene-list` / `outline scene-detect` / `outline scene-update` / `outline scene-remove` 这类轻量结构维护命令
- `outline check` 这类“写作前门禁”命令，以及 `chapter suggest` 的 outline-first workflow gate
  默认门禁口径为 `project.positioning` / `project.storyContract` + chapter `direction` + `beats` + `scenePlans`
- 项目初始化参数装配（如 `init` 写入 positioning / storyContract / commercialPositioning）
- doctor 类命令中的项目元数据校验编排

## 3. Must Not Own

- 纯计算逻辑（委托 services/）
- 状态管理规则（委托 protocol/）
- 文本处理算法（委托 utils/）

## 4. 关键入口

- `commands/__init__.py`: 所有 `register_*_commands` 的导出汇总
- `cli.py`: `build_parser()` 构建完整 argparse 树
- 每个子模块: `register_xxx_commands` + `command_xxx_*` 函数

## 5. 关键依赖

- 依赖 `protocol/`: `ensure_project_root`, `load_project_state`, `save_state`
- 依赖 `services/`: 各业务逻辑服务
- 依赖 `utils/`: `now_iso`, `stable_hash`, 文本工具

## 6. 不变量

- 每个命令函数必须 `return 0` 表示成功
- 致命错误必须 `raise SystemExit("中文消息")`
- 输出统一使用 `print(json.dumps(result, ensure_ascii=False, indent=2))`
- 新命令必须在 `__init__.py` 和 `cli.py` 双重注册

## 7. 常见坑

- 忘记在 `cli.py` 的 `build_parser()` 中调用 `register_xxx_commands(subparsers)` 会导致命令不可见
- `argparse` 的 `dest` 参数和 `--entity-id` 的 kebab-case 需要显式 `dest="entity_id"`
- `review scene` 的段落范围是 1-based 且基于“去掉标题后的正文段落”计数，和 markdown 原始行号不是一回事
- `review scene --scene-index` 在没有 `scenePlans` 时会回退到启发式候选场景
- 一旦章节里存在显式 `scenePlans`，`review scene --scene-index` 会优先使用显式边界，而不是启发式切分
- `outline scene-update` 更新段落范围时，必须同时提供 `--start-paragraph` 和 `--end-paragraph`
- `outline scene-detect` 默认不会覆盖已有 `scenePlans`，需要显式传入 `--replace`
- `chapter suggest` 默认要求目标章节先通过 `outline check`，旧项目如需跳过必须显式传 `--allow-without-outline`
- `outline check` 默认是严格模式；只有显式传入 `--allow-missing-project-gate`、`--allow-missing-beats`、`--allow-missing-scene-plans` 才会放宽

## 8. 测试方式

- 单元测试: 各 `tests/smoke/test_xxx_command.py`
- 调用方式: `from story_harness_cli.cli import main; main(["command", "subcommand", ...])`
- 输出捕获: `contextlib.redirect_stdout(StringIO())`

## 9. 文档同步触发条件

- 新增/删除命令
- 命令参数变化（breaking change）
- 输出格式变化
- workflow 文件读写路径变化
- 注册方式变化
