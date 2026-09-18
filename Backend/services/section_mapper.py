import re
from collections import OrderedDict

SECTION_ALIASES = OrderedDict({
    "summary": {
        "summary", "professional summary", "profile", "career objective",
        "objective", "about me"
    },
    "skills": {
        "skills", "technical skills", "core skills", "key skills",
        "competencies", "core competencies", "technologies", "tech stack"
    },
    "experience": {
        "experience", "work experience", "professional experience",
        "employment", "employment history", "work history",
        "internship", "internships", "internship experience",
        "industrial training", "training experience", "professional internship"
    },
    "projects": {
        "projects", "academic projects", "personal projects", "key projects",
        "project experience"
    },
    "education": {
        "education", "academic background", "academic qualifications",
        "qualifications", "education details"
    },
    "certifications": {
        "certifications", "certificates", "licenses and certifications",
        "courses", "training"
    },
    "achievements": {
        "achievements", "awards", "honors", "accomplishments"
    },
    "publications": {
        "publications", "research", "research work"
    },
})


def _normalize_heading(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"^[\-•|:]+|[\-•|:]+$", "", value).strip()
    value = re.sub(r"\s+", " ", value)
    return value


def _detect_heading(line: str):
    normalized = _normalize_heading(line)
    if not normalized or len(normalized) > 70:
        return None

    normalized = normalized.rstrip(":")

    for section, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return section

    return None


def map_sections(text: str) -> dict:
    """Map resume text into canonical sections without discarding raw content."""
    raw_text = text or ""
    lines = [line.strip() for line in raw_text.splitlines()]

    sections = OrderedDict()
    current = "other"
    sections[current] = []

    for line in lines:
        if not line:
            continue

        heading = _detect_heading(line)
        if heading:
            current = heading
            sections.setdefault(current, [])
            continue

        sections.setdefault(current, []).append(line)

    mapped = {
        name: "\n".join(content).strip()
        for name, content in sections.items()
        if "\n".join(content).strip()
    }

    detected = [name for name in mapped if name != "other"]

    return {
        "sections": mapped,
        "detected_sections": detected,
        "section_count": len(detected),
    }
