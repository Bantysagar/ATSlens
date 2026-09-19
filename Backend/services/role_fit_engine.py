"""Evidence-aware multi-role fit scoring for Career Intelligence V4.2.

V4.2 keeps exact skill matches separate from conservative, explicit related
skill evidence (for example FastAPI -> API, ChromaDB -> vector database).
Related evidence receives partial credit and is never relabeled as an exact
match.
"""

from __future__ import annotations

import re

from analyzer import clean_text, extract_skills
from services.related_skill_evidence import best_related_match
from services.role_profiles import get_role_profiles
from services.section_mapper import map_sections
from services.skill_taxonomy import aliases_for, canonicalize_skills


SECTION_WEIGHT = {
    "experience": 1.00,
    "projects": 0.92,
    "certifications": 0.76,
    "skills": 0.64,
    "summary": 0.54,
    "education": 0.42,
    "achievements": 0.72,
    "publications": 0.72,
    "other": 0.35,
}

CATEGORY_WEIGHT = {"core": 0.60, "preferred": 0.30, "optional": 0.10}


def _contains_skill(text: str, skill: str) -> bool:
    normalized = clean_text(text or "")
    for alias in aliases_for(skill):
        a = clean_text(alias)
        if not a:
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", normalized):
            return True
    return False


def _skill_evidence(skill: str, sections: dict) -> dict:
    found = []
    for section, text in (sections or {}).items():
        if _contains_skill(text, skill):
            found.append(section)
    found.sort(key=lambda s: SECTION_WEIGHT.get(s, 0.3), reverse=True)
    best = found[0] if found else None
    return {
        "sections": found,
        "best_section": best,
        "evidence_weight": round(SECTION_WEIGHT.get(best, 0.0), 3) if best else 0.0,
    }


def _resolve_skill_match(skill: str, resume_skills: set[str], sections: dict) -> dict:
    """Resolve exact first, then conservative related evidence."""
    if skill in resume_skills:
        evidence = _skill_evidence(skill, sections)
        return {
            "matched": True,
            "match_type": "exact",
            "match_strength": 1.0,
            "related_from": None,
            **evidence,
        }

    related = best_related_match(skill, resume_skills)
    if related:
        source_skill = related["source_skill"]
        evidence = _skill_evidence(source_skill, sections)
        return {
            "matched": True,
            "match_type": "related",
            "match_strength": related["strength"],
            "related_from": source_skill,
            **evidence,
        }

    return {
        "matched": False,
        "match_type": "none",
        "match_strength": 0.0,
        "related_from": None,
        "sections": [],
        "best_section": None,
        "evidence_weight": 0.0,
    }


def _category_stats(profile_skills: list[str], resume_skills: set[str], sections: dict) -> dict:
    total = len(profile_skills)
    rows = []
    matched = 0
    exact_count = 0
    related_count = 0
    coverage_credit = 0.0
    evidence_credit = 0.0
    evidence_denominator = 0.0

    for skill in profile_skills:
        resolution = _resolve_skill_match(skill, resume_skills, sections)
        if resolution["matched"]:
            matched += 1
            if resolution["match_type"] == "exact":
                exact_count += 1
            elif resolution["match_type"] == "related":
                related_count += 1

            strength = float(resolution["match_strength"])
            coverage_credit += strength
            # Evidence remains source-section grounded, while relation strength
            # discounts how strongly it supports the requested target skill.
            evidence_credit += resolution["evidence_weight"] * strength
            evidence_denominator += strength

        rows.append({"skill": skill, **resolution})

    coverage = coverage_credit / total if total else 0.0
    evidence_quality = evidence_credit / evidence_denominator if evidence_denominator else 0.0
    return {
        "total": total,
        "matched": matched,
        "exact_matches": exact_count,
        "related_matches": related_count,
        "coverage_credit": round(coverage_credit, 3),
        "coverage": round(coverage, 4),
        "coverage_percent": round(coverage * 100, 1),
        "evidence_quality": round(evidence_quality, 4),
        "evidence_quality_percent": round(evidence_quality * 100, 1),
        "skills": rows,
    }


