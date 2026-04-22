from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.services.timeline import (
    add_timeline_event,
    check_timeline_conflicts,
    list_timeline_events,
)


def command_timeline_add(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    entity_ids = []
    if args.entity_id:
        entity_ids = args.entity_id

    event = add_timeline_event(
        state,
        chapter_id=args.chapter_id,
        description=args.description,
        time_label=args.time_label or "",
        entity_ids=entity_ids,
    )
    save_state(root, state)
    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


def command_timeline_list(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    events = list_timeline_events(
        state,
        chapter_id=args.chapter_id or None,
        entity_id=args.entity_id or None,
    )
    print(json.dumps(events, ensure_ascii=False, indent=2))
    return 0


def command_timeline_check(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    result = check_timeline_conflicts(state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def register_timeline_commands(subparsers) -> None:
    timeline_parser = subparsers.add_parser("timeline", help="Timeline event management")
    timeline_sub = timeline_parser.add_subparsers(dest="timeline_command", required=True)

    add_parser = timeline_sub.add_parser("add", help="Add a timeline event")
    add_parser.add_argument("--root", required=True)
    add_parser.add_argument("--chapter-id", required=True)
    add_parser.add_argument("--description", required=True)
    add_parser.add_argument("--time-label", help="Story-internal time label (e.g. '第一天清晨')")
    add_parser.add_argument("--entity-id", action="append", help="Entity IDs involved (repeatable)")
    add_parser.set_defaults(func=command_timeline_add)

    list_parser = timeline_sub.add_parser("list", help="List timeline events")
    list_parser.add_argument("--root", required=True)
    list_parser.add_argument("--chapter-id", help="Filter by chapter")
    list_parser.add_argument("--entity-id", help="Filter by entity")
    list_parser.set_defaults(func=command_timeline_list)

    check_parser = timeline_sub.add_parser("check", help="Check for timeline conflicts")
    check_parser.add_argument("--root", required=True)
    check_parser.set_defaults(func=command_timeline_check)
