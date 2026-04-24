from __future__ import annotations

import hashlib
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict

from .files import ROOT_FILES, resolve_state_path, root_file
from .io import dump_json_compatible_yaml, load_json_compatible_yaml
from .schema import default_project_state

STATE_FILE_NAMES = (
    "project.yaml",
    "outline.yaml",
    "entities.yaml",
    "timeline.yaml",
    "branches.yaml",
    "proposals/draft-proposals.yaml",
    "reviews/change-requests.yaml",
    "reviews/story-reviews.yaml",
    "projections/projection.yaml",
    "projections/context-lens.yaml",
    "logs/projection-log.yaml",
    "threads.yaml",
    "structures.yaml",
)

# Ordered mapping from state_key (used with resolve_state_path) to the
# internal dict key inside the state dict returned by load_project_state().
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
STATE_META_KEY = "_stateMeta"
STATE_LOCK_FILENAME = ".story-harness.lock"
STATE_LOCK_TIMEOUT_SECONDS = 10.0
STATE_LOCK_POLL_INTERVAL_SECONDS = 0.05


def load_project_state(root: Path) -> Dict[str, Any]:
    defaults = default_project_state()
    state: Dict[str, Any] = {}
    for state_key, internal_key in STATE_KEY_MAP.items():
        fpath = resolve_state_path(root, state_key)
        raw = load_json_compatible_yaml(fpath, defaults[internal_key])
        if state_key in ("project", "story_reviews"):
            state[internal_key] = merge_defaults(raw, defaults[internal_key])
        else:
            state[internal_key] = raw
    state[STATE_META_KEY] = _build_state_meta(root)
    return state


def save_state(root: Path, state: Dict[str, Any], *, timeout_seconds: float = STATE_LOCK_TIMEOUT_SECONDS) -> None:
    with _project_write_lock(root, timeout_seconds=timeout_seconds):
        _ensure_state_not_stale(root, state)
        # Sync volumes → flat chapters/chapterDirections before saving
        _sync_outline(state["outline"])

        for state_key, internal_key in STATE_KEY_MAP.items():
            fpath = resolve_state_path(root, state_key)
            dump_json_compatible_yaml(fpath, state[internal_key])
        state[STATE_META_KEY] = _build_state_meta(root)


def ensure_project_root(root: Path) -> None:
    missing = [name for name in ROOT_FILES if not root_file(root, name).exists()]
    if missing:
        raise SystemExit(f"{root} 不是已初始化的 story harness 项目，缺少: {', '.join(missing)}")


def merge_defaults(payload: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for key, default_value in defaults.items():
        current_value = payload.get(key)
        if isinstance(default_value, dict):
            merged[key] = merge_defaults(current_value if isinstance(current_value, dict) else {}, default_value)
        elif current_value is None:
            merged[key] = default_value
        else:
            merged[key] = current_value
    for key, value in payload.items():
        if key not in merged:
            merged[key] = value
    return merged


def _sync_outline(outline: Dict[str, Any]) -> None:
    volumes = outline.get("volumes")
    if not volumes:
        return
    flat_chapters = []
    flat_directions = []
    for vol in volumes:
        for ch in vol.get("chapters", []):
            flat_entry = {
                "id": ch.get("id"),
                "title": ch.get("title"),
                "status": ch.get("status", "planned"),
                "beats": ch.get("beats", []),
                "scenePlans": ch.get("scenePlans", []),
            }
            flat_chapters.append(flat_entry)
            if ch.get("direction"):
                flat_directions.append({
                    "chapterId": ch.get("id"),
                    "title": ch.get("title"),
                    "summary": ch.get("direction", ""),
                })
    outline["chapters"] = flat_chapters
    outline["chapterDirections"] = flat_directions


def _build_state_meta(root: Path) -> Dict[str, str]:
    return {
        state_key: _fingerprint_path(resolve_state_path(root, state_key))
        for state_key in STATE_KEY_MAP
    }


def _fingerprint_path(path: Path) -> str:
    if not path.exists():
        return "missing"
    return hashlib.sha1(path.read_bytes()).hexdigest()


def _ensure_state_not_stale(root: Path, state: Dict[str, Any]) -> None:
    expected_meta = state.get(STATE_META_KEY)
    if not isinstance(expected_meta, dict) or not expected_meta:
        return
    current_meta = _build_state_meta(root)
    changed_files = [
        state_key for state_key in STATE_KEY_MAP
        if current_meta.get(state_key) != expected_meta.get(state_key)
    ]
    if changed_files:
        changed = "，".join(changed_files)
        raise SystemExit(f"项目状态已被其他命令更新，请重新执行当前命令以避免覆盖：{changed}")


@contextmanager
def _project_write_lock(root: Path, *, timeout_seconds: float = STATE_LOCK_TIMEOUT_SECONDS):
    lock_path = root / STATE_LOCK_FILENAME
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    try:
        if lock_path.stat().st_size == 0:
            handle.write(b"0")
            handle.flush()
        deadline = time.monotonic() + max(timeout_seconds, 0.0)
        while True:
            try:
                _try_acquire_file_lock(handle)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise SystemExit(f"项目状态正被其他命令写入，请稍后重试：{root}")
                time.sleep(STATE_LOCK_POLL_INTERVAL_SECONDS)
        yield
    finally:
        try:
            _release_file_lock(handle)
        except OSError:
            pass
        handle.close()


def _try_acquire_file_lock(handle) -> None:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise BlockingIOError from exc
        return

    import fcntl

    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        raise BlockingIOError from exc


def _release_file_lock(handle) -> None:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return

    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

