from __future__ import annotations

from typing import Any, Dict, Iterable, List

from story_harness_cli.utils import now_iso, stable_hash


def upsert_by_key(items: List[Dict[str, Any]], key_fields: Iterable[str], payload: Dict[str, Any]) -> None:
    for item in items:
        if all(item.get(field) == payload.get(field) for field in key_fields):
            item.update(payload)
            return
    items.append(payload)


def apply_projection(state: Dict[str, Dict[str, Any]], analysis: Dict[str, Any], chapter_id: str | None) -> Dict[str, Any]:
    applied_changes = 0
    requests = state["reviews"].setdefault("changeRequests", [])
    projection = state["projection"]
    log_entries = state["projection_log"].setdefault("projectionChanges", [])

    for request in requests:
        if request.get("status") != "accepted":
            continue
        if request.get("projectionStatus") == "applied":
            continue
        if chapter_id and request.get("chapterId") != chapter_id:
            continue

        if request.get("kind") == "snapshot":
            payload = request.get("suggestedPayload", {})
            upsert_by_key(
                projection.setdefault("snapshotProjections", []),
                ["entityId", "scopeRef"],
                {
                    "entityId": payload.get("entityId"),
                    "entityName": payload.get("entityName"),
                    "scopeRef": request.get("chapterId"),
                    "currentState": payload.get("state"),
                    "sourceChangeIds": [request.get("id")],
                    "updatedAt": now_iso(),
                },
            )
        elif request.get("kind") == "relation":
            payload = request.get("suggestedPayload", {})
            upsert_by_key(
                projection.setdefault("relationProjections", []),
                ["fromId", "toId", "scopeRef"],
                {
                    "fromId": payload.get("fromId"),
                    "fromName": payload.get("fromName"),
                    "toId": payload.get("toId"),
                    "toName": payload.get("toName"),
                    "scopeRef": request.get("chapterId"),
                    "label": payload.get("label"),
                    "sourceChangeIds": [request.get("id")],
                    "updatedAt": now_iso(),
                },
            )

        log_entries.append(
            {
                "id": f"projection-{stable_hash(request.get('id', '') + now_iso())}",
                "sourceType": "change-request",
                "sourceId": request.get("id"),
                "chapterId": request.get("chapterId"),
                "kind": request.get("kind"),
                "createdAt": now_iso(),
            }
        )
        request["projectionStatus"] = "applied"
        request["projectionAppliedAt"] = now_iso()
        request["updatedAt"] = now_iso()
        applied_changes += 1

    proposals = state["proposals"].setdefault("draftProposals", [])
    for proposal in proposals:
        if proposal.get("status") != "applied":
            continue
        if proposal.get("projectionStatus") == "applied":
            continue
        if chapter_id and proposal.get("chapterId") not in {None, chapter_id}:
            continue
        log_entries.append(
            {
                "id": f"projection-{stable_hash(proposal.get('id', '') + now_iso())}",
                "sourceType": "draft-proposal",
                "sourceId": proposal.get("id"),
                "chapterId": proposal.get("chapterId"),
                "kind": proposal.get("kind"),
                "createdAt": now_iso(),
            }
        )
        proposal["projectionStatus"] = "applied"
        proposal["updatedAt"] = now_iso()

    active_entity_ids = analysis.get("sceneScope", {}).get("activeEntityIds", [])
    if chapter_id and active_entity_ids:
        upsert_by_key(
            projection.setdefault("sceneScopeProjections", []),
            ["chapterId"],
            {
                "chapterId": chapter_id,
                "activeEntityIds": active_entity_ids,
                "sourceChangeIds": [
                    request.get("id")
                    for request in requests
                    if request.get("chapterId") == chapter_id and request.get("status") == "accepted"
                ],
                "updatedAt": now_iso(),
            },
        )

    return {"appliedChangeRequests": applied_changes, "chapterId": chapter_id}

