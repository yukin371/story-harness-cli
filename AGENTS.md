# Configuration

此文档用于指导 AI 在本仓库中的工作方式。若与更高优先级系统或维护者指令冲突，以更高优先级为准。

## 项目概览

Story Harness CLI — Agent-native 小说创作工作流工具，Python 3.10+，零外部依赖，使用 argparse + JSON-compatible YAML 文件协议。当前处于早期功能积累阶段。

## 工作原则

1. 修改前先阅读当前执行入口、项目画像、架构护栏和目标模块文档。
2. 不编造事实；未确认项写 `TBD` 并附确认路径。
3. 新增 shared helper / utility / service / adapter 前，必须先搜索现有实现。
4. 非平凡改动前，先输出边界摘要与验证方案。
5. 若任务跨模块或存在风险，先创建 `docs/plans/YYYY-MM-DD-*.md`。
6. 仓库只能维护一个当前执行真相入口，禁止并列维护多个"当前计划"。
7. 修改模块前必须先读该模块文档；没有就先补文档。
8. 完成任务后必须同步文档，并输出验证结果与残留风险。
9. 禁止擅自添加 `Co-Authored-By`、`Pair-Programmed-By`、AI 工具签名或类似协作元信息。
10. 禁止擅自修改协作者、owner、branch protection、ruleset 等仓库设置类配置，除非维护者明确要求。

## 修改前必读顺序

1. `AGENTS.md`
2. 当前执行入口: `docs/roadmap.md`
3. `docs/PROJECT_PROFILE.md`
4. `docs/ARCHITECTURE_GUARDRAILS.md`
5. 目标模块下的 `MODULE.md`
6. 必要时再读相关 `plan` / `ADR`

## 关键项目约定

- **零外部依赖**: 所有代码仅使用 Python stdlib，不引入第三方包
- **JSON-compatible YAML**: 所有 `.yaml` 文件内容必须为合法 JSON（不用 YAML 特有特性）
- **命令注册**: 新命令必须在 `commands/__init__.py` 导出 + `cli.py` 的 `build_parser()` 中注册
- **服务层无副作用**: `services/` 中的函数只接受 state dict 并返回结果 dict，文件 I/O 由 commands 层负责
- **测试模式**: unittest + tempfile fixture，通过 `cli.main()` 直接调用

## 非平凡改动前必须输出

```text
目标模块：
现有 owner：
影响面：
计划改动：
验证方式：
需要同步的文档：
```

高风险改动再补:

```text
架构风险：
重复实现风险：
回滚路径：
兼容性影响：
```

## 必须停下并询问的情况

- 当前执行入口不明确
- 需要在两个模块之间新增共享 owner
- 需要引入 breaking change（CLI 参数、输出格式、数据模型变化）
- 需要改动 secrets、权限、安全边界
- 发现仓库已有未解释的大量脏改动
- 现有文档与代码状态严重冲突，无法推断真实状态
- 需要引入第三方依赖

## 完成后必须输出

```text
已完成改动：
验证结果：
未验证区域：
同步文档：
残留风险：
```
