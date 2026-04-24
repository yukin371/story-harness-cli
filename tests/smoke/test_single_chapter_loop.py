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
        project_path = self.temp_dir / "project.yaml"
        project = json.loads(project_path.read_text(encoding="utf-8"))
        project["positioning"] = {
            "primaryGenre": "mystery",
            "subGenre": "",
            "styleTags": [],
            "targetAudience": ["mystery-reader"],
        }
        project["storyContract"] = {
            "corePromises": ["每章推进账本谜团"],
            "avoidances": [],
            "endingContract": "",
            "paceContract": "中快节奏",
        }
        project_path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        outline_path = self.temp_dir / "outline.yaml"
        outline = json.loads(outline_path.read_text(encoding="utf-8"))
        outline["chapters"][0]["beats"] = [{"id": "beat-001", "summary": "两人在仓库对峙", "status": "planned"}]
        outline["chapters"][0]["scenePlans"] = [
            {
                "id": "scene-001",
                "title": "仓库对峙",
                "summary": "林舟与沈昭必须在这一幕里摊开怀疑。",
                "startParagraph": 1,
                "endParagraph": 3,
            }
        ]
        outline["chapterDirections"] = [
            {
                "chapterId": "chapter-001",
                "title": "第一章方向",
                "summary": "让林舟与沈昭在仓库爆发第一次决定性冲突。",
            }
        ]
        outline_path.write_text(json.dumps(outline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

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
