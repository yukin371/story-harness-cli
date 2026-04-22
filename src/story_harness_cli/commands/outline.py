from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
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

