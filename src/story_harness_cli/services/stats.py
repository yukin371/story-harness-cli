from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from story_harness_cli.utils.text import count_words, paragraphs_from_text, strip_entity_tags


def compute_project_stats(
    state: Dict[str, Dict[str, Any]],
    root: Path,
    *,
    min_chapter_words: int = 2000,
    target_chapter_words: int = 3000,
) -> Dict[str, Any]:
    return {
        "project": _project_info(state),
        "progress": _progress(state),
        "entities": _entity_stats(state),
        "wordCount": _word_count(
            state,
            root,
            min_chapter_words=min_chapter_words,
            target_chapter_words=target_chapter_words,
        ),
        "projections": _projection_stats(state),
    }


def _project_info(state: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    proj = state.get("project", {})
    return {"title": proj.get("title", ""), "genre": proj.get("genre", "")}


def _progress(state: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    volumes = state.get("outline", {}).get("volumes", [])
    chapters = []
    if volumes:
        for vol in volumes:
            chapters.extend(vol.get("chapters", []))
    else:
        chapters = state.get("outline", {}).get("chapters", [])
    total = len(chapters)
    completed = sum(1 for ch in chapters if ch.get("status") == "completed")
    draft = sum(1 for ch in chapters if ch.get("status") == "draft")
    planned = sum(1 for ch in chapters if ch.get("status") not in ("completed", "draft"))
    return {
        "totalChapters": total,
        "completed": completed,
        "draft": draft,
        "planned": planned,
        "completionPercent": round(completed / total * 100) if total else 0,
    }


def _entity_stats(state: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    entities = state.get("entities", {}).get("entities", [])
    by_source: Dict[str, int] = {}
    for e in entities:
        src = e.get("source", "unknown")
        by_source[src] = by_source.get(src, 0) + 1

    # Count mentions from sceneScopeProjections
    mention_counts: Dict[str, int] = {}
    entity_names: Dict[str, str] = {e.get("id", ""): e.get("name", "") for e in entities}
    for scope in state.get("projection", {}).get("sceneScopeProjections", []):
        for eid in scope.get("activeEntityIds", []):
            mention_counts[eid] = mention_counts.get(eid, 0) + 1

    most_mentioned = sorted(
        [{"name": entity_names.get(eid, eid), "mentionCount": count} for eid, count in mention_counts.items()],
        key=lambda x: x["mentionCount"],
        reverse=True,
    )[:5]

    return {"total": len(entities), "bySource": by_source, "mostMentioned": most_mentioned}


def _word_count(
    state: Dict[str, Dict[str, Any]],
    root: Path,
    *,
    min_chapter_words: int,
    target_chapter_words: int,
) -> Dict[str, Any]:
    volumes = state.get("outline", {}).get("volumes", [])
    chapter_entries: List[Dict[str, Any]] = []
    if volumes:
        for vol in volumes:
            for ch in vol.get("chapters", []):
                chapter_entries.append(ch)
    else:
        for ch in state.get("outline", {}).get("chapters", []):
            chapter_entries.append(ch)

    by_chapter = []
    total = 0
    below_minimum = 0
    at_or_above_minimum = 0
    at_or_above_target = 0
    for chapter in chapter_entries:
        cid = chapter.get("id", "")
        title = chapter.get("title", cid)
        cp = root / "chapters" / f"{cid}.md"
        if not cp.exists():
            # Try glob fallback
            for item in (root / "chapters").glob("*.md"):
                if item.stem == cid:
                    cp = item
                    break
        if cp.exists():
            text = cp.read_text(encoding="utf-8")
            clean = "\n\n".join(paragraphs_from_text(strip_entity_tags(text)))
            words = count_words(clean)
            status = _chapter_word_status(words, min_chapter_words, target_chapter_words)
            minimum_gap = max(min_chapter_words - words, 0)
            target_gap = max(target_chapter_words - words, 0)
            if words < min_chapter_words:
                below_minimum += 1
            else:
                at_or_above_minimum += 1
            if words >= target_chapter_words:
                at_or_above_target += 1
            by_chapter.append(
                {
                    "chapterId": cid,
                    "title": title,
                    "words": words,
                    "status": status,
                    "minimumWords": min_chapter_words,
                    "targetWords": target_chapter_words,
                    "missingToMinimum": minimum_gap,
                    "missingToTarget": target_gap,
                }
            )
            total += words

    return {
        "total": total,
        "byChapter": by_chapter,
        "targets": {
            "minimumPerChapter": min_chapter_words,
            "recommendedPerChapter": target_chapter_words,
        },
        "summary": {
            "chaptersBelowMinimum": below_minimum,
            "chaptersAtOrAboveMinimum": at_or_above_minimum,
            "chaptersAtOrAboveRecommended": at_or_above_target,
        },
    }


def _chapter_word_status(words: int, min_chapter_words: int, target_chapter_words: int) -> str:
    if words >= target_chapter_words:
        return "meets-recommended"
    if words >= min_chapter_words:
        return "meets-minimum"
    return "below-minimum"


def _projection_stats(state: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    proj = state.get("projection", {})
    snapshots = len(proj.get("snapshotProjections", []))
    relations = len(proj.get("relationProjections", []))
    pending = sum(1 for cr in state.get("reviews", {}).get("changeRequests", []) if cr.get("status") in ("pending", "deferred"))
    return {"snapshots": snapshots, "relations": relations, "pendingReviews": pending}
