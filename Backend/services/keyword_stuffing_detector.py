"""Conservative keyword-stuffing heuristics."""

from __future__ import annotations

import re

from analyzer import extract_skills, clean_text
from services.skill_taxonomy import aliases_for, canonicalize_skills


def _count_aliases(text: str, skill: str) -> int:
    lower = (text or "").lower()
    total = 0
    for alias in aliases_for(skill):
        total += len(re.findall(r"(?<![a-z0-9])" + re.escape(alias.lower()) + r"(?![a-z0-9])", lower))
    return total


def detect_keyword_stuffing(resume_text: str, section_map: dict) -> dict:
    skills = canonicalize_skills(extract_skills(clean_text(resume_text or "")))
    sections = section_map.get("sections") or {}
    suspicious = []

    for skill in skills:
        total = _count_aliases(resume_text, skill)
        exp_proj = _count_aliases(sections.get("experience", ""), skill) + _count_aliases(sections.get("projects", ""), skill)
        list_like = _count_aliases(sections.get("skills", ""), skill) + _count_aliases(sections.get("summary", ""), skill)
        if total >= 6 and exp_proj == 0 and list_like >= 4:
            suspicious.append({
                "skill": skill,
                "mentions": total,
                "experience_project_mentions": exp_proj,
                "reason": "High repetition without project/experience evidence.",
            })

    word_count = max(len((resume_text or "").split()), 1)
    total_skill_mentions = sum(_count_aliases(resume_text, skill) for skill in skills)
    density = total_skill_mentions / word_count
    evidence_text = f"{sections.get('experience', '')} {sections.get('projects', '')}"
    evidence_mentions = sum(_count_aliases(evidence_text, skill) for skill in skills)
    evidence_ratio = evidence_mentions / max(total_skill_mentions, 1)
    density_flag = (
        density > 0.18
        and total_skill_mentions >= 35
        and evidence_ratio < 0.20
    )

    risk = min(100, len(suspicious) * 18 + (25 if density_flag else 0))
    return {
        "flagged": bool(suspicious or density_flag),
        "risk_score": risk,
        "suspicious_skills": suspicious,
        "skill_mention_density": round(density, 4),
        "density_flag": density_flag,
        "experience_project_evidence_ratio": round(evidence_ratio, 4),
        "method": "conservative-keyword-stuffing-heuristic-v1",
    }
