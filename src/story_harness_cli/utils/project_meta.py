from __future__ import annotations

import re


PRIMARY_GENRE_ALIASES = {
    "纯文学": "literary",
    "文学": "literary",
    "literary": "literary",
    "言情": "romance",
    "romance": "romance",
    "悬疑": "mystery",
    "推理": "mystery",
    "惊悚": "thriller",
    "mystery": "mystery",
    "thriller": "thriller",
    "奇幻": "fantasy",
    "西幻": "fantasy",
    "玄幻": "fantasy",
    "fantasy": "fantasy",
    "科幻": "science-fiction",
    "sci-fi": "science-fiction",
    "science fiction": "science-fiction",
    "science-fiction": "science-fiction",
    "历史": "historical",
    "历史小说": "historical",
    "historical": "historical",
    "青少年": "ya",
    "ya": "ya",
}

DETAIL_LABEL_ALIASES = {
    "西幻": "western-fantasy",
    "western fantasy": "western-fantasy",
    "western-fantasy": "western-fantasy",
    "玄幻": "xuanhuan",
    "xuanhuan": "xuanhuan",
    "轻小说": "light-novel",
    "light novel": "light-novel",
    "light-novel": "light-novel",
}

COMMERCIAL_SERIAL_AUDIENCE = {
    "qidian-reader",
    "web-serial-reader",
    "urban-fantasy-reader",
    "folk-occult-reader",
    "male-young-adult",
    "female-young-adult",
}


def normalize_machine_label(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        return ""
    lowered = normalized.lower()
    alias = (
        DETAIL_LABEL_ALIASES.get(normalized)
        or DETAIL_LABEL_ALIASES.get(lowered)
        or PRIMARY_GENRE_ALIASES.get(normalized)
        or PRIMARY_GENRE_ALIASES.get(lowered)
    )
    if alias:
        return alias
    lowered = lowered.replace("_", "-").replace(" ", "-")
    lowered = re.sub(r"-+", "-", lowered)
    return lowered


def normalize_primary_genre(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        return ""
    lowered = normalized.lower()
    alias = PRIMARY_GENRE_ALIASES.get(normalized) or PRIMARY_GENRE_ALIASES.get(lowered)
    if alias:
        return alias
    return normalize_machine_label(value)


def is_machine_label(value: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value))


def is_commercial_serial_project(project: dict) -> bool:
    positioning = project.get("positioning", {}) if isinstance(project, dict) else {}
    commercial = project.get("commercialPositioning", {}) if isinstance(project, dict) else {}
    style_tags = {normalize_machine_label(item) for item in positioning.get("styleTags", []) if item}
    target_audience = {normalize_machine_label(item) for item in positioning.get("targetAudience", []) if item}
    return bool(
        "web-serial" in style_tags
        or COMMERCIAL_SERIAL_AUDIENCE.intersection(target_audience)
        or commercial.get("targetPlatform")
        or commercial.get("serializationModel")
        or commercial.get("releaseCadence")
        or commercial.get("hookLine")
        or commercial.get("premise")
    )
