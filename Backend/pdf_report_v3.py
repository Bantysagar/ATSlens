from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


NAVY = colors.HexColor("#0F172A")
INDIGO = colors.HexColor("#4F46E5")
SLATE = colors.HexColor("#475569")
LIGHT = colors.HexColor("#F8FAFC")
BORDER = colors.HexColor("#E2E8F0")
GREEN = colors.HexColor("#15803D")
RED = colors.HexColor("#B91C1C")


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("V3Title", parent=base["Title"], fontSize=18, leading=22, textColor=colors.white),
        "h2": ParagraphStyle("V3H2", parent=base["Heading2"], fontSize=11, leading=14, textColor=NAVY, spaceAfter=4),
        "body": ParagraphStyle("V3Body", parent=base["BodyText"], fontSize=8.8, leading=12, textColor=SLATE),
        "small": ParagraphStyle("V3Small", parent=base["BodyText"], fontSize=7.8, leading=10, textColor=SLATE),
        "score": ParagraphStyle("V3Score", parent=base["BodyText"], fontSize=14, leading=16, textColor=NAVY, alignment=1),
    }


def _score_card(label, value, styles):
    return Paragraph(f"<b>{escape(label)}</b><br/><font size='15'>{escape(str(value))}%</font>", styles["score"])


def generate_pdf_report_v3(data: dict) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=13 * mm,
        leftMargin=13 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="ATSLens Advanced V3 Report",
        author="ATSLens",
    )
    styles = _styles()
    story = []

    header = Table([[Paragraph("<b>ATSLens Advanced V3</b><br/><font size='8'>Evidence-aware hybrid resume intelligence report</font>", styles["title"])]] , colWidths=[182 * mm])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story += [header, Spacer(1, 5 * mm)]

    scores = data.get("scores", {})
    cards = Table([[
        _score_card("Overall", scores.get("overall_score", 0), styles),
        _score_card("Job Match", scores.get("job_match_score", 0), styles),
        _score_card("ATS Compatibility", scores.get("ats_compatibility_score", 0), styles),
        _score_card("Resume Quality", scores.get("resume_quality_score", 0), styles),
    ]], colWidths=[45.5 * mm] * 4)
    cards.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [cards, Spacer(1, 5 * mm)]

    meta = [
        ["Resume", data.get("filename", "N/A")],
        ["Candidate", data.get("candidate_type", "N/A")],
        ["Target Field", data.get("target_field", "N/A")],
        ["Preferred Role", data.get("preferred_role", "N/A") or "N/A"],
        ["Engine", data.get("engine_version", "N/A")],
    ]
    table = Table([[Paragraph(f"<b>{escape(str(a))}</b>", styles["small"]), Paragraph(escape(str(b)), styles["small"])] for a, b in meta], colWidths=[42 * mm, 140 * mm])
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, BORDER), ("BACKGROUND", (0, 0), (0, -1), LIGHT), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story += [Paragraph("Profile", styles["h2"]), table, Spacer(1, 5 * mm)]

    hybrid = data.get("hybrid_matching", {})
    story.append(Paragraph("Requirement Matching", styles["h2"]))
    match_rows = [["Requirement", "Priority", "Type", "Score", "Evidence"]]
    for item in (hybrid.get("matches") or [])[:24]:
        match_rows.append([
            item.get("skill", ""),
            item.get("priority", ""),
            item.get("match_type", "none"),
            f"{item.get('match_score_percent', 0)}%",
            (item.get("evidence") or item.get("evidence_section") or "No strong evidence")[:95],
        ])
    mt = Table([[Paragraph(escape(str(x)), styles["small"]) for x in row] for row in match_rows], colWidths=[36 * mm, 23 * mm, 25 * mm, 18 * mm, 80 * mm], repeatRows=1)
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story += [mt, Spacer(1, 5 * mm)]

    explanation = data.get("explanation", {})
    story.append(Paragraph("Grounded Improvement Suggestions", styles["h2"]))
    for suggestion in (explanation.get("suggestions") or [])[:8]:
        story.append(Paragraph(f"• {escape(str(suggestion))}", styles["body"]))
        story.append(Spacer(1, 1.2 * mm))

    reliability = data.get("reliability", {})
    keyword = reliability.get("keyword_stuffing", {})
    timeline = reliability.get("timeline", {})
    contradictions = reliability.get("contradictions", {})
    story += [Spacer(1, 3 * mm), Paragraph("Reliability Checks", styles["h2"])]
    reliability_rows = [
        ["Keyword stuffing risk", f"{keyword.get('risk_score', 0)} / 100"],
        ["Timeline issues", timeline.get("issue_count", 0)],
        ["Explicit contradictions", contradictions.get("issue_count", 0)],
        ["Confidence", f"{scores.get('analysis_confidence', 0)}% ({scores.get('confidence_method', '')})"],
    ]
    rt = Table([[Paragraph(f"<b>{escape(str(a))}</b>", styles["small"]), Paragraph(escape(str(b)), styles["small"])] for a, b in reliability_rows], colWidths=[62 * mm, 120 * mm])
    rt.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, BORDER), ("BACKGROUND", (0, 0), (0, -1), LIGHT)]))
    story += [rt, Spacer(1, 5 * mm)]

    story.append(Paragraph("Important: ATSLens is a decision-support/research prototype. Scores are not proprietary employer ATS probabilities, and related/semantic signals should be validated against labeled data before research claims.", styles["small"]))

    doc.build(story)
    buffer.seek(0)
    return buffer
