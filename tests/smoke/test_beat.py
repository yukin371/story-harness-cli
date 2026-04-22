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
from story_harness_cli.protocol import load_project_state


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


class BeatCommandTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-beat-"))
        _setup_project(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_beat_add(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main([
                "outline", "beat-add", "--root", str(self.temp_dir),
                "--chapter-id", "chapter-001",
                "--summary", "开场对峙",
            ])
        self.assertEqual(result, 0)
        beat = json.loads(buf.getvalue())
        self.assertTrue(beat["id"].startswith("beat-"))
        self.assertEqual(beat["summary"], "开场对峙")
        self.assertEqual(beat["status"], "planned")

        # Verify persisted
        state = load_project_state(self.temp_dir)
        chapter = None
        for ch in state["outline"].get("chapters", []):
            if ch.get("id") == "chapter-001":
                chapter = ch
                break
        self.assertIsNotNone(chapter)
        self.assertEqual(len(chapter["beats"]), 1)

    def test_beat_complete(self):
        # Add a beat first
        buf = StringIO()
        with redirect_stdout(buf):
            main([
                "outline", "beat-add", "--root", str(self.temp_dir),
                "--chapter-id", "chapter-001",
                "--summary", "测试beat",
            ])
        beat = json.loads(buf.getvalue())

        # Complete it
        buf2 = StringIO()
        with redirect_stdout(buf2):
            result = main([
                "outline", "beat-complete", "--root", str(self.temp_dir),
                "--chapter-id", "chapter-001",
                "--beat-id", beat["id"],
            ])
        self.assertEqual(result, 0)
        updated = json.loads(buf2.getvalue())
        self.assertEqual(updated["status"], "completed")
        self.assertIn("completedAt", updated)

    def test_beat_list_filter(self):
        # Add two beats
        for summary in ["beat-A", "beat-B"]:
            main([
                "outline", "beat-add", "--root", str(self.temp_dir),
                "--chapter-id", "chapter-001",
                "--summary", summary,
            ])

        # Complete one
        state = load_project_state(self.temp_dir)
        chapter = next(ch for ch in state["outline"]["chapters"] if ch.get("id") == "chapter-001")
        first_beat_id = chapter["beats"][0]["id"]
        main([
            "outline", "beat-complete", "--root", str(self.temp_dir),
            "--chapter-id", "chapter-001",
            "--beat-id", first_beat_id,
        ])

        # Filter by status
        buf = StringIO()
        with redirect_stdout(buf):
            result = main([
                "outline", "beat-list", "--root", str(self.temp_dir),
                "--chapter-id", "chapter-001",
                "--status", "planned",
            ])
        self.assertEqual(result, 0)
        beats = json.loads(buf.getvalue())
        self.assertEqual(len(beats), 1)
        self.assertEqual(beats[0]["status"], "planned")

    def test_beat_list_empty(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main([
                "outline", "beat-list", "--root", str(self.temp_dir),
                "--chapter-id", "chapter-001",
            ])
        self.assertEqual(result, 0)
        beats = json.loads(buf.getvalue())
        self.assertEqual(beats, [])

    def test_beat_add_nonexistent_chapter(self):
        with self.assertRaises(SystemExit):
            main([
                "outline", "beat-add", "--root", str(self.temp_dir),
                "--chapter-id", "nonexistent-chapter",
                "--summary", "test",
            ])


if __name__ == "__main__":
    unittest.main()
