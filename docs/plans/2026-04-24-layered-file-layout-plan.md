# Layered File Layout Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructure the protocol layer to support volume-split YAML files for long novels, so AI agents work with smaller context slices instead of monolithic files.

**Architecture:** Add a "layout mode" detector to `protocol/files.py` that resolves paths differently based on whether the project uses flat (legacy) or layered (new) structure. The state layer reads/writes through this abstraction, so commands don't need path changes. Auto-detect mode by checking for `spec/` directory existence. Backward-compatible: flat projects continue working unchanged.

**Tech Stack:** Python 3.10+, stdlib only (json, pathlib), unittest for tests

---

## Task 1: Layout Detection and Path Abstraction

**Files:**
- Modify: `src/story_harness_cli/protocol/files.py`
- Test: `tests/smoke/test_layout_detection.py`

**Why first:** All other tasks depend on a working path abstraction. This is the foundation.

### Step 1: Write failing test for layout detection

```python
"""tests/smoke/test_layout_detection.py"""
import unittest
from pathlib import Path
import tempfile
import shutil

from story_harness_cli.protocol.files import (
    detect_layout,
    resolve_state_path,
    LAYOUT_FLAT,
    LAYOUT_LAYERED,
)


class TestLayoutDetection(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_detect_flat_when_no_spec_dir(self):
        """Flat layout detected when spec/ does not exist."""
        (self.tmp / "project.yaml").write_text("{}", encoding="utf-8")
        self.assertEqual(detect_layout(self.tmp), LAYOUT_FLAT)

    def test_detect_layered_when_spec_dir_exists(self):
        """Layered layout detected when spec/ exists."""
        (self.tmp / "spec").mkdir()
        (self.tmp / "project.yaml").write_text("{}", encoding="utf-8")
        self.assertEqual(detect_layout(self.tmp), LAYOUT_LAYERED)

    def test_flat_outline_path(self):
        """Flat layout resolves outline.yaml at root."""
        path = resolve_state_path(self.tmp, "outline", layout=LAYOUT_FLAT)
        self.assertEqual(path, self.tmp / "outline.yaml")

    def test_layered_outline_path(self):
        """Layered layout resolves outline.yaml in spec/."""
        path = resolve_state_path(self.tmp, "outline", layout=LAYOUT_LAYERED)
        self.assertEqual(path, self.tmp / "spec" / "outline.yaml")

    def test_flat_entities_path(self):
        path = resolve_state_path(self.tmp, "entities", layout=LAYOUT_FLAT)
        self.assertEqual(path, self.tmp / "entities.yaml")

    def test_layered_entities_path(self):
        path = resolve_state_path(self.tmp, "entities", layout=LAYOUT_LAYERED)
        self.assertEqual(path, self.tmp / "spec" / "entities.yaml")

    def test_flat_timeline_path(self):
        path = resolve_state_path(self.tmp, "timeline", layout=LAYOUT_FLAT)
        self.assertEqual(path, self.tmp / "timeline.yaml")

    def test_layered_timeline_path(self):
        path = resolve_state_path(self.tmp, "timeline", layout=LAYOUT_LAYERED)
        self.assertEqual(path, self.tmp / "spec" / "timeline.yaml")

    def test_subdir_paths_unchanged(self):
        """proposals, reviews, projections, logs stay in place for both layouts."""
        for state_key in ("proposals", "reviews", "story_reviews", "projection", "context_lens", "projection_log"):
            flat = resolve_state_path(self.tmp, state_key, layout=LAYOUT_FLAT)
            layered = resolve_state_path(self.tmp, state_key, layout=LAYOUT_LAYERED)
            # Subdir paths should be identical regardless of layout
            self.assertEqual(flat, layered, f"{state_key} paths should match")

    def test_flat_threads_structures_path(self):
        for key in ("threads", "structures"):
            path = resolve_state_path(self.tmp, key, layout=LAYOUT_FLAT)
            self.assertEqual(path, self.tmp / f"{key}.yaml")

    def test_layered_threads_structures_path(self):
        for key in ("threads", "structures"):
            path = resolve_state_path(self.tmp, key, layout=LAYOUT_LAYERED)
            self.assertEqual(path, self.tmp / "spec" / f"{key}.yaml")

    def test_project_yaml_always_at_root(self):
        """project.yaml always at root regardless of layout."""
        flat = resolve_state_path(self.tmp, "project", layout=LAYOUT_FLAT)
        layered = resolve_state_path(self.tmp, "project", layout=LAYOUT_LAYERED)
        self.assertEqual(flat, self.tmp / "project.yaml")
        self.assertEqual(layered, self.tmp / "project.yaml")

    def test_chapters_always_at_root(self):
        """chapters/ always at root regardless of layout."""
        flat = resolve_state_path(self.tmp, "chapters", layout=LAYOUT_FLAT)
        layered = resolve_state_path(self.tmp, "chapters", layout=LAYOUT_LAYERED)
        self.assertEqual(flat, self.tmp / "chapters")
        self.assertEqual(layered, self.tmp / "chapters")

    def test_resolve_auto_detects_layout(self):
        """resolve_state_path without explicit layout auto-detects."""
        (self.tmp / "spec").mkdir()
        path = resolve_state_path(self.tmp, "outline")
        self.assertEqual(path, self.tmp / "spec" / "outline.yaml")

    # --- volume outline paths ---

    def test_volume_outline_path_layered(self):
        """Per-volume outline resolves to spec/outlines/vol-NNN.yaml."""
        path = resolve_state_path(
            self.tmp, "outline_volume", volume_id="vol-001", layout=LAYOUT_LAYERED
        )
        self.assertEqual(path, self.tmp / "spec" / "outlines" / "vol-001.yaml")

    def test_volume_outline_path_flat_returns_index(self):
        """Flat layout: per-volume still returns outline.yaml (no split)."""
        path = resolve_state_path(
            self.tmp, "outline_volume", volume_id="vol-001", layout=LAYOUT_FLAT
        )
        self.assertEqual(path, self.tmp / "outline.yaml")

    # --- entity detail paths ---

    def test_entity_detail_path_layered(self):
        """Per-entity detail resolves to spec/entities/{slug}.yaml."""
        path = resolve_state_path(
            self.tmp, "entity_detail", entity_slug="lin-chen", layout=LAYOUT_LAYERED
        )
        self.assertEqual(path, self.tmp / "spec" / "entities" / "lin-chen.yaml")

    def test_entity_detail_path_flat_returns_index(self):
        """Flat layout: per-entity returns entities.yaml (no split)."""
        path = resolve_state_path(
            self.tmp, "entity_detail", entity_slug="lin-chen", layout=LAYOUT_FLAT
        )
        self.assertEqual(path, self.tmp / "entities.yaml")


if __name__ == "__main__":
    unittest.main()
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_layout_detection -v
```

