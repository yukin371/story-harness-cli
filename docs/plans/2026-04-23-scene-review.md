# 一幕级评审落地

> 日期: 2026-04-23
> 状态: 进行中

## 目标模块

- `src/story_harness_cli/commands/review.py`
- `src/story_harness_cli/services/story_review.py`
- `src/story_harness_cli/protocol/schema.py`
- `src/story_harness_cli/protocol/state.py`

## 现有 owner

- 一幕/章节质量评审 owner: `services/story_review.py`
- `review` CLI 编排 owner: `commands/review.py`
- `reviews/story-reviews.yaml` 状态 owner: `protocol/schema.py` + `protocol/state.py`

## 影响面

- 新增 `review scene` 子命令
- `reviews/story-reviews.yaml` 新增 `sceneReviews`
- 章节正文按段落范围抽取片段进行启发式评审
- smoke tests / 文档同步

## 计划改动

1. 在 `story_reviews` schema 中增加 `sceneReviews`
2. 在 `services/story_review.py` 中新增一幕级评分与评论构建函数
3. 在 `review.py` 中新增 `review scene`，支持按章节 + 段落范围评审
4. 复用现有 `story-reviews.yaml` 持久化，按 `fingerprint` 去重
5. 补 smoke tests，覆盖输出结构与持久化
6. 同步 guide / module / file layout 文档

## 最小范围

- 先只支持按 `chapter-id + start-paragraph + end-paragraph` 选取片段
- 先评 5 项：
  - `sceneFunction`
  - `continuity`
  - `logic`
  - `foreshadowing`
  - `sceneClarity`
- 先做启发式，不引入新的结构化伏笔账本

## 验证方式

- `python -m unittest tests.smoke.test_review_scene tests.smoke.test_review_chapter tests.smoke.test_schema`
- `python -m unittest discover -s tests`
- `$env:PYTHONPATH='src'; python -m story_harness_cli review scene --help`

## 需要同步的文档

- `docs/guides/genre-review-rubric.md`
- `docs/protocol/file-layout.md`
- `src/story_harness_cli/commands/MODULE.md`
- `src/story_harness_cli/services/MODULE.md`
- `src/story_harness_cli/protocol/MODULE.md`

## 架构风险

- 片段边界不是结构化 scene，只能用段落范围近似，输出必须明确是启发式

## 重复实现风险

- 不新增第二份 review service；统一放在 `story_review.py`

## 回滚路径

- 若体验不稳定，可移除 `review scene` 命令与 `sceneReviews` 持久化，不影响现有章节评审

## 兼容性影响

- 保留现有 `chapterReviews` 和 `rubricVersion`
- 仅新增 `sceneReviews` / `sceneRubricVersion`
