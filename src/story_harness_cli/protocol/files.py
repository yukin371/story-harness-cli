from __future__ import annotations

from pathlib import Path


ROOT_FILES = [
    "project.yaml",
    "outline.yaml",
    "entities.yaml",
    "timeline.yaml",
    "branches.yaml",
]


def root_file(root: Path, relative: str) -> Path:
    return root / relative


def chapter_path(root: Path, chapter_id: str) -> Path:
    direct = root / "chapters" / f"{chapter_id}.md"
    if direct.exists():
        return direct
    for item in (root / "chapters").glob("*.md"):
        if item.stem == chapter_id:
            return item
    return direct

