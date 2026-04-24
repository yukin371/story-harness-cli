"""migrate.py — migrate flat layout to layered."""
from __future__ import annotations

from pathlib import Path

from story_harness_cli.protocol.files import detect_layout, LAYOUT_FLAT, _SPEC_KEYS


def run_migrate(args) -> None:
    root = Path(args.root).resolve()
    if detect_layout(root) != LAYOUT_FLAT:
        print("Already layered or no project found. Nothing to do.")
        return

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

    print(f"Migrated {len(moved)} files to spec/: {', '.join(moved)}")


def register_migrate_commands(subparsers) -> None:
    migrate_parser = subparsers.add_parser("migrate", help="Migrate flat layout to layered")
    migrate_parser.add_argument("--root", required=True)
    migrate_parser.set_defaults(func=run_migrate)