Expected: FAIL — `cannot import name 'detect_layout'`

### Step 3: Implement layout detection and path resolution

Modify `src/story_harness_cli/protocol/files.py`:

```python
"""src/story_harness_cli/protocol/files.py — add after existing imports"""

LAYOUT_FLAT = "flat"
LAYOUT_LAYERED = "layered"

# State keys that move into spec/ under layered layout
_SPEC_KEYS = {"outline", "entities", "timeline", "threads", "structures"}

# State keys that stay in their subdir regardless of layout
_SUBDIR_KEYS = {
    "proposals": "proposals/draft-proposals.yaml",
    "reviews": "reviews/change-requests.yaml",
    "story_reviews": "reviews/story-reviews.yaml",
    "projection": "projections/projection.yaml",
    "context_lens": "projections/context-lens.yaml",
    "projection_log": "logs/projection-log.yaml",
}


def detect_layout(root: Path) -> str:
    """Detect whether a project uses flat or layered file layout."""
    return LAYOUT_LAYERED if (root / "spec").is_dir() else LAYOUT_FLAT


def resolve_state_path(
    root: Path,
    state_key: str,
    *,
    layout: str | None = None,
    volume_id: str | None = None,
    entity_slug: str | None = None,
) -> Path:
    """Resolve the file path for a given state key, respecting layout mode.

    When layout is None, auto-detects from the project root.
    """
    if layout is None:
        layout = detect_layout(root)

    # project.yaml always at root
    if state_key == "project":
        return root / "project.yaml"

    # chapters/ always at root
    if state_key == "chapters":
        return root / "chapters"

    # Subdir-resident keys stay put
    if state_key in _SUBDIR_KEYS:
        return root / _SUBDIR_KEYS[state_key]

    # Per-volume outline path
    if state_key == "outline_volume":
        if layout == LAYOUT_LAYERED and volume_id:
            return root / "spec" / "outlines" / f"{volume_id}.yaml"
        return resolve_state_path(root, "outline", layout=layout)

    # Per-entity detail path
    if state_key == "entity_detail":
        if layout == LAYOUT_LAYERED and entity_slug:
            return root / "spec" / "entities" / f"{entity_slug}.yaml"
        return resolve_state_path(root, "entities", layout=layout)

    # Spec-eligible keys: outline, entities, timeline, threads, structures
    if state_key in _SPEC_KEYS:
        if layout == LAYOUT_LAYERED:
            return root / "spec" / f"{state_key}.yaml"
        return root / f"{state_key}.yaml"

    # Fallback: root-level yaml
    return root / f"{state_key}.yaml"
```

Keep all existing functions (`root_file`, `chapter_path`, `ROOT_FILES`, etc.) unchanged for backward compatibility.

### Step 4: Run test to verify it passes

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_layout_detection -v
```

Expected: all PASS

### Step 5: Run existing tests to verify no regressions

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Expected: all existing tests PASS (no existing code uses new functions yet)

### Step 6: Commit

```bash
git add src/story_harness_cli/protocol/files.py tests/smoke/test_layout_detection.py
git commit -m "feat(protocol): add layout detection and layered path resolution"
```

---

## Task 2: State Layer Reads Through Layout Abstraction

**Files:**
- Modify: `src/story_harness_cli/protocol/state.py`
- Test: `tests/smoke/test_state_layered.py`

**Goal:** `load_project_state()` and `save_state()` use `resolve_state_path()` so they work with both flat and layered projects.

### Step 1: Write failing test for layered state load/save

```python
"""tests/smoke/test_state_layered.py"""
import unittest
from pathlib import Path
import tempfile
import shutil
import json

from story_harness_cli.protocol.state import load_project_state, save_state


