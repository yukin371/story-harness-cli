from __future__ import annotations

import re
from typing import List, Tuple


STATE_KEYWORDS = {
    "受伤": "受伤",
    "流血": "流血",
    "虚弱": "虚弱",
    "疲惫": "疲惫",
    "愤怒": "愤怒",
    "震惊": "震惊",
    "恐惧": "恐惧",
    "悲伤": "悲伤",
    "开心": "开心",
    "紧张": "紧张",
    "冷静": "冷静",
    "怀疑": "怀疑",
    "信任": "信任",
    "背叛": "背叛",
    "离开": "离开",
    "决裂": "决裂",
}


RELATION_KEYWORDS = {
    "背叛": ("裂痕", "high-risk"),
    "决裂": ("裂痕", "high-risk"),
    "对立": ("对立", "high-risk"),
    "冲突": ("冲突", "suggestion"),
    "争吵": ("冲突", "suggestion"),
    "怀疑": ("信任下降", "high-risk"),
    "信任": ("信任上升", "suggestion"),
    "联手": ("合作", "suggestion"),
    "合作": ("合作", "suggestion"),
    "并肩": ("盟友", "suggestion"),
    "喜欢": ("亲近", "suggestion"),
    "心动": ("亲近", "suggestion"),
}


def paragraphs_from_text(text: str) -> List[str]:
    raw_parts = re.split(r"\n\s*\n", text)
    parts: List[str] = []
    for item in raw_parts:
        normalized = item.strip()
        if not normalized:
            continue
        if normalized.startswith("#"):
            continue
        parts.append(normalized)
    return parts


def extract_tag_mentions(text: str) -> List[str]:
    mentions: List[str] = []
    seen = set()

    for name in re.findall(r"@\{([^{}\n]+)\}", text):
        normalized = name.strip()
        if normalized and normalized not in seen:
            mentions.append(normalized)
            seen.add(normalized)

    simple_pattern = re.compile(
        r"@("
        r"[A-Za-z][A-Za-z0-9_-]{0,31}"
        r"|"
        r"[\u4e00-\u9fff·-]{1,12}(?=[\s，。！？、；：“”‘’（）()《》〈〉【】\[\],.!?:;]|$)"
        r")"
    )
    for name in simple_pattern.findall(text):
        normalized = name.strip()
        if normalized and normalized not in seen:
            mentions.append(normalized)
            seen.add(normalized)

    return mentions


def state_tags_for_paragraph(paragraph: str) -> List[str]:
    return [label for keyword, label in STATE_KEYWORDS.items() if keyword in paragraph]


def relation_for_paragraph(paragraph: str) -> Tuple[str | None, str]:
    for keyword, (label, severity) in RELATION_KEYWORDS.items():
        if keyword in paragraph:
            return label, severity
    return None, "suggestion"

