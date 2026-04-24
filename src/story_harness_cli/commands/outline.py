from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import chapter_path, ensure_project_root, load_project_state, save_state
from story_harness_cli.services import detect_scene_plans, evaluate_project_outline_readiness
from story_harness_cli.utils import now_iso, stable_hash


def command_outline_propose(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    items = []
    for item in args.item or []:
        title, _, summary = item.partition("::")
        title = title.strip()
        summary = summary.strip()
        if not title:
            continue
        items.append({"title": title, "summary": summary})

    proposal_kind = "beat-outline" if items else "chapter-direction"
    proposal_id = f"proposal-{stable_hash(args.title + now_iso())}"
    state["proposals"].setdefault("draftProposals", []).append(
        {
            "id": proposal_id,
            "projectId": state["project"].get("title", "story-project"),
            "chapterId": args.chapter_id or None,
            "source": "structure-assistant",
            "kind": proposal_kind,
            "title": args.title,
            "summary": args.summary,
            "content": {
                "mode": args.mode,
                "prompt": args.prompt or "",
                "items": items,
            },
            "editable": True,
            "status": "draft",
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
        }
    )
    save_state(root, state)
    print(json.dumps({"proposalId": proposal_id, "kind": proposal_kind}, ensure_ascii=False, indent=2))
    return 0


def command_outline_promote(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    proposals = state["proposals"].setdefault("draftProposals", [])
    proposal = next((item for item in proposals if item.get("id") == args.proposal_id), None)
    if proposal is None:
        raise SystemExit(f"未找到 proposal: {args.proposal_id}")

    chapter_id = args.chapter_id or proposal.get("chapterId")
    if not chapter_id:
        raise SystemExit("缺少目标 chapter id")

    outline = state["outline"]
    chapter_entry = next((item for item in outline.get("chapters", []) if item.get("id") == chapter_id), None)
    if chapter_entry is None:
        chapter_entry = {"id": chapter_id, "title": chapter_id, "status": "draft", "beats": [], "scenePlans": []}
        outline.setdefault("chapters", []).append(chapter_entry)

    content = proposal.get("content", {})
    items = content.get("items", [])
    if proposal.get("kind") == "chapter-direction":
        outline.setdefault("chapterDirections", []).append(
            {
                "chapterId": chapter_id,
                "title": proposal.get("title"),
                "summary": proposal.get("summary"),
                "prompt": content.get("prompt", ""),
                "sourceProposalId": proposal.get("id"),
                "updatedAt": now_iso(),
            }
        )
    else:
        beats = chapter_entry.setdefault("beats", [])
        for item in items:
            beats.append(
                {
                    "title": item.get("title"),
                    "summary": item.get("summary", ""),
                    "sourceProposalId": proposal.get("id"),
                }
            )

    proposal["status"] = "applied"
    proposal["adoption"] = {"mode": "full", "appliedAt": now_iso()}
    proposal["projectionStatus"] = "pending"
    proposal["updatedAt"] = now_iso()
    save_state(root, state)
    print(json.dumps({"proposalId": proposal.get("id"), "chapterId": chapter_id, "status": "applied"}, ensure_ascii=False, indent=2))
    return 0


def command_outline_check(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    result = evaluate_project_outline_readiness(
        state,
        chapter_id=args.chapter_id,
        require_beats=not args.allow_missing_beats,
        require_scene_plans=not args.allow_missing_scene_plans,
        require_project_gate=not args.allow_missing_project_gate,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ready"] else 1


def _find_chapter(outline: dict, chapter_id: str) -> dict | None:
    """Find chapter entry in either volumes or flat chapters list."""
    for vol in outline.get("volumes", []):
        for ch in vol.get("chapters", []):
            if ch.get("id") == chapter_id:
                return ch
    for ch in outline.get("chapters", []):
        if ch.get("id") == chapter_id:
            return ch
    return None


def command_outline_beat_add(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id
    summary = args.summary

    chapter = _find_chapter(state["outline"], chapter_id)
    if chapter is None:
        raise SystemExit(f"找不到章节: {chapter_id}")

    beats = chapter.setdefault("beats", [])
    beat_id = f"beat-{stable_hash(summary + now_iso())[:10]}"
    beat = {
        "id": beat_id,
        "summary": summary,
        "status": "planned",
        "createdAt": now_iso(),
    }
    beats.append(beat)
    save_state(root, state)
    print(json.dumps(beat, ensure_ascii=False, indent=2))
    return 0


def command_outline_beat_complete(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id
    beat_id = args.beat_id

    chapter = _find_chapter(state["outline"], chapter_id)
    if chapter is None:
        raise SystemExit(f"找不到章节: {chapter_id}")

    beats = chapter.get("beats", [])
    beat = next((b for b in beats if b.get("id") == beat_id), None)
    if beat is None:
        raise SystemExit(f"找不到 beat: {beat_id}")

    beat["status"] = "completed"
    beat["completedAt"] = now_iso()
    save_state(root, state)
    print(json.dumps(beat, ensure_ascii=False, indent=2))
    return 0


def command_outline_beat_list(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id

    chapter = _find_chapter(state["outline"], chapter_id)
    if chapter is None:
        raise SystemExit(f"找不到章节: {chapter_id}")

    beats = chapter.get("beats", [])
    if args.status:
        beats = [b for b in beats if b.get("status") == args.status]

    print(json.dumps(beats, ensure_ascii=False, indent=2))
    return 0


def command_outline_scene_add(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter = _find_chapter(state["outline"], args.chapter_id)
    if chapter is None:
        raise SystemExit(f"找不到章节: {args.chapter_id}")
    if args.start_paragraph < 1 or args.end_paragraph < args.start_paragraph:
        raise SystemExit("scene 段落范围无效")

    scene_id = f"scene-{stable_hash(args.chapter_id + args.title + now_iso())[:10]}"
    scene = {
        "id": scene_id,
        "title": args.title,
        "summary": args.summary or "",
        "startParagraph": args.start_paragraph,
        "endParagraph": args.end_paragraph,
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    chapter.setdefault("scenePlans", []).append(scene)
    save_state(root, state)
    print(json.dumps(scene, ensure_ascii=False, indent=2))
    return 0


def command_outline_scene_list(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter = _find_chapter(state["outline"], args.chapter_id)
    if chapter is None:
        raise SystemExit(f"找不到章节: {args.chapter_id}")
    print(json.dumps(chapter.get("scenePlans", []), ensure_ascii=False, indent=2))
    return 0


def command_outline_scene_detect(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter = _find_chapter(state["outline"], args.chapter_id)
    if chapter is None:
        raise SystemExit(f"找不到章节: {args.chapter_id}")

    existing_scenes = chapter.get("scenePlans", [])
    if existing_scenes and not args.replace:
        raise SystemExit("该章节已有 scenePlans，如需覆盖请显式传入 --replace")

    target_chapter = chapter_path(root, args.chapter_id)
    if not target_chapter.exists():
        raise SystemExit(f"章节不存在: {target_chapter}")

    chapter_text = target_chapter.read_text(encoding="utf-8")
    detected_scenes = detect_scene_plans(args.chapter_id, chapter_text)
    if not detected_scenes:
        raise SystemExit("未检测到可用场景，请先补充章节正文")

    persisted_scenes = []
    for scene in detected_scenes:
        timestamp = now_iso()
        persisted_scenes.append({**scene, "createdAt": timestamp, "updatedAt": timestamp})

    chapter["scenePlans"] = persisted_scenes
    save_state(root, state)
    print(
        json.dumps(
            {
                "chapterId": args.chapter_id,
                "detected": len(persisted_scenes),
                "replaced": bool(existing_scenes),
                "scenes": persisted_scenes,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _find_scene_plan(chapter: dict, scene_id: str) -> dict | None:
    for scene in chapter.get("scenePlans", []):
        if scene.get("id") == scene_id:
            return scene
    return None


def command_outline_scene_update(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter = _find_chapter(state["outline"], args.chapter_id)
    if chapter is None:
        raise SystemExit(f"找不到章节: {args.chapter_id}")

    scene = _find_scene_plan(chapter, args.scene_id)
    if scene is None:
        raise SystemExit(f"找不到 scene: {args.scene_id}")

    if args.start_paragraph is not None and args.end_paragraph is not None:
        if args.start_paragraph < 1 or args.end_paragraph < args.start_paragraph:
            raise SystemExit("scene 段落范围无效")
        scene["startParagraph"] = args.start_paragraph
        scene["endParagraph"] = args.end_paragraph
    elif args.start_paragraph is not None or args.end_paragraph is not None:
        raise SystemExit("更新段落范围时必须同时提供 --start-paragraph 和 --end-paragraph")

    if args.title is not None:
        scene["title"] = args.title
    if args.summary is not None:
        scene["summary"] = args.summary
    scene["updatedAt"] = now_iso()
    save_state(root, state)
    print(json.dumps(scene, ensure_ascii=False, indent=2))
    return 0


def command_outline_scene_remove(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter = _find_chapter(state["outline"], args.chapter_id)
    if chapter is None:
        raise SystemExit(f"找不到章节: {args.chapter_id}")

    scenes = chapter.get("scenePlans", [])
    remaining = [scene for scene in scenes if scene.get("id") != args.scene_id]
    if len(remaining) == len(scenes):
        raise SystemExit(f"找不到 scene: {args.scene_id}")

    chapter["scenePlans"] = remaining
    save_state(root, state)
    print(json.dumps({"removed": 1, "sceneId": args.scene_id, "chapterId": args.chapter_id}, ensure_ascii=False, indent=2))
    return 0


def register_outline_commands(subparsers) -> None:
    outline_parser = subparsers.add_parser("outline", help="Outline and structure commands")
    outline_subparsers = outline_parser.add_subparsers(dest="outline_command", required=True)

    propose_parser = outline_subparsers.add_parser("propose", help="Persist a structure proposal")
    propose_parser.add_argument("--root", required=True)
    propose_parser.add_argument("--mode", required=True, choices=["volume", "chapter"])
    propose_parser.add_argument("--title", required=True)
    propose_parser.add_argument("--summary", required=True)
    propose_parser.add_argument("--chapter-id")
    propose_parser.add_argument("--prompt")
    propose_parser.add_argument("--item", action="append")
    propose_parser.set_defaults(func=command_outline_propose)

    promote_parser = outline_subparsers.add_parser("promote", help="Promote a draft proposal into outline state")
    promote_parser.add_argument("--root", required=True)
    promote_parser.add_argument("--proposal-id", required=True)
    promote_parser.add_argument("--chapter-id")
    promote_parser.set_defaults(func=command_outline_promote)

    check_parser = outline_subparsers.add_parser(
        "check",
        help="Validate whether chapters are ready for drafting/refinement under the strict project/chapter gate",
    )
    check_parser.add_argument("--root", required=True)
    check_parser.add_argument("--chapter-id")
    check_parser.add_argument(
        "--allow-missing-beats",
        action="store_true",
        help="Relax gate: allow chapters without beats",
    )
    check_parser.add_argument(
        "--allow-missing-scene-plans",
        action="store_true",
        help="Relax gate: allow chapters without explicit scenePlans",
    )
    check_parser.add_argument(
        "--allow-missing-project-gate",
        action="store_true",
        help="Relax gate: ignore project positioning / contract prerequisites",
    )
    check_parser.set_defaults(func=command_outline_check)

    beat_add_parser = outline_subparsers.add_parser("beat-add", help="Add a beat to a chapter")
    beat_add_parser.add_argument("--root", required=True)
    beat_add_parser.add_argument("--chapter-id", required=True)
    beat_add_parser.add_argument("--summary", required=True, help="Beat description")
    beat_add_parser.set_defaults(func=command_outline_beat_add)

    beat_complete_parser = outline_subparsers.add_parser("beat-complete", help="Mark a beat as completed")
    beat_complete_parser.add_argument("--root", required=True)
    beat_complete_parser.add_argument("--chapter-id", required=True)
    beat_complete_parser.add_argument("--beat-id", required=True)
    beat_complete_parser.set_defaults(func=command_outline_beat_complete)

    beat_list_parser = outline_subparsers.add_parser("beat-list", help="List beats for a chapter")
    beat_list_parser.add_argument("--root", required=True)
    beat_list_parser.add_argument("--chapter-id", required=True)
    beat_list_parser.add_argument("--status", choices=["planned", "completed"], help="Filter by status")
    beat_list_parser.set_defaults(func=command_outline_beat_list)

    scene_add_parser = outline_subparsers.add_parser("scene-add", help="Add an explicit scene plan to a chapter")
    scene_add_parser.add_argument("--root", required=True)
    scene_add_parser.add_argument("--chapter-id", required=True)
    scene_add_parser.add_argument("--title", required=True)
    scene_add_parser.add_argument("--summary")
    scene_add_parser.add_argument("--start-paragraph", required=True, type=int)
    scene_add_parser.add_argument("--end-paragraph", required=True, type=int)
    scene_add_parser.set_defaults(func=command_outline_scene_add)

    scene_list_parser = outline_subparsers.add_parser("scene-list", help="List explicit scene plans for a chapter")
    scene_list_parser.add_argument("--root", required=True)
    scene_list_parser.add_argument("--chapter-id", required=True)
    scene_list_parser.set_defaults(func=command_outline_scene_list)

    scene_detect_parser = outline_subparsers.add_parser(
        "scene-detect",
        help="Detect heuristic scene candidates and persist them as explicit scene plans",
    )
    scene_detect_parser.add_argument("--root", required=True)
    scene_detect_parser.add_argument("--chapter-id", required=True)
    scene_detect_parser.add_argument("--replace", action="store_true")
    scene_detect_parser.set_defaults(func=command_outline_scene_detect)

    scene_update_parser = outline_subparsers.add_parser("scene-update", help="Update an explicit scene plan")
    scene_update_parser.add_argument("--root", required=True)
    scene_update_parser.add_argument("--chapter-id", required=True)
    scene_update_parser.add_argument("--scene-id", required=True)
    scene_update_parser.add_argument("--title")
    scene_update_parser.add_argument("--summary")
    scene_update_parser.add_argument("--start-paragraph", type=int)
    scene_update_parser.add_argument("--end-paragraph", type=int)
    scene_update_parser.set_defaults(func=command_outline_scene_update)

    scene_remove_parser = outline_subparsers.add_parser("scene-remove", help="Remove an explicit scene plan")
    scene_remove_parser.add_argument("--root", required=True)
    scene_remove_parser.add_argument("--chapter-id", required=True)
    scene_remove_parser.add_argument("--scene-id", required=True)
    scene_remove_parser.set_defaults(func=command_outline_scene_remove)
