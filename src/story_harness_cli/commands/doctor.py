from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from story_harness_cli.protocol import ROOT_FILES, chapter_path, root_file
from story_harness_cli.protocol.io import load_json_compatible_yaml
from story_harness_cli.protocol.schema import default_project_state


WORKFLOW_FILES = {
    "proposals": "proposals/draft-proposals.yaml",
    "reviews": "reviews/change-requests.yaml",
    "projection": "projections/projection.yaml",
    "context_lens": "projections/context-lens.yaml",
    "projection_log": "logs/projection-log.yaml",
}

WORKFLOW_DIRS = [
    "chapters",
    "proposals",
    "reviews",
    "projections",
    "logs",
]


def record_check(checks: List[Dict[str, str]], level: str, code: str, message: str) -> None:
    checks.append({"level": level, "code": code, "message": message})


def validate_json_compatible_file(
    root: Path,
    relative_path: str,
    default_payload: Dict[str, Any],
    checks: List[Dict[str, str]],
) -> Dict[str, Any]:
    path = root_file(root, relative_path)
    if not path.exists():
        record_check(checks, "error", "missing-file", f"缺少必需文件: {relative_path}")
        return json.loads(json.dumps(default_payload))
    try:
        payload = load_json_compatible_yaml(path, default_payload)
    except SystemExit as exc:
        record_check(checks, "error", "invalid-json-compatible-yaml", str(exc))
        return json.loads(json.dumps(default_payload))
    record_check(checks, "info", "parsed-file", f"文件可解析: {relative_path}")
    return payload


def validate_project_shape(root: Path, checks: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    defaults = default_project_state()
    state = {
        "project": validate_json_compatible_file(root, "project.yaml", defaults["project"], checks),
        "outline": validate_json_compatible_file(root, "outline.yaml", defaults["outline"], checks),
        "entities": validate_json_compatible_file(root, "entities.yaml", defaults["entities"], checks),
        "timeline": validate_json_compatible_file(root, "timeline.yaml", defaults["timeline"], checks),
        "branches": validate_json_compatible_file(root, "branches.yaml", defaults["branches"], checks),
    }
    for key, relative_path in WORKFLOW_FILES.items():
        state[key] = validate_json_compatible_file(root, relative_path, defaults[key], checks)
    return state


def validate_project_links(root: Path, state: Dict[str, Dict[str, Any]], checks: List[Dict[str, str]]) -> None:
    chapters = state["outline"].get("chapters", [])
    outline_ids = set()
    for item in chapters:
        chapter_id = item.get("id")
        if not chapter_id:
            record_check(checks, "warning", "missing-chapter-id", "outline.chapters 中存在缺少 id 的条目")
            continue
        outline_ids.add(chapter_id)
        chapter_file = chapter_path(root, chapter_id)
        if chapter_file.exists():
            record_check(checks, "info", "chapter-file", f"已找到章节文件: chapters/{chapter_file.name}")
        else:
            record_check(checks, "error", "missing-chapter-file", f"outline 中声明了 {chapter_id}，但缺少对应章节文件")

    chapters_dir = root / "chapters"
    if chapters_dir.exists():
        orphan_files = sorted(item.stem for item in chapters_dir.glob("*.md") if item.stem not in outline_ids)
        for chapter_id in orphan_files:
            record_check(checks, "warning", "orphan-chapter-file", f"章节文件 {chapter_id}.md 未在 outline.chapters 中声明")

    active_chapter_id = state["project"].get("activeChapterId")
    if active_chapter_id:
        if chapter_path(root, active_chapter_id).exists():
            record_check(checks, "info", "active-chapter", f"activeChapterId 指向现有章节: {active_chapter_id}")
        else:
            record_check(checks, "error", "missing-active-chapter", f"activeChapterId 指向不存在的章节: {active_chapter_id}")
        if active_chapter_id not in outline_ids:
            record_check(checks, "warning", "active-chapter-not-in-outline", f"activeChapterId 未出现在 outline.chapters 中: {active_chapter_id}")

    context_chapter_id = state["context_lens"].get("currentChapterId")
    if context_chapter_id:
        if chapter_path(root, context_chapter_id).exists():
            record_check(checks, "info", "context-chapter", f"context-lens 指向现有章节: {context_chapter_id}")
        else:
            record_check(checks, "warning", "missing-context-chapter", f"context-lens 指向不存在的章节: {context_chapter_id}")


def command_doctor(args) -> int:
    root = Path(args.root).resolve()
    checks: List[Dict[str, str]] = []

    if not root.exists():
        raise SystemExit(f"{root} 不存在")

    for relative_path in ROOT_FILES:
        if root_file(root, relative_path).exists():
            record_check(checks, "info", "root-file", f"已找到根文件: {relative_path}")
        else:
            record_check(checks, "error", "missing-root-file", f"缺少根文件: {relative_path}")

    for directory in WORKFLOW_DIRS:
        path = root / directory
        if path.exists() and path.is_dir():
            record_check(checks, "info", "workflow-dir", f"已找到目录: {directory}")
        else:
            record_check(checks, "error", "missing-workflow-dir", f"缺少必需目录: {directory}")

    state = validate_project_shape(root, checks)
    validate_project_links(root, state, checks)

    error_count = sum(1 for item in checks if item["level"] == "error")
    warning_count = sum(1 for item in checks if item["level"] == "warning")
    ok = error_count == 0 and (warning_count == 0 or not args.strict)
    payload = {
        "root": str(root),
        "ok": ok,
        "strict": args.strict,
        "summary": {
            "errors": error_count,
            "warnings": warning_count,
            "infos": sum(1 for item in checks if item["level"] == "info"),
        },
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def register_doctor_commands(subparsers) -> None:
    doctor_parser = subparsers.add_parser("doctor", help="Validate story project structure and workflow files")
    doctor_parser.add_argument("--root", required=True)
    doctor_parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    doctor_parser.set_defaults(func=command_doctor)
