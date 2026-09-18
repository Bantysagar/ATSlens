import re
from analyzer import clean_text, extract_skills
from services.skill_taxonomy import aliases_for, canonicalize_skill

MUST_MARKERS = (
    "must have", "must know", "required", "mandatory", "minimum qualification",
    "minimum qualifications", "you must", "need to have", "should have",
    "proficiency in", "proficient in", "strong knowledge of",
    "strong experience in", "strong foundation in", "essential",
)

PREFERRED_MARKERS = (
    "preferred", "preferred qualifications", "preferably", "desired",
    "desirable", "familiarity with", "exposure to",
)

BONUS_MARKERS = (
    "bonus", "nice to have", "good to have", "plus", "added advantage",
    "additional advantage", "would be a plus", "is a plus", "as a plus",
    "optional", "advantageous",
)

SECTION_PRIORITY = {
    "requirements": "must",
    "required skills": "must",
    "required technical skills": "must",
    "required qualifications": "must",
    "minimum qualifications": "must",
    "must have": "must",
    "qualifications": "must",
    "preferred qualifications": "preferred",
    "preferred skills": "preferred",
    "preferred technical skills": "preferred",
    "desired skills": "preferred",
    "good to have": "bonus",
    "nice to have": "bonus",
    "bonus": "bonus",
    "optional skills": "bonus",
}

PRIORITY_RANK = {"bonus": 1, "preferred": 2, "must": 3}

# Headings that start a new JD section but do not themselves imply priority.
# They reset the previous section priority so, for example, a Required
# Qualifications heading does not leak into Key Responsibilities.
NEUTRAL_SECTION_HEADINGS = (
    "position overview", "job summary", "role overview", "about the role",
    "key responsibilities", "responsibilities", "role responsibilities",
    "what you will do", "what you'll do", "job duties", "duties",
)

# Terms that strongly suggest an education eligibility statement rather than
# evidence that a candidate must possess the named concept as a practical skill.
EDUCATION_MARKERS = (
    "bachelor", "bachelor's", "bachelors", "master", "master's", "masters",
    "degree", "academic qualification", "educational qualification",
    "related discipline", "related field", "technical discipline",
)

CAPABILITY_MARKERS = (
    "knowledge of", "understanding of", "experience with", "experience in",
    "proficiency in", "proficient in", "familiarity with", "exposure to",
    "hands-on", "hands on", "ability to", "skills in", "foundation in",
    "develop", "build", "implement", "design", "deploy", "train", "evaluate",
)


def _normalize(value: str) -> str:
    value = (value or "").lower().strip()
    value = re.sub(r"\s+", " ", value)
    return value


def _heading_priority(segment: str):
    normalized = _normalize(segment)
    for heading in sorted(SECTION_PRIORITY, key=len, reverse=True):
        priority = SECTION_PRIORITY[heading]
        if (
            normalized == heading
            or normalized.startswith(heading + ":")
            or normalized.startswith(heading + " -")
            or normalized.startswith(heading + " ")
        ):
            return priority
    return None


def _is_neutral_heading(segment: str) -> bool:
    normalized = _normalize(segment)
    return any(
        normalized == heading
        or normalized.startswith(heading + ":")
        or normalized.startswith(heading + " -")
        or normalized.startswith(heading + " ")
        for heading in NEUTRAL_SECTION_HEADINGS
    )


def _marker_priority(segment: str):
    normalized = _normalize(segment)
    # Bonus/preferred are checked first so a phrase such as "preferred ... plus"
    # does not get upgraded to mandatory by a weaker marker elsewhere.
    if any(marker in normalized for marker in BONUS_MARKERS):
        return "bonus"
    if any(marker in normalized for marker in PREFERRED_MARKERS):
        return "preferred"
    if any(marker in normalized for marker in MUST_MARKERS):
        return "must"
    return None


