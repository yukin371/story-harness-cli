from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.services.entity_enricher import enrich_entities
from story_harness_cli.utils import now_iso


def command_entity_enrich(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id or state["project"].get("activeChapterId")
    if not chapter_id:
        raise SystemExit("缺少 chapter id")
    result = enrich_entities(state, chapter_id, root=root)
    save_state(root, state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_entity_review(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    proposals = state["entities"].setdefault("enrichmentProposals", [])
    decision = args.decision
    changed = 0

    for proposal in proposals:
        if proposal.get("status") != "pending":
            continue
        if not args.all_pending and (not args.proposal_id or proposal.get("id") not in args.proposal_id):
            continue
        proposal["status"] = decision
        proposal["updatedAt"] = now_iso()
        changed += 1

        if decision == "accepted":
            entity_id = proposal.get("entityId")
            field = proposal.get("field")
            detail = proposal.get("detail", "")
            evidence = proposal.get("evidence", "")
            chapter_id = proposal.get("chapterId", "")

            for entity in state["entities"].get("entities", []):
                if entity.get("id") == entity_id:
                    profile = entity.setdefault("profile", {})
                    field_list = profile.setdefault(field, [])
                    entry = {"detail": detail, "source": chapter_id, "evidence": evidence, "confidence": proposal.get("confidence", 0.8)}
                    field_list.append(entry)
                    break

    save_state(root, state)
    print(json.dumps({"updated": changed, "decision": decision}, ensure_ascii=False, indent=2))
    return 0


def register_entity_commands(subparsers) -> None:
    entity_parser = subparsers.add_parser("entity", help="Entity and character card commands")
    entity_sub = entity_parser.add_subparsers(dest="entity_command", required=True)

    enrich_parser = entity_sub.add_parser("enrich", help="Extract character details from chapter")
    enrich_parser.add_argument("--root", required=True)
    enrich_parser.add_argument("--chapter-id")
    enrich_parser.set_defaults(func=command_entity_enrich)

    review_parser = entity_sub.add_parser("review", help="Review enrichment proposals")
    review_parser.add_argument("--root", required=True)
    review_parser.add_argument("--decision", required=True, choices=["accepted", "ignored"])
    review_parser.add_argument("--proposal-id", action="append")
    review_parser.add_argument("--all-pending", action="store_true")
    review_parser.set_defaults(func=command_entity_review)
