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
        ("projections/context-lens.yaml", json.dumps({
            "currentChapterId": "chapter-001",
            "lenses": [{
                "chapterId": "chapter-001",
                "chapterTitle": "裂痕之夜",
                "activeCharacters": [{"id": "char-linzhou", "name": "林舟", "currentState": "受伤；怀疑"}],
                "activeRelations": [],
                "pendingChangeRequestCount": 0,
                "pendingChangeRequests": [],
                "updatedAt": "2026-04-20T00:00:00+08:00",
            }],
        }, ensure_ascii=False)),
        ("logs/projection-log.yaml", '{"projectionChanges":[]}'),
    ]:
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp / name).write_text(content + "\n", encoding="utf-8")


class ContextShowTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-context-"))
        _setup_project(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_context_show_by_chapter_id(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main(["context", "show", "--root", str(self.temp_dir), "--chapter-id", "chapter-001"])
        self.assertEqual(result, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["chapterId"], "chapter-001")
        self.assertEqual(data["chapterTitle"], "裂痕之夜")
        self.assertIn("activeCharacters", data)

    def test_context_show_default_chapter(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main(["context", "show", "--root", str(self.temp_dir)])
        self.assertEqual(result, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["chapterId"], "chapter-001")

    def test_context_show_no_lens(self):
        with self.assertRaises(SystemExit):
            main(["context", "show", "--root", str(self.temp_dir), "--chapter-id", "chapter-999"])


if __name__ == "__main__":
    unittest.main()
