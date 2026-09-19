"""Transparent career-path suggestions from curated role families."""

from __future__ import annotations

from services.role_profiles import get_role_profiles


def build_career_path(best_role: str | None, candidate_type: str = "Fresher", experience_years: int = 0) -> dict:
    profiles = get_role_profiles()
    if not best_role or best_role not in profiles:
        return {"current_stage": None, "path": [], "note": "No best-fit role available."}

    profile = profiles[best_role]
    if experience_years <= 1 or str(candidate_type).lower() == "fresher":
        current_stage = "Entry-level / Fresher"
    elif experience_years <= 3:
        current_stage = "Early-career"
    else:
        current_stage = "Experienced"

    return {
        "current_stage": current_stage,
        "recommended_family": profile.get("family"),
        "path": profile.get("path", [best_role]),
        "note": "Career path is a skills-based progression suggestion, not a guaranteed promotion or hiring trajectory.",
    }
