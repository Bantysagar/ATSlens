"""Conservative date-order consistency checks for resume timelines."""

from __future__ import annotations

import re
from datetime import datetime


MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

MONTH_NAME = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
SEP = r"\s*(?:-|–|—|to|until|through)\s*"
PRESENT = r"(?:present|current|now)"

NAMED_RANGE_RE = re.compile(
    rf"\b(?:(\d{{1,2}})\s+)?({MONTH_NAME})[\s,]+(20\d{{2}}){SEP}(?:(?:(\d{{1,2}})\s+)?({MONTH_NAME})[\s,]+(20\d{{2}})|({PRESENT}))\b",
    re.I,
)

NUMERIC_RANGE_RE = re.compile(
    rf"\b(0?[1-9]|1[0-2])[/-](20\d{{2}}){SEP}(?:(0?[1-9]|1[0-2])[/-](20\d{{2}})|({PRESENT}))\b",
    re.I,
)

ISO_RANGE_RE = re.compile(
    rf"\b(20\d{{2}})-(0?[1-9]|1[0-2]){SEP}(?:(20\d{{2}})-(0?[1-9]|1[0-2])|({PRESENT}))\b",
    re.I,
)

YEAR_RANGE_RE = re.compile(
    rf"\b(20\d{{2}}){SEP}({PRESENT}|20\d{{2}})\b",
    re.I,
)


def _month_number(name: str) -> int:
    return MONTHS.get((name or "").lower(), 1)


def _key(year: int, month: int) -> int:
    return year * 12 + month


def _add_range(ranges: list, issues: list, start_year: int, start_month: int, end_year: int, end_month: int, raw: str, precision: str):
    current = datetime.now()
    ranges.append({
        "start": f"{start_year:04d}-{start_month:02d}",
        "end": f"{end_year:04d}-{end_month:02d}",
        "raw": raw,
        "precision": precision,
    })

    if _key(start_year, start_month) > _key(end_year, end_month):
        issues.append({
            "type": "reversed-date-range",
            "start": f"{start_year:04d}-{start_month:02d}",
            "end": f"{end_year:04d}-{end_month:02d}",
            "severity": "high",
        })

    if start_year < 1990 or _key(end_year, end_month) > _key(current.year + 1, 12):
        issues.append({
            "type": "implausible-date",
            "start": f"{start_year:04d}-{start_month:02d}",
            "end": f"{end_year:04d}-{end_month:02d}",
            "severity": "medium",
        })


def check_timeline(resume_text: str) -> dict:
    text = resume_text or ""
    current = datetime.now()
    issues = []
    ranges = []
    occupied_spans: list[tuple[int, int]] = []

    def overlaps(span):
        return any(not (span[1] <= old[0] or span[0] >= old[1]) for old in occupied_spans)

    for match in NAMED_RANGE_RE.finditer(text):
        start_month = _month_number(match.group(2))
        start_year = int(match.group(3))
        if match.group(7):
            end_month, end_year = current.month, current.year
        else:
            end_month = _month_number(match.group(5))
            end_year = int(match.group(6))
        _add_range(ranges, issues, start_year, start_month, end_year, end_month, match.group(0), "month")
        occupied_spans.append(match.span())

    for match in NUMERIC_RANGE_RE.finditer(text):
        if overlaps(match.span()):
            continue
        start_month, start_year = int(match.group(1)), int(match.group(2))
        if match.group(5):
            end_month, end_year = current.month, current.year
        else:
            end_month, end_year = int(match.group(3)), int(match.group(4))
        _add_range(ranges, issues, start_year, start_month, end_year, end_month, match.group(0), "month")
        occupied_spans.append(match.span())

    for match in ISO_RANGE_RE.finditer(text):
        if overlaps(match.span()):
            continue
        start_year, start_month = int(match.group(1)), int(match.group(2))
        if match.group(5):
            end_month, end_year = current.month, current.year
        else:
            end_year, end_month = int(match.group(3)), int(match.group(4))
        _add_range(ranges, issues, start_year, start_month, end_year, end_month, match.group(0), "month")
        occupied_spans.append(match.span())

    for match in YEAR_RANGE_RE.finditer(text):
        if overlaps(match.span()):
            continue
        start_year = int(match.group(1))
        end_token = match.group(2)
        if end_token.lower() in {"present", "current", "now"}:
            end_year, end_month = current.year, current.month
        else:
            end_year, end_month = int(end_token), 12
        _add_range(ranges, issues, start_year, 1, end_year, end_month, match.group(0), "year")
        occupied_spans.append(match.span())

    # Deduplicate identical normalized ranges while preserving order.
    unique_ranges = []
    seen = set()
    for item in ranges:
        key = (item["start"], item["end"], item["raw"])
        if key not in seen:
            seen.add(key)
            unique_ranges.append(item)

    return {
        "issues": issues,
        "issue_count": len(issues),
        "parsed_ranges": unique_ranges[:30],
        "parsed_range_count": len(unique_ranges),
        "status": "review" if issues else "no-obvious-order-conflict",
        "method": "month-and-year-range-parser-v2",
        "note": "Overlapping education, internships, and jobs are not automatically treated as contradictions.",
    }
