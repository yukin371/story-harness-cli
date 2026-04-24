from __future__ import annotations

import json
import sys
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root
from story_harness_cli.protocol.files import resolve_state_path


def _load_foreshadows(root: Path) -> list:
    path = resolve_state_path(root, "foreshadowing")
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8").strip() or "{}")
    return data.get("foreshadows", [])


def _save_foreshadows(root: Path, foreshadows: list) -> None:
    path = resolve_state_path(root, "foreshadowing")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"foreshadows": foreshadows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _next_id(foreshadows: list) -> str:
    max_num = 0
    for fs in foreshadows:
        fs_id = fs.get("id", "fs-000")
        try:
            num = int(fs_id.split("-")[1])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass
    return f"fs-{max_num + 1:03d}"


def run_plant(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    foreshadows = _load_foreshadows(root)
    entry = {
        "id": _next_id(foreshadows),
        "description": args.description,
        "plantedChapter": args.chapter_id,
        "plantedScene": getattr(args, "scene_index", None),
        "plannedPayoffChapter": getattr(args, "planned_payoff", None),
        "actualPayoffChapter": None,
        "status": "planted",
        "notes": getattr(args, "notes", ""),
    }
    foreshadows.append(entry)
    _save_foreshadows(root, foreshadows)
    print(f"Planted foreshadow {entry['id']}: {entry['description']}")
    return 0


def run_resolve(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    foreshadows = _load_foreshadows(root)
    found = False
    for fs in foreshadows:
        if fs.get("id") == args.foreshadow_id:
            fs["status"] = "resolved"
            fs["actualPayoffChapter"] = getattr(args, "payoff_chapter", None)
            found = True
            break
    if not found:
        print(f"Foreshadow {args.foreshadow_id} not found.", file=sys.stderr)
        return 1
    _save_foreshadows(root, foreshadows)
    print(f"Resolved foreshadow {args.foreshadow_id}")
    return 0


def run_list(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    foreshadows = _load_foreshadows(root)
    status_filter = getattr(args, "status", None)
    if status_filter:
        foreshadows = [fs for fs in foreshadows if fs.get("status") == status_filter]
    if not foreshadows:
        print("No foreshadows found.")
        return 0
    for fs in foreshadows:
        status_mark = "Y" if fs.get("status") == "resolved" else "o"
        payoff = fs.get("actualPayoffChapter") or fs.get("plannedPayoffChapter") or "?"
        print(
            f"  {status_mark} {fs['id']}: {fs.get('description', '')} "
            f"(planted: {fs.get('plantedChapter', '?')}, payoff: {payoff})"
        )
    return 0


def register_foreshadow_commands(subparsers) -> None:
    foreshadow_parser = subparsers.add_parser("foreshadow", help="Foreshadow tracking")
    foreshadow_sub = foreshadow_parser.add_subparsers(dest="foreshadow_action")

    plant = foreshadow_sub.add_parser("plant", help="Plant a foreshadow")
    plant.add_argument("--root", required=True)
    plant.add_argument("--description", required=True)
    plant.add_argument("--chapter-id", required=True)
    plant.add_argument("--scene-index", type=int, default=None)
    plant.add_argument("--planned-payoff", default=None)
    plant.add_argument("--notes", default="")
    plant.set_defaults(func=run_plant)

    resolve = foreshadow_sub.add_parser("resolve", help="Resolve a foreshadow")
    resolve.add_argument("--root", required=True)
    resolve.add_argument("--foreshadow-id", required=True)
    resolve.add_argument("--payoff-chapter", default=None)
    resolve.set_defaults(func=run_resolve)

    list_cmd = foreshadow_sub.add_parser("list", help="List foreshadows")
    list_cmd.add_argument("--root", required=True)
    list_cmd.add_argument("--status", choices=["planted", "resolved"], default=None)
    list_cmd.set_defaults(func=run_list)
