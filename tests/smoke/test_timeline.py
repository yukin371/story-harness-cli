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
        ("entities.yaml", json.dumps({
            "entities": [
                {"id": "char-linzhou", "name": "林舟", "source": "seed", "aliases": [],
                 "seed": {}, "profile": {"appearance": [], "abilities": [], "speech": [], "relationships": []},
                 "currentState": {"status": "active"}},
                {"id": "char-suqing", "name": "苏晴", "source": "seed", "aliases": [],
                 "seed": {}, "profile": {"appearance": [], "abilities": [], "speech": [], "relationships": []},
                 "currentState": {"status": "active"}},
            ],
            "enrichmentProposals": [],
        }, ensure_ascii=False)),
        ("proposals/draft-proposals.yaml", '{"draftProposals":[]}'),
        ("reviews/change-requests.yaml", '{"changeRequests":[]}'),
        ("projections/projection.yaml", '{"snapshotProjections":[],"relationProjections":[],"sceneScopeProjections":[],"timelineProjections":[],"causalityProjections":[]}'),
        ("projections/context-lens.yaml", '{"currentChapterId":null,"lenses":[]}'),
        ("logs/projection-log.yaml", '{"projectionChanges":[]}'),
    ]:
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp / name).write_text(content + "\n", encoding="utf-8")


class TimelineCommandTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-timeline-"))
        _setup_project(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_timeline_add(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main([
                "timeline", "add",
                "--root", str(self.temp_dir),
                "--chapter-id", "chapter-001",
                "--description", "林舟在码头遇见苏晴",
                "--time-label", "第一天清晨",
                "--entity-id", "char-linzhou",
                "--entity-id", "char-suqing",
            ])
        self.assertEqual(result, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["chapterId"], "chapter-001")
        self.assertEqual(data["description"], "林舟在码头遇见苏晴")
        self.assertEqual(data["timeLabel"], "第一天清晨")
        self.assertIn("char-linzhou", data["entityIds"])
        self.assertIn("char-suqing", data["entityIds"])

    def test_timeline_list(self):
        # Add two events
        main([
            "timeline", "add",
            "--root", str(self.temp_dir),
            "--chapter-id", "chapter-001",
            "--description", "事件A",
            "--time-label", "第一天",
        ])
        main([
            "timeline", "add",
            "--root", str(self.temp_dir),
            "--chapter-id", "chapter-002",
            "--description", "事件B",
            "--time-label", "第二天",
        ])
        # List all
        buf = StringIO()
        with redirect_stdout(buf):
            result = main(["timeline", "list", "--root", str(self.temp_dir)])
        self.assertEqual(result, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(len(data), 2)

        # List filtered by chapter
        buf2 = StringIO()
        with redirect_stdout(buf2):
            result2 = main(["timeline", "list", "--root", str(self.temp_dir), "--chapter-id", "chapter-001"])
        self.assertEqual(result2, 0)
        data2 = json.loads(buf2.getvalue())
        self.assertEqual(len(data2), 1)
        self.assertEqual(data2[0]["chapterId"], "chapter-001")

    def test_timeline_check_no_conflicts(self):
        main([
            "timeline", "add",
            "--root", str(self.temp_dir),
            "--chapter-id", "chapter-001",
            "--description", "林舟在码头",
            "--time-label", "第一天",
            "--entity-id", "char-linzhou",
        ])
        buf = StringIO()
        with redirect_stdout(buf):
            result = main(["timeline", "check", "--root", str(self.temp_dir)])
        self.assertEqual(result, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["conflictCount"], 0)

    def test_timeline_check_detects_conflict(self):
        # Same entity in different chapters at same time
        main([
            "timeline", "add",
            "--root", str(self.temp_dir),
            "--chapter-id", "chapter-001",
            "--description", "林舟在码头",
            "--time-label", "第一天清晨",
            "--entity-id", "char-linzhou",
        ])
        main([
            "timeline", "add",
            "--root", str(self.temp_dir),
            "--chapter-id", "chapter-002",
            "--description", "林舟在警局",
            "--time-label", "第一天清晨",
            "--entity-id", "char-linzhou",
        ])
        buf = StringIO()
        with redirect_stdout(buf):
            result = main(["timeline", "check", "--root", str(self.temp_dir)])
        self.assertEqual(result, 0)
        data = json.loads(buf.getvalue())
        self.assertGreater(data["conflictCount"], 0)
        self.assertEqual(data["conflicts"][0]["entityId"], "char-linzhou")


if __name__ == "__main__":
    unittest.main()
