# Protocol 模块说明

> 最后更新: 2026-04-22
> 状态: 当前有效模块文档

## 1. 模块职责

- 定义项目文件结构约定（哪些文件必须存在、路径规则）
- 加载和保存项目状态（所有 YAML 文件的统一读写）
- 提供默认 schema
- 大纲同步（volumes ↔ flat chapters）

## 2. Owns

- `ROOT_FILES` 常量：必须存在的根目录文件列表
- `load_project_state(root)`: 将所有 YAML 文件加载为统一 state dict
- `save_state(root, state)`: 将 state dict 写回各 YAML 文件
- `default_project_state()`: 返回所有 key 的空默认值
- `_sync_outline()`: volumes → flat chapters 自动同步

## 3. Must Not Own

- 业务逻辑（分析、投影、一致性等）
- 文件路径之外的项目约定

## 4. 关键入口

- `protocol/__init__.py`: `ensure_project_root`, `load_project_state`, `save_state`
- `protocol/files.py`: `ROOT_FILES`, `chapter_path`, `root_file`
- `protocol/io.py`: `dump_json_compatible_yaml`, `load_json_compatible_yaml`
- `protocol/schema.py`: `default_project_state`
- `protocol/state.py`: `_sync_outline`, re-exports

## 5. 关键依赖

- 依赖 `utils/hashing.py`: 仅 `state.py` 中的指纹生成

## 6. 不变量

- `save_state` 开头始终调用 `_sync_outline`，保证 volumes 和 flat chapters 一致
- 所有 YAML 文件内容必须为合法 JSON
- `load_project_state` 对缺失文件使用 schema 默认值填充
- `chapter_path` 的 fallback glob 查找只在 `chapters/` 目录内

## 7. 常见坑

- `_sync_outline` 会覆盖 `outline["chapters"]` 和 `outline["chapterDirections"]`，不要手动维护这两个字段
- Windows 下路径需要用 `Path.resolve()` 避免反斜杠问题

## 8. 测试方式

- 单元测试: `tests/smoke/test_schema.py` 验证 schema 默认值
- 集成测试: 几乎所有测试都通过 `load_project_state` 间接测试

## 9. 文档同步触发条件

- 新增或删除 ROOT_FILES 中的文件
- `_sync_outline` 逻辑变化
- `default_project_state` 结构变化
- 文件路径约定变化
