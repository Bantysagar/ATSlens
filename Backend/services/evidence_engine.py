"""Evidence localization, recency, and documentation-strength analysis."""

from __future__ import annotations

import re

from services.proficiency_engine import evidence_signal
from services.skill_recency import recency_from_text
from services.skill_taxonomy import aliases_for


SECTION_WEIGHT = {
    "experience": 1.00,
    "projects": 0.92,
    "certifications": 0.76,
    "skills": 0.62,
    "summary": 0.52,
    "education": 0.42,
    "other": 0.35,
    None: 0.25,
}


def _frequency(text: str, skill: str) -> int:
    lower = (text or "").lower()
    total = 0
    for alias in aliases_for(skill):
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(alias.lower()) + r"(?![a-z0-9])")
        total += len(pattern.findall(lower))
    return total


def _best_exact_snippet(skill: str, section_map: dict, preferred_section: str | None) -> tuple[str | None, str | None]:
    sections = section_map.get("sections") or {}
    order = []
    if preferred_section and preferred_section in sections:
        order.append(preferred_section)
    order.extend([name for name in sections if name not in order])

    for section in order:
        text = sections.get(section, "")
        for line in re.split(r"\n+|(?<=[.!?;])\s+", text):
            low = line.lower()
            if any(alias.lower() in low for alias in aliases_for(skill)):
                return section, re.sub(r"\s+", " ", line).strip()[:420]
    return None, None


def build_evidence_profile(resume_text: str, section_map: dict, hybrid_result: dict) -> dict:
    items = []
    for match in hybrid_result.get("matches", []):
        skill = match["skill"]
        section = match.get("evidence_section")
        snippet = match.get("evidence")
        if match.get("matched") and not snippet:
            found_section, found_snippet = _best_exact_snippet(skill, section_map, section)
            section = found_section or section
            snippet = found_snippet

        freq = _frequency(resume_text, skill)
        section_text = (section_map.get("sections") or {}).get(section, "") if section else ""
        recency = recency_from_text(f"{snippet or ''} {section_text[:900]}")
        strength = evidence_signal(section, snippet, match.get("match_score", 0.0), freq)

        evidence_quality = (
            0.50 * SECTION_WEIGHT.get(section, 0.25)
            + 0.25 * recency["recency_score"]
            + 0.25 * strength["evidence_signal"]
        ) if match.get("matched") else 0.0

        items.append({
            "skill": skill,
            "matched": match.get("matched", False),
            "match_type": match.get("match_type", "none"),
            "source_section": section,
            "evidence": snippet,
            "mention_frequency": freq,
            "recency": recency,
            "documentation_strength": strength,
            "evidence_quality": round(evidence_quality, 4),
            "evidence_quality_percent": round(evidence_quality * 100, 1),
        })

    matched = [item for item in items if item["matched"]]
    mean_quality = (
        sum(item["evidence_quality"] for item in matched) / len(matched)
        if matched else 0.0
    )
    return {
        "skills": items,
        "matched_evidence_count": len(matched),
        "mean_evidence_quality": round(mean_quality * 100, 1),
        "method": "localized-source-recency-documentation-v1",
    }
