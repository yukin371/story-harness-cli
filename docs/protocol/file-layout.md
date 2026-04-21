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
  projections/
    projection.yaml
    context-lens.yaml
  logs/
    latest-analysis.yaml
    projection-log.yaml
```

All `*.yaml` files currently store JSON-formatted text. This keeps the prototype deterministic and stdlib-friendly while remaining YAML 1.2 compatible.

