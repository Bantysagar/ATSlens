"""Compute an observable evidence-strength signal for a skill.

The output deliberately avoids claiming a person's true proficiency. It scores
how strongly the resume documents use of a skill.
"""

from __future__ import annotations

import re


ACTION_VERBS = {
    "built", "developed", "designed", "implemented", "deployed", "trained",
    "evaluated", "optimized", "integrated", "created", "engineered", "led",
    "improved", "automated", "analyzed", "delivered",
}

SECTION_BASE = {
    "experience": 0.90,
    "projects": 0.84,
    "certifications": 0.66,
    "skills": 0.54,
    "summary": 0.48,
    "education": 0.40,
    None: 0.30,
}


def evidence_signal(section: str | None, text: str | None, match_score: float, frequency: int = 1) -> dict:
    normalized = re.sub(r"[^a-z0-9\s-]", " ", (text or "").lower())
    tokens = set(normalized.split())
    action_hits = len(tokens.intersection(ACTION_VERBS))
    action_signal = min(action_hits / 2, 1.0)
    repetition_signal = min(max(frequency, 1) / 3, 1.0)

    raw = (
        0.45 * SECTION_BASE.get(section, 0.30)
        + 0.30 * max(0.0, min(1.0, match_score))
        + 0.15 * action_signal
        + 0.10 * repetition_signal
    )
    score = max(0.0, min(1.0, raw))
    if score >= 0.78:
        label = "strong-documented-evidence"
    elif score >= 0.58:
        label = "moderate-documented-evidence"
    else:
        label = "limited-documented-evidence"

    return {
        "evidence_signal": round(score, 4),
        "evidence_signal_percent": round(score * 100, 1),
        "label": label,
        "action_verb_hits": action_hits,
        "disclaimer": "This is a resume-evidence signal, not a verified proficiency rating.",
    }
