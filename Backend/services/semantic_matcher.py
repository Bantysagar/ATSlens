"""Semantic requirement-to-resume matching for ATSLens V3.1.

Sentence-Transformers is used when available, with TF-IDF as a lightweight
fallback. V3.1 adds conservative guards so one named technology is not treated
as proof of another merely because their surrounding descriptions are similar.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analyzer import clean_text


DEFAULT_MODEL = os.getenv(
    "ATSLENS_SEMANTIC_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

SECTION_WEIGHT = {
    "experience": 1.00,
    "projects": 0.95,
    "certifications": 0.78,
    "skills": 0.70,
    "summary": 0.62,
    "education": 0.45,
    "other": 0.35,
}

# Named tools/frameworks/platforms should normally require deterministic
# evidence. Semantic similarity between FastAPI and Flask, for example, is not
# evidence that the candidate knows Flask.
STRICT_ENTITY_SKILLS = {
    "aws", "azure", "chromadb", "docker", "faiss", "fastapi", "flask",
    "git", "github", "hugging face", "langchain", "matplotlib", "mysql",
    "numpy", "opencv", "pandas", "postgresql", "pytorch", "scikit-learn",
    "tensorflow", "transformers",
}

STOP_TOKENS = {
    "and", "or", "the", "a", "an", "of", "for", "to", "with", "in",
    "on", "using", "based", "skill", "skills", "knowledge", "experience",
}


@lru_cache(maxsize=1)
def _load_sentence_transformer():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(DEFAULT_MODEL)
    except Exception:
        return None


def semantic_backend_status() -> dict:
    model = _load_sentence_transformer()
    return {
        "available": model is not None,
        "backend": "sentence-transformers" if model is not None else "tfidf-fallback",
        "model": DEFAULT_MODEL if model is not None else "tfidf-ngram",
    }


def _split_chunks(section_text: str, max_chars: int = 360) -> list[str]:
    text = (section_text or "").strip()
    if not text:
        return []

    raw_parts = re.split(r"\n+|(?<=[.!?;])\s+", text)
    chunks: list[str] = []
    buffer = ""

    for raw in raw_parts:
        part = re.sub(r"\s+", " ", raw).strip(" -\t")
        if not part:
            continue
        if len(part) > max_chars:
            words = part.split()
            temp = ""
            for word in words:
                candidate = f"{temp} {word}".strip()
                if len(candidate) > max_chars and temp:
                    chunks.append(temp)
                    temp = word
                else:
                    temp = candidate
            if temp:
                chunks.append(temp)
            continue

        candidate = f"{buffer} {part}".strip()
        if len(candidate) > max_chars and buffer:
            chunks.append(buffer)
            buffer = part
        else:
            buffer = candidate

    if buffer:
        chunks.append(buffer)

    return chunks[:120]


def build_resume_chunks(section_map: dict) -> list[dict]:
    chunks: list[dict] = []
    for section_name, text in (section_map.get("sections") or {}).items():
        for chunk in _split_chunks(text):
            if len(clean_text(chunk).split()) < 3:
                continue
            chunks.append({
                "section": section_name,
                "text": chunk,
                "section_weight": SECTION_WEIGHT.get(section_name, 0.35),
            })
    return chunks


def _query_for_requirement(requirement: dict) -> str:
    skill = requirement.get("skill", "")
    evidence = requirement.get("evidence") or []
    context = re.sub(r"\s+", " ", str(evidence[0])).strip()[:180] if evidence else ""
    if context:
        return f"Required capability: {skill}. Context: {context}"
    return f"Required capability: {skill}."


def _skill_tokens(skill: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9+#.-]+", clean_text(skill or ""))
    return {token for token in tokens if len(token) > 2 and token not in STOP_TOKENS}


def _has_lexical_anchor(skill: str, evidence: str) -> bool:
    tokens = _skill_tokens(skill)
    if not tokens:
        return False
    evidence_tokens = set(re.findall(r"[a-z0-9+#.-]+", clean_text(evidence or "")))
    return bool(tokens & evidence_tokens)


def _st_scores(query: str, texts: Iterable[str]) -> list[float] | None:
    model = _load_sentence_transformer()
    if model is None:
        return None
    text_list = list(texts)
    if not text_list:
        return []
    try:
        vectors = model.encode(
            [query] + text_list,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        query_vec = vectors[0]
        return [float(query_vec @ item) for item in vectors[1:]]
    except Exception:
        return None


def _tfidf_scores(query: str, texts: Iterable[str]) -> list[float]:
    text_list = list(texts)
    if not text_list:
        return []
    corpus = [query] + text_list
    try:
        matrix = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            min_df=1,
            sublinear_tf=True,
        ).fit_transform(corpus)
        sims = cosine_similarity(matrix[0:1], matrix[1:]).ravel()
        return [float(x) for x in sims]
    except ValueError:
        return [0.0] * len(text_list)


def _thresholds(method: str, lexical_anchor: bool) -> tuple[float, float]:
    if method == "sentence-transformers":
        # Without a lexical anchor, require substantially stronger semantic
        # evidence. This is what prevents weak contextual false positives such
        # as Prompt Engineering <- generic AI/ML skills text.
        return (0.62, 0.76) if lexical_anchor else (0.72, 0.82)
    return (0.20, 0.36) if lexical_anchor else (0.34, 0.48)


def semantic_match_requirements(
    requirements: list,
    section_map: dict,
    exact_match_result: dict,
) -> dict:
    """Find conservative semantic evidence for non-deterministic requirements."""
    chunks = build_resume_chunks(section_map)
    exact_by_skill = {
        item.get("skill"): item
        for item in (exact_match_result.get("matches") or [])
    }

    results = []
    backend = semantic_backend_status()

    if not chunks:
        return {
            "backend": backend,
            "matches": [],
            "semantic_match_count": 0,
            "threshold_note": "No resume chunks available for semantic comparison.",
        }

    chunk_texts = [item["text"] for item in chunks]

    for requirement in requirements:
        skill = requirement.get("skill", "")
        exact_item = exact_by_skill.get(skill, {})
        if exact_item.get("exact_match"):
            results.append({
                "skill": skill,
                "status": "skipped-deterministic-match",
                "semantic_match": False,
                "similarity": 1.0,
                "section": (exact_item.get("evidence_sections") or [None])[0],
                "evidence": None,
                "method": "deterministic",
            })
            continue

        if skill in STRICT_ENTITY_SKILLS:
            results.append({
                "skill": skill,
                "status": "requires-explicit-evidence",
                "semantic_match": False,
                "similarity": 0.0,
                "similarity_percent": 0.0,
                "strength": "none",
                "section": None,
                "evidence": None,
                "method": "strict-entity-guard",
                "threshold": None,
            })
            continue

        query = _query_for_requirement(requirement)
        scores = _st_scores(query, chunk_texts)
        method = "sentence-transformers"
        if scores is None:
            scores = _tfidf_scores(query, chunk_texts)
            method = "tfidf-fallback"

        if not scores:
            results.append({
                "skill": skill,
                "status": "missing",
                "semantic_match": False,
                "similarity": 0.0,
                "section": None,
                "evidence": None,
                "method": method,
            })
            continue

        weighted = [
            max(0.0, min(1.0, score)) * (0.82 + 0.18 * chunk["section_weight"])
            for score, chunk in zip(scores, chunks)
        ]
        best_index = max(range(len(weighted)), key=weighted.__getitem__)
        best_score = float(weighted[best_index])
        best_chunk = chunks[best_index]
        lexical_anchor = _has_lexical_anchor(skill, best_chunk["text"])
        match_threshold, strong_threshold = _thresholds(method, lexical_anchor)
        matched = best_score >= match_threshold

        results.append({
            "skill": skill,
            "status": "semantic" if matched else "missing",
            "semantic_match": matched,
            "similarity": round(best_score, 4),
            "similarity_percent": round(best_score * 100, 1),
            "strength": (
                "strong" if best_score >= strong_threshold
                else "moderate" if matched
                else "weak"
            ),
            "lexical_anchor": lexical_anchor,
            "section": best_chunk["section"] if matched else None,
            "evidence": best_chunk["text"][:420] if matched else None,
            "method": method,
            "threshold": match_threshold,
        })

    return {
        "backend": backend,
        "matches": results,
        "semantic_match_count": sum(1 for item in results if item.get("semantic_match")),
        "threshold_note": (
            "V3.1 uses conservative, skill-aware semantic thresholds. Named tools require explicit evidence; "
            "thresholds still require labeled-dataset calibration before research claims."
        ),
    }
