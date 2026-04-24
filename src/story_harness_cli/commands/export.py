from __future__ import annotations

import json
import sys
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state
from story_harness_cli.utils.text import count_words, strip_entity_tags


def command_export(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    fmt = args.format

    # Spec formats export structured data, not chapter prose
    if fmt == "spec-outline":
        output = _generate_spec_outline(state)
    elif fmt == "spec-characters":
        output = _generate_spec_characters(state)
    else:
        output = _export_chapter_prose(state, root, fmt, getattr(args, "chapter_id", None))

    # Output destination
    if args.output:
        out_path = Path(args.output)
        if out_path.is_dir():
            ext = _format_extension(fmt)
            out_path = out_path / f"{state['project'].get('title', 'manuscript')}{ext}"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"已导出到 {out_path}", file=sys.stderr)
    else:
        _write_stdout(output)

    return 0


def _chapter_title(state: dict, chapter_id: str) -> str:
    for vol in state.get("outline", {}).get("volumes", []):
        for ch in vol.get("chapters", []):
            if ch.get("id") == chapter_id:
                return ch.get("title", chapter_id)
    for ch in state.get("outline", {}).get("chapters", []):
        if ch.get("id") == chapter_id:
            return ch.get("title", chapter_id)
    return chapter_id


def _export_chapter_prose(state: dict, root: Path, fmt: str, chapter_id: str | None) -> str:
    """Export chapter prose in txt/json/markdown formats."""
    # Determine which chapters to export
    chapter_ids = []
    if chapter_id:
        chapter_ids = [chapter_id]
    else:
        for vol in state["outline"].get("volumes", []):
            for ch in vol.get("chapters", []):
                chapter_ids.append(ch.get("id"))
        if not chapter_ids:
            chapter_ids = [ch.get("id") for ch in state["outline"].get("chapters", [])]

    if not chapter_ids:
        raise SystemExit("没有找到可导出的章节")

    # Collect chapter data
    chapters_data = []
    for cid in chapter_ids:
        cp = _find_chapter_file(root, cid)
        if not cp:
            continue
        raw = cp.read_text(encoding="utf-8")
        clean = strip_entity_tags(raw)
        title = _chapter_title(state, cid)
        chapters_data.append({"chapterId": cid, "title": title, "content": clean, "wordCount": count_words(clean)})

    if not chapters_data:
        raise SystemExit("没有找到章节文件")

    if fmt == "json":
        return json.dumps(chapters_data, ensure_ascii=False, indent=2)
    elif fmt == "markdown":
        parts = []
        for ch in chapters_data:
            parts.append(f"## {ch['title']}\n\n{ch['content']}")
        return "\n\n".join(parts)
    else:  # txt
        return "\n\n".join(ch["content"] for ch in chapters_data)


def _generate_spec_outline(state: dict) -> str:
    """Generate a human-readable Markdown outline spec."""
    title = state["project"].get("title", "未命名")
    parts = [f"# 大纲: {title}", ""]

    outline = state.get("outline", {})
    volumes = outline.get("volumes", [])

    if volumes:
        for vol in volumes:
            vol_title = vol.get("title", "未命名卷")
            parts.append(f"## 卷: {vol_title}")
            parts.append("")
            for ch in vol.get("chapters", []):
                _append_chapter_spec(parts, ch)
    else:
        # Flat chapters list (no volumes)
        for ch in outline.get("chapters", []):
            _append_chapter_spec(parts, ch)

    return "\n".join(parts)


def _append_chapter_spec(parts: list, ch: dict) -> None:
    """Append a single chapter's spec-block to parts list."""
    ch_id = ch.get("id", "unknown")
    ch_title = ch.get("title", "未命名")
    status = ch.get("status", "")
    status_label = f" [{status}]" if status else ""
    parts.append(f"### {ch_id}: {ch_title}{status_label}")

    direction = ch.get("direction")
    if direction:
        parts.append(f"**方向:** {direction}")
        parts.append("")

    beats = ch.get("beats", [])
    if beats:
        parts.append("**细纲:**")
        for beat in beats:
            if isinstance(beat, dict):
                parts.append(f"- {beat.get('description', beat.get('detail', str(beat)))}")
            else:
                parts.append(f"- {beat}")
        parts.append("")

    scenes = ch.get("scenePlans", [])
    if scenes:
        parts.append("**场景:**")
        for i, scene in enumerate(scenes, 1):
            summary = scene.get("summary", scene.get("title", ""))
            parts.append(f"{i}. {summary}")
        parts.append("")

    parts.append("---")
    parts.append("")


def _generate_spec_characters(state: dict) -> str:
    """Generate human-readable Markdown character cards."""
    title = state["project"].get("title", "未命名")
    parts = [f"# 角色卡: {title}", "", "---"]

    entities = state.get("entities", {}).get("entities", [])
    if not entities:
        parts.append("")
        parts.append("暂无角色数据。")
        return "\n".join(parts)

    for ent in entities:
        name = ent.get("name", "未命名")
        etype = ent.get("type", "unknown")
        parts.append("")
        parts.append(f"## {name} ({etype})")

        registered = ent.get("registeredAt", "")
        if registered:
            parts.append(f"> 首次出场: {registered}")

        profile = ent.get("profile", {})
        if isinstance(profile, dict):
            # Traits
            traits = profile.get("traits", [])
            if traits:
                parts.append(f"**特质:** {', '.join(traits)}")

            # Appearance
            appearance = profile.get("appearance", [])
            if appearance:
                app_strs = []
                for item in appearance:
                    if isinstance(item, dict):
                        app_strs.append(item.get("detail", str(item)))
                    else:
                        app_strs.append(str(item))
                parts.append(f"**外貌:** {', '.join(app_strs)}")

            # Abilities
            abilities = profile.get("abilities", [])
            if abilities:
                ab_strs = []
                for item in abilities:
                    if isinstance(item, dict):
                        ab_strs.append(item.get("detail", str(item)))
                    else:
                        ab_strs.append(str(item))
                parts.append(f"**能力:** {', '.join(ab_strs)}")

        parts.append("")
        parts.append("---")

    return "\n".join(parts)


def _format_extension(fmt: str) -> str:
    """Return file extension for a given format."""
    return {
        "json": ".json",
        "markdown": ".md",
        "txt": ".txt",
        "spec-outline": ".md",
        "spec-characters": ".md",
    }.get(fmt, ".txt")


def _write_stdout(output: str) -> None:
    """Write output string to stdout with UTF-8 encoding."""
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print(output)


def _find_chapter_file(root: Path, chapter_id: str) -> Path | None:
    direct = root / "chapters" / f"{chapter_id}.md"
    if direct.exists():
        return direct
    for item in (root / "chapters").glob("*.md"):
        if item.stem == chapter_id:
            return item
    return None


def register_export_commands(subparsers) -> None:
    export_parser = subparsers.add_parser("export", help="Export clean manuscript text")
    export_parser.add_argument("--root", required=True)
    export_parser.add_argument("--chapter-id", help="Export single chapter (default: all)")
    export_parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    export_parser.add_argument("--format", choices=["txt", "json", "markdown", "spec-outline", "spec-characters"], default="txt", help="Output format")
    export_parser.set_defaults(func=command_export)
