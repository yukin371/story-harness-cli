from __future__ import annotations

from typing import Any, Dict, Iterable

from story_harness_cli.utils import now_iso, stable_hash


def generate_change_requests(state: Dict[str, Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
    change_requests = state["reviews"].setdefault("changeRequests", [])
    existing_fingerprints = {item.get("fingerprint") for item in change_requests}
    created = 0

    for candidate in analysis.get("snapshotCandidates", []):
        fingerprint = f"snapshot::{candidate['entityId']}::{candidate['proposedState']}"
        if fingerprint in existing_fingerprints:
            continue
        change_requests.append(
            {
                "id": f"cr-{stable_hash(fingerprint + now_iso())}",
                "chapterId": analysis.get("chapterId"),
                "kind": "snapshot",
                "severity": "suggestion",
                "title": f"更新 {candidate['entityName']} 当前状态",
                "summary": f"检测到 {candidate['entityName']} 可能进入状态：{candidate['proposedState']}",
                "evidence": candidate["evidence"],
                "targetIds": [candidate["entityId"]],
                "confidence": candidate["confidence"],
                "suggestedPayload": {
                    "entityId": candidate["entityId"],
                    "entityName": candidate["entityName"],
                    "state": candidate["proposedState"],
                },
                "status": "pending",
                "projectionStatus": "pending",
                "fingerprint": fingerprint,
                "createdAt": now_iso(),
                "updatedAt": now_iso(),
            }
        )
        existing_fingerprints.add(fingerprint)
        created += 1

    for candidate in analysis.get("relationCandidates", []):
        fingerprint = f"relation::{candidate['fromId']}::{candidate['toId']}::{candidate['label']}"
        if fingerprint in existing_fingerprints:
            continue
        change_requests.append(
            {
                "id": f"cr-{stable_hash(fingerprint + now_iso())}",
                "chapterId": analysis.get("chapterId"),
                "kind": "relation",
                "severity": candidate.get("severity", "suggestion"),
                "title": f"更新 {candidate['fromName']} 与 {candidate['toName']} 的关系",
                "summary": f"检测到两者关系可能变化为：{candidate['label']}",
                "evidence": candidate["evidence"],
                "targetIds": [candidate["fromId"], candidate["toId"]],
                "confidence": candidate["confidence"],
                "suggestedPayload": {
                    "fromId": candidate["fromId"],
                    "fromName": candidate["fromName"],
                    "toId": candidate["toId"],
                    "toName": candidate["toName"],
                    "label": candidate["label"],
                },
                "status": "pending",
                "projectionStatus": "pending",
                "fingerprint": fingerprint,
                "createdAt": now_iso(),
                "updatedAt": now_iso(),
            }
        )
        existing_fingerprints.add(fingerprint)
        created += 1

    return {"created": created, "chapterId": analysis.get("chapterId")}


def review_change_requests(
    state: Dict[str, Dict[str, Any]],
    decision: str,
    chapter_id: str | None = None,
    request_ids: Iterable[str] | None = None,
    all_pending: bool = False,
    reason: str = "",
) -> Dict[str, Any]:
    requests = state["reviews"].setdefault("changeRequests", [])
    selected_ids = set(request_ids or [])
    changed = 0
    for request in requests:
        if chapter_id and request.get("chapterId") != chapter_id:
            continue
        if selected_ids:
            if request.get("id") not in selected_ids:
                continue
        elif not all_pending:
            continue
        elif request.get("status") not in {"pending", "deferred"}:
            continue

        request["status"] = decision
        request["decisionReason"] = reason
        request["updatedAt"] = now_iso()
        changed += 1

    return {"updated": changed, "decision": decision}

