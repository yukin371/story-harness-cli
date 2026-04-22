from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from story_harness_cli.protocol.io import load_json_compatible_yaml
from story_harness_cli.utils.text import (
    ABILITY_KEYWORDS,
    APPEARANCE_KEYWORDS,
    RELATION_KEYWORDS,
    STATE_KEYWORDS,
)


def get_defaults() -> Dict[str, Any]:
    """Return the built-in keyword defaults."""
    return {
        "state": dict(STATE_KEYWORDS),
        "relation": {k: list(v) for k, v in RELATION_KEYWORDS.items()},
        "appearance": dict(APPEARANCE_KEYWORDS),
        "ability": dict(ABILITY_KEYWORDS),
        "activeBehavior": [
            "走", "跑", "说", "笑", "站", "坐", "拿", "看", "握", "挥",
            "推", "拉", "跳", "爬", "骑", "开", "关", "打", "写", "抓",
            "点头", "摇头", "转身", "回头", "弯腰", "抬头", "低头",
            "拥抱", "亲吻", "微笑", "怒吼", "低声", "喊",
        ],
        "intimate": [
            "亲密", "拥抱", "亲吻", "依偎", "牵手", "抚摸", "温柔",
            "默契", "配合", "并肩", "携手", "守护",
        ],
        "negationPrefixes": ["不", "没", "无", "未", "非"],
    }


def merge_with_defaults(custom: Dict[str, Any]) -> Dict[str, Any]:
    """Merge custom keywords over defaults (shallow per-key)."""
    defaults = get_defaults()
    for key in defaults:
        if key in custom:
            defaults[key] = custom[key]
    return defaults


def load_keywords(root: Path) -> Dict[str, Any]:
    """Load custom keywords from project root, falling back to defaults."""
    kw_path = root / "keywords.yaml"
    if kw_path.exists():
        custom = load_json_compatible_yaml(kw_path, {})
        if custom:
            return merge_with_defaults(custom)
    return get_defaults()
