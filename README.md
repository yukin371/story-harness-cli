# Story Harness CLI

Story Harness CLI is an agent-native fiction workflow tool for long-form narrative writing.

It helps AI agents and authors work with structured story state instead of relying on a single giant prompt. The workflow separates prose, proposals, reviews, projection, and local context refresh, so long-form writing can evolve with clearer constraints and less state drift.

If you want the canonical end-to-end writing loop first, read [docs/guides/creative-workflow.md](./docs/guides/creative-workflow.md).

This repository currently provides:

- a file-based story protocol
- a Python CLI for state transitions
- minimal examples and smoke-test fixtures
- commercial long-form samples with project-level positioning and serial-writing blueprint

It does not aim to replace a writing UI. Instead, it provides the protocol and workflow core that different skills, editors, and future interfaces can reuse.

## What It Solves

- Keep proposals separate from canon
- Turn chapter analysis into explicit review steps
- Update machine-readable projection only after a decision step
- Refresh a local writing context for the next loop
- Review both chapter-level and scene-level quality before stopping
- Manage fiction as an iterative engineering workflow instead of a single drafting pass

## Core Model

The current workflow uses these layers:

1. `chapters/*.md` for prose
2. `proposals/draft-proposals.yaml` for write-before-canon proposals
3. `reviews/change-requests.yaml` for write-after-analysis suggestions
4. `projections/projection.yaml` for current machine-facing truth
5. `projections/context-lens.yaml` for local chapter context

## Quickstart

Option A: initialize a new project

```powershell
uv sync
uv run story-harness init --root .\demo --title "Fog Harbor" --genre "Mystery"
```

For a real web-serial project, initialize the commercial blueprint at the same time instead of leaving it as afterthought metadata:

```powershell
uv run story-harness init `
  --root .\demo `
  --title "夜巡收煞录" `
  --genre "奇幻" `
  --primary-genre fantasy `
  --sub-genre urban-occult `
  --style-tag web-serial `
  --target-audience qidian-reader `
  --core-promise "每章结尾保留追读钩子" `
  --pace-contract "中快节奏" `
  --premise "夜班接尸人继承城隍夜巡牌，处理都市异案并追查失踪父亲真相" `
  --hook-line "接尸抬到空棺的当夜，他被迫上岗做城隍夜巡。" `
  --hook-stack career-entry-hook `
  --hook-stack cliffhanger-end `
  --target-platform qidian `
  --serialization-model "2到3章一个单元异案，持续抬升主线阴谋" `
  --release-cadence "日更两章" `
  --chapter-word-floor 2000 `
  --chapter-word-target 3000
```

Then edit `demo/chapters/chapter-001.md` and run:

```powershell
uv run story-harness chapter analyze --root .\demo --chapter-id chapter-001
uv run story-harness chapter suggest --root .\demo --chapter-id chapter-001
uv run story-harness review apply --root .\demo --chapter-id chapter-001 --all-pending --decision accepted
uv run story-harness projection apply --root .\demo --chapter-id chapter-001
uv run story-harness context refresh --root .\demo --chapter-id chapter-001
uv run story-harness review chapter --root .\demo --chapter-id chapter-001
uv run story-harness outline scene-detect --root .\demo --chapter-id chapter-001
uv run story-harness review scene --root .\demo --chapter-id chapter-001 --scene-index 1
uv run story-harness doctor --root .\demo
```

Option B: run the validated short-story baseline

```powershell
uv run story-harness doctor --root .\demo-short-story
uv run story-harness chapter analyze --root .\demo-short-story --chapter-id chapter-001
uv run story-harness chapter suggest --root .\demo-short-story --chapter-id chapter-001
uv run story-harness review apply --root .\demo-short-story --chapter-id chapter-001 --all-pending --decision accepted
uv run story-harness projection apply --root .\demo-short-story --chapter-id chapter-001
uv run story-harness context refresh --root .\demo-short-story --chapter-id chapter-001
uv run story-harness review chapter --root .\demo-short-story --chapter-id chapter-001
uv run story-harness review scene --root .\demo-short-story --chapter-id chapter-001 --scene-index 1
```

