"""Grounded explanation layer.

Default output is deterministic and evidence-bound. The returned grounding
payload can be sent to an external LLM later, but no model is allowed to invent
skills or alter scores.
"""

from __future__ import annotations


PRIORITY_RANK = {"must": 3, "preferred": 2, "bonus": 1}


def _top(items, key, n=5, reverse=True):
    return sorted(items, key=key, reverse=reverse)[:n]


def build_grounded_explanation(requirements: list, hybrid_result: dict, evidence_profile: dict, reliability: dict) -> dict:
    matches = hybrid_result.get("matches", [])
    matched = [item for item in matches if item.get("matched")]
    missing = [item for item in matches if not item.get("matched")]

    strengths = []
    for item in _top(matched, lambda x: (PRIORITY_RANK.get(x.get("priority"), 0), x.get("match_score", 0)), 6):
        strengths.append({
            "skill": item["skill"],
            "priority": item.get("priority"),
            "match_type": item.get("match_type"),
            "reason": f"{item['skill']} is supported by {item.get('match_type', 'matched')} evidence"
                      + (f" in the {item.get('evidence_section')} section." if item.get("evidence_section") else "."),
        })

    gaps = []
    for item in _top(missing, lambda x: PRIORITY_RANK.get(x.get("priority"), 0), 8):
        gaps.append({
            "skill": item["skill"],
            "priority": item.get("priority"),
            "reason": "No sufficiently strong resume evidence was found for this JD requirement.",
        })

    suggestions = []
    for gap in gaps[:5]:
        suggestions.append(
            f"For {gap['skill']}: if you genuinely have relevant experience, add a concrete project or experience bullet showing how you used it; otherwise do not add the keyword just to raise a score."
        )

    if reliability.get("keyword_stuffing", {}).get("flagged"):
        suggestions.append("Reduce repeated skill keywords and replace repetition with specific project/experience evidence.")
    if reliability.get("timeline", {}).get("issue_count"):
        suggestions.append("Review date ranges flagged by the timeline checker before using the resume.")

    grounding_payload = {
        "requirements": requirements,
        "hybrid_matches": matches,
        "evidence_profile": evidence_profile,
        "reliability": reliability,
        "instruction": "Explain only these facts. Do not add unobserved qualifications and do not change numeric scores.",
    }

    return {
        "mode": "deterministic-grounded-default",
        "llm_ready": True,
        "strengths": strengths,
        "gaps": gaps,
        "suggestions": suggestions,
        "grounding_payload": grounding_payload,
        "llm_policy": "An optional external LLM may verbalize this payload, but scoring stays deterministic/hybrid and evidence-bound.",
    }
