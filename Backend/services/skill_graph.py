"""Small transparent skill-relation graph used as a partial-match signal.

This graph is intentionally conservative. A related skill is never treated as
proof that the target skill is possessed; it only contributes a partial signal.
"""

from __future__ import annotations

from analyzer import clean_text, extract_skills
from services.skill_taxonomy import canonicalize_skill, canonicalize_skills


RELATIONS = {
    "deep learning": {
        "machine learning": 0.55,
        "pytorch": 0.90,
        "tensorflow": 0.90,
    },
    "model deployment": {
        "deployment": 0.95,
        "fastapi": 0.62,
        "flask": 0.62,
        "docker": 0.72,
    },
    "deployment": {
        "model deployment": 0.95,
        "fastapi": 0.55,
        "flask": 0.55,
        "docker": 0.65,
    },
    "cloud": {
        "aws": 0.90,
        "azure": 0.90,
        "gcp": 0.90,
    },
    "database": {
        "sql": 0.70,
        "mysql": 0.85,
        "postgresql": 0.85,
        "mongodb": 0.80,
    },
    "generative ai": {
        "large language models": 0.82,
        "retrieval augmented generation": 0.68,
        "prompt engineering": 0.58,
    },
    "retrieval augmented generation": {
        "large language models": 0.70,
        "embeddings": 0.82,
        "chromadb": 0.72,
        "vector database": 0.82,
    },
    "prompt engineering": {
        "generative ai": 0.62,
        "large language models": 0.60,
    },
    "aws": {"cloud": 0.72},
    "azure": {"cloud": 0.72},
    "pytorch": {"deep learning": 0.72},
    "tensorflow": {"deep learning": 0.72},
}


def related_skills(skill: str) -> dict[str, float]:
    canonical = canonicalize_skill(skill)
    return {
        canonicalize_skill(k): float(v)
        for k, v in RELATIONS.get(canonical, {}).items()
    }


def graph_signal(resume_text: str, requirement_skill: str) -> dict:
    resume_skills = set(canonicalize_skills(extract_skills(clean_text(resume_text or ""))))
    relations = related_skills(requirement_skill)
    found = [
        {"skill": skill, "relation_strength": strength}
        for skill, strength in relations.items()
        if skill in resume_skills
    ]
    found.sort(key=lambda item: item["relation_strength"], reverse=True)
    best = found[0]["relation_strength"] if found else 0.0
    return {
        "requirement": canonicalize_skill(requirement_skill),
        "related_evidence": found[:5],
        "graph_signal": round(best, 4),
        "graph_signal_percent": round(best * 100, 1),
        "note": "Related-skill evidence is partial context, not proof of the target skill.",
    }


def graph_match_requirements(resume_text: str, requirements: list) -> dict:
    matches = [graph_signal(resume_text, item.get("skill", "")) for item in requirements]
    return {
        "matches": matches,
        "related_signal_count": sum(1 for item in matches if item["graph_signal"] > 0),
        "graph_version": "transparent-skill-graph-v1",
    }
