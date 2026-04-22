from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .files import ROOT_FILES, root_file
from .io import dump_json_compatible_yaml, load_json_compatible_yaml
from .schema import default_project_state


def load_project_state(root: Path) -> Dict[str, Dict[str, Any]]:
    defaults = default_project_state()
    return {
        "project": load_json_compatible_yaml(root_file(root, "project.yaml"), defaults["project"]),
        "outline": load_json_compatible_yaml(root_file(root, "outline.yaml"), defaults["outline"]),
        "entities": load_json_compatible_yaml(root_file(root, "entities.yaml"), defaults["entities"]),
        "timeline": load_json_compatible_yaml(root_file(root, "timeline.yaml"), defaults["timeline"]),
        "branches": load_json_compatible_yaml(root_file(root, "branches.yaml"), defaults["branches"]),
        "proposals": load_json_compatible_yaml(
            root_file(root, "proposals/draft-proposals.yaml"),
            defaults["proposals"],
        ),
        "reviews": load_json_compatible_yaml(
            root_file(root, "reviews/change-requests.yaml"),
            defaults["reviews"],
        ),
        "projection": load_json_compatible_yaml(
            root_file(root, "projections/projection.yaml"),
            defaults["projection"],
        ),
        "context_lens": load_json_compatible_yaml(
            root_file(root, "projections/context-lens.yaml"),
            defaults["context_lens"],
        ),
        "projection_log": load_json_compatible_yaml(
            root_file(root, "logs/projection-log.yaml"),
            defaults["projection_log"],
        ),
        "threads": load_json_compatible_yaml(root_file(root, "threads.yaml"), defaults["threads"]),
        "structures": load_json_compatible_yaml(root_file(root, "structures.yaml"), defaults["structures"]),
    }


def save_state(root: Path, state: Dict[str, Dict[str, Any]]) -> None:
    # Sync volumes → flat chapters/chapterDirections before saving
    _sync_outline(state["outline"])

    dump_json_compatible_yaml(root_file(root, "project.yaml"), state["project"])
    dump_json_compatible_yaml(root_file(root, "outline.yaml"), state["outline"])
    dump_json_compatible_yaml(root_file(root, "entities.yaml"), state["entities"])
    dump_json_compatible_yaml(root_file(root, "timeline.yaml"), state["timeline"])
    dump_json_compatible_yaml(root_file(root, "branches.yaml"), state["branches"])
    dump_json_compatible_yaml(root_file(root, "proposals/draft-proposals.yaml"), state["proposals"])
    dump_json_compatible_yaml(root_file(root, "reviews/change-requests.yaml"), state["reviews"])
    dump_json_compatible_yaml(root_file(root, "projections/projection.yaml"), state["projection"])
    dump_json_compatible_yaml(root_file(root, "projections/context-lens.yaml"), state["context_lens"])
    dump_json_compatible_yaml(root_file(root, "logs/projection-log.yaml"), state["projection_log"])
    dump_json_compatible_yaml(root_file(root, "threads.yaml"), state["threads"])
    dump_json_compatible_yaml(root_file(root, "structures.yaml"), state["structures"])


def ensure_project_root(root: Path) -> None:
    missing = [name for name in ROOT_FILES if not root_file(root, name).exists()]
    if missing:
        raise SystemExit(f"{root} 不是已初始化的 story harness 项目，缺少: {', '.join(missing)}")


def _sync_outline(outline: Dict[str, Any]) -> None:
    volumes = outline.get("volumes")
    if not volumes:
        return
    flat_chapters = []
    flat_directions = []
    for vol in volumes:
        for ch in vol.get("chapters", []):
            flat_entry = {
                "id": ch.get("id"),
                "title": ch.get("title"),
                "status": ch.get("status", "planned"),
                "beats": ch.get("beats", []),
                "scenePlans": ch.get("scenePlans", []),
            }
            flat_chapters.append(flat_entry)
            if ch.get("direction"):
                flat_directions.append({
                    "chapterId": ch.get("id"),
                    "title": ch.get("title"),
                    "summary": ch.get("direction", ""),
                })
    outline["chapters"] = flat_chapters
    outline["chapterDirections"] = flat_directions

