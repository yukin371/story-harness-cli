# Services 模块说明

> 最后更新: 2026-04-23
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
- `outline_guard.py`: 章节大纲前置检查，判断是否具备项目定位 / 故事契约 + direction / beats / scenePlans 进入写作或细化
- `story_review.py`: 章节回顾评分、一幕评审、类型/平台加权评分、评论、改稿建议、契约对齐与商业连载对齐检查
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
- `evaluate_project_story_gate(state)`: 检查项目是否已具备 `primaryGenre`、`targetAudience`、`corePromises`、`paceContract`
- `evaluate_chapter_outline_readiness(state, chapter_id, require_beats=True, require_scene_plans=True, require_project_gate=True)`: 检查单章是否已具备严格大纲前置设计
- `evaluate_project_outline_readiness(state, chapter_id=None, require_beats=True, require_scene_plans=True, require_project_gate=True)`: 生成项目级或章节级大纲门禁报告
- `build_chapter_review(state, chapter_id, chapter_text, analysis)`: 章节质量回顾，输出通用 `scores`、类型/平台加权 `weightedScores`、`contractAlignment` 与 `commercialAlignment`
- `build_scene_review(state, chapter_id, chapter_text, start_paragraph, end_paragraph, analysis)`: 一幕质量回顾，输出功能性、连续性、逻辑、伏笔、清晰度，以及一幕级 `contractAlignment` 与 `commercialAlignment`
- `list_scene_candidates(chapter_text)`: 基于正文段落启发式切分候选 scene 范围，供 `review scene --list-scenes/--scene-index` 使用
- `resolve_scene_candidates(chapter_entry, chapter_text)`: 优先读取显式 `scenePlans`，否则回退到启发式候选 scene
- `detect_scene_plans(chapter_id, chapter_text)`: 把启发式候选 scene 转成可持久化的显式 `scenePlans`
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
- `story_review.py` 里 `primaryGenre` 与 `subGenre`/`styleTags` 的归一化口径不同：前者归主类，后者保留细分类 slug
- `story_review.py` 的 `weightedScores.profile` 现在还会保留 `commercialPositioning.targetPlatform`，用于解释平台修正来源
- `build_scene_review` 当前按段落范围近似 scene，不是结构化 scene graph；结果应视为启发式提示
- `resolve_scene_candidates` 只有在 `scenePlans` 缺失时才会启用启发式切分
- `detect_scene_plans` 只是把启发式切分结果显式化，不代表作者意图已完全确认
- 一幕级 `contractAlignment` 复用了章节级契约思想，但阈值更偏向“局部兑现/局部钩子”，不等同于整章判断
- `commercialAlignment` 目前基于 hook、字数目标、章末钩子等启发式信号，不等同于真实市场反馈预测
- `evaluate_project_story_gate` 的用途是把“先确定市场定位和故事承诺，再拆章节”变成硬门禁，而不是 review 阶段的软建议

## 8. 测试方式

- 单元测试: `tests/smoke/test_*_engine.py`, `tests/smoke/test_*_enricher.py`
- 通常通过 commands 层间接测试

## 9. 文档同步触发条件

- 新增/删除 service
- service 接口变化（参数、返回值结构）
- 评分 rubric 或 review 结果结构变化
- 契约对齐规则变化
- 关键词表变化
- 去重/匹配逻辑变化
