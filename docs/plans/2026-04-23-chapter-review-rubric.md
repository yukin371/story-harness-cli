# 章节回顾与评分能力设计

> 日期: 2026-04-23
> 状态: 已落地

## 背景

当前 CLI 已覆盖创作前约束和章节分析/审批/投影流程，但缺少“写完后怎么回顾并改进”的标准化能力。现有 `review apply` 只负责审批 `changeRequests`，不适合承载章节质量评分与评论。

## 目标

1. 为已写章节生成结构化回顾报告
2. 提供稳定的评分 rubric，便于横向比较和迭代改稿
3. 不影响既有 `review apply` 审批流与 projection 流

## 设计决策

### 命令

- 扩展 `review` 命令组，新增 `review chapter`
- 输入: `--root`、`--chapter-id`
- 输出: JSON 格式章节回顾报告

### 状态与文件

- 新增状态 key: `story_reviews`
- 新增文件: `reviews/story-reviews.yaml`
- 文件结构:

```json
{
  "rubricVersion": "chapter-review-v1",
  "chapterReviews": []
}
```

### Rubric

采用五个维度，每项 0-20 分，总分 100 分：

1. `plotMomentum`: 情节推进
2. `characterPressure`: 人物压力与状态变化
3. `conflictTension`: 冲突/悬念张力
4. `sceneClarity`: 场景与叙事清晰度
5. `proseControl`: 段落控制与表达节奏

每个维度输出：

- `score`
- `maxScore`
- `comment`
- `signals`
- `suggestions`

### 评分来源

- 章节正文文本
- `chapter analyze` 的分析结果（若存在日志则复用）
- 现有 utils 文本能力：段落切分、字数统计、标签提取

### 兼容性策略

- `review apply` 保持原语义，不复用 `reviews.changeRequests`
- `doctor`、`init`、`load/save state` 补齐对新文件的识别
- 没有分析日志时，`review chapter` 仍可仅基于正文给出回顾结果

## 验证

- 新增 smoke test 覆盖：
  - `review chapter` 生成报告并持久化
  - 无分析日志时仍能运行
- 回归：
  - `test_schema.py`
  - `test_doctor.py`
  - `test_full_creative_loop.py`
