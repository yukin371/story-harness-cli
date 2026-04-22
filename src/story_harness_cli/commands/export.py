from __future__ import annotations

import sys
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state
from story_harness_cli.utils.text import strip_entity_tags


def command_export(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    # Determine which chapters to export
    chapter_ids = []
    if args.chapter_id:
        chapter_ids = [args.chapter_id]
    else:
        # Collect from outline volumes, then fall back to flat chapters
        for vol in state["outline"].get("volumes", []):
            for ch in vol.get("chapters", []):
                chapter_ids.append(ch.get("id"))
        if not chapter_ids:
            chapter_ids = [ch.get("id") for ch in state["outline"].get("chapters", [])]

    if not chapter_ids:
        raise SystemExit("没有找到可导出的章节")

    # Build clean text
    parts = []
    for cid in chapter_ids:
        cp = _find_chapter_file(root, cid)
        if not cp:
            continue
        raw = cp.read_text(encoding="utf-8")
        clean = strip_entity_tags(raw)
        parts.append(clean)

    if not parts:
        raise SystemExit("没有找到章节文件")

    output = "\n\n".join(parts)

    # Output destination
    if args.output:
        out_path = Path(args.output)
        if out_path.is_dir():
            out_path = out_path / f"{state['project'].get('title', 'manuscript')}.txt"
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
    export_parser.set_defaults(func=command_export)
