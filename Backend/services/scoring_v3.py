"""Hybrid scoring for ATSLens V3."""

from __future__ import annotations

from services.scoring_v2 import _ats_compatibility, _resume_quality, _target_field_coverage


PRIORITY_WEIGHT = {"must": 3.0, "preferred": 2.0, "bonus": 1.0}


def _clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))


def _hybrid_coverage(matches: list) -> float:
    denominator = sum(PRIORITY_WEIGHT.get(item.get("priority"), 1.0) for item in matches)
    if denominator <= 0:
        return 0.0
    numerator = sum(
        PRIORITY_WEIGHT.get(item.get("priority"), 1.0) * float(item.get("match_score", 0.0))
        for item in matches
    )
    return numerator / denominator


def _must_have_coverage(matches: list) -> float:
    must = [item for item in matches if item.get("priority") == "must"]
    if not must:
        return 1.0
    return sum(float(item.get("match_score", 0.0)) for item in must) / len(must)


def score_v3(
    resume_text: str,
    target_field: str,
    section_map: dict,
    hybrid_result: dict,
    evidence_profile: dict,
    keyword_result: dict,
    contradiction_result: dict,
    timeline_result: dict,
) -> dict:
    matches = hybrid_result.get("matches", [])
    hybrid_coverage = _hybrid_coverage(matches)
    must_coverage = _must_have_coverage(matches)
    evidence_quality = min(evidence_profile.get("mean_evidence_quality", 0.0) / 100, 1.0)
    field_coverage = _target_field_coverage(resume_text, target_field)

    reliability_penalty = min(
        0.12,
        (keyword_result.get("risk_score", 0) / 100) * 0.08
        + contradiction_result.get("issue_count", 0) * 0.015
        + timeline_result.get("issue_count", 0) * 0.02,
    )

    job_raw = (
        0.52 * hybrid_coverage
        + 0.18 * must_coverage
        + 0.18 * evidence_quality
        + 0.12 * field_coverage
        - reliability_penalty
    )
    job_match = _clamp(job_raw * 100)

    ats = _ats_compatibility(section_map, resume_text)
    if keyword_result.get("flagged"):
        ats = _clamp(ats - min(keyword_result.get("risk_score", 0) * 0.15, 12))

    # Reuse the stable Phase-1 resume-quality structure/evidence heuristic with
    # a V3 reliability adjustment. Convert hybrid matches to the minimal shape
    # expected by the Phase-1 helper.
    compatibility_matches = [
        {
            "exact_match": item.get("matched", False),
            "priority": item.get("priority", "preferred"),
            "evidence_strength": item.get("evidence_strength", "none"),
        }
        for item in matches
    ]
    quality = _resume_quality(section_map, compatibility_matches, resume_text)
    quality = _clamp(0.70 * quality + 30 * evidence_quality - reliability_penalty * 100)

    overall = _clamp(0.52 * job_match + 0.24 * ats + 0.24 * quality)

    return {
        "overall_score": overall,
        "job_match_score": job_match,
        "ats_compatibility_score": ats,
        "resume_quality_score": quality,
        "components": {
            "hybrid_requirement_coverage": round(hybrid_coverage * 100, 1),
            "must_have_coverage": round(must_coverage * 100, 1),
            "evidence_quality": round(evidence_quality * 100, 1),
            "target_field_coverage": round(field_coverage * 100, 1),
            "reliability_penalty": round(reliability_penalty * 100, 1),
        },
        "method": "hybrid-evidence-aware-score-v1",
        "score_scope": "Decision-support score; not a proprietary employer ATS probability.",
    }
