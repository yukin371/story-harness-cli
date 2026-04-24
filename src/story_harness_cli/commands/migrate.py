"""migrate.py — migrate flat layout to layered."""
from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol.files import detect_layout, LAYOUT_FLAT, _SPEC_KEYS
from story_harness_cli.protocol.io import load_json_compatible_yaml
from story_harness_cli.protocol.state import save_state, load_project_state


def run_migrate(args) -> int:
    root = Path(args.root).resolve()
    if detect_layout(root) != LAYOUT_FLAT:
        print("Already layered or no project found. Nothing to do.")
        return 0

    spec_dir = root / "spec"
    spec_dir.mkdir(exist_ok=True)
    (spec_dir / "outlines").mkdir(exist_ok=True)

    moved = []
    for key in sorted(_SPEC_KEYS):
        src = root / f"{key}.yaml"
        dst = spec_dir / f"{key}.yaml"
        if src.exists():
            src.rename(dst)
            moved.append(key)

    # Extract detailed outlines from existing outline chapters.
    state = load_project_state(root)
    save_state(root, state)

    extracted = len(state.get("detailed_outlines", {}).get("entries", []))
    print(f"Migrated {len(moved)} files to spec/: {', '.join(moved)}")
    if extracted:
        print(f"Extracted {extracted} chapter details to detailed-outlines.yaml")
    return 0


def register_migrate_commands(subparsers) -> None:
    migrate_parser = subparsers.add_parser("migrate", help="Migrate flat layout to layered")
    migrate_parser.add_argument("--root", required=True)
    migrate_parser.set_defaults(func=run_migrate)
