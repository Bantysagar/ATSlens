from analyzer import clean_text, contains_phrase, extract_skills
from services.skill_taxonomy import aliases_for, canonicalize_skill, canonicalize_skills

SECTION_EVIDENCE_WEIGHT = {
    "experience": 1.00,
    "projects": 0.90,
    "certifications": 0.80,
    "skills": 0.65,
    "summary": 0.50,
    "education": 0.40,
    "other": 0.35,
    "achievements": 0.70,
    "publications": 0.70,
}


def _strength_from_sections(sections: list) -> str:
    weights = [SECTION_EVIDENCE_WEIGHT.get(section, 0.30) for section in sections]
    best = max(weights, default=0.0)
    if best >= 0.90:
        return "strong"
    if best >= 0.60:
        return "medium"
    if best > 0:
        return "low"
    return "none"


def _matched_aliases(text: str, skill: str) -> list[str]:
    normalized_text = clean_text(text or "")
    found = []
    for alias in aliases_for(skill):
        if contains_phrase(normalized_text, alias):
            found.append(alias)
    return found


def match_requirements(resume_text: str, section_map: dict, requirements: list) -> dict:
    cleaned_resume = clean_text(resume_text or "")
    raw_resume_skills = extract_skills(cleaned_resume)
    resume_skills = set(canonicalize_skills(raw_resume_skills))
    sections = section_map.get("sections", {})

    matches = []

    for requirement in requirements:
        skill = canonicalize_skill(requirement["skill"])
        deterministic_match = skill in resume_skills
        whole_resume_aliases = _matched_aliases(resume_text, skill) if deterministic_match else []

        canonical_present = contains_phrase(cleaned_resume, skill) if deterministic_match else False
        alias_only = deterministic_match and not canonical_present and bool(whole_resume_aliases)

        evidence_sections = []
        evidence_terms = []
        if deterministic_match:
            for section_name, section_text in sections.items():
                matched_terms = _matched_aliases(section_text, skill)
                if matched_terms:
                    evidence_sections.append(section_name)
                    evidence_terms.extend(matched_terms)

        evidence_sections = sorted(
            set(evidence_sections),
            key=lambda name: SECTION_EVIDENCE_WEIGHT.get(name, 0.30),
            reverse=True,
        )
        evidence_terms = sorted(set(evidence_terms), key=lambda item: (-len(item), item))

        if not deterministic_match:
            status = "missing"
            match_type = "none"
        elif alias_only:
            status = "alias"
            match_type = "alias"
        else:
            status = "exact"
            match_type = "exact"

        matches.append({
            "skill": skill,
            "priority": requirement["priority"],
            "status": status,
            # Kept for backward compatibility with Phase-1 scoring.
            "exact_match": deterministic_match,
            "match_type": match_type,
            "matched_terms": evidence_terms,
            "evidence_sections": evidence_sections,
            "evidence_strength": _strength_from_sections(evidence_sections),
        })

    matched = [item for item in matches if item["exact_match"]]
    missing = [item for item in matches if not item["exact_match"]]

    return {
        "matches": matches,
        "matched_count": len(matched),
        "missing_count": len(missing),
        "matched_skills": [item["skill"] for item in matched],
        "missing_skills": [item["skill"] for item in missing],
        "exact_count": sum(1 for item in matched if item["match_type"] == "exact"),
        "alias_count": sum(1 for item in matched if item["match_type"] == "alias"),
    }
