# Story Harness CLI

Story Harness CLI is an agent-native fiction workflow tool for long-form narrative writing.

It helps AI agents and authors work with structured story state instead of relying on a single giant prompt. The workflow separates prose, proposals, reviews, projection, and local context refresh, so long-form writing can evolve with clearer constraints and less state drift.

This repository currently provides:

- a file-based story protocol
- a Python CLI for state transitions
- minimal examples and smoke-test fixtures

It does not aim to replace a writing UI. Instead, it provides the protocol and workflow core that different skills, editors, and future interfaces can reuse.

## What It Solves

- Keep proposals separate from canon
- Turn chapter analysis into explicit review steps
- Update machine-readable projection only after a decision step
- Refresh a local writing context for the next loop

## Core Model

The current workflow uses these layers:

1. `chapters/*.md` for prose
2. `proposals/draft-proposals.yaml` for write-before-canon proposals
3. `reviews/change-requests.yaml` for write-after-analysis suggestions
4. `projections/projection.yaml` for current machine-facing truth
5. `projections/context-lens.yaml` for local chapter context

## Quickstart

```powershell
uv sync
uv run story-harness init --root .\demo --title "Fog Harbor" --genre "Mystery"
```

Then edit `demo/chapters/chapter-001.md` and run:

```powershell
uv run story-harness chapter analyze --root .\demo --chapter-id chapter-001
uv run story-harness chapter suggest --root .\demo --chapter-id chapter-001
uv run story-harness review apply --root .\demo --chapter-id chapter-001 --all-pending --decision accepted
uv run story-harness projection apply --root .\demo --chapter-id chapter-001
uv run story-harness context refresh --root .\demo --chapter-id chapter-001
uv run story-harness doctor --root .\demo
```

## Example Workflow

Single chapter loop:

```text
chapter.md
  -> chapter analyze
  -> chapter suggest
  -> review apply
  -> projection apply
  -> context refresh
```

Outline loop:

```text
goal or reasoning
  -> outline propose
  -> outline promote
  -> projection apply
```

## Command Overview

- `story-harness init`
- `story-harness chapter analyze`
- `story-harness chapter suggest`
- `story-harness review apply`
- `story-harness outline propose`
- `story-harness outline promote`
- `story-harness projection apply`
- `story-harness context refresh`
- `story-harness doctor`

## Project Layout

- `src/story_harness_cli/` - CLI implementation
- `adapters/` - host-specific adapter sources for Codex, Claude Code, and future hosts
- `scripts/install_adapter.py` - install a host adapter into Codex or Claude skill directories
- `scripts/install_adapters.py` - batch-install adapters for multiple hosts
- `docs/` - protocol and guide docs
- `examples/` - user-facing sample projects
- `tests/` - smoke tests and fixtures

## Current Scope

The current implementation focuses on:

- file-based protocol
- heuristic chapter analysis
- change request generation
- explicit review decisions
- projection updates
- context lens refresh

The current release does not yet include dedicated graph, timeline, or branch analysis commands.

## Development

Sync the environment:

```powershell
uv sync
```

Run smoke tests:

```powershell
uv run python -m unittest discover -s tests
```

Run structural validation against a story project:

```powershell
uv run story-harness doctor --root .\demo
```

Install a host adapter:

```powershell
uv run python scripts/install_adapter.py --host codex --force
uv run python scripts/install_adapter.py --host claude --workspace <workspace-root> --force
```

Install multiple adapters in one shot:

```powershell
uv run python scripts/install_adapters.py --workspace <workspace-root> --force
```

Contributor and release docs:

- `CONTRIBUTING.md`
- `docs/guides/releasing.md`

## Roadmap

- Stabilize command contract and fixtures
- Validate against real Story Harness chapter samples
- Add deeper schema validation for timeline / branch / graph semantics
- Evaluate Go rewrite when distribution and binary size become release concerns
