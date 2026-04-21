from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.protocol.io import load_json_compatible_yaml
from story_harness_cli.services import refresh_context_lens
from story_harness_cli.utils import now_iso


def command_context_refresh(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id or state["project"].get("activeChapterId")
    if not chapter_id:
        raise SystemExit("缺少 chapter id")
    analysis = load_json_compatible_yaml(root / "logs" / (f"analysis-{chapter_id}.yaml" if chapter_id else "latest-analysis.yaml"), {})
    if not analysis:
        analysis = load_json_compatible_yaml(root / "logs" / "latest-analysis.yaml", {})

    lens = refresh_context_lens(state, chapter_id, analysis)
    state["project"]["activeChapterId"] = chapter_id
    state["project"]["updatedAt"] = now_iso()
    save_state(root, state)
    print(json.dumps(lens, ensure_ascii=False, indent=2))
    return 0


def register_context_commands(subparsers) -> None:
    context_parser = subparsers.add_parser("context", help="Context lens commands")
    context_subparsers = context_parser.add_subparsers(dest="context_command", required=True)

    refresh_parser = context_subparsers.add_parser("refresh", help="Refresh local writing context")
    refresh_parser.add_argument("--root", required=True)
    refresh_parser.add_argument("--chapter-id")
    refresh_parser.set_defaults(func=command_context_refresh)

