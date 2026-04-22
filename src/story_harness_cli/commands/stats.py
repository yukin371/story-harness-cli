from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state
from story_harness_cli.services.stats import compute_project_stats


def command_stats(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    result = compute_project_stats(state, root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def register_stats_commands(subparsers) -> None:
    stats_parser = subparsers.add_parser("stats", help="Show project statistics")
    stats_parser.add_argument("--root", required=True)
    stats_parser.set_defaults(func=command_stats)