Option C: run the validated style-driven baseline

```powershell
uv run story-harness doctor --root .\demo-light-novel-short
uv run story-harness chapter analyze --root .\demo-light-novel-short --chapter-id chapter-001
uv run story-harness review chapter --root .\demo-light-novel-short --chapter-id chapter-001
uv run story-harness review scene --root .\demo-light-novel-short --chapter-id chapter-001 --scene-index 1
uv run story-harness export --root .\demo-light-novel-short --format markdown --output .\demo-light-novel-short\manuscript.md
```

Option D: run the validated xuanhuan web-serial baseline

```powershell
uv run story-harness doctor --root .\demo-xuanhuan-short
uv run story-harness chapter analyze --root .\demo-xuanhuan-short --chapter-id chapter-001
uv run story-harness review chapter --root .\demo-xuanhuan-short --chapter-id chapter-001
uv run story-harness review scene --root .\demo-xuanhuan-short --chapter-id chapter-001 --scene-index 1
uv run story-harness export --root .\demo-xuanhuan-short --format markdown --output .\demo-xuanhuan-short\manuscript.md
```

Repository fallback:

```powershell
$env:PYTHONPATH='src'
python -m story_harness_cli chapter analyze --root .\demo --chapter-id chapter-001
```

Use `demo-short-story` when you want a genre-neutral regression baseline. Use `demo-light-novel-short` when you want to verify that `subGenre`, `styleTags`, and `targetAudience` survive the review loop. Use `demo-xuanhuan-short` when you want to verify `xuanhuan + web-serial` weighting and short-form progression pacing. For the current sample catalog, see [docs/guides/sample-matrix.md](./docs/guides/sample-matrix.md).

Use `demo-urban-occult-long` when you want a more realistic commercial-serial baseline with explicit `commercialPositioning`, volume skeleton, and chapter word targets.

For the full close-the-loop sequence and stop conditions, see [docs/guides/creative-workflow.md](./docs/guides/creative-workflow.md) and [docs/guides/quickstart.md](./docs/guides/quickstart.md).

## Example Workflow

Single chapter loop:

```text
chapter.md
  -> chapter analyze
  -> chapter suggest
  -> review apply
  -> projection apply
  -> context refresh
  -> review chapter
  -> scene detect / maintain scenePlans
  -> review scene
  -> revise prose or scene plan if score is weak
  -> repeat until acceptable
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
- `story-harness review chapter`
- `story-harness review scene`
- `story-harness outline propose`
- `story-harness outline promote`
- `story-harness outline beat-add`
- `story-harness outline beat-complete`
- `story-harness outline beat-list`
- `story-harness outline scene-add`
- `story-harness outline scene-list`
- `story-harness outline scene-detect`
- `story-harness outline scene-update`
- `story-harness outline scene-remove`
- `story-harness projection apply`
- `story-harness context refresh`
- `story-harness entity review`
- `story-harness entity graph`
- `story-harness timeline add/list/check`
- `story-harness causality add/list/check`
- `story-harness search`
- `story-harness export --format json|markdown|txt`
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
- chapter and scene review scoring
- explicit scene plan maintenance
- timeline, search, and causality tooling
- entity graph export
- positioning and story contract checks
- commercial serial blueprint checks (`premise`, hook line, platform, cadence, word targets)
- commercial review alignment output (`commercialAlignment`) and platform-aware review weighting

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
uv run story-harness doctor --root .\demo-short-story
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
- `docs/guides/creative-workflow.md`
- `docs/guides/quickstart.md`
- `docs/guides/sample-matrix.md`
- `docs/guides/releasing.md`

## Roadmap

- Stabilize command contract and fixtures
- Validate against real Story Harness chapter samples
- Add deeper schema validation for timeline / branch / graph semantics
- Evaluate Go rewrite when distribution and binary size become release concerns
