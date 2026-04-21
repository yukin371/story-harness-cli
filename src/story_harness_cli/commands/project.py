from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import chapter_path, load_project_state, save_state
from story_harness_cli.protocol.io import dump_json_compatible_yaml
from story_harness_cli.protocol.schema import default_project_state
from story_harness_cli.utils import now_iso


def command_init(args) -> int:
    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "chapters").mkdir(exist_ok=True)
    (root / "proposals").mkdir(exist_ok=True)
    (root / "reviews").mkdir(exist_ok=True)
    (root / "projections").mkdir(exist_ok=True)
    (root / "logs").mkdir(exist_ok=True)

    defaults = default_project_state()
    project = {
        "title": args.title,
        "genre": args.genre,
        "defaultMode": args.default_mode,
        "activeChapterId": args.chapter_id,
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    outline = {
        "chapters": [
            {
                "id": args.chapter_id,
                "title": args.chapter_title,
                "status": "draft",
                "beats": [],
                "scenePlans": [],
            }
        ],
        "chapterDirections": [],
    }

    dump_json_compatible_yaml(root / "project.yaml", project)
    dump_json_compatible_yaml(root / "outline.yaml", outline)
    dump_json_compatible_yaml(root / "entities.yaml", defaults["entities"])
    dump_json_compatible_yaml(root / "timeline.yaml", defaults["timeline"])
    dump_json_compatible_yaml(root / "branches.yaml", defaults["branches"])
    dump_json_compatible_yaml(root / "proposals" / "draft-proposals.yaml", defaults["proposals"])
    dump_json_compatible_yaml(root / "reviews" / "change-requests.yaml", defaults["reviews"])
    dump_json_compatible_yaml(root / "projections" / "projection.yaml", defaults["projection"])
    dump_json_compatible_yaml(root / "projections" / "context-lens.yaml", {"currentChapterId": args.chapter_id, "lenses": []})
    dump_json_compatible_yaml(root / "logs" / "projection-log.yaml", defaults["projection_log"])

    chapter_file = chapter_path(root, args.chapter_id)
    if not chapter_file.exists() or args.force:
        chapter_file.write_text(
            (
                f"# {args.chapter_title}\n\n"
                "在这里开始写作。建议在中文连续正文中使用 `@{实体}`，"
                "或在有明确分隔符时使用 `@实体`，以便原型分析器识别。\n"
            ),
            encoding="utf-8",
        )

    print(
        json.dumps(
            {
                "root": str(root),
                "title": args.title,
                "genre": args.genre,
                "chapterId": args.chapter_id,
                "chapterFile": str(chapter_file),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def register_project_commands(subparsers) -> None:
    init_parser = subparsers.add_parser("init", help="Initialize a story harness project")
    init_parser.add_argument("--root", required=True)
    init_parser.add_argument("--title", required=True)
    init_parser.add_argument("--genre", required=True)
    init_parser.add_argument("--default-mode", default="driving")
    init_parser.add_argument("--chapter-id", default="chapter-001")
    init_parser.add_argument("--chapter-title", default="第一章")
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(func=command_init)

