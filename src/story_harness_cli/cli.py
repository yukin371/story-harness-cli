from __future__ import annotations

import argparse
from typing import List

from story_harness_cli.commands import (
    register_brainstorm_commands,
    register_causality_commands,
    register_chapter_commands,
    register_consistency_commands,
    register_context_commands,
    register_doctor_commands,
    register_entity_commands,
    register_export_commands,
    register_outline_commands,
    register_projection_commands,
    register_project_commands,
    register_review_commands,
    register_stats_commands,
    register_timeline_commands,
    register_search_commands,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Story Harness CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    register_brainstorm_commands(subparsers)
    register_causality_commands(subparsers)
    register_project_commands(subparsers)
    register_chapter_commands(subparsers)
    register_review_commands(subparsers)
    register_outline_commands(subparsers)
    register_projection_commands(subparsers)
    register_context_commands(subparsers)
    register_doctor_commands(subparsers)
    register_consistency_commands(subparsers)
    register_entity_commands(subparsers)
    register_export_commands(subparsers)
    register_stats_commands(subparsers)
    register_timeline_commands(subparsers)
    register_search_commands(subparsers)
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
