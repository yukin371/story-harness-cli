from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state
from story_harness_cli.protocol.files import chapter_path
from story_harness_cli.protocol.io import dump_json_compatible_yaml
from story_harness_cli.services.consistency_engine import check_consistency
from story_harness_cli.utils import now_iso, stable_hash


def command_consistency_check(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id or state["project"].get("activeChapterId")
    if not chapter_id:
        raise SystemExit("缺少 chapter id")

    chapter_file = chapter_path(root, chapter_id)
    if not chapter_file.exists():
        raise SystemExit(f"章节不存在: {chapter_file}")

    chapter_text = chapter_file.read_text(encoding="utf-8")
    result = check_consistency(state, chapter_text, chapter_id)
    result["checkId"] = f"check-{chapter_id}-{stable_hash(now_iso())}"
    result["chapterId"] = chapter_id
    result["checkedAt"] = now_iso()

    check_path = root / "projections" / f"consistency-check-{chapter_id}.yaml"
    dump_json_compatible_yaml(check_path, result)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def register_consistency_commands(subparsers) -> None:
    consistency_parser = subparsers.add_parser("consistency", help="Consistency check commands")
    con_sub = consistency_parser.add_subparsers(dest="consistency_command", required=True)

    check_parser = con_sub.add_parser("check", help="Run consistency check on a chapter")
    check_parser.add_argument("--root", required=True)
    check_parser.add_argument("--chapter-id")
    check_parser.set_defaults(func=command_consistency_check)
