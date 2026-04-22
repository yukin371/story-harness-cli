from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

TEMPLATES_FILE = Path(__file__).parent.parent / "data" / "structure_templates.json"


def _load_templates() -> List[Dict]:
    return json.loads(TEMPLATES_FILE.read_text(encoding="utf-8"))


def list_templates() -> List[Dict]:
    """Return all available templates (id, name, beat count)."""
    templates = _load_templates()
    return [{"id": t["id"], "name": t["name"], "beatCount": len(t["beats"])} for t in templates]


def apply_template(state: Dict, template_id: str) -> Dict:
    """Activate a template and generate empty mappings."""
    templates = _load_templates()
    target = None
    for t in templates:
        if t["id"] == template_id:
            target = t
            break
    if target is None:
        raise ValueError(f"Template '{template_id}' not found")

    structures = state.setdefault("structures", {"activeStructure": None, "mappings": []})
    structures["activeStructure"] = template_id
    structures["mappings"] = [
        {"beatName": b["name"], "chapterId": None}
        for b in target["beats"]
    ]
    return {"activeStructure": template_id, "beatCount": len(target["beats"])}


def show_structure(state: Dict) -> Dict:
    """Show current active template with mappings and chapter info."""
    structures = state.get("structures", {})
    active = structures.get("activeStructure")
    if not active:
        return {"activeStructure": None, "beats": []}

    templates = _load_templates()
    template = next((t for t in templates if t["id"] == active), None)
    if not template:
        return {"activeStructure": active, "beats": [], "error": "template not found"}

    mappings = structures.get("mappings", [])
    chapters = state.get("outline", {}).get("chapters", [])
    total_chapters = len(chapters)

    beats = []
    for beat in template["beats"]:
        mapping = next(
            (m for m in mappings if m["beatName"] == beat["name"]),
            {"chapterId": None},
        )
        ch_id = mapping.get("chapterId")
        # Auto-suggest chapter based on position
        suggested = None
        if total_chapters > 0:
            idx = min(int(beat["position"] * total_chapters), total_chapters - 1)
            suggested = chapters[idx].get("id")

        beats.append({
            "name": beat["name"],
            "position": beat["position"],
            "description": beat["description"],
            "mappedChapterId": ch_id,
            "suggestedChapterId": suggested,
        })

    return {"activeStructure": active, "templateName": template["name"], "beats": beats}


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
        ch = beat.get("mappedChapterId")
        if ch:
            mapped += 1
            # Check adjacent beats on same chapter
            if ch == prev_chapter:
                warnings.append({
                    "type": "adjacent_same_chapter",
                    "beatName": beat["name"],
                    "chapterId": ch,
                    "message": f"节拍 '{beat['name']}' 与前一节拍落在同一章节 {ch}，节奏可能过密",
                })
            prev_chapter = ch
        else:
            if beat["position"] in critical_positions:
                warnings.append({
                    "type": "missing_critical_beat",
                    "beatName": beat["name"],
                    "position": beat["position"],
                    "message": f"关键节拍 '{beat['name']}' 未映射到任何章节",
                })
            else:
                warnings.append({
                    "type": "unmapped_beat",
                    "beatName": beat["name"],
                    "position": beat["position"],
                    "message": f"节拍 '{beat['name']}' 未映射",
                })

    coverage = mapped / total if total else 0
    return {
        "activeStructure": shown["activeStructure"],
        "templateName": shown.get("templateName", ""),
        "warnings": warnings,
        "coverage": round(coverage, 2),
        "mappedBeats": mapped,
        "totalBeats": total,
    }
