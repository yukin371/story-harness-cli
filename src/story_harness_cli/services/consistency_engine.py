from __future__ import annotations

from typing import Any, Dict, List

from story_harness_cli.utils.text import paragraphs_from_text


ACTIVE_BEHAVIOR_KEYWORDS = [
    "走", "跑", "说", "笑", "站", "坐", "拿", "看", "握", "挥",
    "推", "拉", "跳", "爬", "骑", "开", "关", "打", "写", "抓",
    "点头", "摇头", "转身", "回头", "弯腰", "抬头", "低头",
    "拥抱", "亲吻", "微笑", "怒吼", "低声", "喊",
]

INTIMATE_KEYWORDS = [
    "亲密", "拥抱", "亲吻", "依偎", "牵手", "抚摸", "温柔",
    "默契", "配合", "并肩", "携手", "守护",
]

NEGATION_PREFIXES = ("不", "没", "无", "未", "非")

INTIMATE_WORDS_NEED_NEGATION_CHECK = {"信任", "爱", "喜欢"}


def check_consistency(
    state: Dict[str, Dict[str, Any]],
    chapter_text: str,
    chapter_id: str,
    keywords: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    hard: Dict[str, List] = {
        "stateContradictions": [],
        "relationContradictions": [],
        "timelineConflicts": [],
    }
    soft: Dict[str, List] = {
        "outlineDeviations": [],
    }

    active_kw = (keywords or {}).get("activeBehavior", ACTIVE_BEHAVIOR_KEYWORDS)
    intimate_kw = (keywords or {}).get("intimate", INTIMATE_KEYWORDS)
    negation_kw = tuple((keywords or {}).get("negationPrefixes", NEGATION_PREFIXES))

    _check_state_contradictions(state, chapter_text, chapter_id, hard["stateContradictions"], active_kw)
    _check_relation_contradictions(
        state, chapter_text, chapter_id, hard["relationContradictions"], intimate_kw, negation_kw,
    )
    _check_outline_deviations(state, chapter_id, soft["outlineDeviations"])

    context_for_ai = _build_ai_context(state, chapter_text, chapter_id)

    return {
        "hardChecks": hard,
        "softChecks": soft,
        "contextForAI": context_for_ai,
    }


def _check_state_contradictions(
    state: Dict, chapter_text: str, chapter_id: str, results: List, active_kw: List[str]
) -> None:
    entities = state.get("entities", {}).get("entities", [])
    paragraphs = paragraphs_from_text(chapter_text)

    for entity in entities:
        current = entity.get("currentState", {})
        if current.get("status") != "deceased":
            continue
        name = entity.get("name", "")
        for para in paragraphs:
            if name not in para:
                continue
            has_active = any(kw in para for kw in active_kw)
            if has_active:
                last_chapter = current.get("lastUpdatedChapter", "unknown")
                results.append({
                    "entity": entity.get("id"),
                    "entityName": name,
                    "issue": f"projection 标记为 deceased，但正文中 {name} 有活跃描写",
                    "evidence": [
                        f"projection: status=deceased (chapter-{last_chapter})",
                        f"chapter: {chapter_id} 段落: '{para[:80]}...'",
                    ],
                    "severity": "strict",
                })
                break


def _check_relation_contradictions(
    state: Dict, chapter_text: str, chapter_id: str, results: List,
    intimate_kw: List[str], negation_kw: tuple,
) -> None:
    relations = state.get("projection", {}).get("relationProjections", [])
    paragraphs = paragraphs_from_text(chapter_text)

    broken_labels = {"裂痕", "对立", "决裂"}
    for rel in relations:
        label = rel.get("label", "")
        if label not in broken_labels:
            continue
        from_name = rel.get("fromName", "")
        to_name = rel.get("toName", "")
        scope_ref = rel.get("scopeRef", "")

        for para in paragraphs:
            if from_name not in para or to_name not in para:
                continue
            has_intimate = False
            for kw in intimate_kw:
                if kw not in para:
                    continue
                if kw in INTIMATE_WORDS_NEED_NEGATION_CHECK:
                    idx = para.index(kw)
                    if idx > 0 and para[idx - 1] in negation_kw:
                        continue
                has_intimate = True
                break
            if has_intimate:
                results.append({
                    "from": rel.get("fromId"),
                    "fromName": from_name,
                    "to": rel.get("toId"),
                    "toName": to_name,
                    "issue": f"projection 标记关系为'{label}'(chapter-{scope_ref})，但正文表现亲密",
                    "previousLabel": label,
                    "currentEvidence": f"{chapter_id} 段落: '{para[:80]}...'",
                    "severity": "strict",
                })
                break


def _check_outline_deviations(
    state: Dict, chapter_id: str, results: List
) -> None:
    outline = state.get("outline", {})
    volumes = outline.get("volumes", [])

    for vol in volumes:
        for ch in vol.get("chapters", []):
            if ch.get("id") != chapter_id:
                continue
            if ch.get("status") != "completed":
                continue
            for beat in ch.get("beats", []):
                if beat.get("status") == "planned":
                    results.append({
                        "beatId": beat.get("id"),
                        "summary": beat.get("summary", ""),
                        "status": "planned",
                        "note": "细纲中规划的场景在正文中未出现，可能是故意跳过",
                        "severity": "advisory",
                    })


def _build_ai_context(
    state: Dict, chapter_text: str, chapter_id: str
) -> Dict[str, Any]:
    entities = state.get("entities", {}).get("entities", [])
    projection = state.get("projection", {})
    outline = state.get("outline", {})

    entity_cards = []
    for e in entities:
        entity_cards.append({
            "id": e.get("id"),
            "name": e.get("name"),
            "seed": e.get("seed", {}),
            "profile": e.get("profile", {}),
            "currentState": e.get("currentState", {}),
        })

    relevant_snapshots = [
        s for s in projection.get("snapshotProjections", [])
        if s.get("scopeRef") == chapter_id
    ]
    relevant_relations = [
        r for r in projection.get("relationProjections", [])
        if r.get("scopeRef") == chapter_id
    ]

    outline_expectation = ""
    for vol in outline.get("volumes", []):
        for ch in vol.get("chapters", []):
            if ch.get("id") == chapter_id:
                outline_expectation = ch.get("direction", "")
                break

    return {
        "entityCards": entity_cards,
        "relevantProjections": {
            "snapshots": relevant_snapshots,
            "relations": relevant_relations,
        },
        "chapterContent": chapter_text,
        "outlineExpectation": outline_expectation,
    }
