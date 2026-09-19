"""Best-fit and related-role recommendation layer for ATSLens V4."""

from __future__ import annotations

from services.role_profiles import get_role_profiles
from services.skill_taxonomy import canonicalize_skills


def _profile_skill_set(profile: dict) -> set[str]:
    return set(canonicalize_skills(
        profile.get("core", []) + profile.get("preferred", []) + profile.get("optional", [])
    ))


def _role_similarity(role_a: str, role_b: str) -> float:
    profiles = get_role_profiles()
    a = _profile_skill_set(profiles[role_a])
    b = _profile_skill_set(profiles[role_b])
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def build_recommendations(role_results: list[dict], top_n: int = 5) -> dict:
    ranked = role_results[:]
    if not ranked:
        return {"best_fit_role": None, "top_roles": [], "related_roles": []}

    best = ranked[0]
    best_name = best["role"]
    related = []
    for item in ranked[1:]:
        similarity = _role_similarity(best_name, item["role"])
        related.append({
            "role": item["role"],
            "role_fit_score": item["role_fit_score"],
            "career_readiness_score": item["career_readiness_score"],
            "profile_similarity_to_best": round(similarity * 100, 1),
        })
    related.sort(
        key=lambda x: (x["profile_similarity_to_best"], x["role_fit_score"]),
        reverse=True,
    )

    return {
        "best_fit_role": {
            "role": best_name,
            "role_fit_score": best["role_fit_score"],
            "career_readiness_score": best["career_readiness_score"],
            "skill_coverage_score": best["skill_coverage_score"],
            "evidence_strength_score": best["evidence_strength_score"],
        },
        "top_roles": [
            {
                "rank": idx + 1,
                "role": item["role"],
                "role_fit_score": item["role_fit_score"],
                "career_readiness_score": item["career_readiness_score"],
                "critical_gap_count": len(item.get("critical_missing_skills", [])),
            }
            for idx, item in enumerate(ranked[:top_n])
        ],
        "related_roles": related[:top_n],
        "ranking_note": "Ranking is based on transparent role-profile fit and resume evidence, not predicted hiring outcomes.",
    }