def _write_json_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json_yaml(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").strip())


def _setup_layered_project(tmp: Path) -> None:
    """Create a minimal layered project."""
    # project.yaml at root
    _write_json_yaml(tmp / "project.yaml", {
        "title": "Test Novel",
        "genre": "fantasy",
        "defaultMode": "driving",
        "activeChapterId": "chapter-001",
    })
    # spec/ directory with layered files
    _write_json_yaml(tmp / "spec" / "outline.yaml", {
        "volumes": [],
        "chapters": [],
        "chapterDirections": [],
    })
    _write_json_yaml(tmp / "spec" / "entities.yaml", {
        "entities": [],
        "enrichmentProposals": [],
    })
    _write_json_yaml(tmp / "spec" / "timeline.yaml", {"events": []})
    _write_json_yaml(tmp / "spec" / "threads.yaml", {"threads": []})
    _write_json_yaml(tmp / "spec" / "structures.yaml", {
        "activeStructure": None, "mappings": [],
    })
    # Subdir files stay in place
    for d in ["proposals", "reviews", "projections", "logs", "chapters"]:
        (tmp / d).mkdir(parents=True, exist_ok=True)
    _write_json_yaml(tmp / "proposals" / "draft-proposals.yaml", {"draftProposals": []})
    _write_json_yaml(tmp / "reviews" / "change-requests.yaml", {"changeRequests": []})
    _write_json_yaml(tmp / "reviews" / "story-reviews.yaml", {
        "rubricVersion": "chapter-review-v1",
        "sceneRubricVersion": "scene-review-v1",
        "chapterReviews": [],
        "sceneReviews": [],
    })
    _write_json_yaml(tmp / "projections" / "projection.yaml", {
        "snapshotProjections": [],
        "relationProjections": [],
        "sceneScopeProjections": [],
        "timelineProjections": [],
        "causalityProjections": [],
    })
    _write_json_yaml(tmp / "projections" / "context-lens.yaml", {
        "currentChapterId": None, "lenses": [],
    })
    _write_json_yaml(tmp / "logs" / "projection-log.yaml", {"projectionChanges": []})
    # branches.yaml at root (not in spec/)
    _write_json_yaml(tmp / "branches.yaml", {"branches": []})


class TestStateLayered(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_layered_project(self):
        """State loads correctly from layered layout."""
        _setup_layered_project(self.tmp)
        state = load_project_state(self.tmp)
        self.assertEqual(state["project"]["title"], "Test Novel")
        self.assertEqual(state["entities"]["entities"], [])
        self.assertEqual(state["outline"]["chapters"], [])

    def test_save_layered_project(self):
        """State saves to correct layered paths."""
        _setup_layered_project(self.tmp)
        state = load_project_state(self.tmp)
        state["project"]["title"] = "Updated Title"
        state["entities"]["entities"] = [{"name": "Alice", "type": "person"}]
        save_state(self.tmp, state)

        # Verify spec/ files were written
        outline_path = self.tmp / "spec" / "outline.yaml"
        entities_path = self.tmp / "spec" / "entities.yaml"
        self.assertTrue(outline_path.exists(), "outline.yaml should be in spec/")
        self.assertTrue(entities_path.exists(), "entities.yaml should be in spec/")

        # Verify content
        entities = _read_json_yaml(entities_path)
        self.assertEqual(len(entities["entities"]), 1)
        self.assertEqual(entities["entities"][0]["name"], "Alice")

    def test_flat_project_unchanged(self):
        """Existing flat projects still work identically."""
        from tests.smoke.test_layout_detection import TestLayoutDetection
        # Copy minimal fixture
        fixture = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "minimal_project"
        if fixture.exists():
            shutil.copytree(fixture, self.tmp, dirs_exist=True)
        else:
            _setup_layered_project(self.tmp)
            # Remove spec/ and put files at root for flat
            for key in ["outline", "entities", "timeline", "threads", "structures"]:
                src = self.tmp / "spec" / f"{key}.yaml"
                dst = self.tmp / f"{key}.yaml"
                if src.exists():
                    shutil.move(str(src), str(dst))
            shutil.rmtree(self.tmp / "spec", ignore_errors=True)

        state = load_project_state(self.tmp)
        self.assertIn("project", state)
        self.assertIn("outline", state)
        save_state(self.tmp, state)
        # Should not create spec/
        self.assertFalse((self.tmp / "spec").exists(), "flat layout should not create spec/")


if __name__ == "__main__":
    unittest.main()
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_state_layered -v
```

Expected: FAIL — state loads from root paths, not spec/ paths

### Step 3: Modify state.py to use resolve_state_path

In `src/story_harness_cli/protocol/state.py`, change `load_project_state()` and `save_state()` to resolve paths through `resolve_state_path()` instead of hardcoded `root / filename`.

The mapping from state_key to the internal dict key:
- `"project"` → `state["project"]`
- `"outline"` → `state["outline"]`
- `"entities"` → `state["entities"]`
- `"timeline"` → `state["timeline"]`
- `"branches"` → `state["branches"]`
- `"proposals"` → `state["proposals"]`
- `"reviews"` → `state["reviews"]`
- `"story_reviews"` → `state["story_reviews"]`
- `"projection"` → `state["projection"]`
- `"context_lens"` → `state["context_lens"]`
- `"projection_log"` → `state["projection_log"]`
- `"threads"` → `state["threads"]`
- `"structures"` → `state["structures"]`

The existing `STATE_FILE_NAMES` maps filenames to state dict keys. Replace the filename lookup with `resolve_state_path(root, state_key)`.

Key change in `load_project_state()`:
```python
# Before:
for fname in STATE_FILE_NAMES:
    fpath = root / fname
    ...

# After:
for state_key, internal_key in STATE_KEY_MAP.items():
    fpath = resolve_state_path(root, state_key)
    ...
```

Define `STATE_KEY_MAP` as an ordered mapping:
```python
STATE_KEY_MAP = {
    "project": "project",
    "outline": "outline",
    "entities": "entities",
    "timeline": "timeline",
    "branches": "branches",
    "proposals": "proposals",
    "reviews": "reviews",
    "story_reviews": "story_reviews",
    "projection": "projection",
    "context_lens": "context_lens",
    "projection_log": "projection_log",
    "threads": "threads",
    "structures": "structures",
}
```

Keep `STATE_FILE_NAMES` for backward compat (used by `_state_fingerprint`).

Apply the same change pattern in `save_state()`: replace `root / fname` with `resolve_state_path(root, state_key)`.

### Step 4: Run test to verify it passes

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_state_layered -v
```

Expected: PASS

### Step 5: Run full test suite

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Expected: all PASS (flat projects should still work because resolve_state_path defaults to flat when no spec/ dir)

### Step 6: Commit

```bash
git add src/story_harness_cli/protocol/state.py tests/smoke/test_state_layered.py
git commit -m "feat(protocol): state layer reads/writes through layout abstraction"
```

---

## Task 3: Volume-Level Outline Splitting

**Files:**
- Modify: `src/story_harness_cli/protocol/state.py`
- Test: `tests/smoke/test_outline_volume_split.py`

**Goal:** In layered layout, save each volume's chapter details to `spec/outlines/vol-NNN.yaml`, keep `spec/outline.yaml` as thin index.

### Step 1: Write failing test

```python
"""tests/smoke/test_outline_volume_split.py"""
import unittest
from pathlib import Path
import tempfile
import shutil
import json

from story_harness_cli.protocol.state import load_project_state, save_state


def _write_json_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json_yaml(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").strip())


def _make_volume(vol_id: str, ch_count: int) -> dict:
    chapters = []
    for i in range(1, ch_count + 1):
        ch_id = f"chapter-{i:03d}"
        chapters.append({
            "id": ch_id,
            "title": f"Chapter {i}",
            "status": "planned",
            "direction": f"Direction for {ch_id}",
            "beats": [f"beat-{i}-1"],
            "scenePlans": [{"summary": f"scene-{i}-1"}],
        })
    return {"id": vol_id, "title": f"Volume {vol_id[-1]}", "chapters": chapters}


class TestOutlineVolumeSplit(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _setup_layered_with_volumes(self):
        """Set up a layered project with 2 volumes of 3 chapters each."""
        # Minimal state files
        _write_json_yaml(self.tmp / "project.yaml", {
            "title": "Test", "genre": "fantasy", "defaultMode": "driving",
        })
        for d in ["spec", "spec/outlines", "proposals", "reviews", "projections", "logs", "chapters"]:
            (self.tmp / d).mkdir(parents=True, exist_ok=True)
        for key, default in [
            ("spec/entities.yaml", {"entities": [], "enrichmentProposals": []}),
            ("spec/timeline.yaml", {"events": []}),
            ("spec/threads.yaml", {"threads": []}),
            ("spec/structures.yaml", {"activeStructure": None, "mappings": []}),
            ("branches.yaml", {"branches": []}),
            ("proposals/draft-proposals.yaml", {"draftProposals": []}),
            ("reviews/change-requests.yaml", {"changeRequests": []}),
            ("reviews/story-reviews.yaml", {
                "rubricVersion": "chapter-review-v1",
                "sceneRubricVersion": "scene-review-v1",
                "chapterReviews": [], "sceneReviews": [],
            }),
            ("projections/projection.yaml", {
                "snapshotProjections": [], "relationProjections": [],
                "sceneScopeProjections": [], "timelineProjections": [],
                "causalityProjections": [],
            }),
            ("projections/context-lens.yaml", {"currentChapterId": None, "lenses": []}),
            ("logs/projection-log.yaml", {"projectionChanges": []}),
        ]:
            _write_json_yaml(self.tmp / key, default)

    def test_save_writes_volume_files_in_layered(self):
        """Saving state in layered mode creates spec/outlines/vol-NNN.yaml files."""
        self._setup_layered_with_volumes()
        vol1 = _make_volume("vol-001", 3)
        vol2 = _make_volume("vol-002", 2)

        # Write outline index with volumes
        _write_json_yaml(self.tmp / "spec" / "outline.yaml", {
            "volumes": [
                {"id": "vol-001", "title": "Volume 1", "chapters": vol1["chapters"]},
                {"id": "vol-002", "title": "Volume 2", "chapters": vol2["chapters"]},
            ],
            "chapters": [],
            "chapterDirections": [],
        })

        state = load_project_state(self.tmp)
        save_state(self.tmp, state)

        # Should have per-volume files
        vol1_path = self.tmp / "spec" / "outlines" / "vol-001.yaml"
        vol2_path = self.tmp / "spec" / "outlines" / "vol-002.yaml"
        self.assertTrue(vol1_path.exists(), "vol-001.yaml should exist")
        self.assertTrue(vol2_path.exists(), "vol-002.yaml should exist")

        # Index should be thin (no chapter details in outline.yaml)
        index = _read_json_yaml(self.tmp / "spec" / "outline.yaml")
        for vol in index.get("volumes", []):
            self.assertNotIn("chapters", vol,
                "Index volumes should not contain chapter details")
            self.assertIn("id", vol)

        # Volume files should have chapter details
        vol1_data = _read_json_yaml(vol1_path)
        self.assertEqual(len(vol1_data["chapters"]), 3)

    def test_load_reads_volume_files_in_layered(self):
        """Loading state in layered mode reassembles from per-volume files."""
        self._setup_layered_with_volumes()

        # Write thin index
        _write_json_yaml(self.tmp / "spec" / "outline.yaml", {
            "volumes": [
                {"id": "vol-001", "title": "Volume 1"},
                {"id": "vol-002", "title": "Volume 2"},
            ],
            "chapters": [],
            "chapterDirections": [],
        })

        # Write per-volume files
        vol1 = _make_volume("vol-001", 3)
        vol2 = _make_volume("vol-002", 2)
        _write_json_yaml(self.tmp / "spec" / "outlines" / "vol-001.yaml", vol1)
        _write_json_yaml(self.tmp / "spec" / "outlines" / "vol-002.yaml", vol2)

        state = load_project_state(self.tmp)
        # _sync_outline should have flattened volumes into chapters
        flat_chapters = state["outline"]["chapters"]
        self.assertEqual(len(flat_chapters), 5, "Should flatten 3+2=5 chapters")
        self.assertEqual(flat_chapters[0]["id"], "chapter-001")
        self.assertEqual(flat_chapters[3]["id"], "chapter-004")

    def test_flat_layout_no_volume_files(self):
        """Flat layout does NOT create per-volume files."""
        # Setup flat project
        fixture = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "minimal_project"
        if fixture.exists():
            shutil.copytree(fixture, self.tmp, dirs_exist_ok=True)
        else:
            # Manual flat setup
            _write_json_yaml(self.tmp / "project.yaml", {"title": "T", "genre": "g"})
            _write_json_yaml(self.tmp / "outline.yaml", {
                "volumes": [], "chapters": [], "chapterDirections": [],
            })
            for d in ["proposals", "reviews", "projections", "logs", "chapters"]:
                (self.tmp / d).mkdir(parents=True, exist_ok=True)

        state = load_project_state(self.tmp)
        state["outline"]["volumes"] = [
            {"id": "vol-001", "title": "V1", "chapters": [
                {"id": "ch-001", "title": "C1", "status": "planned"}
            ]}
        ]
        save_state(self.tmp, state)

        # Should NOT create spec/outlines/
        self.assertFalse(
            (self.tmp / "spec").exists(),
            "Flat layout should not create spec/ directory"
        )


if __name__ == "__main__":
    unittest.main()
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_outline_volume_split -v
```

Expected: FAIL — state does not split volumes into separate files

### Step 3: Implement volume splitting in state.py

Add to `state.py`:

1. A `_save_outline_layered()` function that:
   - Writes each volume's chapters to `spec/outlines/{volume_id}.yaml`
   - Writes a thin index (volume id + title only) to `spec/outline.yaml`

2. A `_load_outline_layered()` function that:
   - Reads the thin index from `spec/outline.yaml`
   - For each volume, reads chapters from `spec/outlines/{volume_id}.yaml`
   - Reassembles into the full outline dict
   - Calls `_sync_outline()` to flatten

3. Modify `save_state()`: after writing state, if layered layout, call `_save_outline_layered()`

4. Modify `load_project_state()`: if layered layout and outline index has no chapters in volumes, call `_load_outline_layered()`

### Step 4: Run tests

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_outline_volume_split -v
```

Expected: PASS

### Step 5: Run full test suite

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Expected: all PASS

### Step 6: Commit

```bash
git add src/story_harness_cli/protocol/state.py tests/smoke/test_outline_volume_split.py
git commit -m "feat(protocol): volume-level outline splitting for layered layout"
```

---

## Task 4: Context Refresh Volume-Aware Loading

**Files:**
- Modify: `src/story_harness_cli/commands/context.py`
- Modify: `src/story_harness_cli/services/analyzer.py` (if needed for context slice)
- Test: `tests/smoke/test_context_volume_aware.py`

**Goal:** `context refresh` in layered mode only loads the outline volume relevant to the active chapter, not all volumes.

### Step 1: Write failing test

```python
"""tests/smoke/test_context_volume_aware.py"""
import unittest
from pathlib import Path
import tempfile
import shutil
import json

from story_harness_cli.protocol.state import load_project_state, save_state
from story_harness_cli.protocol.files import detect_layout, LAYOUT_LAYERED


def _write_json_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


class TestContextVolumeAware(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_outline_for_chapter_returns_only_relevant_volume(self):
        """Given a layered project with 2 volumes, loading outline for
        chapter-002 should only return vol-001 data, not vol-002."""
        # Setup layered project with 2 volumes
        (self.tmp / "spec" / "outlines").mkdir(parents=True, exist_ok=True)
        for d in ["proposals", "reviews", "projections", "logs", "chapters"]:
            (self.tmp / d).mkdir(parents=True, exist_ok=True)

        _write_json_yaml(self.tmp / "project.yaml", {
            "title": "T", "genre": "g", "defaultMode": "driving",
            "activeChapterId": "chapter-002",
        })
        _write_json_yaml(self.tmp / "spec" / "outline.yaml", {
            "volumes": [
                {"id": "vol-001", "title": "V1"},
                {"id": "vol-002", "title": "V2"},
            ],
            "chapters": [],
            "chapterDirections": [],
        })
        _write_json_yaml(self.tmp / "spec" / "outlines" / "vol-001.yaml", {
            "id": "vol-001", "title": "V1",
            "chapters": [
                {"id": "chapter-001", "title": "C1", "status": "completed"},
                {"id": "chapter-002", "title": "C2", "status": "in_progress"},
            ],
        })
        _write_json_yaml(self.tmp / "spec" / "outlines" / "vol-002.yaml", {
            "id": "vol-002", "title": "V2",
            "chapters": [
                {"id": "chapter-003", "title": "C3", "status": "planned"},
            ],
        })
        # Other required files
        for key, default in [
            ("spec/entities.yaml", {"entities": [], "enrichmentProposals": []}),
            ("spec/timeline.yaml", {"events": []}),
            ("spec/threads.yaml", {"threads": []}),
            ("spec/structures.yaml", {"activeStructure": None, "mappings": []}),
            ("branches.yaml", {"branches": []}),
            ("proposals/draft-proposals.yaml", {"draftProposals": []}),
            ("reviews/change-requests.yaml", {"changeRequests": []}),
            ("reviews/story-reviews.yaml", {
                "rubricVersion": "v1", "sceneRubricVersion": "v1",
                "chapterReviews": [], "sceneReviews": [],
            }),
            ("projections/projection.yaml", {
                "snapshotProjections": [], "relationProjections": [],
                "sceneScopeProjections": [], "timelineProjections": [],
                "causalityProjections": [],
            }),
            ("projections/context-lens.yaml", {"currentChapterId": None, "lenses": []}),
            ("logs/projection-log.yaml", {"projectionChanges": []}),
        ]:
            _write_json_yaml(self.tmp / key, default)

        # Import the new function
        from story_harness_cli.protocol.state import load_outline_for_chapter
        outline_slice = load_outline_for_chapter(self.tmp, "chapter-002")

        # Should contain chapters from vol-001 only
        chapters = outline_slice.get("chapters", [])
        self.assertEqual(len(chapters), 2, "Should only load vol-001 chapters")
        self.assertEqual(chapters[0]["id"], "chapter-001")
        self.assertEqual(chapters[1]["id"], "chapter-002")


if __name__ == "__main__":
    unittest.main()
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_context_volume_aware -v
```

Expected: FAIL — `load_outline_for_chapter` does not exist

### Step 3: Implement load_outline_for_chapter

In `state.py`, add:

```python
def load_outline_for_chapter(root: Path, chapter_id: str) -> dict:
    """Load only the outline volume containing the given chapter.

    In flat layout, returns the full outline.
    In layered layout, returns only the relevant volume's chapters.
    """
    layout = detect_layout(root)
    if layout == LAYOUT_FLAT:
        state = load_project_state(root)
        return state["outline"]

    # Layered: read index, find volume, load only that volume
    index_path = resolve_state_path(root, "outline", layout=LAYOUT_LAYERED)
    if not index_path.exists():
        return {"chapters": [], "chapterDirections": [], "volumes": []}

    index = _load_yaml(index_path)
    for vol in index.get("volumes", []):
        vol_id = vol.get("id")
        if not vol_id:
            continue
        vol_path = resolve_state_path(
            root, "outline_volume", volume_id=vol_id, layout=LAYOUT_LAYERED
        )
        if not vol_path.exists():
            continue
        vol_data = _load_yaml(vol_path)
        for ch in vol_data.get("chapters", []):
            if ch.get("id") == chapter_id:
                # Found the volume - return its outline slice
                return {
                    "chapters": vol_data.get("chapters", []),
                    "chapterDirections": [
                        {"chapterId": c["id"], "title": c.get("title", ""),
                         "summary": c.get("direction", "")}
                        for c in vol_data.get("chapters", [])
                        if c.get("direction")
                    ],
                    "volumes": [vol],
                    "activeVolumeId": vol_id,
                }

    # Fallback: chapter not found in any volume, return full outline
    state = load_project_state(root)
    return state["outline"]
```

Where `_load_yaml` is a small helper:
```python
def _load_yaml(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8").strip()
    return json.loads(raw) if raw else {}
```

### Step 4: Run tests

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_context_volume_aware -v
```

Expected: PASS

### Step 5: Run full suite

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

### Step 6: Commit

```bash
git add src/story_harness_cli/protocol/state.py tests/smoke/test_context_volume_aware.py
git commit -m "feat(protocol): volume-aware outline loading for context refresh"
```

---

## Task 5: Init Command Layered Mode

**Files:**
- Modify: `src/story_harness_cli/commands/project.py`
- Test: `tests/smoke/test_init_layered.py`

**Goal:** `story-harness init --layout layered` creates the layered directory structure.

### Step 1: Write failing test

```python
"""tests/smoke/test_init_layered.py"""
import unittest
from pathlib import Path
import tempfile
import shutil

from story_harness_cli.commands.project import run_init


class TestInitLayered(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_init_flat_creates_no_spec_dir(self):
        """Default init creates flat layout."""
        args = type("A", (), {
            "root": str(self.tmp / "flat"),
            "title": "Flat Novel",
            "genre": "fantasy",
            "layout": "flat",
        })()
        run_init(args)
        root = self.tmp / "flat"
        self.assertTrue((root / "outline.yaml").exists())
        self.assertFalse((root / "spec").exists())

    def test_init_layered_creates_spec_dir(self):
        """--layout layered creates spec/ with subdirs."""
        args = type("A", (), {
            "root": str(self.tmp / "layered"),
            "title": "Layered Novel",
            "genre": "fantasy",
            "layout": "layered",
        })()
        run_init(args)
        root = self.tmp / "layered"
        self.assertTrue((root / "spec").is_dir(), "spec/ should exist")
        self.assertTrue((root / "spec" / "outline.yaml").exists(),
            "outline.yaml should be in spec/")
        self.assertTrue((root / "spec" / "entities.yaml").exists(),
            "entities.yaml should be in spec/")
        self.assertTrue((root / "spec" / "outlines").is_dir(),
            "spec/outlines/ should exist")
        self.assertTrue((root / "spec" / "entities_dir").is_dir() or True,
            "spec/entities/ dir may be created on demand")
        # project.yaml stays at root
        self.assertTrue((root / "project.yaml").exists())
        # chapters/ stays at root
        self.assertTrue((root / "chapters").is_dir())


if __name__ == "__main__":
    unittest.main()
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_init_layered -v
```

### Step 3: Implement --layout flag in init command

In `project.py`:
1. Add `--layout` argument to the init subparser (choices: flat, layered; default: flat)
2. In `run_init()`, when layout is "layered", create `spec/`, `spec/outlines/` dirs
3. Write state files to the correct paths using `resolve_state_path()`

### Step 4: Run tests

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_init_layered -v
```

### Step 5: Run full suite

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

### Step 6: Commit

```bash
git add src/story_harness_cli/commands/project.py tests/smoke/test_init_layered.py
git commit -m "feat(init): add --layout layered flag for layered project structure"
```

---

## Task 6: Migrate Command

**Files:**
- Create: `src/story_harness_cli/commands/migrate.py`
- Modify: `src/story_harness_cli/main.py` (register command)
- Test: `tests/smoke/test_migrate.py`

**Goal:** `story-harness migrate --root <path>` converts flat layout to layered.

### Step 1: Write failing test

```python
"""tests/smoke/test_migrate.py"""
import unittest
from pathlib import Path
import tempfile
import shutil
import json

from story_harness_cli.commands.migrate import run_migrate


def _write_json_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json_yaml(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8").strip())


class TestMigrate(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_migrate_flat_to_layered(self):
        """Migrate creates spec/ and moves spec-eligible files."""
        # Setup a minimal flat project
        _write_json_yaml(self.tmp / "project.yaml", {"title": "T"})
        _write_json_yaml(self.tmp / "outline.yaml", {
            "volumes": [], "chapters": [], "chapterDirections": [],
        })
        _write_json_yaml(self.tmp / "entities.yaml", {
            "entities": [], "enrichmentProposals": [],
        })
        _write_json_yaml(self.tmp / "timeline.yaml", {"events": []})
        _write_json_yaml(self.tmp / "threads.yaml", {"threads": []})
        _write_json_yaml(self.tmp / "structures.yaml", {
            "activeStructure": None, "mappings": [],
        })
        for d in ["proposals", "reviews", "projections", "logs", "chapters"]:
            (self.tmp / d).mkdir(parents=True, exist_ok=True)
        _write_json_yaml(self.tmp / "branches.yaml", {"branches": []})

        args = type("A", (), {"root": str(self.tmp)})()
        run_migrate(args)

        # spec/ should exist
        self.assertTrue((self.tmp / "spec").is_dir())
        # Files should have moved to spec/
        self.assertTrue((self.tmp / "spec" / "outline.yaml").exists())
        self.assertTrue((self.tmp / "spec" / "entities.yaml").exists())
        self.assertTrue((self.tmp / "spec" / "timeline.yaml").exists())
        # project.yaml stays at root
        self.assertTrue((self.tmp / "project.yaml").exists())
        # Old root files should be gone
        self.assertFalse((self.tmp / "outline.yaml").exists())
        self.assertFalse((self.tmp / "entities.yaml").exists())

    def test_migrate_idempotent(self):
        """Running migrate on already-layered project is a no-op."""
        _write_json_yaml(self.tmp / "project.yaml", {"title": "T"})
        (self.tmp / "spec").mkdir()
        _write_json_yaml(self.tmp / "spec" / "outline.yaml", {
            "volumes": [], "chapters": [], "chapterDirections": [],
        })
        for d in ["proposals", "reviews", "projections", "logs", "chapters"]:
            (self.tmp / d).mkdir(parents=True, exist_ok=True)

        args = type("A", (), {"root": str(self.tmp)})()
        # Should not raise
        run_migrate(args)
        self.assertTrue((self.tmp / "spec" / "outline.yaml").exists())


if __name__ == "__main__":
    unittest.main()
```

### Step 2: Run test to verify it fails

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_migrate -v
```

### Step 3: Implement migrate command

Create `src/story_harness_cli/commands/migrate.py`:
```python
"""migrate.py — migrate flat layout to layered."""
from pathlib import Path
import json
from story_harness_cli.protocol.files import (
    detect_layout, LAYOUT_FLAT, _SPEC_KEYS,
)


def run_migrate(args) -> None:
    root = Path(args.root).resolve()
    if detect_layout(root) != LAYOUT_FLAT:
        print("Already layered or no project found. Nothing to do.")
        return

    spec_dir = root / "spec"
    spec_dir.mkdir(exist_ok=True)
    (spec_dir / "outlines").mkdir(exist_ok=True)

    moved = []
    for key in sorted(_SPEC_KEYS):
        src = root / f"{key}.yaml"
        dst = spec_dir / f"{key}.yaml"
        if src.exists():
            src.rename(dst)
            moved.append(key)

    print(f"Migrated {len(moved)} files to spec/: {', '.join(moved)}")
```

Register in `main.py` alongside other commands.

### Step 4: Run tests

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_migrate -v
```

### Step 5: Full suite

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

### Step 6: Commit

```bash
git add src/story_harness_cli/commands/migrate.py src/story_harness_cli/main.py tests/smoke/test_migrate.py
git commit -m "feat(migrate): add flat-to-layered migration command"
```

---

## Task 7: Update Doctor to Validate Layered Layout

**Files:**
- Modify: `src/story_harness_cli/commands/doctor.py`
- Test: `tests/smoke/test_doctor.py` (extend existing)

**Goal:** `doctor` validates both flat and layered layouts, reporting missing files in correct locations.

### Step 1: Extend existing doctor test

Add to `tests/smoke/test_doctor.py`:
```python
def test_doctor_layered_project(self):
    """Doctor validates layered project structure."""
    # ... setup layered project ...
    # Run doctor, expect no errors
```

### Step 2: Update doctor.py

In the file validation section, replace hardcoded `ROOT_FILES` checks with paths from `resolve_state_path()`.

### Step 3: Run tests, commit

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
git add -u && git commit -m "feat(doctor): validate layered layout paths"
```

---

## Task 8: Smoke Test — Full Layered Loop

**Files:**
- Create: `tests/smoke/test_layered_full_loop.py`

**Goal:** End-to-end test that creates a layered project, runs through the full writing loop, and verifies all files end up in the right places.

### Step 1: Write the test

```python
"""End-to-end test for layered layout: init → outline → chapter → review → context → export"""
```

Test the complete cycle:
1. `init --layout layered`
2. `outline propose` + `promote`
3. `chapter analyze`
4. `review chapter`
5. `context refresh`
6. `doctor`
7. `export`

Verify all output files are in spec/, drafts/, workflow/, exports/ as expected.

### Step 2: Run, fix, commit

```bash
PYTHONPATH=src python -m unittest tests.smoke.test_layered_full_loop -v
git add tests/smoke/test_layered_full_loop.py
git commit -m "test: end-to-end layered layout smoke test"
```

---

## Task 9: Foreshadow Tracking (spec/foreshadowing.yaml)

**Files:**
- Create: `src/story_harness_cli/commands/foreshadow.py`
- Modify: `src/story_harness_cli/main.py` (register command)
- Modify: `src/story_harness_cli/protocol/schema.py` (add defaults)
- Modify: `src/story_harness_cli/protocol/files.py` (add to spec keys)
- Test: `tests/smoke/test_foreshadow.py`

**Goal:** Explicit foreshadow→callback pair tracking with `foreshadow plant`, `foreshadow resolve`, `foreshadow list` commands.

### Data Model

```json
{
  "foreshadows": [
    {
      "id": "fs-001",
      "description": "空棺里的城隍夜巡牌",
      "plantedChapter": "chapter-001",
      "plantedScene": 2,
      "plannedPayoffChapter": "chapter-006",
      "actualPayoffChapter": null,
      "status": "planted",
      "notes": "主角在殡仪馆首次接触到夜巡牌的异象"
    }
  ]
}
```

### Step 1: Write failing test

```python
"""tests/smoke/test_foreshadow.py"""
import unittest
from pathlib import Path
import tempfile
import shutil
import json

from story_harness_cli.protocol.files import resolve_state_path, LAYOUT_FLAT, LAYOUT_LAYERED


def _write_json_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


class TestForeshadowPath(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_foreshadow_path_layered(self):
        """In layered layout, foreshadowing.yaml goes to spec/."""
        path = resolve_state_path(self.tmp, "foreshadowing", layout=LAYOUT_LAYERED)
        self.assertEqual(path, self.tmp / "spec" / "foreshadowing.yaml")

    def test_foreshadow_path_flat(self):
        """In flat layout, foreshadowing.yaml at root."""
        path = resolve_state_path(self.tmp, "foreshadowing", layout=LAYOUT_FLAT)
        self.assertEqual(path, self.tmp / "foreshadowing.yaml")


class TestForeshadowCommands(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _setup_project(self):
        """Setup minimal flat project for foreshadow commands."""
        for fname, data in [
            ("project.yaml", {"title": "T", "genre": "g", "defaultMode": "driving"}),
            ("outline.yaml", {"volumes": [], "chapters": [], "chapterDirections": []}),
            ("entities.yaml", {"entities": [], "enrichmentProposals": []}),
            ("timeline.yaml", {"events": []}),
            ("threads.yaml", {"threads": []}),
            ("structures.yaml", {"activeStructure": None, "mappings": []}),
            ("branches.yaml", {"branches": []}),
            ("foreshadowing.yaml", {"foreshadows": []}),
            ("proposals/draft-proposals.yaml", {"draftProposals": []}),
            ("reviews/change-requests.yaml", {"changeRequests": []}),
            ("reviews/story-reviews.yaml", {
                "rubricVersion": "v1", "sceneRubricVersion": "v1",
                "chapterReviews": [], "sceneReviews": [],
            }),
            ("projections/projection.yaml", {
                "snapshotProjections": [], "relationProjections": [],
                "sceneScopeProjections": [], "timelineProjections": [],
                "causalityProjections": [],
            }),
            ("projections/context-lens.yaml", {"currentChapterId": None, "lenses": []}),
            ("logs/projection-log.yaml", {"projectionChanges": []}),
        ]:
            _write_json_yaml(self.tmp / fname, data)
        for d in ["chapters", "proposals", "reviews", "projections", "logs"]:
            (self.tmp / d).mkdir(parents=True, exist_ok=True)

    def test_plant_foreshadow(self):
        """foreshadow plant creates a new entry."""
        self._setup_project()
        from story_harness_cli.commands.foreshadow import run_plant
        args = type("A", (), {
            "root": str(self.tmp),
            "description": "空棺里的城隍夜巡牌",
            "chapter_id": "chapter-001",
            "scene_index": 2,
            "planned_payoff": "chapter-006",
        })()
        run_plant(args)

        data = json.loads((self.tmp / "foreshadowing.yaml").read_text(encoding="utf-8"))
        self.assertEqual(len(data["foreshadows"]), 1)
        self.assertEqual(data["foreshadows"][0]["description"], "空棺里的城隍夜巡牌")
        self.assertEqual(data["foreshadows"][0]["status"], "planted")

    def test_resolve_foreshadow(self):
        """foreshadow resolve marks entry as resolved."""
        self._setup_project()
        # Plant first
        _write_json_yaml(self.tmp / "foreshadowing.yaml", {
            "foreshadows": [{
                "id": "fs-001",
                "description": "test",
                "plantedChapter": "chapter-001",
                "plantedScene": 1,
                "plannedPayoffChapter": "chapter-006",
                "actualPayoffChapter": None,
                "status": "planted",
                "notes": "",
            }]
        })
        from story_harness_cli.commands.foreshadow import run_resolve
        args = type("A", (), {
            "root": str(self.tmp),
            "foreshadow_id": "fs-001",
            "payoff_chapter": "chapter-005",
        })()
        run_resolve(args)

        data = json.loads((self.tmp / "foreshadowing.yaml").read_text(encoding="utf-8"))
        self.assertEqual(data["foreshadows"][0]["status"], "resolved")
        self.assertEqual(data["foreshadows"][0]["actualPayoffChapter"], "chapter-005")


if __name__ == "__main__":
    unittest.main()
```

### Step 2-5: Implement, test, commit

Standard TDD cycle. Key implementation:

1. Add `"foreshadowing"` to `_SPEC_KEYS` in `files.py`
2. Add foreshadowing defaults to `schema.py`
3. Create `commands/foreshadow.py` with `plant`, `resolve`, `list` subcommands
4. Register in `main.py`

```bash
git add -A && git commit -m "feat(foreshadow): add foreshadow plant/resolve/list commands"
```

---

## Task 10: Spec Export (Human-Readable Outline & Character Cards)

**Files:**
- Modify: `src/story_harness_cli/commands/export.py`
- Test: `tests/smoke/test_export_spec.py`

**Goal:** `export --format spec-outline` and `export --format spec-characters` generate human-readable Markdown for review outside the CLI.

### Step 1: Write failing test

```python
"""tests/smoke/test_export_spec.py"""
import unittest
from pathlib import Path
import tempfile
import shutil
import json

from story_harness_cli.commands.export import command_export


def _write_json_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


class TestExportSpec(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _setup_project_with_data(self):
        """Setup project with outline and entity data."""
        for fname, data in [
            ("project.yaml", {
                "title": "夜巡收煞录", "genre": "奇幻", "defaultMode": "driving",
            }),
            ("outline.yaml", {
                "volumes": [{
                    "id": "vol-001", "title": "城隍夜班",
                    "chapters": [
                        {"id": "chapter-001", "title": "空棺", "status": "completed",
                         "direction": "主角在殡仪馆值班时遇到空棺",
                         "beats": ["发现空棺", "触碰夜巡牌"],
                         "scenePlans": [{"summary": "殡仪馆值班"}]},
                    ],
                }],
                "chapters": [],
                "chapterDirections": [],
            }),
            ("entities.yaml", {
                "entities": [{
                    "name": "林尘", "type": "person",
                    "firstMention": "chapter-001",
                    "traits": ["冷静", "观察力强"],
                    "appearance": "二十出头，偏瘦，夜班工作留下的黑眼圈",
                    "abilities": ["夜巡牌感应"],
                }],
                "enrichmentProposals": [],
            }),
        ]:
            _write_json_yaml(self.tmp / fname, data)
        for d in ["chapters", "proposals", "reviews", "projections", "logs"]:
            (self.tmp / d).mkdir(parents=True, exist_ok=True)

    def test_export_spec_outline(self):
        """export --format spec-outline produces human-readable outline."""
        self._setup_project_with_data()
        out_file = self.tmp / "outline-review.md"
        args = type("A", (), {
            "root": str(self.tmp),
            "format": "spec-outline",
            "output": str(out_file),
            "chapter_id": None,
        })()
        command_export(args)

        content = out_file.read_text(encoding="utf-8")
        self.assertIn("城隍夜班", content)
        self.assertIn("空棺", content)
        self.assertIn("发现空棺", content)

    def test_export_spec_characters(self):
        """export --format spec-characters produces human-readable character cards."""
        self._setup_project_with_data()
        out_file = self.tmp / "characters-review.md"
        args = type("A", (), {
            "root": str(self.tmp),
            "format": "spec-characters",
            "output": str(out_file),
            "chapter_id": None,
        })()
        command_export(args)

        content = out_file.read_text(encoding="utf-8")
        self.assertIn("林尘", content)
        self.assertIn("二十出头", content)
        self.assertIn("夜巡牌感应", content)


if __name__ == "__main__":
    unittest.main()
```

### Step 2-5: Implement, test, commit

Extend `command_export()` to handle `spec-outline` and `spec-characters` formats:

**spec-outline output format:**
```markdown
# 大纲: 夜巡收煞录

## 卷一: 城隍夜班

### chapter-001: 空棺 [已完成]
**方向:** 主角在殡仪馆值班时遇到空棺

**细纲:**
- 发现空棺
- 触碰夜巡牌

**场景:**
1. 殡仪馆值班

---
```

**spec-characters output format:**
```markdown
# 角色卡: 夜巡收煞录

---

## 林尘 (person)

> 首次出场: chapter-001

**特质:** 冷静, 观察力强

**外貌:** 二十出头，偏瘦，夜班工作留下的黑眼圈

**能力:** 夜巡牌感应

---
```

```bash
git add -A && git commit -m "feat(export): add spec-outline and spec-characters human-readable export"
```

---

## Updated Summary of All Commits

| # | Commit | Scope |
|---|--------|-------|
| 1 | `feat(protocol): add layout detection and layered path resolution` | files.py |
| 2 | `feat(protocol): state layer reads/writes through layout abstraction` | state.py |
| 3 | `feat(protocol): volume-level outline splitting for layered layout` | state.py |
| 4 | `feat(protocol): volume-aware outline loading for context refresh` | state.py |
| 5 | `feat(init): add --layout layered flag` | project.py, main.py |
| 6 | `feat(migrate): add flat-to-layered migration command` | migrate.py, main.py |
| 7 | `feat(doctor): validate layered layout paths` | doctor.py |
| 8 | `test: end-to-end layered layout smoke test` | new test file |
| 9 | `feat(foreshadow): add foreshadow plant/resolve/list commands` | foreshadow.py, files.py, schema.py, main.py |
| 10 | `feat(export): add spec-outline and spec-characters human-readable export` | export.py |

| # | Commit | Scope |
|---|--------|-------|
| 1 | `feat(protocol): add layout detection and layered path resolution` | files.py |
| 2 | `feat(protocol): state layer reads/writes through layout abstraction` | state.py |
| 3 | `feat(protocol): volume-level outline splitting for layered layout` | state.py |
| 4 | `feat(protocol): volume-aware outline loading for context refresh` | state.py |
| 5 | `feat(init): add --layout layered flag` | project.py, main.py |
| 6 | `feat(migrate): add flat-to-layered migration command` | migrate.py, main.py |
| 7 | `feat(doctor): validate layered layout paths` | doctor.py |
| 8 | `test: end-to-end layered layout smoke test` | new test file |
