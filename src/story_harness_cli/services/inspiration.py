from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_table(name: str) -> Dict[str, Any]:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def generate_name(gender: str | None = None) -> str:
    names = _load_table("names_cn.yaml")
    surname = random.choice(names["surnames"])
    if gender == "female":
        given = random.choice(names["givenNamesFemale"])
    elif gender == "male":
        given = random.choice(names["givenNamesMale"])
    else:
        given = random.choice(names["givenNamesMale"] + names["givenNamesFemale"])
    return surname + given


def generate_character_suggestions(count: int = 3) -> List[Dict[str, Any]]:
    archetypes = _load_table("archetypes.yaml")["archetypes"]
    motivations = _load_table("motivations.yaml")["motivations"]
    personalities = _load_table("personalities.yaml")
    conflicts = _load_table("conflicts.yaml")["conflictTypes"]

    results = []
    for _ in range(count):
        archetype = random.choice(archetypes)
        motivation = random.choice(motivations)
        trait_count = random.randint(2, 4)
        traits = random.sample(personalities["traits"], min(trait_count, len(personalities["traits"])))
        conflict = random.choice(conflicts)
        gender = random.choice(["male", "female"])
        results.append({
            "name": generate_name(gender),
            "gender": gender,
            "archetype": archetype["label"],
            "archetypeId": archetype["id"],
            "personality": traits,
            "motivation": motivation["label"],
            "motivationId": motivation["id"],
            "potentialConflict": conflict["label"],
        })
    return results


def generate_world_suggestions(count: int = 3) -> List[Dict[str, Any]]:
    world = _load_table("world_elements.yaml")

    results = []
    for _ in range(count):
        era = random.choice(world["eras"])
        sub = random.choice(era["subLabels"]) if era["subLabels"] else era["label"]
        location = random.choice(world["locations"])
        power = random.choice(world["powerSystems"])
        results.append({
            "era": era["label"],
            "subEra": sub,
            "location": location,
            "powerSystem": power["label"],
            "powerSystemId": power["id"],
        })
    return results


def generate_outline_skeleton(
    volumes: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    result = []
    for vol_idx, vol in enumerate(volumes):
        chapters = []
        chapter_count = vol.get("chapterCount", 3)
        for i in range(1, chapter_count + 1):
            chapters.append({
                "id": f"chapter-{vol_idx+1:03d}-{i:03d}",
                "title": f"{vol['title']} 第{i}章",
                "status": "planned",
                "direction": "",
                "beats": [],
            })
        result.append({
            "id": f"vol-{vol_idx+1:03d}",
            "title": vol.get("title", "未命名卷"),
            "theme": vol.get("theme", ""),
            "chapters": chapters,
        })
    return result
