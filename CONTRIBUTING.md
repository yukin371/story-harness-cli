# Contributing

## Development Environment

```powershell
uv sync
```

The current repository keeps the core CLI stdlib-first on Python 3.10+ so iteration stays fast and packaging stays simple.

## Common Commands

```powershell
uv run story-harness --help
uv run story-harness doctor --root .\examples\minimal-project
uv run python -m unittest discover -s tests
```

## Enable Local Git Hooks

The repository ships hook templates under `.githooks/`, but Git does not enable them automatically.

Enable them locally with:

```powershell
git config core.hooksPath .githooks
```

Current hooks:

1. `pre-commit`: checks obvious sensitive files, AI co-author markers, and generated artifacts.
2. `commit-msg`: enforces conventional commit format.

## Adapter Development

Codex adapter install:

```powershell
uv run python scripts/install_adapter.py --host codex --force
```

Claude Code adapter install:

```powershell
uv run python scripts/install_adapter.py --host claude --workspace <workspace-root> --force
```

Batch install:

```powershell
uv run python scripts/install_adapters.py --workspace <workspace-root> --force
```

Use `--dry-run` before copying when you only want to inspect resolved paths.

## Before Opening A PR

1. Run `uv run story-harness --help`.
2. Run `uv run python -m unittest discover -s tests`.
3. Run `uv run story-harness doctor --root .\examples\minimal-project`.
4. If you changed adapters or install scripts, run at least one adapter install in `--dry-run` mode.
5. Update `README.md` or `docs/` when command contract or workflow semantics change.
