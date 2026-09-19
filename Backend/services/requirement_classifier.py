import re
from analyzer import clean_text, extract_skills
from services.skill_taxonomy import aliases_for, canonicalize_skill


EXPLICIT_MUST_MARKERS = (
    "must have", "must know", "required", "mandatory", "essential",
    "minimum qualification", "minimum qualifications", "you must",
    "need to have",
)

CAPABILITY_MUST_MARKERS = (
    "should have", "proficiency in", "proficient in", "strong knowledge of",
    "strong experience in", "strong foundation in",
)

PREFERRED_MARKERS = (
    "preferred", "preferably", "desired", "desirable",
    "familiarity with", "exposure to",
)

BONUS_MARKERS = (
    "bonus", "nice to have", "good to have", "added advantage",
    "additional advantage", "would be a plus", "is a plus", "as a plus",
    "optional", "advantageous",
)

SECTION_PRIORITY = {
    "requirements": ("must", 3),
    "required skills": ("must", 3),
    "required technical skills": ("must", 3),
    "required qualifications": ("must", 3),
    "minimum qualifications": ("must", 3),
    "must have": ("must", 3),
    "core requirements": ("must", 3),
    "mandatory skills": ("must", 3),

    "preferred qualifications": ("preferred", 3),
    "preferred skills": ("preferred", 3),
    "preferred technical skills": ("preferred", 3),
    "preferred projects": ("preferred", 2),
    "preferred experience": ("preferred", 3),
    "desired skills": ("preferred", 3),
    "additional skills": ("preferred", 2),

    "good to have": ("bonus", 3),
    "nice to have": ("bonus", 3),
    "bonus": ("bonus", 3),
    "optional skills": ("bonus", 3),

    "typical technology stack": ("bonus", 2),
    "technology stack": ("bonus", 2),
    "tech stack": ("bonus", 2),
    "example technology stack": ("bonus", 2),
    "example stack": ("bonus", 2),
}

NEUTRAL_SECTION_HEADINGS = (
    "position overview", "job summary", "role overview", "about the role",
    "key responsibilities", "responsibilities", "role responsibilities",
    "what you will do", "what you'll do", "job duties", "duties",
    "experience", "education", "about you", "who you are",
    "soft skills", "projects", "project expectations", "preferred profile",
    "benefits", "about the company", "company overview",
)

SUBSECTION_HINTS = (
    "programming", "programming languages", "languages",
    "machine learning", "ml", "deep learning",
    "natural language processing", "nlp", "generative ai",
    "generative ai / llm", "large language models", "llm",
    "backend", "backend development", "api development",
    "backend / api development", "backend & api development",
    "apis", "databases", "database", "version control",
    "cloud", "cloud platforms", "deployment", "cloud / deployment",
    "cloud & deployment", "cloud and deployment", "mlops",
    "frameworks", "libraries", "tools", "tools and technologies",
    "data handling", "data preprocessing", "vector databases",
)

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

CHOICE_MARKERS = (
    "such as", "for example", "e.g.", "e.g.,", "one of", "any of",
    "or similar", "or equivalent", "and/or",
)

PRIORITY_RANK = {"bonus": 1, "preferred": 2, "must": 3}


