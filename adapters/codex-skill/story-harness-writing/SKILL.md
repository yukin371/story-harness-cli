---
name: story-harness-writing
description: Structured fiction writing adapter for Codex. Use when Codex needs to operate the Story Harness CLI on a long-form writing project with explicit story state, chapter analysis, draft proposals, change requests, projections, and context refresh. Trigger for tasks such as initializing a story project, analyzing a chapter after writing, generating or reviewing change requests, refreshing a context lens, creating outline proposals, or running the Story Harness workflow without a visual editor.
---

# Story Harness Writing

## Overview

Use this skill as the Codex adapter for the `story-harness-cli` repository.

The CLI repository is the source of truth:

```text
<story-harness-cli-repo-root>
```

This skill should stay thin. Its job is to:

1. trigger the right workflow
2. point Codex at the right files
3. route execution through `uv run story-harness ...`

## Workflow Decision Tree

### If `story-harness` is not installed or not executable

Run the repository fallback instead:

```powershell
$env:PYTHONPATH='src'
python -m story_harness_cli <command> ...
```

### If no story project exists yet

```powershell
uv run story-harness init --root <project-dir> --title "<title>" --genre "<genre>"
```

For long-form novels (5万字+), use layered layout to keep spec files organized and save AI context tokens:

```powershell
uv run story-harness init --root <project-dir> --title "<title>" --genre "<genre>" --layout layered
```

To migrate an existing flat project to layered layout:

```powershell
uv run story-harness migrate --root <project-dir>
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

### If the user wants the full writing-and-review loop

Run the chapter loop first, then close the loop with review and rewrite:

```text
write or revise chapter prose
  -> chapter analyze
  -> chapter suggest
  -> review apply
  -> projection apply
  -> context refresh
  -> review chapter
  -> review scene
  -> if scores are weak: revise prose / scenePlans
  -> chapter analyze
  -> review chapter
  -> review scene
  -> export or stop with explicit accepted risk
```

Do not stop at the first score if the weakest dimensions still contradict the story contract or target style.

### If the user wants foreshadow tracking

```powershell
uv run story-harness foreshadow plant --root <project-dir> --description "<伏笔描述>" --chapter-id <chapter-id> --planned-payoff <payoff-chapter-id>
uv run story-harness foreshadow resolve --root <project-dir> --foreshadow-id <fs-id> --payoff-chapter <chapter-id>
uv run story-harness foreshadow list --root <project-dir>
uv run story-harness foreshadow list --root <project-dir> --status planted
```

### If the user wants to review spec files (outline, character cards)

```powershell
uv run story-harness export --root <project-dir> --format spec-outline --output <path>.md
uv run story-harness export --root <project-dir> --format spec-characters --output <path>.md
```

These generate human-readable Markdown for outline review and character card review outside the CLI.

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
6. Treat `review chapter` and `review scene` as quality gates, not optional reporting. For commercial serials, also inspect `commercialAlignment` and platform-aware `weightedScores`.
7. If `scenePlans` exist in `outline.yaml`, use them as canonical scene boundaries before relying on heuristic splits.
8. In layered projects (`spec/` directory exists), spec files live in `spec/` — do not look for them at root.
9. Use `foreshadow plant` when planting a setup and `foreshadow resolve` when paying it off. Do not manually edit `foreshadowing.yaml`.
10. Use `export --format spec-outline / spec-characters` to generate human-readable Markdown for review before or during writing.

## Core Files

Read [references/protocol.md](./references/protocol.md) when you need the file layout or state semantics.

The most important files (flat layout — files at project root):

1. `project.yaml`
2. `outline.yaml`
3. `entities.yaml`
4. `chapters/*.md`
5. `proposals/draft-proposals.yaml`
6. `reviews/change-requests.yaml`
7. `reviews/story-reviews.yaml`
8. `projections/projection.yaml`
9. `projections/context-lens.yaml`
10. `foreshadowing.yaml`

In layered layout (when `spec/` directory exists), spec-eligible files move to `spec/`:

1. `project.yaml` (stays at root)
2. `spec/outline.yaml` (thin index; volume details in `spec/outlines/vol-NNN.yaml`)
3. `spec/entities.yaml`
4. `spec/timeline.yaml`
5. `spec/threads.yaml`
6. `spec/structures.yaml`
7. `spec/foreshadowing.yaml`
8. `chapters/*.md` (stays at root)
9. `proposals/`, `reviews/`, `projections/`, `logs/` (stay at root)

## Recommended Agent Behavior

1. Read `context-lens.yaml` first if it exists.
2. Read `project.yaml`, especially `positioning` and `storyContract`.
3. Read `outline.yaml` (or only the relevant volume via `load_outline_for_chapter` in layered projects), and use explicit `scenePlans` if present.
4. Read the target chapter or outline.
5. Route execution through `uv run story-harness ...`.
6. Run `review chapter`.
7. Run `review scene` on the weakest or most important scene.
8. If the result is weak, revise prose and re-run analysis + review before stopping.
9. Summarize accepted, deferred, low-score dimensions, and next-step context after each loop.
10. In layered layout, context refresh only loads the active volume's outline — saves context window for long novels.

## Stop Conditions

You may stop after one pass only when at least one of the following is true:

1. the user explicitly asked for a single pass
2. `review chapter` and `review scene` are already acceptable for the current target
3. remaining weaknesses are explicitly called out as accepted risk

If the weakest dimensions are still `needs-revision` or clearly conflict with `storyContract`, continue the loop.

## Validation

Use the CLI repository for validation:

```powershell
uv run story-harness --help
uv run python -m unittest discover -s tests
```
