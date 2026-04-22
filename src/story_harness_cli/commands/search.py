from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state
from story_harness_cli.services.search import search_chapters


def command_search(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    results = search_chapters(
        state,
        root,
        query=args.query,
        chapter_id=args.chapter_id or None,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


def register_search_commands(subparsers) -> None:
    search_parser = subparsers.add_parser("search", help="Search text across chapters")
    search_parser.add_argument("--root", required=True)
    search_parser.add_argument("--query", required=True, help="Search keyword or phrase")
    search_parser.add_argument("--chapter-id", help="Limit to single chapter")
    search_parser.set_defaults(func=command_search)
