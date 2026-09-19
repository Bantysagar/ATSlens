"""Structured confidence signal for ATSLens V3.

This remains an engineering confidence score until calibrated on labeled data.
"""

from __future__ import annotations


def compute_confidence(
    resume_text: str,
    section_map: dict,
    requirements: list,
    hybrid_result: dict,
    evidence_profile: dict,
    semantic_result: dict,
    keyword_result: dict,
    contradiction_result: dict,
    timeline_result: dict,
) -> dict:
    section_signal = min(section_map.get("section_count", 0) / 6, 1.0)
    requirement_signal = min(len(requirements) / 10, 1.0)
    text_signal = min(len((resume_text or "").split()) / 350, 1.0)

    matched = [item for item in hybrid_result.get("matches", []) if item.get("matched")]
    localized = sum(1 for item in matched if item.get("evidence_section"))
    localization_signal = localized / len(matched) if matched else 0.0
    evidence_signal = min((evidence_profile.get("mean_evidence_quality", 0.0) / 100), 1.0)

    base = (
        0.20 * section_signal
        + 0.15 * requirement_signal
        + 0.15 * text_signal
        + 0.25 * localization_signal
        + 0.25 * evidence_signal
    )

    penalty = 0.0
    penalty += min(keyword_result.get("risk_score", 0) / 100, 1.0) * 0.10
    penalty += min(contradiction_result.get("issue_count", 0) * 0.04, 0.12)
    penalty += min(timeline_result.get("issue_count", 0) * 0.04, 0.12)

    raw = max(0.0, base - penalty)
    score = min(round(raw * 100), 92)
    backend = (semantic_result.get("backend") or {}).get("backend", "unknown")

    return {
        "score": score,
        "method": "structured-heuristic-v2-not-statistically-calibrated",
        "semantic_backend": backend,
        "signals": {
            "section_quality": round(section_signal * 100, 1),
            "requirement_volume": round(requirement_signal * 100, 1),
            "text_sufficiency": round(text_signal * 100, 1),
            "evidence_localization": round(localization_signal * 100, 1),
            "evidence_quality": round(evidence_signal * 100, 1),
        },
        "calibration_status": "pending-labeled-dataset-evaluation",
    }
