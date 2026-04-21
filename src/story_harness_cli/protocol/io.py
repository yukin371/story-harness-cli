from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def dump_json_compatible_yaml(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json_compatible_yaml(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return json.loads(json.dumps(default))
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return json.loads(json.dumps(default))
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"无法解析 {path}。本原型要求 *.yaml 文件使用 JSON 兼容格式。{exc}") from exc

