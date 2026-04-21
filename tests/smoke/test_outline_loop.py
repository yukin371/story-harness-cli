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


class OutlineLoopSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-outline-"))
        main(
            [
                "init",
                "--root",
                str(self.temp_dir),
                "--title",
                "雾港疑案",
                "--genre",
                "悬疑",
                "--chapter-id",
                "chapter-001",
                "--chapter-title",
                "裂痕之夜",
            ]
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_outline_loop(self) -> None:
        args_root = str(self.temp_dir)
        self.assertEqual(
            main(
                [
                    "outline",
                    "propose",
                    "--root",
                    args_root,
                    "--mode",
                    "chapter",
                    "--title",
                    "第二章方向草案",
                    "--summary",
                    "让林舟继续追查账本。",
                    "--chapter-id",
                    "chapter-002",
                    "--item",
                    "港区追踪::林舟沿着血迹和传闻追查账本。",
                ]
            ),
            0,
        )

        proposals = json.loads((self.temp_dir / "proposals" / "draft-proposals.yaml").read_text(encoding="utf-8"))
        proposal_id = proposals["draftProposals"][0]["id"]

        self.assertEqual(
            main(
                [
                    "outline",
                    "promote",
                    "--root",
                    args_root,
                    "--proposal-id",
                    proposal_id,
                    "--chapter-id",
                    "chapter-002",
                ]
            ),
            0,
        )
        self.assertEqual(main(["projection", "apply", "--root", args_root, "--chapter-id", "chapter-002"]), 0)

        outline = json.loads((self.temp_dir / "outline.yaml").read_text(encoding="utf-8"))
        projection_log = json.loads((self.temp_dir / "logs" / "projection-log.yaml").read_text(encoding="utf-8"))

        chapter_002 = next(item for item in outline["chapters"] if item["id"] == "chapter-002")
        self.assertTrue(chapter_002["beats"])
        self.assertTrue(projection_log["projectionChanges"])


if __name__ == "__main__":
    unittest.main()

