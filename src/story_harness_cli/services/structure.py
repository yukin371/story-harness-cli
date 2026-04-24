from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from story_harness_cli.utils import stable_hash

TEMPLATES_FILE = Path(__file__).parent.parent / "data" / "structure_templates.json"
STRUCTURE_DIRECTION_PREFIX = "结构指引："


def _load_templates() -> List[Dict]:
    return json.loads(TEMPLATES_FILE.read_text(encoding="utf-8"))


def list_templates() -> List[Dict]:
    """Return all available templates (id, name, beat count)."""
    templates = _load_templates()
    return [{"id": item["id"], "name": item["name"], "beatCount": len(item["beats"])} for item in templates]


def apply_template(state: Dict, template_id: str) -> Dict:
    """Activate a template and generate empty mappings."""
    templates = _load_templates()
    target = None
    for item in templates:
        if item["id"] == template_id:
            target = item
            break
    if target is None:
        raise ValueError(f"Template '{template_id}' not found")

    structures = state.setdefault("structures", {"activeStructure": None, "mappings": []})
    structures["activeStructure"] = template_id
    structures["mappings"] = [
        {"beatName": beat["name"], "chapterId": None}
        for beat in target["beats"]
    ]
    return {"activeStructure": template_id, "beatCount": len(target["beats"])}


def _outline_chapters_for_edit(state: Dict) -> List[Dict[str, Any]]:
    outline = state.setdefault("outline", {})
    volumes = outline.get("volumes", [])
    if volumes:
        chapters: List[Dict[str, Any]] = []
        for volume in volumes:
            chapters.extend(volume.get("chapters", []))
        return chapters
    return outline.setdefault("chapters", [])


def _render_direction(beats: List[Dict[str, Any]]) -> str:
    parts = []
    for beat in beats:
        description = beat.get("description", "")
        if description:
            parts.append(f"{beat['name']}：{description}")
        else:
            parts.append(beat["name"])
    return f"{STRUCTURE_DIRECTION_PREFIX}{'；'.join(parts)}"


def show_structure(state: Dict) -> Dict:
    """Show current active template with mappings and chapter info."""
    structures = state.get("structures", {})
    active = structures.get("activeStructure")
    if not active:
        return {"activeStructure": None, "beats": []}

    templates = _load_templates()
    template = next((item for item in templates if item["id"] == active), None)
    if not template:
        return {"activeStructure": active, "beats": [], "error": "template not found"}

    mappings = structures.get("mappings", [])
    chapters = state.get("outline", {}).get("chapters", [])
    total_chapters = len(chapters)

    beats = []
    for beat in template["beats"]:
        mapping = next(
            (item for item in mappings if item["beatName"] == beat["name"]),
            {"chapterId": None},
        )
        chapter_id = mapping.get("chapterId")
        suggested = None
        if total_chapters > 0:
            index = min(int(beat["position"] * total_chapters), total_chapters - 1)
            suggested = chapters[index].get("id")

        beats.append(
            {
                "name": beat["name"],
                "position": beat["position"],
                "description": beat["description"],
                "mappedChapterId": chapter_id,
                "suggestedChapterId": suggested,
            }
        )

    return {"activeStructure": active, "templateName": template["name"], "beats": beats}


