---
name: story-harness-writing
description: Structured fiction writing adapter for Codex. Use when Codex needs to operate the Story Harness CLI on a long-form writing project with explicit story state, chapter analysis, draft proposals, change requests, projections, and context refresh. Trigger for tasks such as initializing a story project, analyzing a chapter after writing, generating or reviewing change requests, refreshing a context lens, creating outline proposals, or running the Story Harness workflow without a visual editor.
---

# Story Harness Writing

## Overview

Use this skill as the Codex adapter for the `story-harness-cli` repository.

This skill does not own the core workflow logic anymore. The CLI repository is the source of truth:

```text
<story-harness-cli-repo-root>
```

Use the CLI to operate the workflow, and treat this skill as:

1. a trigger surface
2. a command guide
3. a reminder of protocol boundaries

## Workflow Decision Tree

### If the Story Harness CLI repo is available locally

Run commands from the repository root with `uv run`.

### If no story project exists yet

```powershell
uv run story-harness init --root <project-dir> --title "<title>" --genre "<genre>"
```

### If the user wants a single-chapter writing loop

Run these steps in order:

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

### For chapter-writing support

1. Read `context-lens.yaml` first if it exists.
2. Read the target chapter.
3. Run the single-chapter loop through `uv run story-harness ...`.
4. Summarize:
   - what changed
   - what was accepted or deferred
   - what the next chapter should remember

### For structure support

1. Read `outline.yaml` and the current chapter.
2. Draft the proposal in your own reasoning.
3. Persist it via `uv run story-harness outline propose ...`.
4. Only promote it after explicit author confirmation or a clearly requested autonomous run.

## Validation

Use the CLI repository for validation:

```powershell
uv run story-harness --help
uv run python -m unittest discover -s tests
```
