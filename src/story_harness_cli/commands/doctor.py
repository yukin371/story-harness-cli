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


def _check_outline_volumes(root: Path, issues: list) -> None:
    """Validate outline.yaml has volumes structure."""
    outline_path = root / "outline.yaml"
    if not outline_path.exists():
        return
    outline = load_json_compatible_yaml(outline_path, {})
    volumes = outline.get("volumes")
    if volumes is None:
        issues.append({"level": "warn", "message": "outline.yaml 缺少 volumes 字段，建议运行 brainstorm outline 初始化"})
    else:
        for vol in volumes:
            for ch in vol.get("chapters", []):
                for beat in ch.get("beats", []):
                    if beat.get("status") == "planned" and ch.get("status") == "completed":
                        issues.append({
                            "level": "info",
                            "message": f"卷 '{vol.get('title')}' 章 '{ch.get('title')}' 的 beat '{beat.get('summary')}' 状态仍为 planned，但章节已标记 completed",
                        })


def _check_entity_profiles(root: Path, issues: list) -> None:
    """Validate entities have profile structure."""
    entities_path = root / "entities.yaml"
    if not entities_path.exists():
        return
    entities_data = load_json_compatible_yaml(entities_path, {})
    for entity in entities_data.get("entities", []):
        if "profile" not in entity:
            issues.append({
                "level": "warn",
                "message": f"实体 '{entity.get('name')}' 缺少 profile 字段，建议重新初始化或运行 entity enrich",
            })
        if "seed" not in entity:
            issues.append({
                "level": "info",
                "message": f"实体 '{entity.get('name')}' 缺少 seed 字段，建议通过 brainstorm character 创建种子",
            })
        if entity.get("source") == "inferred" and not entity.get("profile"):
            issues.append({
                "level": "info",
                "message": f"推断实体 '{entity.get('name')}' 缺少 profile，建议运行 entity enrich 补充",
            })


def _check_threads(root: Path, state: Dict, issues: list) -> None:
    """Check thread (suspense) health."""
    from story_harness_cli.services.thread import check_threads as thread_check

    threads_data = state.get("threads", {})
    if not threads_data.get("threads"):
        return
    outline = state.get("outline", {})
    chapters = outline.get("chapters", [])
    last_ch_id = chapters[-1].get("id") if chapters else None
    result = thread_check(state, current_chapter_id=last_ch_id)
    for w in result.get("warnings", []):
        issues.append({"level": "warning", "message": w.get("message", "")})
    stats = result.get("stats", {})
    if stats.get("overdue", 0) > 0:
        issues.append({"level": "warning", "message": f"有 {stats['overdue']} 条悬念线索已逾期未回收"})
    open_count = stats.get("majorOpen", 0) + stats.get("minorOpen", 0)
    if open_count > 0:
        issues.append({"level": "info", "message": f"有 {open_count} 条悬念线索待回收"})


def _check_arcs(root: Path, state: Dict, issues: list) -> None:
    """Check character arc completeness."""
    from story_harness_cli.services.arc import check_arcs as arc_check

    result = arc_check(state)
    for w in result.get("warnings", []):
        issues.append({"level": "warning", "message": w.get("message", "")})
    for a in result.get("advisory", []):
        issues.append({"level": "info", "message": a.get("message", "")})


def _check_structure_coverage(root: Path, state: Dict, issues: list) -> None:
    """Check narrative structure coverage."""
    from story_harness_cli.services.structure import check_structure as struct_check

    structures = state.get("structures", {})
    if not structures.get("activeStructure"):
        return
    result = struct_check(state)
    for w in result.get("warnings", []):
        level = "warning" if w.get("type") == "missing_critical_beat" else "info"
        issues.append({"level": level, "message": w.get("message", "")})
    coverage = result.get("coverage", 0)
    if coverage < 1.0:
        issues.append({"level": "info", "message": f"叙事结构覆盖率: {int(coverage * 100)}%"})


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
    _check_outline_volumes(root, checks)
    _check_entity_profiles(root, checks)
    _check_threads(root, state, checks)
    _check_arcs(root, state, checks)
    _check_structure_coverage(root, state, checks)

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