def scaffold_structure_to_outline(
    state: Dict,
    *,
    mapped_only: bool = False,
    replace_directions: bool = False,
) -> Dict[str, Any]:
    shown = show_structure(state)
    if not shown.get("activeStructure"):
        raise ValueError("No active structure. Run 'structure apply' first.")
    if not shown.get("beats"):
        raise ValueError("Active structure has no beats to scaffold.")

    chapters = _outline_chapters_for_edit(state)
    if not chapters:
        raise ValueError("Outline has no chapters to scaffold.")

    chapter_map = {
        chapter.get("id"): chapter
        for chapter in chapters
        if chapter.get("id")
    }
    chapter_order = [chapter.get("id") for chapter in chapters if chapter.get("id")]
    assignments: Dict[str, List[Dict[str, Any]]] = {}
    unresolved: List[Dict[str, Any]] = []
    missing_chapters: List[Dict[str, Any]] = []

    for beat in shown["beats"]:
        chapter_id = beat.get("mappedChapterId")
        source = "mapped"
        if not chapter_id and not mapped_only:
            chapter_id = beat.get("suggestedChapterId")
            source = "suggested"
        if not chapter_id:
            unresolved.append({"beatName": beat["name"], "reason": "unmapped"})
            continue
        chapter = chapter_map.get(chapter_id)
        if chapter is None:
            missing_chapters.append({"beatName": beat["name"], "chapterId": chapter_id})
            continue
        beat_assignment = dict(beat)
        beat_assignment["assignmentSource"] = source
        assignments.setdefault(chapter_id, []).append(beat_assignment)

    directions_cleared = 0
    for chapter in chapters:
        chapter["beats"] = [
            item
            for item in chapter.get("beats", [])
            if item.get("source") != "structure-scaffold"
        ]
        chapter_id = chapter.get("id")
        if (
            chapter_id
            and chapter_id not in assignments
            and (chapter.get("direction") or "").startswith(STRUCTURE_DIRECTION_PREFIX)
        ):
            chapter["direction"] = ""
            directions_cleared += 1

    chapter_results: List[Dict[str, Any]] = []
    beats_generated = 0
    directions_updated = 0
    directions_preserved = 0

    for chapter_id in chapter_order:
        chapter = chapter_map[chapter_id]
        assigned = sorted(assignments.get(chapter_id, []), key=lambda item: item["position"])
        if not assigned:
            continue

        generated_beats = []
        assignment_sources = []
        active_structure = shown["activeStructure"]
        for beat in assigned:
            assignment_sources.append(beat["assignmentSource"])
            fingerprint = f"{active_structure}:{chapter_id}:{beat['name']}"
            generated_beats.append(
                {
                    "id": f"beat-{stable_hash(fingerprint, size=12)}",
                    "summary": f"{beat['name']}：{beat['description']}",
                    "status": "planned",
                    "source": "structure-scaffold",
                    "structureTemplateId": active_structure,
                    "structureBeatName": beat["name"],
                    "position": beat["position"],
                }
            )

        chapter.setdefault("beats", []).extend(generated_beats)
        beats_generated += len(generated_beats)

        generated_direction = _render_direction(assigned)
        existing_direction = (chapter.get("direction") or "").strip()
        direction_updated = False
        if replace_directions or not existing_direction or existing_direction.startswith(STRUCTURE_DIRECTION_PREFIX):
            chapter["direction"] = generated_direction
            directions_updated += 1
            direction_updated = True
        else:
            directions_preserved += 1

        chapter_results.append(
            {
                "chapterId": chapter_id,
                "title": chapter.get("title", chapter_id),
                "beatNames": [beat["name"] for beat in assigned],
                "assignmentSources": sorted(set(assignment_sources)),
                "generatedBeatCount": len(generated_beats),
                "directionUpdated": direction_updated,
            }
        )

    return {
        "activeStructure": shown["activeStructure"],
        "templateName": shown.get("templateName", ""),
        "chaptersUpdated": chapter_results,
        "beatsGenerated": beats_generated,
        "directionsUpdated": directions_updated,
        "directionsPreserved": directions_preserved,
        "directionsCleared": directions_cleared,
        "unresolvedBeats": unresolved,
        "missingChapterMappings": missing_chapters,
        "mappedOnly": mapped_only,
        "replaceDirections": replace_directions,
    }


def check_structure(state: Dict) -> Dict:
    """Check structure coverage: unmapped beats, adjacent beats on same chapter, missing key beats."""
    shown = show_structure(state)
    if not shown.get("beats"):
        return {"activeStructure": None, "warnings": [], "coverage": 0}

    warnings: List[Dict[str, Any]] = []
    mapped = 0
    total = len(shown["beats"])
    prev_chapter = None

    critical_positions = {0.12, 0.25, 0.50, 0.88, 1.0}

    for beat in shown["beats"]:
        chapter_id = beat.get("mappedChapterId")
        if chapter_id:
            mapped += 1
            if chapter_id == prev_chapter:
                warnings.append(
                    {
                        "type": "adjacent_same_chapter",
                        "beatName": beat["name"],
                        "chapterId": chapter_id,
                        "message": f"节拍 '{beat['name']}' 与前一节拍落在同一章节 {chapter_id}，节奏可能过密",
                    }
                )
            prev_chapter = chapter_id
        else:
            if beat["position"] in critical_positions:
                warnings.append(
                    {
                        "type": "missing_critical_beat",
                        "beatName": beat["name"],
                        "position": beat["position"],
                        "message": f"关键节拍 '{beat['name']}' 未映射到任何章节",
                    }
                )
            else:
                warnings.append(
                    {
                        "type": "unmapped_beat",
                        "beatName": beat["name"],
                        "position": beat["position"],
                        "message": f"节拍 '{beat['name']}' 未映射",
                    }
                )

    coverage = mapped / total if total else 0
    return {
        "activeStructure": shown["activeStructure"],
        "templateName": shown.get("templateName", ""),
        "warnings": warnings,
        "coverage": round(coverage, 2),
        "mappedBeats": mapped,
        "totalBeats": total,
    }
