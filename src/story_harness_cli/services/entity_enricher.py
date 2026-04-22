from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Set

from story_harness_cli.protocol.files import chapter_path
from story_harness_cli.utils import now_iso, stable_hash
from story_harness_cli.utils.text import (
    ability_tags_for_paragraph,
    appearance_tags_for_paragraph,
    paragraphs_from_text,
)


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences on Chinese/English sentence-ending punctuation."""
    parts = re.split(r'(?<=[。！？；.!?])\s*', text)
    return [s.strip() for s in parts if s.strip()]


def _matched_entities(text: str, name_to_entity: Dict[str, Any]) -> List[Dict]:
    """Find entities whose name appears in the given text."""
    matched = []
    seen_ids: Set[str] = set()
    for name, entity in name_to_entity.items():
        if name in text and entity["id"] not in seen_ids:
            matched.append(entity)
            seen_ids.add(entity["id"])
    return matched


def enrich_entities(
    state: Dict[str, Dict[str, Any]],
    chapter_id: str,
    root: Path | None = None,
) -> Dict[str, Any]:
    if not root:
        return {"created": 0, "error": "no root path"}

    chapter_file = chapter_path(root, chapter_id)
    if not chapter_file.exists():
        return {"created": 0, "error": f"chapter not found: {chapter_id}"}

    text = chapter_file.read_text(encoding="utf-8")
    paragraphs = paragraphs_from_text(text)
    entities_list = state["entities"].get("entities", [])
    existing_proposals = state["entities"].setdefault("enrichmentProposals", [])
    existing_fingerprints: Set[str] = {p.get("fingerprint") for p in existing_proposals}

    # Build set of existing profile details per entity for cross-chapter dedup
    existing_details: Dict[str, set] = {}
    for entity in entities_list:
        details = set()
        for entry in entity.get("profile", {}).get("appearance", []):
            text = entry.get("detail", "") if isinstance(entry, dict) else str(entry)
            for part in text.split("；"):
                details.add(part)
        for entry in entity.get("profile", {}).get("abilities", []):
            text = entry.get("detail", "") if isinstance(entry, dict) else str(entry)
            for part in text.split("；"):
                details.add(part)
        existing_details[entity["id"]] = details

    name_to_entity: Dict[str, Dict] = {}
    for entity in entities_list:
        name_to_entity[entity["name"]] = entity
        for alias in entity.get("aliases", []):
            name_to_entity[alias] = entity

    created = 0
    for paragraph in paragraphs:
        # Split into sentences for per-entity attribution.
        # Each sentence's tags are only assigned to entities mentioned
        # in that same sentence, preventing cross-entity misattribution.
        for sentence in _split_sentences(paragraph):
            appearance_tags = appearance_tags_for_paragraph(sentence)
            ability_tags = ability_tags_for_paragraph(sentence)
            sentence_entities = _matched_entities(sentence, name_to_entity)

            for entity in sentence_entities:
                if appearance_tags:
                    detail = "；".join(sorted(set(appearance_tags)))
                    already_have = existing_details.get(entity["id"], set())
                    if all(tag in already_have for tag in set(appearance_tags)):
                        continue
                    fp = f"enrich::appearance::{entity['id']}::{detail}"
                    if fp not in existing_fingerprints:
                        existing_proposals.append({
                            "id": f"enrich-{stable_hash(fp + now_iso())}",
                            "entityId": entity["id"],
                            "entityName": entity["name"],
                            "chapterId": chapter_id,
                            "field": "appearance",
                            "detail": detail,
                            "evidence": sentence,
                            "confidence": 0.85,
                            "status": "pending",
                            "fingerprint": fp,
                            "createdAt": now_iso(),
                        })
                        existing_fingerprints.add(fp)
                        created += 1

                if ability_tags:
                    detail = "；".join(sorted(set(ability_tags)))
                    already_have = existing_details.get(entity["id"], set())
                    if all(tag in already_have for tag in set(ability_tags)):
                        continue
                    fp = f"enrich::ability::{entity['id']}::{detail}"
                    if fp not in existing_fingerprints:
                        existing_proposals.append({
                            "id": f"enrich-{stable_hash(fp + now_iso())}",
                            "entityId": entity["id"],
                            "entityName": entity["name"],
                            "chapterId": chapter_id,
                            "field": "abilities",
                            "detail": detail,
                            "evidence": sentence,
                            "confidence": 0.80,
                            "status": "pending",
                            "fingerprint": fp,
                            "createdAt": now_iso(),
                        })
                        existing_fingerprints.add(fp)
                        created += 1

    return {"created": created, "chapterId": chapter_id}
