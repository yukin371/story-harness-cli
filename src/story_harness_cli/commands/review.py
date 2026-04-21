from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.services import review_change_requests


def command_review_apply(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    result = review_change_requests(
        state,
        decision=args.decision,
        chapter_id=args.chapter_id,
        request_ids=args.request_id or [],
        all_pending=args.all_pending,
        reason=args.reason or "",
    )
    save_state(root, state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def register_review_commands(subparsers) -> None:
    review_parser = subparsers.add_parser("review", help="Review change requests")
    review_subparsers = review_parser.add_subparsers(dest="review_command", required=True)

    apply_parser = review_subparsers.add_parser("apply", help="Apply decisions to change requests")
    apply_parser.add_argument("--root", required=True)
    apply_parser.add_argument("--decision", required=True, choices=["accepted", "ignored", "deferred"])
    apply_parser.add_argument("--request-id", action="append")
    apply_parser.add_argument("--all-pending", action="store_true")
    apply_parser.add_argument("--chapter-id")
    apply_parser.add_argument("--reason")
    apply_parser.set_defaults(func=command_review_apply)

