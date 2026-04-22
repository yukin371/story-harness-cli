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


class SearchCommandTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-search-"))
        _setup_project(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_search_finds_keyword_in_fixture(self):
        """The fixture chapter mentions 林舟 and 沈昭."""
        buf = StringIO()
        with redirect_stdout(buf):
            result = main([
                "search", "--root", str(self.temp_dir),
                "--query", "林舟",
            ])
        self.assertEqual(result, 0)
        data = json.loads(buf.getvalue())
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]["chapterId"], "chapter-001")
        self.assertIn("林舟", data[0]["snippet"])

    def test_search_no_results(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main([
                "search", "--root", str(self.temp_dir),
                "--query", "不存在的关键词XYZ",
            ])
        self.assertEqual(result, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data, [])

    def test_search_single_chapter(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main([
                "search", "--root", str(self.temp_dir),
                "--query", "沈昭",
                "--chapter-id", "chapter-001",
            ])
        self.assertEqual(result, 0)
        data = json.loads(buf.getvalue())
        self.assertGreater(len(data), 0)


if __name__ == "__main__":
    unittest.main()
