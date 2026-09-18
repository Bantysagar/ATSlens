import re
from analyzer import FIELD_SKILLS, clean_text, extract_skills
from services.skill_taxonomy import canonicalize_skills

PRIORITY_WEIGHT = {
    "must": 3.0,
    "preferred": 2.0,
    "bonus": 1.0,
}

EVIDENCE_FACTOR = {
    "strong": 1.0,
    "medium": 0.75,
    "low": 0.45,
    "none": 0.0,
}

EXPECTED_SECTIONS = {
    "summary", "skills", "experience", "projects", "education", "certifications"
}

FIELD_ALIASES = {
    "ai/ml": "AI/ML Engineer",
    "ai ml": "AI/ML Engineer",
    "ai": "AI/ML Engineer",
    "artificial intelligence": "AI/ML Engineer",
    "machine learning": "AI/ML Engineer",
    "ai engineer": "AI/ML Engineer",
    "ml engineer": "AI/ML Engineer",
    "ai/ml engineer": "AI/ML Engineer",
    "software": "Software Engineer",
    "software engineering": "Software Engineer",
    "backend": "Backend Developer",
    "full stack": "Full Stack Developer",
    "data analytics": "Data Analyst",
    "analytics": "Data Analyst",
    "cloud": "Cloud Engineer",
    "cybersecurity": "Cybersecurity Analyst",
}


def _clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))


def _resolve_target_field(target_field: str) -> str:
    raw = (target_field or "").strip()
    if raw in FIELD_SKILLS:
        return raw

    normalized = re.sub(r"\s+", " ", raw.lower()).strip()
    alias = FIELD_ALIASES.get(normalized)
    if alias:
        return alias

    for field_name in FIELD_SKILLS:
        if field_name.lower() == normalized:
            return field_name
    return raw


def _requirement_coverage(matches: list) -> float:
    denominator = sum(PRIORITY_WEIGHT.get(item["priority"], 1.0) for item in matches)
    if denominator <= 0:
        return 0.0

    numerator = sum(
        PRIORITY_WEIGHT.get(item["priority"], 1.0)
        for item in matches
        if item.get("exact_match")
    )
    return numerator / denominator


def _evidence_quality(matches: list) -> float:
    matched = [item for item in matches if item.get("exact_match")]
    if not matched:
        return 0.0

    weighted_total = 0.0
    weight_sum = 0.0
    for item in matched:
        p_weight = PRIORITY_WEIGHT.get(item["priority"], 1.0)
        weighted_total += p_weight * EVIDENCE_FACTOR.get(item["evidence_strength"], 0.0)
        weight_sum += p_weight
    return weighted_total / weight_sum if weight_sum else 0.0


def _target_field_coverage(resume_text: str, target_field: str) -> float:
    resolved_field = _resolve_target_field(target_field)
    target = set(canonicalize_skills(FIELD_SKILLS.get(resolved_field, [])))
    if not target:
        return 0.0

    resume = set(canonicalize_skills(extract_skills(clean_text(resume_text or ""))))
    return len(resume.intersection(target)) / len(target)


def _ats_compatibility(section_map: dict, raw_text: str) -> int:
    detected = set(section_map.get("detected_sections", []))
    core = {"skills", "education"}
    career = {"experience", "projects"}

    section_score = 0
    section_score += 35 * (len(detected.intersection(EXPECTED_SECTIONS)) / len(EXPECTED_SECTIONS))
    section_score += 15 if core.issubset(detected) else 7 * len(core.intersection(detected))
    section_score += 15 if career.intersection(detected) else 0

    text = raw_text or ""
    readable_chars = sum(ch.isalnum() or ch.isspace() or ch in ".,;:-_/@+()" for ch in text)
    readability_ratio = readable_chars / max(len(text), 1)
    readability_score = 20 * min(readability_ratio, 1.0)
    length_score = 15 if len(text.split()) >= 150 else 10 if len(text.split()) >= 80 else 5
    return _clamp(section_score + readability_score + length_score)


def _resume_quality(section_map: dict, exact_matches: list, raw_text: str) -> int:
    detected = set(section_map.get("detected_sections", []))
    section_depth = min(len(detected) / 6, 1.0)
    evidence = _evidence_quality(exact_matches)

    words = (raw_text or "").lower().split()
    has_number = any(any(ch.isdigit() for ch in token) for token in words)
    action_terms = {
        "built", "developed", "designed", "implemented", "improved",
        "reduced", "increased", "deployed", "created", "led"
    }
    action_hits = sum(1 for token in words if token.strip(".,;:()") in action_terms)
    impact = min(action_hits / 5, 1.0) * 0.7 + (0.3 if has_number else 0.0)
    return _clamp(35 * section_depth + 45 * evidence + 20 * min(impact, 1.0))


def _analysis_confidence(section_map: dict, requirements: list, matches: list, raw_text: str) -> int:
    section_signal = min(section_map.get("section_count", 0) / 6, 1.0)
    requirement_signal = min(len(requirements) / 8, 1.0)
    text_signal = min(len((raw_text or "").split()) / 350, 1.0)

    matched = [item for item in matches if item.get("exact_match")]
    if matched:
        localized = sum(1 for item in matched if item.get("evidence_sections"))
        evidence_localization_signal = localized / len(matched)
    else:
        evidence_localization_signal = 0.0

    raw_score = (
        section_signal * 0.30
        + requirement_signal * 0.20
        + text_signal * 0.20
        + evidence_localization_signal * 0.30
    ) * 100
    return min(_clamp(raw_score), 95)


def score_v2(resume_text: str, target_field: str, section_map: dict, exact_match_result: dict, requirements: list) -> dict:
    matches = exact_match_result.get("matches", [])
    req_coverage = _requirement_coverage(matches)
    evidence_quality = _evidence_quality(matches)
    field_coverage = _target_field_coverage(resume_text, target_field)

    job_match = _clamp(60 * req_coverage + 25 * evidence_quality + 15 * field_coverage)
    ats_compatibility = _ats_compatibility(section_map, resume_text)
    resume_quality = _resume_quality(section_map, matches, resume_text)
    overall = _clamp(0.50 * job_match + 0.30 * ats_compatibility + 0.20 * resume_quality)
    confidence = _analysis_confidence(section_map, requirements, matches, resume_text)

    return {
        "overall_score": overall,
        "job_match_score": job_match,
        "ats_compatibility_score": ats_compatibility,
        "resume_quality_score": resume_quality,
        "analysis_confidence": confidence,
        "confidence_method": "heuristic-v1-not-calibrated",
        "components": {
            "requirement_coverage": round(req_coverage * 100, 1),
            "evidence_quality": round(evidence_quality * 100, 1),
            "target_field_coverage": round(field_coverage * 100, 1),
        },
    }
