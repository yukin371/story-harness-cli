# Protocol

This Codex adapter follows the `story-harness-cli` file protocol.

The current project layout is:

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

Key constraints:

1. `Draft Proposal` is not canon.
2. `Change Request` is not canon.
3. `Projection` only consumes accepted or applied inputs.
4. `Context Lens` is derived from projection and recent analysis.

Chinese prose guidance:

1. Use `@{实体}` in continuous Chinese prose.
2. Use `@entity` when the mention is already delimited by whitespace or punctuation.

For the repository-owned protocol docs, read:

1. `docs/protocol/overview.md`
2. `docs/protocol/file-layout.md`
3. `docs/protocol/lifecycle.md`

