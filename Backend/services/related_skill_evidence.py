"""Conservative skill-relation rules for ATSLens Career Intelligence V4.2.

Relations are directional: a specific resume skill may provide partial evidence
for a broader target capability. They are intentionally not treated as exact
aliases and therefore receive a score below 1.0.
"""

from __future__ import annotations

from services.skill_taxonomy import canonicalize_skill


# target_skill -> {resume_skill: relation_strength}
# Keep this map small, explicit, and technically defensible. Do not add broad
# semantic guesses here; learned/embedding relations belong in a separately
# evaluated research layer.
RELATED_SKILL_EVIDENCE = {
    "api": {
        "rest api": 0.95,
        "fastapi": 0.90,
    },
    "rest api": {
        "fastapi": 0.88,
    },
    "vector database": {
        "chromadb": 0.96,
        "faiss": 0.90,
    },
    "database": {
        "postgresql": 0.92,
        "mysql": 0.92,
        "mongodb": 0.88,
    },
    "cloud": {
        "aws": 0.92,
        "azure": 0.92,
        "gcp": 0.92,
    },
    "git": {
        "github": 0.78,
    },
    "data visualization": {
        "matplotlib": 0.92,
        "power bi": 0.90,
        "tableau": 0.90,
    },
    "dashboard": {
        "power bi": 0.88,
        "tableau": 0.88,
    },
}


def related_sources_for(target_skill: str) -> dict[str, float]:
    """Return canonical related-source skills and their strengths."""
    target = canonicalize_skill(target_skill)
    raw = RELATED_SKILL_EVIDENCE.get(target, {})
    return {
        canonicalize_skill(source): float(strength)
        for source, strength in raw.items()
    }


def best_related_match(target_skill: str, resume_skills: set[str]) -> dict | None:
    """Return the strongest explicit related-skill match, if one exists."""
    candidates = []
    for source, strength in related_sources_for(target_skill).items():
        if source in resume_skills:
            candidates.append((source, strength))

    if not candidates:
        return None

    source, strength = max(candidates, key=lambda item: (item[1], item[0]))
    return {
        "source_skill": source,
        "strength": round(float(strength), 3),
    }