def _prepare_segments(job_description: str) -> list[str]:
    text = job_description or ""
    text = re.sub(r"[•●▪◦]", "\n", text)

    # Help sentence splitting when a JD was pasted as one long line.
    for heading in sorted(SECTION_PRIORITY, key=len, reverse=True):
        text = re.sub(
            rf"(?i)(?<!\n)\b({re.escape(heading)})\s*:",
            r"\n\1:",
            text,
        )

    segments = []
    for line in text.splitlines():
        line = line.strip(" -\t")
        if not line:
            continue
        parts = re.split(r"(?<=[.!?;])\s+", line)
        for part in parts:
            part = part.strip(" -\t")
            if part:
                segments.append(part)
    return segments


def _segment_mentions_skill(segment: str, skill: str) -> bool:
    normalized_segment = clean_text(segment)
    for alias in aliases_for(skill):
        normalized_alias = clean_text(alias)
        if not normalized_alias:
            continue
        pattern = re.compile(
            r"(?<![a-z0-9])" + re.escape(normalized_alias) + r"(?![a-z0-9])",
            re.I,
        )
        if pattern.search(normalized_segment):
            return True
    return False


def _is_education_only_context(segment: str) -> bool:
    normalized = _normalize(segment)
    has_education = any(marker in normalized for marker in EDUCATION_MARKERS)
    has_capability = any(marker in normalized for marker in CAPABILITY_MARKERS)
    return has_education and not has_capability


def classify_requirements(job_description: str) -> dict:
    """Classify canonical JD skills with local evidence and separate education-only fields."""
    jd = job_description or ""
    raw_skills = extract_skills(clean_text(jd))
    segments = _prepare_segments(jd)

    contextual_segments = []
    active_priority = None
    for segment in segments:
        heading_priority = _heading_priority(segment)
        if heading_priority:
            active_priority = heading_priority
        elif _is_neutral_heading(segment):
            active_priority = None
        marker_priority = _marker_priority(segment)
        contextual_segments.append(
            (segment, marker_priority or heading_priority or active_priority)
        )

    # Deduplicate aliases before scoring. Example:
    # LLM + Large Language Models -> one canonical requirement.
    canonical_skills = []
    seen = set()
    for skill in raw_skills:
        canonical = canonicalize_skill(skill)
        if canonical not in seen:
            seen.add(canonical)
            canonical_skills.append(canonical)

    requirements = []
    qualifications = []

    for skill in canonical_skills:
        skill_evidence = []
        qualification_evidence = []
        detected_priorities = []

        for segment, context_priority in contextual_segments:
            if not _segment_mentions_skill(segment, skill):
                continue

            if _is_education_only_context(segment):
                qualification_evidence.append(segment[:260])
                continue

            skill_evidence.append(segment[:260])
            local_priority = _marker_priority(segment) or context_priority
            if local_priority:
                detected_priorities.append(local_priority)

        # If the concept appears only as an accepted degree/education field,
        # keep it out of skill coverage and expose it separately.
        if qualification_evidence and not skill_evidence:
            qualifications.append({
                "skill": skill,
                "type": "education-field",
                "evidence": qualification_evidence[:3],
                "classification_basis": "education-context",
            })
            continue

        if detected_priorities:
            priority = max(
                detected_priorities,
                key=lambda value: PRIORITY_RANK.get(value, 0),
            )
            basis = "local-context"
        else:
            priority = "preferred"
            basis = "conservative-default"

        requirements.append({
            "skill": skill,
            "aliases": aliases_for(skill),
            "priority": priority,
            "evidence": skill_evidence[:3],
            "classification_basis": basis,
        })

    counts = {
        "must": sum(1 for item in requirements if item["priority"] == "must"),
        "preferred": sum(1 for item in requirements if item["priority"] == "preferred"),
        "bonus": sum(1 for item in requirements if item["priority"] == "bonus"),
    }

    return {
        "requirements": requirements,
        "counts": counts,
        "extracted_skill_count": len(requirements),
        "qualifications": qualifications,
        "qualification_count": len(qualifications),
        "canonicalization": "deterministic-alias-taxonomy-v1",
    }
