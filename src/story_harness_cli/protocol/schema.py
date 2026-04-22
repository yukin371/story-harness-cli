from __future__ import annotations

from typing import Any, Dict


def default_project_state() -> Dict[str, Dict[str, Any]]:
    return {
        "project": {},
        "outline": {"chapters": [], "chapterDirections": [], "volumes": []},
        "entities": {"entities": [], "enrichmentProposals": []},
        "timeline": {"events": []},
        "branches": {"branches": []},
        "proposals": {"draftProposals": []},
        "reviews": {"changeRequests": []},
        "projection": {
            "snapshotProjections": [],
            "relationProjections": [],
            "sceneScopeProjections": [],
            "timelineProjections": [],
            "causalityProjections": [],
        },
        "context_lens": {"currentChapterId": None, "lenses": []},
        "projection_log": {"projectionChanges": []},
        "threads": {"threads": []},
        "structures": {"activeStructure": None, "mappings": []},
    }

