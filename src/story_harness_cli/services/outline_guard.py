from __future__ import annotations

from typing import Any, Dict, List


def _iter_outline_chapters(outline: Dict[str, Any]) -> List[Dict[str, Any]]:
    volumes = outline.get("volumes", [])
    if volumes:
        chapters: List[Dict[str, Any]] = []
        for volume in volumes:
            chapters.extend(volume.get("chapters", []))
        return chapters
    return outline.get("chapters", [])


def _find_chapter_entry(outline: Dict[str, Any], chapter_id: str) -> Dict[str, Any] | None:
    for chapter in _iter_outline_chapters(outline):
        if chapter.get("id") == chapter_id:
            return chapter
    return None


def _resolve_direction(outline: Dict[str, Any], chapter: Dict[str, Any] | None, chapter_id: str) -> tuple[str, str | None]:
    chapter_direction = (chapter or {}).get("direction", "")
    if isinstance(chapter_direction, str) and chapter_direction.strip():
        return chapter_direction.strip(), "chapter.direction"

    for item in outline.get("chapterDirections", []):
        if item.get("chapterId") != chapter_id:
            continue
        summary = item.get("summary", "")
        if isinstance(summary, str) and summary.strip():
            return summary.strip(), "chapterDirections"
    return "", None


def evaluate_project_story_gate(state: Dict[str, Any]) -> Dict[str, Any]:
    project = state.get("project", {})
    positioning = project.get("positioning", {})
    story_contract = project.get("storyContract", {})

    has_primary_genre = bool((positioning.get("primaryGenre") or "").strip())
    has_target_audience = bool(positioning.get("targetAudience") or [])
    has_core_promises = bool(story_contract.get("corePromises") or [])
    has_pace_contract = bool((story_contract.get("paceContract") or "").strip())

    missing: List[Dict[str, str]] = []
    next_actions: List[str] = []
    if not has_primary_genre:
        missing.append({"code": "missing-primary-genre", "message": "缺少 primaryGenre"})
        next_actions.append("先明确作品主类型，避免后续大纲与评审口径漂移")
    if not has_target_audience:
        missing.append({"code": "missing-target-audience", "message": "缺少 targetAudience"})
        next_actions.append("先声明目标读者，再继续细化章节")
    if not has_core_promises:
        missing.append({"code": "missing-core-promises", "message": "缺少 corePromises"})
        next_actions.append("先写出作品核心卖点承诺，再继续细化章节")
    if not has_pace_contract:
        missing.append({"code": "missing-pace-contract", "message": "缺少 paceContract"})
        next_actions.append("先声明节奏策略，再进入章节细化")

    ready = has_primary_genre and has_target_audience and has_core_promises and has_pace_contract
    return {
        "ready": ready,
        "hasPrimaryGenre": has_primary_genre,
        "hasTargetAudience": has_target_audience,
        "hasCorePromises": has_core_promises,
        "hasPaceContract": has_pace_contract,
        "missing": missing,
        "nextActions": next_actions,
    }


def evaluate_chapter_outline_readiness(
    state: Dict[str, Any],
    chapter_id: str,
    *,
    require_beats: bool = True,
    require_scene_plans: bool = True,
    require_project_gate: bool = True,
) -> Dict[str, Any]:
    outline = state.get("outline", {})
    chapter = _find_chapter_entry(outline, chapter_id)
    project_gate = evaluate_project_story_gate(state)
    direction, direction_source = _resolve_direction(outline, chapter, chapter_id)
    beats = chapter.get("beats", []) if chapter else []
    scene_plans = chapter.get("scenePlans", []) if chapter else []

    has_chapter_entry = chapter is not None
    has_direction = bool(direction)
    has_beats = bool(beats)
    has_scene_plans = bool(scene_plans)

    missing: List[Dict[str, str]] = []
    next_actions: List[str] = []
    if require_project_gate and not project_gate["ready"]:
        for item in project_gate["missing"]:
            missing.append(
                {
                    "code": f"project-{item['code']}",
                    "message": f"项目前置约束未完成：{item['message']}",
                }
            )
        next_actions.extend(project_gate["nextActions"])
    if not has_chapter_entry:
        missing.append({"code": "missing-chapter-entry", "message": "outline 中不存在该章节条目"})
        next_actions.append("先在 outline 中创建章节条目")
    if not has_direction:
        missing.append({"code": "missing-direction", "message": "缺少章节方向或章节目标"})
        next_actions.append("补 chapter direction 或通过 outline propose/promote 写入章节方向")
    if require_beats and not has_beats:
        missing.append({"code": "missing-beats", "message": "缺少章节 beats 拆解"})
        next_actions.append("先补 beats，明确本章关键推进节点")
    if require_scene_plans and not has_scene_plans:
        missing.append({"code": "missing-scene-plans", "message": "缺少 scenePlans 场景拆解"})
        next_actions.append("补 scenePlans，明确每幕边界后再继续")

    ready = (
        has_chapter_entry
        and has_direction
        and (project_gate["ready"] or not require_project_gate)
        and (has_beats or not require_beats)
        and (has_scene_plans or not require_scene_plans)
    )
    if ready:
        status = "ready"
    elif require_project_gate and not project_gate["ready"]:
        status = "missing-project-gate"
    elif not has_chapter_entry:
        status = "missing-chapter-entry"
    elif not has_direction:
        status = "missing-direction"
    elif require_beats and not has_beats:
        status = "missing-beats"
    elif require_scene_plans and not has_scene_plans:
        status = "missing-scene-plans"
    else:
        status = "missing-outline"

    return {
        "chapterId": chapter_id,
        "title": (chapter or {}).get("title", chapter_id),
        "ready": ready,
        "status": status,
        "projectGateReady": project_gate["ready"],
        "hasChapterEntry": has_chapter_entry,
        "hasDirection": has_direction,
        "directionSource": direction_source,
        "hasBeats": has_beats,
        "hasScenePlans": has_scene_plans,
        "missing": missing,
        "nextActions": next_actions,
    }


def evaluate_project_outline_readiness(
    state: Dict[str, Any],
    *,
    chapter_id: str | None = None,
    require_beats: bool = True,
    require_scene_plans: bool = True,
    require_project_gate: bool = True,
) -> Dict[str, Any]:
    outline = state.get("outline", {})
    project_gate = evaluate_project_story_gate(state)
    chapter_ids = []
    if chapter_id:
        chapter_ids = [chapter_id]
    else:
        chapter_ids = [item.get("id") for item in _iter_outline_chapters(outline) if item.get("id")]

    reports = [
        evaluate_chapter_outline_readiness(
            state,
            current_id,
            require_beats=require_beats,
            require_scene_plans=require_scene_plans,
            require_project_gate=require_project_gate,
        )
        for current_id in chapter_ids
    ]

    ready_count = sum(1 for item in reports if item["ready"])
    return {
        "ready": (project_gate["ready"] or not require_project_gate) and bool(reports) and ready_count == len(reports),
        "projectGate": project_gate,
        "requireBeats": require_beats,
        "requireScenePlans": require_scene_plans,
        "requireProjectGate": require_project_gate,
        "summary": {
            "totalChapters": len(reports),
            "readyChapters": ready_count,
            "notReadyChapters": len(reports) - ready_count,
        },
        "chapters": reports,
    }
