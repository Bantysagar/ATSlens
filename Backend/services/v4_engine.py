"""Orchestrator for ATSLens Career Intelligence V4."""

from __future__ import annotations

from services.career_gap_engine import build_gap_analysis
from services.career_path_engine import build_career_path
from services.career_recommender import build_recommendations
from services.role_fit_engine import analyze_all_roles
from services.skill_transfer_engine import analyze_skill_transferability


def analyze_career_intelligence_v4(
    resume_text: str,
    candidate_type: str = "Fresher",
    experience_years: int = 0,
    target_field: str = "AI/ML",
) -> dict:
    role_analysis = analyze_all_roles(resume_text)
    recommendations = build_recommendations(role_analysis["roles"])
    best_role = (recommendations.get("best_fit_role") or {}).get("role")

    return {
        "engine_version": "ATSLens-Career-Intelligence-V4",
        "logic_version": "V4.2-related-evidence",
        "research_status": "engineering-prototype-needs-role-dataset-calibration",
        "candidate_type": candidate_type,
        "experience_years": experience_years,
        "target_field": target_field,
        "best_fit": recommendations.get("best_fit_role"),
        "top_roles": recommendations.get("top_roles", []),
        "related_roles": recommendations.get("related_roles", []),
        "role_analysis": role_analysis["roles"],
        "skill_transferability": analyze_skill_transferability(resume_text),
        "gap_analysis": build_gap_analysis(role_analysis["roles"]),
        "career_path": build_career_path(best_role, candidate_type, experience_years),
        "detected_sections": role_analysis.get("detected_sections", []),
        "notes": [
            "Role Fit and Career Readiness are decision-support scores, not hiring-selection probabilities.",
            "Exact matches and conservative related-skill evidence are reported separately; related evidence receives partial credit.",
            "Role profiles and relation strengths are transparent engineering defaults and should be calibrated against labeled role/resume datasets before research claims.",
            "Best-fit ranking reflects the resume evidence supplied to ATSLens and can change as the resume changes.",
        ],
    }
