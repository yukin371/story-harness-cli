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


class DoctorSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-doctor-"))
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

    def test_doctor_passes_for_minimal_project(self) -> None:
        buffer = StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["doctor", "--root", str(self.temp_dir)])
        payload = json.loads(buffer.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["summary"]["errors"], 0)

    def test_doctor_fails_for_missing_chapter_file(self) -> None:
        (self.temp_dir / "chapters" / "chapter-001.md").unlink()
        buffer = StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["doctor", "--root", str(self.temp_dir)])
        payload = json.loads(buffer.getvalue())

        self.assertEqual(exit_code, 1)
        self.assertFalse(payload["ok"])
        self.assertGreaterEqual(payload["summary"]["errors"], 1)


if __name__ == "__main__":
    unittest.main()
