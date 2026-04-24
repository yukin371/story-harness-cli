from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import chapter_path, load_project_state, save_state
from story_harness_cli.protocol.files import LAYOUT_FLAT, LAYOUT_LAYERED, resolve_state_path
from story_harness_cli.protocol.io import dump_json_compatible_yaml
from story_harness_cli.protocol.schema import default_project_state
from story_harness_cli.utils import now_iso
from story_harness_cli.utils.project_meta import normalize_machine_label, normalize_primary_genre


def command_init(args) -> int:
    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)

    layout_name = getattr(args, "layout", "flat")
    layout = LAYOUT_LAYERED if layout_name == "layered" else LAYOUT_FLAT

    # In layered layout, create spec/ and spec/outlines/ directories
    if layout == LAYOUT_LAYERED:
        (root / "spec").mkdir(exist_ok=True)
        (root / "spec" / "outlines").mkdir(exist_ok=True)

    (root / "chapters").mkdir(exist_ok=True)
    (root / "proposals").mkdir(exist_ok=True)
    (root / "reviews").mkdir(exist_ok=True)
    (root / "projections").mkdir(exist_ok=True)
    (root / "logs").mkdir(exist_ok=True)

    defaults = default_project_state()
    project = defaults["project"] | {
        "title": args.title,
        "genre": args.genre,
        "defaultMode": args.default_mode,
        "activeChapterId": args.chapter_id,
        "positioning": {
            "primaryGenre": normalize_primary_genre(args.primary_genre or args.genre),
            "subGenre": normalize_machine_label(args.sub_genre or ""),
            "styleTags": [normalize_machine_label(item) for item in (args.style_tag or []) if item.strip()],
            "targetAudience": [normalize_machine_label(item) for item in (args.target_audience or []) if item.strip()],
        },
        "storyContract": {
            "corePromises": args.core_promise or [],
            "avoidances": args.avoidance or [],
            "endingContract": args.ending_contract or "",
            "paceContract": args.pace_contract or "",
        },
        "commercialPositioning": {
            "premise": args.premise or "",
            "hookLine": args.hook_line or "",
            "hookStack": [normalize_machine_label(item) for item in (args.hook_stack or []) if item.strip()],
            "benchmarkWorks": [item.strip() for item in (args.benchmark_work or []) if item.strip()],
            "targetPlatform": normalize_machine_label(args.target_platform or ""),
            "serializationModel": args.serialization_model or "",
            "releaseCadence": args.release_cadence or "",
            "chapterWordFloor": args.chapter_word_floor or 0,
            "chapterWordTarget": args.chapter_word_target or 0,
        },
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

    # project.yaml always at root
    dump_json_compatible_yaml(resolve_state_path(root, "project", layout=layout), project)

    # spec-eligible files routed through resolve_state_path
    dump_json_compatible_yaml(resolve_state_path(root, "outline", layout=layout), outline)
    dump_json_compatible_yaml(resolve_state_path(root, "entities", layout=layout), defaults["entities"])
    dump_json_compatible_yaml(resolve_state_path(root, "timeline", layout=layout), defaults["timeline"])
    dump_json_compatible_yaml(resolve_state_path(root, "threads", layout=layout), defaults["threads"])
    dump_json_compatible_yaml(resolve_state_path(root, "structures", layout=layout), defaults["structures"])

    # branches is not in _SPEC_KEYS, stays at root via resolve_state_path fallback
    dump_json_compatible_yaml(root / "branches.yaml", defaults["branches"])

    # subdir-resident files (same path in both layouts)
    dump_json_compatible_yaml(resolve_state_path(root, "proposals", layout=layout), defaults["proposals"])
    dump_json_compatible_yaml(resolve_state_path(root, "reviews", layout=layout), defaults["reviews"])
    dump_json_compatible_yaml(resolve_state_path(root, "story_reviews", layout=layout), defaults["story_reviews"])
    dump_json_compatible_yaml(resolve_state_path(root, "projection", layout=layout), defaults["projection"])
    dump_json_compatible_yaml(resolve_state_path(root, "context_lens", layout=layout), {"currentChapterId": args.chapter_id, "lenses": []})
    dump_json_compatible_yaml(resolve_state_path(root, "projection_log", layout=layout), defaults["projection_log"])

    chapter_file = chapter_path(root, args.chapter_id)
    if not chapter_file.exists() or args.force:
        chapter_file.write_text(
            (
                f"# {args.chapter_title}\n\n"
                "先补章节方向、beats 或 scenePlans，再开始细化正文。"
                "建议在中文连续正文中使用 `@{实体}`，"
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
                "positioning": project["positioning"],
                "storyContract": project["storyContract"],
                "commercialPositioning": project["commercialPositioning"],
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
    init_parser.add_argument("--primary-genre")
    init_parser.add_argument("--sub-genre")
    init_parser.add_argument("--style-tag", action="append")
    init_parser.add_argument("--target-audience", action="append")
    init_parser.add_argument("--core-promise", action="append")
    init_parser.add_argument("--avoidance", action="append")
    init_parser.add_argument("--ending-contract")
    init_parser.add_argument("--pace-contract")
    init_parser.add_argument("--premise")
    init_parser.add_argument("--hook-line")
    init_parser.add_argument("--hook-stack", action="append")
    init_parser.add_argument("--benchmark-work", action="append")
    init_parser.add_argument("--target-platform")
    init_parser.add_argument("--serialization-model")
    init_parser.add_argument("--release-cadence")
    init_parser.add_argument("--chapter-word-floor", type=int)
    init_parser.add_argument("--chapter-word-target", type=int)
    init_parser.add_argument("--chapter-id", default="chapter-001")
    init_parser.add_argument("--chapter-title", default="第一章")
    init_parser.add_argument("--force", action="store_true")
    init_parser.add_argument(
        "--layout", choices=["flat", "layered"], default="flat",
        help="Project file layout mode (default: flat)",
    )
    init_parser.set_defaults(func=command_init)