def _normalize(value: str) -> str:
    value = (value or "").lower().strip()
    value = re.sub(r"[*_`]+", "", value)
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"\s+", " ", value)
    return value


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized = _normalize(text)
    phrase = _normalize(phrase)
    if not phrase:
        return False
    return bool(re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", normalized))


def _match_named_heading(segment: str):
    normalized = _normalize(segment).rstrip(":")
    for heading in sorted(SECTION_PRIORITY, key=len, reverse=True):
        priority, strength = SECTION_PRIORITY[heading]
        if (
            normalized == heading
            or normalized.startswith(heading + ":")
            or normalized.startswith(heading + " -")
            or normalized.startswith(heading + " ")
        ):
            return heading, priority, strength
    return None


def _is_neutral_heading(segment: str) -> bool:
    normalized = _normalize(segment).rstrip(":")
    return any(
        normalized == heading
        or normalized.startswith(heading + ":")
        or normalized.startswith(heading + " -")
        for heading in NEUTRAL_SECTION_HEADINGS
    )


def _explicit_marker_priority(segment: str):
    if any(_contains_phrase(segment, marker) for marker in BONUS_MARKERS):
        return "bonus", 5, "explicit-bonus-marker"
    if any(_contains_phrase(segment, marker) for marker in PREFERRED_MARKERS):
        return "preferred", 5, "explicit-preferred-marker"
    if any(_contains_phrase(segment, marker) for marker in EXPLICIT_MUST_MARKERS):
        return "must", 5, "explicit-must-marker"
    if any(_contains_phrase(segment, marker) for marker in CAPABILITY_MUST_MARKERS):
        return "must", 3, "capability-wording"
    return None


def _prepare_segments(job_description: str) -> list[dict]:
    text = (job_description or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[•●▪◦]", "\n", text)

    # Force commonly inline section titles onto their own line.
    for heading in (
        "Typical Technology Stack",
        "Example Technology Stack",
        "Technology Stack",
        "Tech Stack",
    ):
        text = re.sub(
            rf"(?i)(?<!\n)(?<![A-Za-z0-9])({re.escape(heading)})(?![A-Za-z0-9])",
            r"\n\1:\n",
            text,
        )

    text = re.sub(r"(?<!\n)\s+(?=#{1,6}\s+)", "\n", text)
    text = re.sub(r"(?<!\n)\s+\*\s+(?=[A-Za-z0-9])", "\n* ", text)
    text = re.sub(r"(?<!\n)\s+[+-]\s+(?=[A-Za-z0-9])", "\n- ", text)

    # Split inline bold labels such as **Languages:**, **ML:**, **Backend:**.
    text = re.sub(r"\s+(?=\*\*[A-Za-z][A-Za-z0-9 /&+-]{0,40}:\*\*)", "\n", text)

    all_headings = tuple(SECTION_PRIORITY) + tuple(NEUTRAL_SECTION_HEADINGS)
    for heading in sorted(set(all_headings), key=len, reverse=True):
        text = re.sub(
            rf"(?i)(?<!\n)(?<![A-Za-z0-9])({re.escape(heading)})\s*:",
            r"\n\1:",
            text,
        )

    segments: list[dict] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        heading_level = None
        heading_match = re.match(r"^(#{1,6})\s*(.+)$", line)
        if heading_match:
            heading_level = len(heading_match.group(1))
            line = heading_match.group(2).strip()

        is_bullet = bool(re.match(r"^[*+-]\s+", line))
        line = re.sub(r"^[*+-]\s+", "", line).strip()
        if not line:
            continue

        parts = [line]
        if heading_level is None and not is_bullet:
            parts = re.split(r"(?<=[.!?;])\s+", line)

        for part in parts:
            part = part.strip(" -\t")
            if not part:
                continue
            segments.append({
                "text": part,
                "heading_level": heading_level,
                "is_bullet": is_bullet,
            })
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


def _looks_like_subsection(segment: str, heading_level=None) -> bool:
    normalized = _normalize(segment).strip(":")
    if heading_level is not None and heading_level >= 3:
        return True

    if len(normalized.split()) <= 9:
        for hint in SUBSECTION_HINTS:
            if (
                normalized == hint
                or normalized.startswith(hint + " -")
                or normalized.startswith(hint + " /")
                or normalized.startswith(hint + " &")
                or normalized.startswith(hint + " (")
                or normalized.startswith(hint + ":")
            ):
                return True
    return False


def _is_choice_or_example_context(segment: str) -> bool:
    normalized = _normalize(segment)

    if any(marker in normalized for marker in CHOICE_MARKERS):
        return True

    if " or " in normalized:
        try:
            mentioned = len({
                canonicalize_skill(candidate)
                for candidate in extract_skills(clean_text(segment))
                if canonicalize_skill(candidate)
            })
        except Exception:
            mentioned = 0
        if mentioned >= 2:
            return True

    if re.search(r"\b[a-z0-9.+#-]+\s*/\s*[a-z0-9.+#-]+\b", normalized):
        return True

    return False


def _resolve_segment_priority(segment: str, active_context):
    explicit = _explicit_marker_priority(segment)

    if explicit:
        priority, strength, source = explicit
        if source == "capability-wording" and active_context:
            active_priority, active_strength, active_source = active_context
            if active_strength >= strength:
                return active_priority, active_strength, active_source
        return explicit

    if active_context:
        return active_context

    return "preferred", 2, "unscoped-skill-evidence"


def _choose_final_priority(candidates: list[tuple[str, int, str]]):
    if not candidates:
        return "preferred", "conservative-default"

    # A skill explicitly labelled preferred/optional should not become MUST
    # merely because it also occurs in a broad summary or parent section.
    explicit_specific = [
        item for item in candidates
        if item[2] in ("explicit-preferred-marker", "explicit-bonus-marker")
    ]
    explicit_must = [item for item in candidates if item[2] == "explicit-must-marker"]

    if explicit_must:
        return "must", "explicit-must-marker"

    if explicit_specific:
        best = max(explicit_specific, key=lambda item: item[1])
        return best[0], best[2]

    # Required-section evidence outranks weak "preferred projects" mentions.
    must_candidates = [
        item for item in candidates
        if item[0] == "must" and (
            item[2].startswith("section:required")
            or item[2].startswith("section:minimum")
            or item[2] in ("capability-wording",)
        )
    ]
    if must_candidates:
        best = max(must_candidates, key=lambda item: item[1])
        return "must", best[2]

    max_strength = max(item[1] for item in candidates)
    finalists = [item for item in candidates if item[1] == max_strength]
    priority, strength, source = max(
        finalists,
        key=lambda item: PRIORITY_RANK.get(item[0], 0),
    )
    return priority, source


def classify_requirements(job_description: str) -> dict:
    jd = job_description or ""
    raw_skills = extract_skills(clean_text(jd))
    segments = _prepare_segments(jd)

    contextual_segments = []
    parent_context = None
    active_context = None

    for item in segments:
        segment = item["text"]
        heading_level = item.get("heading_level")

        named_heading = _match_named_heading(segment)
        explicit = _explicit_marker_priority(segment)
        is_subsection = _looks_like_subsection(segment, heading_level)

        if named_heading:
            heading_name, priority, strength = named_heading
            parent_context = (priority, strength, f"section:{heading_name}")
            active_context = parent_context

            normalized = _normalize(segment)
            pure_heading = normalized.rstrip(":") == heading_name
            contextual_segments.append({
                "text": segment,
                "context": active_context,
                "is_heading": pure_heading,
                "explicit_heading": False,
            })
            continue

        if _is_neutral_heading(segment):
            parent_context = None
            active_context = None
            contextual_segments.append({
                "text": segment,
                "context": None,
                "is_heading": True,
                "explicit_heading": False,
            })
            continue

        if is_subsection and explicit and explicit[2] != "capability-wording":
            active_context = explicit
            contextual_segments.append({
                "text": segment,
                "context": active_context,
                "is_heading": True,
                "explicit_heading": True,
            })
            continue

        if is_subsection:
            active_context = parent_context
            contextual_segments.append({
                "text": segment,
                "context": active_context,
                "is_heading": True,
                # A skill-named subsection under a parent requirement is evidence.
                "explicit_heading": bool(active_context),
            })
            continue

        contextual_segments.append({
            "text": segment,
            "context": active_context,
            "is_heading": False,
            "explicit_heading": False,
        })

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
        priority_candidates = []

        for item in contextual_segments:
            segment = item["text"]
            if not _segment_mentions_skill(segment, skill):
                continue

            if item["is_heading"] and not item["explicit_heading"]:
                continue

            if _is_education_only_context(segment):
                qualification_evidence.append(segment[:320])
                continue

            skill_evidence.append(segment[:320])
            priority, strength, source = _resolve_segment_priority(
                segment,
                item["context"],
            )

            if priority == "must" and _is_choice_or_example_context(segment):
                priority = "preferred"
                source = "alternative-or-example-context"

            priority_candidates.append((priority, strength, source))

        if qualification_evidence and not skill_evidence:
            qualifications.append({
                "skill": skill,
                "type": "education-field",
                "evidence": qualification_evidence[:3],
                "classification_basis": "education-context",
            })
            continue

        priority, basis = _choose_final_priority(priority_candidates)

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
        "priority_method": "section-aware-specificity-preserving-v4",
    }
