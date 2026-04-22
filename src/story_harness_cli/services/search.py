from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from story_harness_cli.protocol.files import chapter_path


def search_chapters(
    state: Dict[str, Dict[str, Any]],
    root: Path,
    query: str,
    chapter_id: str | None = None,
) -> List[Dict[str, Any]]:
    """Search for a keyword/phrase across chapter files.

    Returns list of matches with chapter context.
    """
    # Determine which chapters to search
    chapter_ids = []
    if chapter_id:
        chapter_ids = [chapter_id]
    else:
        volumes = state.get("outline", {}).get("volumes", [])
        if volumes:
            for vol in volumes:
                for ch in vol.get("chapters", []):
                    chapter_ids.append(ch.get("id", ""))
        else:
            for ch in state.get("outline", {}).get("chapters", []):
                chapter_ids.append(ch.get("id", ""))

    results: List[Dict[str, Any]] = []
    for cid in chapter_ids:
        cp = _find_chapter_file(root, cid)
        if not cp:
            continue
        text = cp.read_text(encoding="utf-8")
        paragraphs = text.split("\n")
        for line_num, line in enumerate(paragraphs, 1):
            if query in line:
                # Trim long lines for readability
                snippet = line.strip()
                if len(snippet) > 200:
                    idx = snippet.index(query)
                    start = max(0, idx - 50)
                    end = min(len(snippet), idx + len(query) + 50)
                    snippet = ("..." if start > 0 else "") + snippet[start:end] + ("..." if end < len(line.strip()) else "")
                results.append({
                    "chapterId": cid,
                    "line": line_num,
                    "snippet": snippet,
                })

    return results


def _find_chapter_file(root: Path, chapter_id: str) -> Path | None:
    direct = root / "chapters" / f"{chapter_id}.md"
    if direct.exists():
        return direct
    for item in (root / "chapters").glob("*.md"):
        if item.stem == chapter_id:
            return item
    return None
