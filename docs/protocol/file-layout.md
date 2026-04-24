# File Layout

```text
story-project/
  project.yaml
  outline.yaml
  entities.yaml
  timeline.yaml
  branches.yaml
  chapters/
    chapter-001.md
  proposals/
    draft-proposals.yaml
  reviews/
    change-requests.yaml
    story-reviews.yaml
  projections/
    projection.yaml
    context-lens.yaml
  logs/
    latest-analysis.yaml
    projection-log.yaml
```

All `*.yaml` files currently store JSON-formatted text. This keeps the prototype deterministic and stdlib-friendly while remaining YAML 1.2 compatible.

`project.yaml` 现在除了基础的 `positioning` / `storyContract`，还可维护 `commercialPositioning`，用于记录连载项目的 premise、hook、平台、更新节奏和章节字数目标。

`reviews/story-reviews.yaml` currently stores both `chapterReviews` and `sceneReviews`.

`outline.yaml` 的章节条目可选维护 `scenePlans`，供 `review scene --scene-index` 优先读取显式场景边界。
