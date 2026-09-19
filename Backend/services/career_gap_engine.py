"""Actionable role-gap analysis for Career Intelligence V4."""

from __future__ import annotations


def build_gap_analysis(role_results: list[dict], top_n: int = 5) -> dict:
    output = []
    for item in role_results[:top_n]:
        critical = item.get("critical_missing_skills", [])
        preferred = item.get("preferred_missing_skills", [])
        output.append({
            "role": item["role"],
            "role_fit_score": item["role_fit_score"],
            "critical_missing_skills": critical,
            "preferred_missing_skills": preferred,
            "priority_learning_plan": critical[:4] + [s for s in preferred if s not in critical][:2],
            "gap_summary": (
                "No critical core-skill gaps detected."
                if not critical
                else f"{len(critical)} core skill gap(s) should be addressed before treating this role as a strong target."
            ),
        })
    return {"roles": output, "method": "role-gap-priority-v1"}
