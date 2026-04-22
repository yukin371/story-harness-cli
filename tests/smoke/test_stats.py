from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.cli import main


def _setup_project(tmp: Path):
    fixture = REPO_ROOT / "tests" / "fixtures" / "minimal_project"
    shutil.copytree(fixture, tmp, dirs_exist_ok=True)
    for d in ["proposals", "reviews", "projections", "logs"]:
        (tmp / d).mkdir(exist_ok=True)
    for name, content in [
        ("entities.yaml", '{"entities":[],"enrichmentProposals":[]}'),
        ("proposals/draft-proposals.yaml", '{"draftProposals":[]}'),
        ("reviews/change-requests.yaml", '{"changeRequests":[]}'),
        ("projections/projection.yaml", '{"snapshotProjections":[],"relationProjections":[],"sceneScopeProjections":[],"timelineProjections":[],"causalityProjections":[]}'),
        ("projections/context-lens.yaml", '{"currentChapterId":null,"lenses":[]}'),
        ("logs/projection-log.yaml", '{"projectionChanges":[]}'),
    ]:
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp / name).write_text(content + "\n", encoding="utf-8")


class StatsCommandTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-stats-"))
        _setup_project(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _run_stats(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main(["stats", "--root", str(self.temp_dir)])
        self.assertEqual(result, 0)
        return json.loads(buf.getvalue())

    def test_stats_basic(self):
        data = self._run_stats()
        for key in ("project", "progress", "entities", "wordCount", "projections"):
            self.assertIn(key, data)
        self.assertEqual(data["project"]["title"], "雾港疑案")

    def test_stats_word_count(self):
        data = self._run_stats()
        self.assertGreater(data["wordCount"]["total"], 0)
        chapters = data["wordCount"]["byChapter"]
        self.assertTrue(any(c["chapterId"] == "chapter-001" for c in chapters))

    def test_stats_progress(self):
        data = self._run_stats()
        self.assertGreaterEqual(data["progress"]["totalChapters"], 1)

    def test_stats_with_entities(self):
        entities = {
            "entities": [
                {"id": "char-001", "name": "林舟", "source": "seed", "aliases": [],
                 "seed": {}, "profile": {}, "currentState": {"status": "active"}},
            ],
            "enrichmentProposals": [],
        }
        (self.temp_dir / "entities.yaml").write_text(
            json.dumps(entities, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        data = self._run_stats()
        self.assertEqual(data["entities"]["total"], 1)
        self.assertEqual(data["entities"]["bySource"].get("seed", 0), 1)


if __name__ == "__main__":
    unittest.main()
