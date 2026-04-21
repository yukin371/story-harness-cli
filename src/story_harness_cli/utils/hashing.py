from __future__ import annotations

import hashlib


def stable_hash(value: str, size: int = 10) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:size]

