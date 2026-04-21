from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.protocol.io import load_json_compatible_yaml
from story_harness_cli.services import apply_projection


def command_projection_apply(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id or state["project"].get("activeChapterId")
    analysis = load_json_compatible_yaml(root / "logs" / (f"analysis-{chapter_id}.yaml" if chapter_id else "latest-analysis.yaml"), {})
    if not analysis:
        analysis = load_json_compatible_yaml(root / "logs" / "latest-analysis.yaml", {})
    result = apply_projection(state, analysis, chapter_id)
    save_state(root, state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def register_projection_commands(subparsers) -> None:
    projection_parser = subparsers.add_parser("projection", help="Projection-related commands")
    projection_subparsers = projection_parser.add_subparsers(dest="projection_command", required=True)

    apply_parser = projection_subparsers.add_parser("apply", help="Apply accepted changes to projection state")
    apply_parser.add_argument("--root", required=True)
    apply_parser.add_argument("--chapter-id")
    apply_parser.set_defaults(func=command_projection_apply)

