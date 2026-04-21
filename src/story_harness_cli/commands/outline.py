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

