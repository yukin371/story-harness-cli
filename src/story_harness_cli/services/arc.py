from __future__ import annotations

import re
from typing import Any, Dict, List

from story_harness_cli.utils import now_iso, stable_hash


def _find_entity(
    state: Dict[str, Dict[str, Any]],
    entity_id_or_name: str,
) -> Dict[str, Any] | None:
    """Find an entity by id (exact) or name in state['entities']['entities']."""
    entities = state.get("entities", {}).get("entities", [])
    for e in entities:
        if e.get("id") == entity_id_or_name:
            return e
        if e.get("name") == entity_id_or_name:
            return e
    return None


def _chapter_sort_key(chapter_id: str) -> int:
    """Extract the numeric portion from a chapter id like 'chapter-001'."""
    m = re.search(r"\d+", chapter_id)
    return int(m.group()) if m else 0


def define_arc(
    state: Dict[str, Dict[str, Any]],
    entity_id_or_name: str,
    motivation: str,
    internal_conflict: str,
) -> Dict[str, Any]:
    """Create or update an arc on the matching entity.

    Sets motivation, internalConflict, and resets milestones/resolutionChapterId
    only when creating a new arc. On update, preserves existing milestones and
    resolution, but updates motivation and conflict.
    """
    entity = _find_entity(state, entity_id_or_name)
    if entity is None:
        raise ValueError(f"Entity '{entity_id_or_name}' not found")

    existing = entity.get("arc")
    if existing:
        existing["motivation"] = motivation
        existing["internalConflict"] = internal_conflict
        return existing

    arc = {
        "motivation": motivation,
        "internalConflict": internal_conflict,
        "milestones": [],
        "resolutionChapterId": None,
    }
    entity["arc"] = arc
    return arc


def add_milestone(
    state: Dict[str, Dict[str, Any]],
    entity_id_or_name: str,
    chapter_id: str,
    milestone_type: str,
    description: str,
) -> Dict[str, Any]:
    """Add a milestone to an entity's arc. Returns the milestone dict."""
    entity = _find_entity(state, entity_id_or_name)
    if entity is None:
        raise ValueError(f"Entity '{entity_id_or_name}' not found")

    arc = entity.get("arc")
    if arc is None:
        raise ValueError(f"Entity '{entity.get('name', entity_id_or_name)}' has no arc defined. Run 'arc define' first.")

    entity_id = entity.get("id", entity_id_or_name)
    milestone_id = f"milestone-{stable_hash(entity_id + chapter_id + now_iso())}"

    milestone = {
        "id": milestone_id,
        "chapterId": chapter_id,
        "type": milestone_type,
        "description": description,
    }
    arc["milestones"].append(milestone)
    return milestone


def list_arcs(
    state: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return summary info for all entities that have arc data."""
    entities = state.get("entities", {}).get("entities", [])
    result = []
    for entity in entities:
        arc = entity.get("arc")
        if arc is None:
            continue
        result.append({
            "entityId": entity.get("id"),
            "entityName": entity.get("name"),
            "motivation": arc.get("motivation", ""),
            "milestoneCount": len(arc.get("milestones", [])),
            "resolutionChapterId": arc.get("resolutionChapterId"),
        })
    return result


def check_arcs(
    state: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Validate arc completeness. Returns warnings, advisories, and arc count."""
    entities = state.get("entities", {}).get("entities", [])
    outline = state.get("outline", {})
    chapters = outline.get("chapters", [])

    # Build set of valid chapter ids
    valid_chapter_ids = {ch.get("id") for ch in chapters if ch.get("id")}

    warnings: List[Dict[str, str]] = []
    advisory: List[Dict[str, str]] = []
    arc_count = 0

    for entity in entities:
        arc = entity.get("arc")
        if arc is None:
            # Check if entity is a significant character without an arc
            profile = entity.get("profile", {})
            role = profile.get("role", "")
            has_background = bool(profile.get("background"))
            has_motivation = bool(profile.get("motivation"))
            if has_background or has_motivation:
                advisory.append({
                    "entityId": entity.get("id", ""),
                    "entityName": entity.get("name", ""),
                    "message": f"{entity.get('name', entity.get('id', '?'))}: 缺少弧线定义",
                })
            continue

        arc_count += 1
        entity_id = entity.get("id", "")
        entity_name = entity.get("name", "")

        # Must have non-empty motivation
        if not arc.get("motivation"):
            warnings.append({
                "entityId": entity_id,
                "entityName": entity_name,
                "type": "missing_motivation",
                "message": f"{entity_name}: 弧线缺少动机(motivation)",
            })

        # Must have at least 1 milestone
        milestones = arc.get("milestones", [])
        if not milestones:
            warnings.append({
                "entityId": entity_id,
                "entityName": entity_name,
                "type": "no_milestones",
                "message": f"{entity_name}: 弧线没有里程碑(milestones)",
            })
        else:
            # Each milestone chapterId must exist in outline chapters
            for ms in milestones:
                ms_ch = ms.get("chapterId", "")
                if ms_ch and ms_ch not in valid_chapter_ids:
                    warnings.append({
                        "entityId": entity_id,
                        "entityName": entity_name,
                        "type": "invalid_chapter",
                        "message": f"{entity_name}: 里程碑 '{ms.get('type', '')}' 引用了不存在的章节 {ms_ch}",
                    })

        # Check arc span: if >3 chapters but <2 milestones, warn about fracture risk
        first_milestone_ch = milestones[0].get("chapterId", "") if milestones else ""
        resolution_ch = arc.get("resolutionChapterId", "")
        if first_milestone_ch and resolution_ch:
            span = _chapter_sort_key(resolution_ch) - _chapter_sort_key(first_milestone_ch)
            if span > 3 and len(milestones) < 2:
                warnings.append({
                    "entityId": entity_id,
                    "entityName": entity_name,
                    "type": "fracture_risk",
                    "message": f"{entity_name}: 弧线断裂风险 (跨{span}章但仅{len(milestones)}个里程碑)",
                })

    return {
        "warnings": warnings,
        "advisory": advisory,
        "arcCount": arc_count,
    }
