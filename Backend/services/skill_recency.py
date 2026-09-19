"""Estimate skill recency from nearby resume dates.

This is an evidence signal only. It does not infer actual competence.
"""

from __future__ import annotations

import re
from datetime import datetime


YEAR_RE = re.compile(r"\b(20\d{2})\b")


def recency_from_text(text: str) -> dict:
    current_year = datetime.now().year
    years = [int(x) for x in YEAR_RE.findall(text or "")]
    if not years:
        return {
            "latest_year": None,
            "recency_score": 0.60,
            "label": "date-unknown",
        }

    latest = min(max(years), current_year + 1)
    age = max(0, current_year - latest)
    if age <= 1:
        score, label = 1.0, "recent"
    elif age <= 2:
        score, label = 0.88, "recent"
    elif age <= 4:
        score, label = 0.68, "moderate"
    else:
        score, label = 0.48, "older"

    return {
        "latest_year": latest,
        "recency_score": score,
        "recency_percent": round(score * 100, 1),
        "label": label,
    }
