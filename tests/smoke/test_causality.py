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
        (
            "projections/projection.yaml",
            '{"snapshotProjections":[],"relationProjections":[],'
            '"sceneScopeProjections":[],"timelineProjections":[],"causalityProjections":[]}',
        ),
        ("projections/context-lens.yaml", '{"currentChapterId":null,"lenses":[]}'),
        ("logs/projection-log.yaml", '{"projectionChanges":[]}'),
    ]:
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp / name).write_text(content + "\n", encoding="utf-8")


class CausalityCommandTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-causality-"))
        _setup_project(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _add_event(self, chapter_id: str, description: str, time_label: str = "") -> dict:
        buf = StringIO()
        args = [
            "timeline", "add", "--root", str(self.temp_dir),
            "--chapter-id", chapter_id,
            "--description", description,
        ]
        if time_label:
            args += ["--time-label", time_label]
        with redirect_stdout(buf):
            main(args)
        return json.loads(buf.getvalue())

    def test_causality_add_and_list(self):
        ev1 = self._add_event("chapter-001", "林舟受伤")
        ev2 = self._add_event("chapter-001", "沈昭愤怒质问")

        buf = StringIO()
        with redirect_stdout(buf):
            result = main([
                "causality", "add", "--root", str(self.temp_dir),
                "--cause-event-id", ev1["id"],
                "--effect-event-id", ev2["id"],
                "--description", "受伤引发质问",
            ])
        self.assertEqual(result, 0)
        link = json.loads(buf.getvalue())
        self.assertEqual(link["causeEventId"], ev1["id"])
        self.assertEqual(link["effectEventId"], ev2["id"])

        # List all
        buf2 = StringIO()
        with redirect_stdout(buf2):
            main(["causality", "list", "--root", str(self.temp_dir)])
        links = json.loads(buf2.getvalue())
        self.assertEqual(len(links), 1)

    def test_causality_list_filter_by_event(self):
        ev1 = self._add_event("chapter-001", "事件A")
        ev2 = self._add_event("chapter-001", "事件B")
        ev3 = self._add_event("chapter-001", "事件C")

        main([
            "causality", "add", "--root", str(self.temp_dir),
            "--cause-event-id", ev1["id"], "--effect-event-id", ev2["id"],
        ])
        main([
            "causality", "add", "--root", str(self.temp_dir),
            "--cause-event-id", ev2["id"], "--effect-event-id", ev3["id"],
        ])

        buf = StringIO()
        with redirect_stdout(buf):
            main(["causality", "list", "--root", str(self.temp_dir), "--event-id", ev2["id"]])
        links = json.loads(buf.getvalue())
        # ev2 is effect in first link, cause in second
        self.assertEqual(len(links), 2)

    def test_causality_check_clean(self):
        ev1 = self._add_event("chapter-001", "起因")
        ev2 = self._add_event("chapter-001", "结果")
        main([
            "causality", "add", "--root", str(self.temp_dir),
            "--cause-event-id", ev1["id"], "--effect-event-id", ev2["id"],
        ])

        buf = StringIO()
        with redirect_stdout(buf):
            main(["causality", "check", "--root", str(self.temp_dir)])
        result = json.loads(buf.getvalue())
        self.assertEqual(result["conflictCount"], 0)
        self.assertEqual(result["totalLinks"], 1)

    def test_causality_check_duplicate(self):
        ev1 = self._add_event("chapter-001", "A")
        ev2 = self._add_event("chapter-001", "B")

        main([
            "causality", "add", "--root", str(self.temp_dir),
            "--cause-event-id", ev1["id"], "--effect-event-id", ev2["id"],
        ])
        main([
            "causality", "add", "--root", str(self.temp_dir),
            "--cause-event-id", ev1["id"], "--effect-event-id", ev2["id"],
        ])

        buf = StringIO()
        with redirect_stdout(buf):
            main(["causality", "check", "--root", str(self.temp_dir)])
        result = json.loads(buf.getvalue())
        self.assertGreater(result["conflictCount"], 0)
        types = [c["type"] for c in result["conflicts"]]
        self.assertIn("duplicate-causality", types)

    def test_causality_self_link_rejected(self):
        ev1 = self._add_event("chapter-001", "自指事件")
        with self.assertRaises(SystemExit):
            main([
                "causality", "add", "--root", str(self.temp_dir),
                "--cause-event-id", ev1["id"], "--effect-event-id", ev1["id"],
            ])

    def test_causality_nonexistent_event_rejected(self):
        with self.assertRaises(SystemExit):
            main([
                "causality", "add", "--root", str(self.temp_dir),
                "--cause-event-id", "event-nonexistent",
                "--effect-event-id", "event-also-nonexistent",
            ])


if __name__ == "__main__":
    unittest.main()