def score_role_fit(resume_text: str, role_name: str, profile: dict, section_map: dict | None = None) -> dict:
    section_map = section_map or map_sections(resume_text)
    sections = section_map.get("sections", {})
    resume_skills = set(canonicalize_skills(extract_skills(clean_text(resume_text or ""))))

    stats = {
        category: _category_stats(profile.get(category, []), resume_skills, sections)
        for category in ("core", "preferred", "optional")
    }

    weighted_coverage = sum(
        CATEGORY_WEIGHT[c] * stats[c]["coverage"] for c in CATEGORY_WEIGHT
    )

    matched_rows = [
        row
        for c in ("core", "preferred", "optional")
        for row in stats[c]["skills"]
        if row["matched"]
    ]

    # Evidence quality is also relation-strength aware so a related match never
    # contributes exactly the same as an explicit target skill mention.
    evidence_numerator = sum(
        row["evidence_weight"] * row.get("match_strength", 1.0)
        for row in matched_rows
    )
    evidence_denominator = sum(
        row.get("match_strength", 1.0) for row in matched_rows
    )
    evidence_quality = (
        evidence_numerator / evidence_denominator if evidence_denominator else 0.0
    )

    strong_evidence_credit = sum(
        row.get("match_strength", 1.0)
        for row in matched_rows
        if row["best_section"] in ("experience", "projects")
    )
    total_match_credit = sum(
        row.get("match_strength", 1.0) for row in matched_rows
    )
    strong_evidence_ratio = (
        strong_evidence_credit / total_match_credit if total_match_credit else 0.0
    )

    # Role Fit = skill coverage + actual resume evidence. Not a hiring probability.
    role_fit = 0.72 * weighted_coverage + 0.28 * evidence_quality
    # Readiness gives extra weight to project/experience evidence.
    readiness = 0.58 * weighted_coverage + 0.24 * evidence_quality + 0.18 * strong_evidence_ratio

    critical_missing = [row["skill"] for row in stats["core"]["skills"] if not row["matched"]]
    preferred_missing = [row["skill"] for row in stats["preferred"]["skills"] if not row["matched"]]
    related_evidence = [
        {
            "target_skill": row["skill"],
            "related_from": row["related_from"],
            "match_strength": row["match_strength"],
            "best_section": row["best_section"],
        }
        for c in ("core", "preferred", "optional")
        for row in stats[c]["skills"]
        if row.get("match_type") == "related"
    ]
    strongest = sorted(
        [row for row in matched_rows],
        key=lambda r: (
            r["evidence_weight"] * r.get("match_strength", 1.0),
            r["skill"],
        ),
        reverse=True,
    )[:6]

    return {
        "role": role_name,
        "family": profile.get("family"),
        "role_fit_score": round(role_fit * 100, 1),
        "career_readiness_score": round(readiness * 100, 1),
        "skill_coverage_score": round(weighted_coverage * 100, 1),
        "evidence_strength_score": round(evidence_quality * 100, 1),
        "experience_project_evidence_score": round(strong_evidence_ratio * 100, 1),
        "coverage": stats,
        "critical_missing_skills": critical_missing,
        "preferred_missing_skills": preferred_missing,
        "related_evidence": related_evidence,
        "strongest_evidence": strongest,
        "score_scope": "Role-fit/readiness decision-support score; not a hiring or selection probability.",
    }


def analyze_all_roles(resume_text: str) -> dict:
    profiles = get_role_profiles()
    section_map = map_sections(resume_text)
    results = [
        score_role_fit(resume_text, role, profile, section_map)
        for role, profile in profiles.items()
    ]
    results.sort(
        key=lambda item: (item["role_fit_score"], item["career_readiness_score"]),
        reverse=True,
    )
    return {
        "roles": results,
        "detected_sections": section_map.get("detected_sections", []),
        "role_count": len(results),
        "method": "evidence-aware-multi-role-fit-v2-related-evidence",
    }
