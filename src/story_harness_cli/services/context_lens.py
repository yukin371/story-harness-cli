from __future__ import annotations

from typing import Any, Dict

from story_harness_cli.services.analyzer import chapter_title, entity_registry
from story_harness_cli.services.projection_engine import upsert_by_key
from story_harness_cli.utils import now_iso


def refresh_context_lens(state: Dict[str, Dict[str, Any]], chapter_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    projection = state["projection"]
    entities_by_id = entity_registry(state["entities"])

    scope = next(
        (item for item in projection.get("sceneScopeProjections", []) if item.get("chapterId") == chapter_id),
        None,
    )
    active_entity_ids = (scope or {}).get("activeEntityIds") or analysis.get("sceneScope", {}).get("activeEntityIds", [])
    snapshot_index = {
        (item.get("entityId"), item.get("scopeRef")): item
        for item in projection.get("snapshotProjections", [])
    }

    active_characters = []
    for entity_id in active_entity_ids[:6]:
        entity = entities_by_id.get(entity_id) or {
            "id": entity_id,
            "name": entity_id.replace("inferred::", ""),
            "currentState": "",
        }
        snapshot = snapshot_index.get((entity_id, chapter_id))
        active_characters.append(
            {
                "id": entity_id,
                "name": entity.get("name", entity_id),
                "currentState": (snapshot or {}).get("currentState") or entity.get("currentState", ""),
            }
        )

    active_set = set(active_entity_ids)
    active_relations = [
        {
            "fromId": item.get("fromId"),
            "fromName": item.get("fromName"),
            "toId": item.get("toId"),
            "toName": item.get("toName"),
            "label": item.get("label"),
        }
        for item in projection.get("relationProjections", [])
        if item.get("scopeRef") == chapter_id
        and item.get("fromId") in active_set
        and item.get("toId") in active_set
    ]

    pending_requests = [
        item
        for item in state["reviews"].get("changeRequests", [])
        if item.get("chapterId") == chapter_id and item.get("status") in {"pending", "deferred"}
    ]
    lens = {
        "chapterId": chapter_id,
        "chapterTitle": chapter_title(state["outline"], chapter_id),
        "activeCharacters": active_characters,
        "activeRelations": active_relations,
        "pendingChangeRequestCount": len(pending_requests),
        "pendingChangeRequests": [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "kind": item.get("kind"),
                "status": item.get("status"),
            }
            for item in pending_requests[:5]
        ],
        "updatedAt": now_iso(),
    }

    lenses = state["context_lens"].setdefault("lenses", [])
    upsert_by_key(lenses, ["chapterId"], lens)
    state["context_lens"]["currentChapterId"] = chapter_id
    return lens

