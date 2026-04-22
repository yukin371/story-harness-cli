from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.services.causality import (
    add_causality_link,
    check_causality_conflicts,
    list_causality_links,
)


def command_causality_add(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    entry = add_causality_link(
        state,
        cause_event_id=args.cause_event_id,
        effect_event_id=args.effect_event_id,
        description=args.description or "",
    )
    save_state(root, state)
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    return 0


def command_causality_list(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    links = list_causality_links(
        state,
        event_id=args.event_id or None,
    )
    print(json.dumps(links, ensure_ascii=False, indent=2))
    return 0


def command_causality_check(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    result = check_causality_conflicts(state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def register_causality_commands(subparsers) -> None:
    causality_parser = subparsers.add_parser("causality", help="Causality chain tracking")
    causality_sub = causality_parser.add_subparsers(dest="causality_command", required=True)

    add_parser = causality_sub.add_parser("add", help="Add a cause → effect link between timeline events")
    add_parser.add_argument("--root", required=True)
    add_parser.add_argument("--cause-event-id", required=True)
    add_parser.add_argument("--effect-event-id", required=True)
    add_parser.add_argument("--description", help="Why cause leads to effect")
    add_parser.set_defaults(func=command_causality_add)

    list_parser = causality_sub.add_parser("list", help="List causality links")
    list_parser.add_argument("--root", required=True)
    list_parser.add_argument("--event-id", help="Filter by event involvement (cause or effect)")
    list_parser.set_defaults(func=command_causality_list)

    check_parser = causality_sub.add_parser("check", help="Check for causality conflicts")
    check_parser.add_argument("--root", required=True)
    check_parser.set_defaults(func=command_causality_check)
