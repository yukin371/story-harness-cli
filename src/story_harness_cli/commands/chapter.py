from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.protocol.io import load_json_compatible_yaml
from story_harness_cli.services import analyze_chapter, generate_change_requests
from story_harness_cli.utils import now_iso


def command_chapter_analyze(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id or state["project"].get("activeChapterId")
    if not chapter_id:
        raise SystemExit("缺少 chapter id")

    analysis = analyze_chapter(root, state, chapter_id)

    # Auto-update chapter status in outline volumes
    for vol in state["outline"].get("volumes", []):
        for ch in vol.get("chapters", []):
            if ch.get("id") == chapter_id:
                ch["status"] = "completed"
                break

    state["project"]["activeChapterId"] = chapter_id
    state["project"]["updatedAt"] = now_iso()
    save_state(root, state)
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
    return 0


def command_chapter_suggest(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id or state["project"].get("activeChapterId")
    analysis_path = root / "logs" / (f"analysis-{chapter_id}.yaml" if chapter_id else "latest-analysis.yaml")
    if not analysis_path.exists():
        analysis_path = root / "logs" / "latest-analysis.yaml"
    if not analysis_path.exists():
        raise SystemExit("还没有分析结果，请先运行 chapter analyze")

    analysis = load_json_compatible_yaml(analysis_path, {})
    result = generate_change_requests(state, analysis)
    save_state(root, state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def register_chapter_commands(subparsers) -> None:
    chapter_parser = subparsers.add_parser("chapter", help="Chapter-oriented commands")
    chapter_subparsers = chapter_parser.add_subparsers(dest="chapter_command", required=True)

    analyze_parser = chapter_subparsers.add_parser("analyze", help="Analyze one chapter")
    analyze_parser.add_argument("--root", required=True)
    analyze_parser.add_argument("--chapter-id")
    analyze_parser.set_defaults(func=command_chapter_analyze)

    suggest_parser = chapter_subparsers.add_parser("suggest", help="Generate change requests from latest analysis")
    suggest_parser.add_argument("--root", required=True)
    suggest_parser.add_argument("--chapter-id")
    suggest_parser.set_defaults(func=command_chapter_suggest)

