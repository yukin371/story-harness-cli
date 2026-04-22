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

    # Determine which chapters to export
    chapter_ids = []
    if args.chapter_id:
        chapter_ids = [args.chapter_id]
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
        output = json.dumps(chapters_data, ensure_ascii=False, indent=2)
    elif fmt == "markdown":
        parts = []
        for ch in chapters_data:
            parts.append(f"## {ch['title']}\n\n{ch['content']}")
        output = "\n\n".join(parts)
    else:  # txt
        output = "\n\n".join(ch["content"] for ch in chapters_data)

    # Output destination
    if args.output:
        out_path = Path(args.output)
        if out_path.is_dir():
            ext = {"json": ".json", "markdown": ".md", "txt": ".txt"}[fmt]
            out_path = out_path / f"{state['project'].get('title', 'manuscript')}{ext}"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"已导出到 {out_path}", file=sys.stderr)
    else:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass
        print(output)

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
    export_parser.add_argument("--format", choices=["txt", "json", "markdown"], default="txt", help="Output format")
    export_parser.set_defaults(func=command_export)
