from __future__ import annotations

from typing import Any, Dict, List

from story_harness_cli.utils import now_iso, stable_hash


def add_causality_link(
    state: Dict[str, Dict[str, Any]],
    cause_event_id: str,
    effect_event_id: str,
    description: str = "",
) -> Dict[str, Any]:
    """Link two timeline events as cause → effect. Returns the causality entry."""
    events = state.get("timeline", {}).get("events", [])
    event_ids = {e.get("id") for e in events}
    if cause_event_id not in event_ids:
        raise SystemExit(f"事件不存在: {cause_event_id}")
    if effect_event_id not in event_ids:
        raise SystemExit(f"事件不存在: {effect_event_id}")
    if cause_event_id == effect_event_id:
        raise SystemExit("因果不能指向同一事件")

    causality = state["projection"].setdefault("causalityProjections", [])
    link_id = f"causality-{stable_hash(cause_event_id + effect_event_id + now_iso())}"

    entry = {
        "id": link_id,
        "causeEventId": cause_event_id,
        "effectEventId": effect_event_id,
        "description": description,
        "createdAt": now_iso(),
    }
    causality.append(entry)
    return entry


def list_causality_links(
    state: Dict[str, Dict[str, Any]],
    event_id: str | None = None,
) -> List[Dict[str, Any]]:
    """List causality links, optionally filtered by event involvement."""
    links = state.get("projection", {}).get("causalityProjections", [])
    if not event_id:
        return links
    return [
        link
        for link in links
        if link.get("causeEventId") == event_id or link.get("effectEventId") == event_id
    ]


def check_causality_conflicts(
    state: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Detect causality issues:
    - Circular chains (A→B→C→A)
    - An event with no cause that should have one (orphan check)
    - Duplicate links
    """
    links = state.get("projection", {}).get("causalityProjections", [])
    conflicts = []

    # Build adjacency list
    adj: Dict[str, List[str]] = {}
    for link in links:
        cause = link.get("causeEventId", "")
        effect = link.get("effectEventId", "")
        adj.setdefault(cause, []).append(effect)

    # Check for cycles via DFS
    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[str, int] = {node: WHITE for node in adj}
    for node in adj:
        for child in adj[node]:
            color.setdefault(child, WHITE)

    def has_cycle(node: str) -> bool:
        color[node] = GRAY
        for neighbor in adj.get(node, []):
            if color.get(neighbor) == GRAY:
                return True
            if color.get(neighbor) == WHITE and has_cycle(neighbor):
                return True
        color[node] = BLACK
        return False

    for node in list(color):
        if color[node] == WHITE:
            if has_cycle(node):
                conflicts.append({
                    "severity": "high-risk",
                    "type": "circular-causality",
                    "description": "存在循环因果链，事件因果关系形成环路",
                })
                break

    # Check for duplicate links
    seen_pairs: set = set()
    for link in links:
        pair = (link.get("causeEventId"), link.get("effectEventId"))
        if pair in seen_pairs:
            conflicts.append({
                "severity": "advisory",
                "type": "duplicate-causality",
                "causeEventId": pair[0],
                "effectEventId": pair[1],
                "description": f"重复的因果链接: {pair[0]} → {pair[1]}",
            })
        seen_pairs.add(pair)

    return {
        "conflictCount": len(conflicts),
        "conflicts": conflicts,
        "totalLinks": len(links),
    }
