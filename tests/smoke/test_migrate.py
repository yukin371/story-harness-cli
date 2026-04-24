"""test_migrate.py — tests for the migrate (flat -> layered) command."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.protocol.files import detect_layout, LAYOUT_FLAT, LAYOUT_LAYERED, _SPEC_KEYS
from story_harness_cli.commands.migrate import run_migrate


def _write_json_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


def _make_flat_project(root: Path):
    """Create a minimal flat-layout project at *root*."""
    _write_json_yaml(root / "project.yaml", {"title": "Test Project"})
    for key in _SPEC_KEYS:
        _write_json_yaml(root / f"{key}.yaml", {key: f"{key}-data"})
    # branches.yaml is NOT a spec key — it stays at root
    _write_json_yaml(root / "branches.yaml", {"branches": []})


class TestMigrateFlatToLayered(unittest.TestCase):
    def test_migrate_flat_to_layered(self):
        with tempfile.TemporaryDirectory(prefix="story-harness-migrate-") as tmp:
            root = Path(tmp)
            _make_flat_project(root)

            # Sanity: starts as flat
            self.assertEqual(detect_layout(root), LAYOUT_FLAT)

            # Run migrate
            args = type("Args", (), {"root": str(root)})()
            run_migrate(args)

            # Now layered
            self.assertEqual(detect_layout(root), LAYOUT_LAYERED)

            # spec/ directory created
            self.assertTrue((root / "spec").is_dir())
            self.assertTrue((root / "spec" / "outlines").is_dir())

            # Spec-eligible files moved to spec/
            for key in _SPEC_KEYS:
                self.assertTrue(
                    (root / "spec" / f"{key}.yaml").exists(),
                    f"spec/{key}.yaml should exist after migration",
                )
                self.assertFalse(
                    (root / f"{key}.yaml").exists(),
                    f"{key}.yaml should no longer exist at root",
                )

            # project.yaml stays at root
            self.assertTrue((root / "project.yaml").exists())

            # branches.yaml stays at root (not in _SPEC_KEYS)
            self.assertTrue((root / "branches.yaml").exists())
            self.assertFalse((root / "spec" / "branches.yaml").exists())


class TestMigrateIdempotent(unittest.TestCase):
    def test_migrate_idempotent(self):
        with tempfile.TemporaryDirectory(prefix="story-harness-migrate-idem-") as tmp:
            root = Path(tmp)
            _make_flat_project(root)

            # First migration
            args = type("Args", (), {"root": str(root)})()
            run_migrate(args)
            self.assertEqual(detect_layout(root), LAYOUT_LAYERED)

            # Second migration should be a no-op (no error)
            run_migrate(args)
            self.assertEqual(detect_layout(root), LAYOUT_LAYERED)

            # Files still present under spec/
            for key in _SPEC_KEYS:
                self.assertTrue((root / "spec" / f"{key}.yaml").exists())


class TestMigratePreservesContent(unittest.TestCase):
    def test_migrate_preserves_content(self):
        with tempfile.TemporaryDirectory(prefix="story-harness-migrate-content-") as tmp:
            root = Path(tmp)
            _make_flat_project(root)

            # Write specific data to outline.yaml
            original_data = {
                "chapters": [
                    {"id": "ch-001", "title": "The Beginning"},
                    {"id": "ch-002", "title": "The Middle"},
                ],
                "volumes": [],
            }
            outline_path = root / "outline.yaml"
            _write_json_yaml(outline_path, original_data)

            # Run migrate
            args = type("Args", (), {"root": str(root)})()
            run_migrate(args)

            # Read back from spec/outline.yaml
            new_outline_path = root / "spec" / "outline.yaml"
            self.assertTrue(new_outline_path.exists())
            content = new_outline_path.read_text(encoding="utf-8")
            migrated_data = json.loads(content)

            self.assertEqual(migrated_data, original_data)


if __name__ == "__main__":
    unittest.main()
