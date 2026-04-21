from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.cli import main


class SingleChapterLoopSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-smoke-"))
        fixture_root = REPO_ROOT / "tests" / "fixtures" / "minimal_project"
        shutil.copytree(fixture_root, self.temp_dir, dirs_exist_ok=True)
        for relative in [
            "proposals",
            "reviews",
            "projections",
            "logs",
        ]:
            (self.temp_dir / relative).mkdir(exist_ok=True)
        (self.temp_dir / "proposals" / "draft-proposals.yaml").write_text('{"draftProposals":[]}\n', encoding="utf-8")
        (self.temp_dir / "reviews" / "change-requests.yaml").write_text('{"changeRequests":[]}\n', encoding="utf-8")
        (self.temp_dir / "projections" / "projection.yaml").write_text(
            '{"snapshotProjections":[],"relationProjections":[],"sceneScopeProjections":[],"timelineProjections":[],"causalityProjections":[]}\n',
            encoding="utf-8",
        )
        (self.temp_dir / "projections" / "context-lens.yaml").write_text(
            '{"currentChapterId":"chapter-001","lenses":[]}\n',
            encoding="utf-8",
        )
        (self.temp_dir / "logs" / "projection-log.yaml").write_text('{"projectionChanges":[]}\n', encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_single_chapter_loop(self) -> None:
        args_root = str(self.temp_dir)
        self.assertEqual(main(["chapter", "analyze", "--root", args_root, "--chapter-id", "chapter-001"]), 0)
        self.assertEqual(main(["chapter", "suggest", "--root", args_root, "--chapter-id", "chapter-001"]), 0)
        self.assertEqual(
            main(
                [
                    "review",
                    "apply",
                    "--root",
                    args_root,
                    "--chapter-id",
                    "chapter-001",
                    "--all-pending",
                    "--decision",
                    "accepted",
                ]
            ),
            0,
        )
        self.assertEqual(main(["projection", "apply", "--root", args_root, "--chapter-id", "chapter-001"]), 0)
        self.assertEqual(main(["context", "refresh", "--root", args_root, "--chapter-id", "chapter-001"]), 0)

        projection = json.loads((self.temp_dir / "projections" / "projection.yaml").read_text(encoding="utf-8"))
        context_lens = json.loads((self.temp_dir / "projections" / "context-lens.yaml").read_text(encoding="utf-8"))

        self.assertTrue(projection["snapshotProjections"])
        self.assertTrue(projection["relationProjections"])
        self.assertEqual(context_lens["currentChapterId"], "chapter-001")
        self.assertTrue(context_lens["lenses"])


if __name__ == "__main__":
    unittest.main()

