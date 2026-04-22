from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.services.arc import add_milestone, check_arcs, define_arc, list_arcs


def command_arc_define(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    entity_id_or_name = getattr(args, "entity_id", None) or args.name
    if not entity_id_or_name:
        raise SystemExit("必须指定 --entity-id 或 --name")

    try:
        result = define_arc(
            state,
            entity_id_or_name=entity_id_or_name,
            motivation=args.motivation,
            internal_conflict=args.conflict,
        )
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    save_state(root, state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_arc_milestone(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    entity_id_or_name = getattr(args, "entity_id", None) or args.name
    if not entity_id_or_name:
        raise SystemExit("必须指定 --entity-id 或 --name")

    try:
        result = add_milestone(
            state,
            entity_id_or_name=entity_id_or_name,
            chapter_id=args.chapter_id,
            milestone_type=args.type,
            description=args.description,
        )
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    save_state(root, state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_arc_list(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    result = list_arcs(state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_arc_check(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    result = check_arcs(state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def register_arc_commands(subparsers) -> None:
    arc_parser = subparsers.add_parser("arc", help="Character arc tracking")
    arc_sub = arc_parser.add_subparsers(dest="arc_command", required=True)

    # arc define
    define_parser = arc_sub.add_parser("define", help="Define or update a character arc")
    define_parser.add_argument("--root", required=True)
    define_parser.add_argument("--name", help="Entity name")
    define_parser.add_argument("--entity-id", dest="entity_id", help="Entity id")
    define_parser.add_argument("--motivation", required=True, help="Character motivation")
    define_parser.add_argument("--conflict", required=True, help="Internal conflict")
    define_parser.set_defaults(func=command_arc_define)

    # arc milestone
    milestone_parser = arc_sub.add_parser("milestone", help="Add a milestone to a character arc")
    milestone_parser.add_argument("--root", required=True)
    milestone_parser.add_argument("--name", help="Entity name")
    milestone_parser.add_argument("--entity-id", dest="entity_id", help="Entity id")
    milestone_parser.add_argument("--chapter-id", required=True, help="Chapter where milestone occurs")
    milestone_parser.add_argument("--type", required=True, help="Milestone type")
    milestone_parser.add_argument("--description", required=True, help="Milestone description")
    milestone_parser.set_defaults(func=command_arc_milestone)

    # arc list
    list_parser = arc_sub.add_parser("list", help="List all character arcs")
    list_parser.add_argument("--root", required=True)
    list_parser.set_defaults(func=command_arc_list)

    # arc check
    check_parser = arc_sub.add_parser("check", help="Validate arc completeness")
    check_parser.add_argument("--root", required=True)
    check_parser.set_defaults(func=command_arc_check)
