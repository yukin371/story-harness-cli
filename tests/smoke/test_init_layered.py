from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.commands.project import command_init


class _Args:
    """Minimal Namespace-like object for testing command_init."""

    def __init__(self, **kwargs):
        self.root = kwargs.get("root")
        self.title = kwargs.get("title", "Test Novel")
        self.genre = kwargs.get("genre", "fantasy")
        self.default_mode = kwargs.get("default_mode", "driving")
        self.primary_genre = kwargs.get("primary_genre", None)
        self.sub_genre = kwargs.get("sub_genre", None)
        self.style_tag = kwargs.get("style_tag", None)
        self.target_audience = kwargs.get("target_audience", None)
        self.core_promise = kwargs.get("core_promise", None)
        self.avoidance = kwargs.get("avoidance", None)
        self.ending_contract = kwargs.get("ending_contract", None)
        self.pace_contract = kwargs.get("pace_contract", None)
        self.premise = kwargs.get("premise", None)
        self.hook_line = kwargs.get("hook_line", None)
        self.hook_stack = kwargs.get("hook_stack", None)
        self.benchmark_work = kwargs.get("benchmark_work", None)
        self.target_platform = kwargs.get("target_platform", None)
        self.serialization_model = kwargs.get("serialization_model", None)
        self.release_cadence = kwargs.get("release_cadence", None)
        self.chapter_word_floor = kwargs.get("chapter_word_floor", None)
        self.chapter_word_target = kwargs.get("chapter_word_target", None)
        self.chapter_id = kwargs.get("chapter_id", "chapter-001")
        self.chapter_title = kwargs.get("chapter_title", "Chapter 1")
        self.force = kwargs.get("force", False)
        self.layout = kwargs.get("layout", "flat")


class TestInitFlat(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-init-flat-"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_flat_creates_no_spec_dir(self):
        args = _Args(root=str(self.temp_dir))
        result = command_init(args)
        self.assertEqual(result, 0)

        # outline.yaml at root, NOT inside spec/
        self.assertTrue((self.temp_dir / "outline.yaml").exists())
        self.assertFalse((self.temp_dir / "spec").is_dir())

        # Other spec-eligible files also at root
        self.assertTrue((self.temp_dir / "entities.yaml").exists())
        self.assertTrue((self.temp_dir / "timeline.yaml").exists())
        self.assertTrue((self.temp_dir / "threads.yaml").exists())
        self.assertTrue((self.temp_dir / "structures.yaml").exists())

        # project.yaml at root
        self.assertTrue((self.temp_dir / "project.yaml").exists())

        # chapters/ at root
        self.assertTrue((self.temp_dir / "chapters").is_dir())


class TestInitLayered(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-init-layered-"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_layered_creates_spec_dir(self):
        args = _Args(root=str(self.temp_dir), layout="layered")
        result = command_init(args)
        self.assertEqual(result, 0)

        # spec/ directory must exist
        self.assertTrue((self.temp_dir / "spec").is_dir())

        # spec/outline.yaml (not at root)
        self.assertTrue((self.temp_dir / "spec" / "outline.yaml").exists())
        self.assertFalse((self.temp_dir / "outline.yaml").exists())

        # spec/entities.yaml
        self.assertTrue((self.temp_dir / "spec" / "entities.yaml").exists())
        self.assertFalse((self.temp_dir / "entities.yaml").exists())

        # spec/outlines/ directory exists
        self.assertTrue((self.temp_dir / "spec" / "outlines").is_dir())

        # spec/timeline.yaml, spec/threads.yaml, spec/structures.yaml
        self.assertTrue((self.temp_dir / "spec" / "timeline.yaml").exists())
        self.assertTrue((self.temp_dir / "spec" / "threads.yaml").exists())
        self.assertTrue((self.temp_dir / "spec" / "structures.yaml").exists())

        # project.yaml still at root
        self.assertTrue((self.temp_dir / "project.yaml").exists())

        # chapters/ at root
        self.assertTrue((self.temp_dir / "chapters").is_dir())

        # branches.yaml stays at root (not a spec-eligible key)
        self.assertTrue((self.temp_dir / "branches.yaml").exists())

        # Subdir-based files still in their usual locations
        self.assertTrue((self.temp_dir / "proposals" / "draft-proposals.yaml").exists())
        self.assertTrue((self.temp_dir / "reviews" / "change-requests.yaml").exists())

    def test_init_layered_backward_compat_no_layout_attr(self):
        """If args has no 'layout' attribute, it should default to flat."""
        args = _Args(root=str(self.temp_dir))
        del args.layout
        result = command_init(args)
        self.assertEqual(result, 0)

        # Should behave as flat: no spec/ dir
        self.assertFalse((self.temp_dir / "spec").is_dir())
        self.assertTrue((self.temp_dir / "outline.yaml").exists())


if __name__ == "__main__":
    unittest.main()
