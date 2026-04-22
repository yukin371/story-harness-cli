from __future__ import annotations

from typing import Any, Dict, List


def add_timeline_event(
    state: Dict[str, Dict[str, Any]],
    chapter_id: str,
    description: str,
    time_label: str = "",
    entity_ids: List[str] | None = None,
) -> Dict[str, Any]:
    """Add a timeline event. Returns the created event dict."""
    from story_harness_cli.utils import now_iso, stable_hash

    events = state.setdefault("timeline", {}).setdefault("events", [])
    event_id = f"event-{stable_hash(chapter_id + description + now_iso())}"

    event = {
        "id": event_id,
        "chapterId": chapter_id,
        "description": description,
        "timeLabel": time_label,
        "entityIds": entity_ids or [],
        "createdAt": now_iso(),
    }
    events.append(event)
    return event


def list_timeline_events(
    state: Dict[str, Dict[str, Any]],
    chapter_id: str | None = None,
    entity_id: str | None = None,
) -> List[Dict[str, Any]]:
    """List timeline events, optionally filtered by chapter or entity."""
    events = state.get("timeline", {}).get("events", [])
    result = events
    if chapter_id:
        result = [e for e in result if e.get("chapterId") == chapter_id]
    if entity_id:
        result = [e for e in result if entity_id in e.get("entityIds", [])]
    return result


def check_timeline_conflicts(
    state: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Check for timeline contradictions:
    - Same entity in overlapping time labels (same timeLabel, different locations)
    - Events with same timeLabel referencing conflicting entity states
    """
    events = state.get("timeline", {}).get("events", [])
    entities = state.get("entities", {}).get("entities", [])
    entity_names = {e.get("id", ""): e.get("name", "") for e in entities}

    conflicts = []

    # Group events by timeLabel
    by_time: Dict[str, List[Dict]] = {}
    for event in events:
        label = event.get("timeLabel", "")
        if not label:
            continue
        by_time.setdefault(label, []).append(event)

    # Check: same entity appearing in multiple events at same timeLabel
    entity_chapters: Dict[str, Dict[str, List[str]]] = {}  # entity_id -> {timeLabel: [chapter_ids]}
    for event in events:
        label = event.get("timeLabel", "")
        if not label:
            continue
        for eid in event.get("entityIds", []):
            entity_chapters.setdefault(eid, {}).setdefault(label, []).append(event.get("chapterId", ""))

    for eid, time_map in entity_chapters.items():
        for label, chapter_ids in time_map.items():
            unique_chapters = set(chapter_ids)
            if len(unique_chapters) > 1:
                conflicts.append({
                    "severity": "high-risk",
                    "type": "entity-in-multiple-chapters-at-same-time",
                    "entityId": eid,
                    "entityName": entity_names.get(eid, eid),
                    "timeLabel": label,
                    "chapterIds": list(unique_chapters),
                    "description": f"{entity_names.get(eid, eid)} 同时出现在多个章节（同一时间点 '{label}'）",
                })

    return {
        "conflictCount": len(conflicts),
        "conflicts": conflicts,
    }
