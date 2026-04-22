# Services 模块说明

> 最后更新: 2026-04-22
> 状态: 当前有效模块文档

## 1. 模块职责

- 纯业务逻辑：章节分析、变更请求生成、投影管理、一致性校验、实体丰富化、灵感生成、统计计算
- 所有函数接受 state dict（+ 必要参数），返回结果 dict
- 无副作用：不读写文件，不打印输出

## 2. Owns

- `analyzer.py`: 章节分析（实体识别、状态检测、关系检测、场景范围）
- `change_requests.py`: 变更请求生成与审核
- `projection_engine.py`: 投影状态管理（upsert_by_key 去重）
- `consistency_engine.py`: 一致性校验（hard checks: 状态/关系矛盾; soft checks: 大纲偏离）
- `entity_enricher.py`: 角色外貌/能力提取与丰富化提案
- `context_lens.py`: 写作上下文构建
- `inspiration.py`: 随机灵感生成（姓名、角色、世界、大纲骨架）
- `stats.py`: 项目统计（进度、字数、实体、投影）

## 3. Must Not Own

- 文件 I/O（不读文件、不写文件）
- argparse 参数处理
- JSON 输出格式化
- 状态持久化决策

## 4. 关键入口

- `analyze_chapter(root, state, chapter_id)`: 完整章节分析
- `generate_change_requests(state, analysis)`: 分析 → 变更请求
- `apply_projection(state, analysis, chapter_id)`: 投影应用
- `check_consistency(state, chapter_text, chapter_id)`: 一致性校验
- `enrich_entities(state, chapter_id, root)`: 实体丰富化
- `refresh_context_lens(state, chapter_id, analysis)`: 上下文刷新
- `compute_project_stats(state, root)`: 项目统计

## 5. 关键依赖

- 依赖 `utils/text.py`: 关键词匹配、标签提取、段落拆分
- 依赖 `utils/hashing.py`: 指纹生成（去重用）
- 依赖 `data/`: 创作数据表（inspiration.py 专用）

## 6. 不变量

- 纯函数：相同输入必定产生相同输出
- 不修改传入的 state dict（返回新 dict）
- `entity_enricher.py` 是唯一例外：接受 `root: Path` 参数读取章节文件

## 7. 常见坑

- `entity_enricher.py` 跨段落实体归属问题：当多个实体出现在同一段落时，提取的属性可能错配给后出现的实体
- `consistency_engine.py` 的 negation 检查仅适用于 `INTIMATE_WORDS_NEED_NEGATION_CHECK` 集合中的词
- `projection_engine.py` 的 `upsert_by_key` 使用 `|` 合并 dict，确保 payload 完整覆盖

## 8. 测试方式

- 单元测试: `tests/smoke/test_*_engine.py`, `tests/smoke/test_*_enricher.py`
- 通常通过 commands 层间接测试

## 9. 文档同步触发条件

- 新增/删除 service
- service 接口变化（参数、返回值结构）
- 关键词表变化
- 去重/匹配逻辑变化
