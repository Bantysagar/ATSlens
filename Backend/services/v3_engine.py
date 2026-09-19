"""Integrated ATSLens V3 research/development engine."""

from __future__ import annotations

from services.confidence_engine import compute_confidence
from services.contradiction_detector import detect_contradictions
from services.evidence_engine import build_evidence_profile
from services.exact_matcher import match_requirements
from services.grounded_explainer import build_grounded_explanation
from services.hybrid_matcher import combine_matches
from services.keyword_stuffing_detector import detect_keyword_stuffing
from services.requirement_classifier import classify_requirements
from services.scoring_v3 import score_v3
from services.section_mapper import map_sections
from services.semantic_matcher import semantic_match_requirements
from services.skill_graph import graph_match_requirements
from services.timeline_checker import check_timeline


def _normalize_candidate_type(value: str) -> str:
    raw = (value or "").strip().lower()
    typo_map = {
        "frasher": "Fresher",
        "fresher": "Fresher",
        "freshers": "Fresher",
        "experienced": "Experienced",
        "experience": "Experienced",
    }
    return typo_map.get(raw, (value or "Fresher").strip().title())


def analyze_resume_v3(
    resume_text: str,
    job_description: str,
    candidate_type: str,
    target_field: str,
    experience_years: int = 0,
    preferred_role: str = "",
    target_company: str = "MNC",
) -> dict:
    if len((resume_text or "").split()) < 40:
        raise ValueError("Resume text is too short or unreadable.")
    if len((job_description or "").split()) < 5:
        raise ValueError("Job description is too short.")

    normalized_candidate = _normalize_candidate_type(candidate_type)
    section_map = map_sections(resume_text)
    requirement_map = classify_requirements(job_description)
    requirements = requirement_map["requirements"]

    exact_result = match_requirements(resume_text, section_map, requirements)
    semantic_result = semantic_match_requirements(requirements, section_map, exact_result)
    graph_result = graph_match_requirements(resume_text, requirements)
    hybrid_result = combine_matches(requirements, exact_result, semantic_result, graph_result)
    evidence_profile = build_evidence_profile(resume_text, section_map, hybrid_result)

    keyword_result = detect_keyword_stuffing(resume_text, section_map)
    contradiction_result = detect_contradictions(resume_text, normalized_candidate, experience_years)
    timeline_result = check_timeline(resume_text)
    reliability = {
        "keyword_stuffing": keyword_result,
        "contradictions": contradiction_result,
        "timeline": timeline_result,
    }

    scores = score_v3(
        resume_text=resume_text,
        target_field=target_field,
        section_map=section_map,
        hybrid_result=hybrid_result,
        evidence_profile=evidence_profile,
        keyword_result=keyword_result,
        contradiction_result=contradiction_result,
        timeline_result=timeline_result,
    )

    confidence = compute_confidence(
        resume_text=resume_text,
        section_map=section_map,
        requirements=requirements,
        hybrid_result=hybrid_result,
        evidence_profile=evidence_profile,
        semantic_result=semantic_result,
        keyword_result=keyword_result,
        contradiction_result=contradiction_result,
        timeline_result=timeline_result,
    )
    scores["analysis_confidence"] = confidence["score"]
    scores["confidence_method"] = confidence["method"]

    explanation = build_grounded_explanation(requirements, hybrid_result, evidence_profile, reliability)

    return {
        "engine_version": "ATSLens-Advanced-V3-Integrated",
        "research_status": "integrated-research-prototype-needs-benchmark-calibration",
        "candidate_type": normalized_candidate,
        "target_field": target_field,
        "preferred_role": preferred_role,
        "target_company": target_company,
        "experience_years": experience_years,
        "scores": scores,
        "confidence": confidence,
        "sections": {
            "detected": section_map["detected_sections"],
            "count": section_map["section_count"],
        },
        "requirements": requirement_map,
        "deterministic_matching": exact_result,
        "semantic_matching": semantic_result,
        "skill_graph": graph_result,
        "hybrid_matching": hybrid_result,
        "evidence_intelligence": evidence_profile,
        "reliability": reliability,
        "explanation": explanation,
        "limitations": [
            "Semantic thresholds are engineering defaults until calibrated on a labeled resume-JD dataset.",
            "Related-skill graph signals are partial evidence and never prove possession of a missing skill.",
            "Confidence is structured but not statistically calibrated yet.",
            "The default explanation layer is deterministic and grounded; external LLM verbalization is optional.",
            "Scores are decision-support metrics, not proprietary employer ATS probabilities or hiring decisions.",
        ],
    }
