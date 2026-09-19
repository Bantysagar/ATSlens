"""Skill transferability analysis across role profiles."""

from __future__ import annotations

from analyzer import clean_text, extract_skills
from services.role_profiles import get_role_profiles
from services.skill_taxonomy import canonicalize_skills


def analyze_skill_transferability(resume_text: str) -> dict:
    resume_skills = set(canonicalize_skills(extract_skills(clean_text(resume_text or ""))))
    profiles = get_role_profiles()
    rows = []

    for skill in sorted(resume_skills):
        roles = []
        for role, profile in profiles.items():
            if skill in set(profile.get("core", []) + profile.get("preferred", []) + profile.get("optional", [])):
                roles.append(role)
        if roles:
            rows.append({
                "skill": skill,
                "applicable_role_count": len(roles),
                "applicable_roles": roles,
            })

    rows.sort(key=lambda x: (x["applicable_role_count"], x["skill"]), reverse=True)
    return {
        "skills": rows,
        "most_transferable": rows[:8],
        "method": "role-profile-skill-overlap-v1",
    }
