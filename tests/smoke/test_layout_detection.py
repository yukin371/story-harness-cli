from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.protocol.files import (
    LAYOUT_FLAT,
    LAYOUT_LAYERED,
    detect_layout,
    resolve_state_path,
)


class LayoutDetectionTest(unittest.TestCase):
    """Tests for layout detection and layered path resolution."""

    # -- detect_layout --------------------------------------------------------

    def test_detect_flat_when_no_spec_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(detect_layout(root), LAYOUT_FLAT)

    def test_detect_layered_when_spec_dir_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            self.assertEqual(detect_layout(root), LAYOUT_LAYERED)

    # -- outline paths --------------------------------------------------------

    def test_flat_outline_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = resolve_state_path(root, "outline", layout=LAYOUT_FLAT)
            self.assertEqual(path, root / "outline.yaml")

    def test_layered_outline_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            path = resolve_state_path(root, "outline", layout=LAYOUT_LAYERED)
            self.assertEqual(path, root / "spec" / "outline.yaml")

    # -- entities paths -------------------------------------------------------

    def test_flat_entities_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = resolve_state_path(root, "entities", layout=LAYOUT_FLAT)
            self.assertEqual(path, root / "entities.yaml")

    def test_layered_entities_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            path = resolve_state_path(root, "entities", layout=LAYOUT_LAYERED)
            self.assertEqual(path, root / "spec" / "entities.yaml")

    # -- subdir-resident keys (identical for both layouts) --------------------

    def test_subdir_paths_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subdir_cases = {
                "proposals": "proposals/draft-proposals.yaml",
                "reviews": "reviews/change-requests.yaml",
                "story_reviews": "reviews/story-reviews.yaml",
                "projection": "projections/projection.yaml",
                "context_lens": "projections/context-lens.yaml",
                "projection_log": "logs/projection-log.yaml",
            }
            for key, expected_rel in subdir_cases.items():
                flat_path = resolve_state_path(root, key, layout=LAYOUT_FLAT)
                layered_path = resolve_state_path(root, key, layout=LAYOUT_LAYERED)
                expected = root / expected_rel
                self.assertEqual(
                    flat_path,
                    expected,
                    f"{key}: flat path mismatch",
                )
                self.assertEqual(
                    layered_path,
                    expected,
                    f"{key}: layered path should match flat for subdir keys",
                )

    # -- project.yaml always at root -----------------------------------------

    def test_project_yaml_always_at_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            flat = resolve_state_path(root, "project", layout=LAYOUT_FLAT)
            layered = resolve_state_path(root, "project", layout=LAYOUT_LAYERED)
            self.assertEqual(flat, root / "project.yaml")
            self.assertEqual(layered, root / "project.yaml")

    # -- chapters directory always at root ------------------------------------

    def test_chapters_always_at_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            flat = resolve_state_path(root, "chapters", layout=LAYOUT_FLAT)
            layered = resolve_state_path(root, "chapters", layout=LAYOUT_LAYERED)
            self.assertEqual(flat, root / "chapters")
            self.assertEqual(layered, root / "chapters")

    # -- auto-detection -------------------------------------------------------

    def test_resolve_auto_detects_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # flat auto-detect
            path_flat = resolve_state_path(root, "outline")
            self.assertEqual(path_flat, root / "outline.yaml")

            # switch to layered
            (root / "spec").mkdir()
            path_layered = resolve_state_path(root, "outline")
            self.assertEqual(path_layered, root / "spec" / "outline.yaml")

    # -- outline_volume -------------------------------------------------------

    def test_volume_outline_path_layered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            path = resolve_state_path(
                root,
                "outline_volume",
                layout=LAYOUT_LAYERED,
                volume_id="vol-001",
            )
            self.assertEqual(path, root / "spec" / "outlines" / "vol-001.yaml")

    def test_volume_outline_path_flat_returns_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = resolve_state_path(
                root,
                "outline_volume",
                layout=LAYOUT_FLAT,
                volume_id="vol-001",
            )
            self.assertEqual(path, root / "outline.yaml")

    # -- entity_detail --------------------------------------------------------

    def test_entity_detail_path_layered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            path = resolve_state_path(
                root,
                "entity_detail",
                layout=LAYOUT_LAYERED,
                entity_slug="lin-chen",
            )
            self.assertEqual(path, root / "spec" / "entities" / "lin-chen.yaml")

    def test_entity_detail_path_flat_returns_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = resolve_state_path(
                root,
                "entity_detail",
                layout=LAYOUT_FLAT,
                entity_slug="lin-chen",
            )
            self.assertEqual(path, root / "entities.yaml")

    # -- threads / structures -------------------------------------------------

    def test_flat_threads_structures_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            threads = resolve_state_path(root, "threads", layout=LAYOUT_FLAT)
            structs = resolve_state_path(root, "structures", layout=LAYOUT_FLAT)
            self.assertEqual(threads, root / "threads.yaml")
            self.assertEqual(structs, root / "structures.yaml")

    def test_layered_threads_structures_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            threads = resolve_state_path(root, "threads", layout=LAYOUT_LAYERED)
            structs = resolve_state_path(root, "structures", layout=LAYOUT_LAYERED)
            self.assertEqual(threads, root / "spec" / "threads.yaml")
            self.assertEqual(structs, root / "spec" / "structures.yaml")

    # -- timeline -------------------------------------------------------------

    def test_flat_timeline_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = resolve_state_path(root, "timeline", layout=LAYOUT_FLAT)
            self.assertEqual(path, root / "timeline.yaml")

    def test_layered_timeline_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "spec").mkdir()
            path = resolve_state_path(root, "timeline", layout=LAYOUT_LAYERED)
            self.assertEqual(path, root / "spec" / "timeline.yaml")


if __name__ == "__main__":
    unittest.main()
