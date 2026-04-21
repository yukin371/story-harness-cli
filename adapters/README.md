# Adapters

This directory stores host-specific adapters for the `story-harness-cli` core.

Current rule:

1. the CLI repository owns adapter source
2. local installed skills are treated as deployed copies
3. adapters must stay thin and delegate execution to `story-harness`

Current hosts:

1. `codex-skill/`
2. `claude-code/`

Each adapter should explain:

1. when to invoke the CLI
2. which protocol files matter
3. which commands correspond to the writing loop

Install adapters with:

```powershell
uv run python scripts/install_adapter.py --host codex --force
uv run python scripts/install_adapter.py --host claude --workspace <workspace-root> --force
uv run python scripts/install_adapters.py --workspace <workspace-root> --force
```

Rules:

1. Codex installs to `~/.codex/skills/<skill-name>` by default.
2. Claude installs to `<workspace>/.claude/skills/<skill-name>` by default.
3. Use `--target-dir` to override the default target.
4. Use `--dry-run` to inspect the resolved source and target without copying files.
5. `install_adapters.py` defaults to `codex` only, or `codex + claude` when `--workspace` is provided.
