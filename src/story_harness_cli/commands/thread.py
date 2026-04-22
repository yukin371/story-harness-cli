from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.services.thread import (
    check_threads,
    list_threads,
    plant_thread,
    resolve_thread,
)


def command_thread_plant(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    try:
        thread = plant_thread(
            state,
            name=args.name,
            chapter_id=args.chapter_id,
            severity=args.severity or "major",
            resolve_by=args.resolve_by or None,
            description=args.description or "",
        )
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    save_state(root, state)
    print(json.dumps(thread, ensure_ascii=False, indent=2))
    return 0


def command_thread_resolve(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    name_or_id = args.name or args.thread_id
    if not name_or_id:
        print(json.dumps({"error": "Must provide --name or --thread-id"}, ensure_ascii=False, indent=2))
        return 1

    try:
        thread = resolve_thread(
            state,
            name_or_id=name_or_id,
            chapter_id=args.chapter_id,
        )
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    save_state(root, state)
    print(json.dumps(thread, ensure_ascii=False, indent=2))
    return 0


def command_thread_list(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    result = list_threads(
        state,
        status_filter=args.status or None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_thread_check(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)

    result = check_threads(
        state,
        current_chapter_id=args.chapter_id or None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def register_thread_commands(subparsers) -> None:
    thread_parser = subparsers.add_parser("thread", help="Suspense thread tracking")
    thread_sub = thread_parser.add_subparsers(dest="thread_command", required=True)

    # thread plant
    plant_parser = thread_sub.add_parser("plant", help="Plant a suspense thread")
    plant_parser.add_argument("--root", required=True)
    plant_parser.add_argument("--name", required=True, help="Thread name")
    plant_parser.add_argument("--chapter-id", required=True, help="Chapter where thread is planted")
    plant_parser.add_argument("--severity", choices=["major", "minor"], default="major")
    plant_parser.add_argument("--resolve-by", help="Expected resolution chapter id")
    plant_parser.add_argument("--description", help="Optional description")
    plant_parser.set_defaults(func=command_thread_plant)

    # thread resolve
    resolve_parser = thread_sub.add_parser("resolve", help="Resolve a suspense thread")
    resolve_parser.add_argument("--root", required=True)
    resolve_parser.add_argument("--name", help="Thread name to resolve")
    resolve_parser.add_argument("--thread-id", help="Thread id to resolve")
    resolve_parser.add_argument("--chapter-id", required=True, help="Chapter where thread is resolved")
    resolve_parser.set_defaults(func=command_thread_resolve)

    # thread list
    list_parser = thread_sub.add_parser("list", help="List suspense threads")
    list_parser.add_argument("--root", required=True)
    list_parser.add_argument("--status", choices=["open", "resolved", "overdue"], help="Filter by status")
    list_parser.set_defaults(func=command_thread_list)

    # thread check
    check_parser = thread_sub.add_parser("check", help="Check thread health and stats")
    check_parser.add_argument("--root", required=True)
    check_parser.add_argument("--chapter-id", help="Current chapter id for overdue calculation")
    check_parser.set_defaults(func=command_thread_check)
