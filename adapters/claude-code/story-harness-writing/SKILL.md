---
name: story-harness-writing
description: Structured fiction writing adapter for Claude Code. Use when Claude Code needs to operate the Story Harness CLI on a long-form writing project with explicit story state, chapter analysis, draft proposals, change requests, projections, and context refresh. Trigger for tasks such as initializing a story project, analyzing a chapter after writing, generating or reviewing change requests, refreshing a context lens, creating outline proposals, or running the Story Harness workflow without a visual editor.
---

# Story Harness Writing

## Overview

Use this skill as the Claude Code adapter for the `story-harness-cli` repository.

The CLI repository is the source of truth:

```text
<story-harness-cli-repo-root>
```

This skill should stay thin. Its job is to:

1. trigger the right workflow
2. point Claude Code at the right files
3. route execution through `uv run story-harness ...`

## Workflow Decision Tree

### If no story project exists yet

```powershell
uv run story-harness init --root <project-dir> --title "<title>" --genre "<genre>"
```

### If the user wants a single-chapter writing loop

```powershell
uv run story-harness chapter analyze --root <project-dir> --chapter-id <chapter-id>
uv run story-harness chapter suggest --root <project-dir> --chapter-id <chapter-id>
uv run story-harness review apply --root <project-dir> --all-pending --decision accepted --chapter-id <chapter-id>
uv run story-harness projection apply --root <project-dir> --chapter-id <chapter-id>
uv run story-harness context refresh --root <project-dir> --chapter-id <chapter-id>
```

Use `ignored` or `deferred` instead of `accepted` when the author does not want a suggestion to enter canon.

### If the user wants structure planning or chapter direction proposals

```powershell
uv run story-harness outline propose --root <project-dir> --mode chapter --title "<title>" --summary "<summary>" --chapter-id <chapter-id> --prompt "<prompt>" --item "<beat title>::<beat summary>"
uv run story-harness outline promote --root <project-dir> --proposal-id <proposal-id> --chapter-id <chapter-id>
uv run story-harness projection apply --root <project-dir> --chapter-id <chapter-id>
```

## Operational Rules

1. Keep `Draft Proposal`, `Change Request`, `Projection`, and chapter prose separate.
2. Never write canon changes straight into projection files without an explicit decision step.
3. Treat `chapters/*.md` as author-facing prose and the `*.yaml` files as machine-facing state.
4. Prefer explicit `@{实体}` mentions in Chinese prose when no entity registry exists yet; keep `@entity` as shorthand for English or clearly delimited mentions.
5. Use the CLI as the execution layer and keep freeform editing for prose or intentional proposal revisions.

## Core Files

Read [references/protocol.md](./references/protocol.md) when you need the file layout or state semantics.

The most important files are:

1. `project.yaml`
2. `outline.yaml`
3. `entities.yaml`
4. `chapters/*.md`
5. `proposals/draft-proposals.yaml`
6. `reviews/change-requests.yaml`
7. `projections/projection.yaml`
8. `projections/context-lens.yaml`

## Recommended Agent Behavior

1. Read `context-lens.yaml` first if it exists.
2. Read the target chapter or outline.
3. Route execution through `uv run story-harness ...`.
4. Summarize accepted, deferred, and next-step context after each loop.

## Validation

Use the CLI repository for validation:

```powershell
uv run story-harness --help
uv run python -m unittest discover -s tests
```
