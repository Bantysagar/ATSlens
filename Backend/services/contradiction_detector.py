"""Detect a small set of explicit contradictions without guessing intent."""

from __future__ import annotations

import re


def detect_contradictions(resume_text: str, candidate_type: str, experience_years: int) -> dict:
    text = (resume_text or "").lower()
    issues = []

    year_claims = [int(x) for x in re.findall(r"\b(\d{1,2})\+?\s+years?\s+(?:of\s+)?experience\b", text)]
    if year_claims and experience_years >= 0:
        highest = max(year_claims)
        if experience_years == 0 and highest >= 2:
            issues.append({
                "type": "input-vs-resume-experience",
                "severity": "medium",
                "detail": f"Form says 0 years while resume text mentions {highest} years of experience.",
            })
        elif abs(highest - experience_years) >= 3:
            issues.append({
                "type": "input-vs-resume-experience",
                "severity": "medium",
                "detail": f"Form and resume experience claims differ materially ({experience_years} vs {highest}).",
            })

    normalized_type = (candidate_type or "").strip().lower()
    if normalized_type == "fresher" and experience_years >= 3:
        issues.append({
            "type": "candidate-type-vs-experience",
            "severity": "low",
            "detail": "Candidate type is Fresher but entered experience is 3+ years; review the form value.",
        })

    return {
        "issues": issues,
        "issue_count": len(issues),
        "status": "review" if issues else "no-explicit-contradiction-detected",
        "scope_note": "Only explicit text/form conflicts are checked; the system does not infer dishonesty or intent.",
    }
