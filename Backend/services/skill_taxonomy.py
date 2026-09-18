"""Shared deterministic skill taxonomy for ATSLens V2.

Phase 1.2 keeps aliases deterministic and transparent. Semantic similarity is
intentionally NOT performed here; that belongs to Phase 2.
"""

import re


CANONICAL_ALIASES = {
    "large language models": {
        "llm", "llms", "large language model", "large language models"
    },
    "natural language processing": {
        "nlp", "natural language processing"
    },
    "retrieval augmented generation": {
        "rag", "retrieval augmented generation",
        "retrieval-augmented generation"
    },
    "generative ai": {
        "genai", "gen ai", "generative ai", "generative artificial intelligence"
    },
    "scikit-learn": {
        "scikit-learn", "scikit learn", "sklearn"
    },
    "github": {"github", "git hub"},
    "fastapi": {"fastapi", "fast api"},
    "pytorch": {"pytorch", "py torch"},
    "tensorflow": {"tensorflow", "tensor flow"},
    "chromadb": {"chromadb", "chroma db"},
}


def _norm(value: str) -> str:
    value = (value or "").lower().strip()
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"\s+", " ", value)
    return value


_ALIAS_TO_CANONICAL = {}
for canonical, aliases in CANONICAL_ALIASES.items():
    _ALIAS_TO_CANONICAL[_norm(canonical)] = canonical
    for alias in aliases:
        _ALIAS_TO_CANONICAL[_norm(alias)] = canonical


def canonicalize_skill(skill: str) -> str:
    normalized = _norm(skill)
    return _ALIAS_TO_CANONICAL.get(normalized, normalized)


def aliases_for(skill: str) -> list[str]:
    canonical = canonicalize_skill(skill)
    values = set(CANONICAL_ALIASES.get(canonical, {canonical}))
    values.add(canonical)
    return sorted(values, key=lambda item: (-len(item), item))


def canonicalize_skills(skills) -> list[str]:
    return sorted({canonicalize_skill(skill) for skill in (skills or []) if skill})
