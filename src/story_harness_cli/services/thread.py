from __future__ import annotations

import re
from typing import Any, Dict, List

from story_harness_cli.utils import now_iso, stable_hash


def _chapter_sort_key(chapter_id: str) -> int:
    """Extract the numeric portion from a chapter id like 'chapter-001'."""
    m = re.search(r"\d+", chapter_id)
    return int(m.group()) if m else 0


def plant_thread(
    state: Dict[str, Dict[str, Any]],
    name: str,
    chapter_id: str,
    severity: str = "major",
    resolve_by: str | None = None,
    description: str = "",
) -> Dict[str, Any]:
    """Plant (create) a suspense thread. Returns the created thread dict."""
    threads = state.setdefault("threads", {}).setdefault("threads", [])

    # Check for duplicate name
    for t in threads:
        if t.get("name") == name:
            raise ValueError(f"Thread with name '{name}' already exists (id: {t['id']})")

    if severity not in ("major", "minor"):
        raise ValueError(f"Invalid severity '{severity}', must be 'major' or 'minor'")

    thread_id = f"thread-{stable_hash(name + chapter_id + now_iso())}"

    thread = {
        "id": thread_id,
        "name": name,
        "description": description,
        "plantedAt": chapter_id,
        "expectedResolveBy": resolve_by,
        "resolvedAt": None,
        "severity": severity,
        "status": "open",
    }
    threads.append(thread)
    return thread


def resolve_thread(
    state: Dict[str, Dict[str, Any]],
    name_or_id: str,
    chapter_id: str,
) -> Dict[str, Any]:
    """Resolve a thread by name or id. Returns the updated thread dict."""
    threads = state.setdefault("threads", {}).setdefault("threads", [])

    target = None
    for t in threads:
        if t.get("id") == name_or_id or t.get("name") == name_or_id:
            target = t
            break

    if target is None:
        raise ValueError(f"Thread '{name_or_id}' not found")

    if target.get("status") == "resolved":
        raise ValueError(f"Thread '{target['name']}' is already resolved")

    target["resolvedAt"] = chapter_id
    target["status"] = "resolved"
    return target


def list_threads(
    state: Dict[str, Dict[str, Any]],
    status_filter: str | None = None,
) -> List[Dict[str, Any]]:
    """List threads, optionally filtered by status."""
    threads = state.get("threads", {}).get("threads", [])
    if status_filter:
        return [t for t in threads if t.get("status") == status_filter]
    return list(threads)


def check_threads(
    state: Dict[str, Dict[str, Any]],
    current_chapter_id: str | None = None,
) -> Dict[str, Any]:
    """Check thread health: overdue, unresolved at end, density warnings, and stats."""
    threads = state.get("threads", {}).get("threads", [])
    outline = state.get("outline", {})
    chapters = outline.get("chapters", [])

    current_num = _chapter_sort_key(current_chapter_id) if current_chapter_id else 0

    # Find last chapter number from outline
    last_chapter_num = 0
    last_chapter_id = None
    for ch in chapters:
        ch_id = ch.get("id", "")
        ch_num = _chapter_sort_key(ch_id)
        if ch_num > last_chapter_num:
            last_chapter_num = ch_num
            last_chapter_id = ch_id

    warnings: List[Dict[str, str]] = []

    # Mark overdue threads
    for t in threads:
        if t.get("status") == "resolved":
            continue
        expected = t.get("expectedResolveBy")
        if expected and _chapter_sort_key(expected) < current_num:
            t["status"] = "overdue"

    # Check for unresolved threads at last chapter
    if last_chapter_id and current_chapter_id == last_chapter_id:
        unresolved = [t for t in threads if t.get("status") in ("open", "overdue")]
        for t in unresolved:
            warnings.append({
                "type": "unresolved",
                "threadId": t["id"],
                "threadName": t.get("name", ""),
                "message": f"未回收的悬念: {t.get('name', t['id'])}",
            })

    # Check density: count threads planted per chapter
    density: Dict[str, int] = {}
    for t in threads:
        planted = t.get("plantedAt", "")
        if planted:
            density[planted] = density.get(planted, 0) + 1

    for ch_id, count in density.items():
        if count > 3:
            warnings.append({
                "type": "density",
                "chapterId": ch_id,
                "count": str(count),
                "message": f"线索密度过高: {ch_id} 有 {count} 条线索",
            })

    # Compute stats
    major_open = 0
    major_resolved = 0
    minor_open = 0
    minor_resolved = 0
    overdue_count = 0

    for t in threads:
        sev = t.get("severity", "major")
        st = t.get("status", "open")
        if st == "resolved":
            if sev == "major":
                major_resolved += 1
            else:
                minor_resolved += 1
        else:
            if sev == "major":
                major_open += 1
            else:
                minor_open += 1
        if st == "overdue":
            overdue_count += 1

    total_major = major_open + major_resolved
    total_minor = minor_open + minor_resolved

    return {
        "warnings": warnings,
        "stats": {
            "majorResolveRate": major_resolved / total_major if total_major else 0,
            "minorResolveRate": minor_resolved / total_minor if total_minor else 0,
            "majorOpen": major_open,
            "majorResolved": major_resolved,
            "minorOpen": minor_open,
            "minorResolved": minor_resolved,
            "overdue": overdue_count,
        },
    }
