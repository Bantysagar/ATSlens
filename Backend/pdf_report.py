from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def generate_pdf_report(data: dict) -> BytesIO:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#172554"),
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#475569"),
        spaceAfter=14
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1d4ed8"),
        spaceBefore=14,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#111827")
    )

    story = []

    story.append(Paragraph("ATSLens - Resume Analysis Report", title_style))
    story.append(Paragraph("AI Powered ATS Resume Analyzer | Professional Marksheet", subtitle_style))
    story.append(Spacer(1, 10))

    summary_table = Table([
        ["Resume File", data.get("filename", "N/A")],
        ["Candidate Type", data.get("candidate_type", "N/A")],
        ["Target Field", data.get("target_field", "N/A")],
        ["Preferred Role", data.get("preferred_role", "N/A") or "N/A"],
        ["Target Company", data.get("target_company", "N/A")],
        ["Overall ATS Score", f"{data.get('score', 0)}%"],
        ["Grade", data.get("grade", "N/A")],
        ["Verdict", data.get("verdict", "N/A")],
        ["MNC Shortlisting Chance", f"{data.get('mnc_chance', 0)}%"]
    ], colWidths=[2.3 * inch, 4.6 * inch])

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef4ff")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    story.append(summary_table)

    story.append(Paragraph("Detailed Score Breakdown", heading_style))

    breakdown = data.get("breakdown", {})

    rows = [
        ["Section", "Score", "Max Score", "Percentage"],
        ["Resume Structure", breakdown.get("structure", 0), 20, percent(breakdown.get("structure", 0), 20)],
        ["Skills", breakdown.get("skills", 0), 20, percent(breakdown.get("skills", 0), 20)],
        ["Technologies", breakdown.get("technologies", 0), 20, percent(breakdown.get("technologies", 0), 20)],
        ["Projects", breakdown.get("projects", 0), 20, percent(breakdown.get("projects", 0), 20)],
        ["Experience", breakdown.get("experience", 0), 20, percent(breakdown.get("experience", 0), 20)],
        ["Education", breakdown.get("education", 0), 10, percent(breakdown.get("education", 0), 10)],
        ["Keywords", breakdown.get("keywords", 0), 10, percent(breakdown.get("keywords", 0), 10)],
        ["Formatting", breakdown.get("formatting", 0), 10, percent(breakdown.get("formatting", 0), 10)],
        ["Total", data.get("total_obtained", 0), data.get("total_marks", 130), f"{data.get('score', 0)}%"]
    ]

    score_table = Table(rows, colWidths=[2.6 * inch, 1.2 * inch, 1.4 * inch, 1.5 * inch])

    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dcfce7")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    story.append(score_table)

    story.append(Paragraph("Performance Summary", heading_style))
    story.append(Paragraph(data.get("summary", "No summary available."), normal_style))

    story.append(Paragraph("Matched Skills", heading_style))
    story.append(Paragraph(comma_text(data.get("matched_skills", []), "No matched skills found."), normal_style))

    story.append(Paragraph("Missing Skills", heading_style))
    story.append(Paragraph(comma_text(data.get("missing_skills", []), "No missing skills found."), normal_style))

    story.append(Paragraph("Key Strengths", heading_style))
    story.append(Paragraph(list_to_text(data.get("key_strengths", [])), normal_style))

    story.append(Paragraph("Recommended Roadmap", heading_style))
    story.append(Paragraph(list_to_text(data.get("roadmap", [])), normal_style))

    story.append(Paragraph("Career Field Matches", heading_style))
    field_text = []

    for item in data.get("field_matches", [])[:5]:
        field_text.append(f"{item.get('field', 'Unknown')}: {item.get('match', 0)}%")

    story.append(Paragraph("<br/>".join(field_text) if field_text else "No field match data available.", normal_style))

    story.append(Paragraph("MNC Readiness", heading_style))
    story.append(Paragraph(
        f"{data.get('mnc_label', 'N/A')} - {data.get('mnc_message', 'No MNC readiness message available.')}",
        normal_style
    ))

    story.append(Paragraph("Final Recommendation", heading_style))
    story.append(Paragraph(data.get("final_advice", "No recommendation available."), normal_style))

    story.append(Spacer(1, 18))
    story.append(Paragraph("Generated by ATSLens AI Resume Analyzer", subtitle_style))

    doc.build(story)

    buffer.seek(0)
    return buffer


def percent(score, max_score):
    if max_score == 0:
        return "0%"

    return f"{round((score / max_score) * 100)}%"


def comma_text(items, fallback):
    if not items:
        return fallback

    return ", ".join(items)


def list_to_text(items):
    if not items:
        return "No data available."

    return "<br/>".join([f"• {item}" for item in items])