from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ============================================================
# COLORS
# ============================================================

NAVY = colors.HexColor("#0B1739")
BLUE = colors.HexColor("#4F46E5")

GREEN = colors.HexColor("#15803D")
GREEN_BG = colors.HexColor("#ECFDF3")

RED = colors.HexColor("#B91C1C")
RED_BG = colors.HexColor("#FEF2F2")

AMBER = colors.HexColor("#B45309")
AMBER_BG = colors.HexColor("#FFF7ED")

SLATE_900 = colors.HexColor("#0F172A")
SLATE_700 = colors.HexColor("#334155")
SLATE_600 = colors.HexColor("#475569")
SLATE_500 = colors.HexColor("#64748B")
SLATE_300 = colors.HexColor("#CBD5E1")
SLATE_200 = colors.HexColor("#E2E8F0")
SLATE_50 = colors.HexColor("#F8FAFC")

WHITE = colors.white


# ============================================================
# MARKSHEET SECTIONS
# ============================================================

SECTION_CONFIG = [

    (
        "Resume Structure",
        "structure",
        20
    ),

    (
        "Skills",
        "skills",
        20
    ),

    (
        "Technologies",
        "technologies",
        20
    ),

    (
        "Projects",
        "projects",
        20
    ),

    (
        "Experience",
        "experience",
        20
    ),

    (
        "Education",
        "education",
        10
    ),

    (
        "JD Keywords",
        "keywords",
        10
    ),

    (
        "Formatting & Readability",
        "formatting",
        10
    ),

]


# ============================================================
# MAIN PDF FUNCTION
# ============================================================

def generate_pdf_report(data: dict) -> BytesIO:

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,

        pagesize=A4,

        rightMargin=13 * mm,
        leftMargin=13 * mm,

        topMargin=16 * mm,
        bottomMargin=17 * mm,

        title=(
            "ATSLens Resume Evaluation Report - "
            f"{data.get('analysis_id', '')}"
        ),

        author="ATSLens",

        subject=(
            "Professional Resume Evaluation Marksheet"
        )
    )

    styles = build_styles()

    story = []


    # ========================================================
    # HEADER
    # ========================================================

    header = Table(

        [[

            Paragraph(
                """
                <font color="#FFFFFF">
                    <b>ATSLens</b>
                </font>

                <br/>

                <font
                    color="#C7D2FE"
                    size="8"
                >
                    Resume Intelligence Platform
                </font>
                """,
                styles["brand"]
            ),

            Paragraph(
                """
                <font color="#FFFFFF">
                    <b>
                        RESUME EVALUATION MARKSHEET
                    </b>
                </font>

                <br/>

                <font
                    color="#C7D2FE"
                    size="8"
                >
                    Evidence-based ATS & JD Readiness Report
                </font>
                """,
                styles["header_right"]
            )

        ]],

        colWidths=[
            64 * mm,
            118 * mm
        ]
    )


    header.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                NAVY
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.7,
                NAVY
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

        ])
    )


    story.append(header)

    story.append(
        Spacer(
            1,
            5 * mm
        )
    )


    # ========================================================
    # REPORT INFORMATION
    # ========================================================

    report_id = data.get(
        "analysis_id",
        "N/A"
    )

    created_at = data.get(
        "created_at",
        "N/A"
    )


    identity = Table(

        [[

            Paragraph(
                f"""
                <b>Report ID</b>
                <br/>
                <font color="#475569">
                    ATS-{escape(str(report_id))}
                </font>
                """,
                styles["small"]
            ),

            Paragraph(
                f"""
                <b>Generated On</b>
                <br/>
                <font color="#475569">
                    {escape(str(created_at))}
                </font>
                """,
                styles["small"]
            ),

            Paragraph(
                """
                <b>Report Type</b>
                <br/>
                <font color="#475569">
                    ATS + JD Readiness
                </font>
                """,
                styles["small"]
            )

        ]],

        colWidths=[
            60.7 * mm,
            60.7 * mm,
            60.6 * mm
        ]
    )


    identity.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                SLATE_50
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.45,
                SLATE_200
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

        ])
    )


    story.append(identity)

    story.append(
        Spacer(
            1,
            4 * mm
        )
    )


    # ========================================================
    # CANDIDATE PROFILE
    # ========================================================

    story.append(

        Paragraph(
            "CANDIDATE & TARGET PROFILE",
            styles["section_title"]
        )

    )


    profile_rows = [

        [

            label_value(
                "Resume File",
                data.get(
                    "filename",
                    "N/A"
                ),
                styles
            ),

            label_value(
                "Candidate Type",
                data.get(
                    "candidate_type",
                    "N/A"
                ),
                styles
            ),

        ],

        [

            label_value(
                "Target Field",
                data.get(
                    "target_field",
                    "N/A"
                ),
                styles
            ),

            label_value(
                "Preferred Role",
                data.get(
                    "preferred_role",
                    "N/A"
                )
                or
                "N/A",
                styles
            ),

        ],

        [

            label_value(
                "Target Company",
                data.get(
                    "target_company",
                    "N/A"
                ),
                styles
            ),

            label_value(
                "Experience",
                (
                    f"{data.get('experience_years', 0)} "
                    "year(s)"
                ),
                styles
            )

        ]

    ]


    profile_table = Table(

        profile_rows,

        colWidths=[
            91 * mm,
            91 * mm
        ]
    )


    profile_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                WHITE
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                SLATE_200
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

        ])
    )


    story.append(profile_table)

    story.append(
        Spacer(
            1,
            5 * mm
        )
    )


    # ========================================================
    # OVERALL RESULT
    # ========================================================

    score = safe_number(
        data.get(
            "score",
            0
        )
    )


    grade = str(
        data.get(
            "grade",
            "N/A"
        )
    )


    verdict = str(
        data.get(
            "verdict",
            "N/A"
        )
    )


    total_obtained = safe_number(
        data.get(
            "total_obtained",
            0
        )
    )


    total_marks = safe_number(
        data.get(
            "total_marks",
            130
        )
    )


    mnc_chance = safe_number(
        data.get(
            "mnc_chance",
            0
        )
    )


    result_cells = [

        metric_cell(
            "OVERALL SCORE",
            f"{num_text(score)}%",
            styles
        ),

        metric_cell(
            "TOTAL MARKS",
            (
                f"{num_text(total_obtained)}"
                f" / "
                f"{num_text(total_marks)}"
            ),
            styles
        ),

        metric_cell(
            "GRADE",
            grade,
            styles
        ),

        metric_cell(
            "VERDICT",
            verdict,
            styles
        ),

        metric_cell(
            "MNC READINESS",
            f"{num_text(mnc_chance)}%",
            styles
        ),

    ]


    result_table = Table(

        [result_cells],

        colWidths=[
            36.4 * mm
        ] * 5

    )


    result_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor(
                    "#EEF2FF"
                )
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.7,
                colors.HexColor(
                    "#C7D2FE"
                )
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

        ])
    )


    story.append(
        result_table
    )


    story.append(
        Spacer(
            1,
            4 * mm
        )
    )


    # ========================================================
    # DETAILED MARKSHEET
    # ========================================================

    story.append(

        Paragraph(
            "DETAILED SCORE MARKSHEET",
            styles["section_title"]
        )

    )


    breakdown = (
        data.get(
            "breakdown",
            {}
        )
        or
        {}
    )


    marks_rows = [

        [

            Paragraph(
                "<b>S.No.</b>",
                styles[
                    "table_header"
                ]
            ),

            Paragraph(
                "<b>Evaluation Section</b>",
                styles[
                    "table_header"
                ]
            ),

            Paragraph(
                "<b>Max</b>",
                styles[
                    "table_header_center"
                ]
            ),

            Paragraph(
                "<b>Obtained</b>",
                styles[
                    "table_header_center"
                ]
            ),

            Paragraph(
                "<b>%</b>",
                styles[
                    "table_header_center"
                ]
            ),

            Paragraph(
                "<b>Performance</b>",
                styles[
                    "table_header_center"
                ]
            ),

        ]

    ]


    for index, (
        label,
        key,
        max_score
    ) in enumerate(
        SECTION_CONFIG,
        start=1
    ):

        obtained = safe_number(
            breakdown.get(
                key,
                0
            )
        )


        percentage = percentage_value(
            obtained,
            max_score
        )


        marks_rows.append([

            str(index),

            Paragraph(
                escape(label),
                styles["table_body"]
            ),

            num_text(
                max_score
            ),

            num_text(
                obtained
            ),

            f"{percentage}%",

            performance_label(
                percentage
            )

        ])


    marks_rows.append([

        "",

        Paragraph(
            "<b>GRAND TOTAL</b>",
            styles["table_total"]
        ),

        Paragraph(
            f"<b>{num_text(total_marks)}</b>",
            styles[
                "table_total_center"
            ]
        ),

        Paragraph(
            f"<b>{num_text(total_obtained)}</b>",
            styles[
                "table_total_center"
            ]
        ),

        Paragraph(
            f"<b>{num_text(score)}%</b>",
            styles[
                "table_total_center"
            ]
        ),

        Paragraph(
            f"<b>{escape(grade)}</b>",
            styles[
                "table_total_center"
            ]
        ),

    ])


    marks_table = Table(

        marks_rows,

        colWidths=[

            12 * mm,
            66 * mm,
            19 * mm,
            24 * mm,
            19 * mm,
            42 * mm

        ],

        repeatRows=1
    )


    marks_style = [

        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            BLUE
        ),

        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            WHITE
        ),

        (
            "ALIGN",
            (0, 0),
            (0, -1),
            "CENTER"
        ),

        (
            "ALIGN",
            (2, 1),
            (-1, -1),
            "CENTER"
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.45,
            SLATE_300
        ),

        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -2),

            [
                WHITE,
                SLATE_50
            ]
        ),

        (
            "BACKGROUND",
            (0, -1),
            (-1, -1),

            colors.HexColor(
                "#E0E7FF"
            )
        ),

        (
            "BOX",
            (0, -1),
            (-1, -1),

            0.8,
            BLUE
        ),

        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),

        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),

        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            7
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            7
        ),

        (
            "FONTNAME",
            (0, 1),
            (-1, -2),
            "Helvetica"
        ),

        (
            "FONTSIZE",
            (0, 1),
            (-1, -2),
            8.5
        )

    ]


    # Color performance column

    for row_index, (
        _,
        key,
        max_score
    ) in enumerate(
        SECTION_CONFIG,
        start=1
    ):

        obtained = safe_number(
            breakdown.get(
                key,
                0
            )
        )


        percentage = percentage_value(
            obtained,
            max_score
        )


        bg_color, text_color = (
            performance_colors(
                percentage
            )
        )


        marks_style.extend([

            (
                "BACKGROUND",
                (5, row_index),
                (5, row_index),
                bg_color
            ),

            (
                "TEXTCOLOR",
                (5, row_index),
                (5, row_index),
                text_color
            ),

            (
                "FONTNAME",
                (5, row_index),
                (5, row_index),
                "Helvetica-Bold"
            )

        ])


    marks_table.setStyle(
        TableStyle(
            marks_style
        )
    )


    story.append(
        marks_table
    )


    story.append(
        Spacer(
            1,
            3 * mm
        )
    )


    # ========================================================
    # PERFORMANCE SCALE
    # ========================================================

    legend = Table(

        [[

            Paragraph(
                "90-100: Outstanding",
                styles["legend"]
            ),

            Paragraph(
                "80-89: Excellent",
                styles["legend"]
            ),

            Paragraph(
                "70-79: Strong",
                styles["legend"]
            ),

            Paragraph(
                "60-69: Good",
                styles["legend"]
            ),

            Paragraph(
                "Below 60: Improve",
                styles["legend"]
            )

        ]],

        colWidths=[
            36.4 * mm
        ] * 5

    )


    legend.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                SLATE_50
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.4,
                SLATE_200
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )

        ])
    )


    story.append(
        legend
    )


    story.append(
        Spacer(
            1,
            4 * mm
        )
    )


    # ========================================================
    # PERFORMANCE SUMMARY
    # ========================================================

    story.append(

        Paragraph(
            "PERFORMANCE SUMMARY",
            styles[
                "section_title"
            ]
        )

    )


    story.append(

        info_box(

            data.get(
                "summary",
                "No summary available."
            ),

            styles

        )

    )


    story.append(
        Spacer(
            1,
            4 * mm
        )
    )


    # ========================================================
    # SKILL MATRIX
    # ========================================================

    story.append(

        Paragraph(
            "SKILLS MATRIX",
            styles[
                "section_title"
            ]
        )

    )


    matched_text = comma_text(

        data.get(
            "matched_skills",
            []
        ),

        "No matched skills detected."

    )


    missing_text = comma_text(

        data.get(
            "missing_skills",
            []
        ),

        "No major missing skills detected."

    )


    skills_table = Table(

        [

            [

                Paragraph(
                    "<b>MATCHED SKILLS</b>",
                    styles[
                        "subhead_green"
                    ]
                ),

                Paragraph(
                    "<b>MISSING / PRIORITY SKILLS</b>",
                    styles[
                        "subhead_red"
                    ]
                )

            ],

            [

                Paragraph(
                    escape(
                        matched_text
                    ),
                    styles["body"]
                ),

                Paragraph(
                    escape(
                        missing_text
                    ),
                    styles["body"]
                )

            ]

        ],

        colWidths=[
            91 * mm,
            91 * mm
        ]

    )


    skills_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (0, 0),
                GREEN_BG
            ),

            (
                "BACKGROUND",
                (1, 0),
                (1, 0),
                RED_BG
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                SLATE_200
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )


    story.append(
        skills_table
    )


    story.append(
        Spacer(
            1,
            4 * mm
        )
    )


    # ========================================================
    # READINESS INSIGHTS
    # ========================================================

    story.append(

        Paragraph(
            "READINESS INSIGHTS",
            styles[
                "section_title"
            ]
        )

    )


    strengths = bullet_text(

        data.get(
            "key_strengths",
            []
        ),

        styles

    )


    mnc_label = escape(

        str(
            data.get(
                "mnc_label",
                "N/A"
            )
        )

    )


    mnc_message = escape(

        str(
            data.get(
                "mnc_message",

                (
                    "No readiness message "
                    "available."
                )
            )
        )

    )


    insight_table = Table(

        [

            [

                Paragraph(
                    "<b>KEY STRENGTHS</b>",
                    styles[
                        "subhead_blue"
                    ]
                ),

                Paragraph(
                    "<b>MNC READINESS</b>",
                    styles[
                        "subhead_blue"
                    ]
                )

            ],

            [

                strengths,

                Paragraph(

                    (
                        f"<b>"
                        f"{num_text(mnc_chance)}% "
                        f"- {mnc_label}"
                        f"</b>"
                        f"<br/>"
                        f"{mnc_message}"
                    ),

                    styles["body"]

                )

            ]

        ],

        colWidths=[
            91 * mm,
            91 * mm
        ]

    )


    insight_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),

                colors.HexColor(
                    "#EFF6FF"
                )
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                SLATE_200
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )


    story.append(
        insight_table
    )


    story.append(
        Spacer(
            1,
            4 * mm
        )
    )


    # ========================================================
    # CAREER MATCH
    # ========================================================

    story.append(

        Paragraph(
            "CAREER FIELD ALIGNMENT",
            styles[
                "section_title"
            ]
        )

    )


    field_rows = [

        [

            Paragraph(
                "<b>Rank</b>",
                styles[
                    "table_header_center"
                ]
            ),

            Paragraph(
                "<b>Career Field</b>",
                styles[
                    "table_header"
                ]
            ),

            Paragraph(
                "<b>Match</b>",
                styles[
                    "table_header_center"
                ]
            ),

            Paragraph(
                "<b>Alignment</b>",
                styles[
                    "table_header_center"
                ]
            )

        ]

    ]


    field_matches = (
        data.get(
            "field_matches",
            []
        )
        or
        []
    )


    for rank, item in enumerate(

        field_matches[:5],

        start=1

    ):

        match = safe_number(
            item.get(
                "match",
                0
            )
        )


        field_rows.append([

            str(rank),

            Paragraph(

                escape(
                    str(
                        item.get(
                            "field",
                            "Unknown"
                        )
                    )
                ),

                styles[
                    "table_body"
                ]

            ),

            f"{num_text(match)}%",

            alignment_label(
                match
            )

        ])


    if len(field_rows) == 1:

        field_rows.append([

            "-",

            "No field match data available",

            "0%",

            "N/A"

        ])


    field_table = Table(

        field_rows,

        colWidths=[

            18 * mm,
            94 * mm,
            28 * mm,
            42 * mm

        ],

        repeatRows=1

    )


    field_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                NAVY
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                WHITE
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.45,
                SLATE_300
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),

                [
                    WHITE,
                    SLATE_50
                ]
            ),

            (
                "ALIGN",
                (0, 0),
                (0, -1),
                "CENTER"
            ),

            (
                "ALIGN",
                (2, 1),
                (-1, -1),
                "CENTER"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "FONTSIZE",
                (0, 1),
                (-1, -1),
                8.5
            )

        ])
    )


    story.append(
        field_table
    )


    story.append(
        Spacer(
            1,
            4 * mm
        )
    )


    # ========================================================
    # ROADMAP
    # ========================================================

    story.append(

        Paragraph(
            "RECOMMENDED IMPROVEMENT ROADMAP",
            styles[
                "section_title"
            ]
        )

    )


    roadmap = (
        data.get(
            "roadmap",
            []
        )
        or
        []
    )


    roadmap_rows = []


    if roadmap:

        for number, item in enumerate(

            roadmap,

            start=1

        ):

            roadmap_rows.append([

                Paragraph(
                    f"<b>{number:02d}</b>",
                    styles[
                        "roadmap_number"
                    ]
                ),

                Paragraph(

                    escape(
                        str(item)
                    ),

                    styles[
                        "body"
                    ]

                )

            ])

    else:

        roadmap_rows.append([

            "01",

            Paragraph(
                "No roadmap available.",
                styles[
                    "body"
                ]
            )

        ])


    roadmap_table = Table(

        roadmap_rows,

        colWidths=[
            14 * mm,
            168 * mm
        ]

    )


    roadmap_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),

                colors.HexColor(
                    "#EEF2FF"
                )
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.45,
                SLATE_200
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "ALIGN",
                (0, 0),
                (0, -1),
                "CENTER"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )

        ])
    )


    story.append(
        roadmap_table
    )


    story.append(
        Spacer(
            1,
            4 * mm
        )
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    story.append(

        Paragraph(
            "FINAL RECOMMENDATION",
            styles[
                "section_title"
            ]
        )

    )


    readiness = readiness_status(
        score
    )


    final_advice = escape(

        str(
            data.get(
                "final_advice",

                (
                    "No recommendation "
                    "available."
                )
            )
        )

    )


    final_table = Table(

        [

            [

                Paragraph(
                    "<b>READINESS STATUS</b>",
                    styles[
                        "final_label"
                    ]
                ),

                Paragraph(
                    "<b>FINAL ADVICE</b>",
                    styles[
                        "final_label"
                    ]
                )

            ],

            [

                Paragraph(

                    (
                        f"<b>"
                        f"{escape(readiness)}"
                        f"</b>"
                        f"<br/>"
                        f"Grade: "
                        f"{escape(grade)}"
                        f" | "
                        f"Score: "
                        f"{num_text(score)}%"
                    ),

                    styles[
                        "final_status"
                    ]

                ),

                Paragraph(

                    (
                        final_advice

                        +

                        """
                        <br/>
                        <br/>

                        <font
                            size="6"
                            color="#B45309"
                        >

                        <b>
                            Method note:
                        </b>

                        ATSLens is an internal
                        resume-to-JD readiness
                        estimate, not an employer's
                        official ATS score.

                        </font>
                        """
                    ),

                    styles["body"]

                )

            ]

        ],

        colWidths=[
            55 * mm,
            127 * mm
        ]

    )


    final_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                NAVY
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                WHITE
            ),

            (
                "BACKGROUND",
                (0, 1),
                (0, 1),

                colors.HexColor(
                    "#EEF2FF"
                )
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                SLATE_300
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                9
            )

        ])
    )


    story.append(
        final_table
    )


    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(

        story,

        onFirstPage=draw_page_footer,

        onLaterPages=draw_page_footer

    )


    buffer.seek(0)

    return buffer


# ============================================================
# STYLES
# ============================================================

def build_styles():

    base = getSampleStyleSheet()


    return {

        "brand":

            ParagraphStyle(

                "Brand",

                parent=base["Normal"],

                fontName="Helvetica-Bold",

                fontSize=16,

                leading=18,

                textColor=WHITE

            ),


        "header_right":

            ParagraphStyle(

                "HeaderRight",

                parent=base["Normal"],

                fontSize=11,

                leading=15,

                alignment=TA_RIGHT,

                textColor=WHITE

            ),


        "section_title":

            ParagraphStyle(

                "SectionTitle",

                parent=base[
                    "Heading2"
                ],

                fontName=(
                    "Helvetica-Bold"
                ),

                fontSize=10.5,

                leading=13,

                textColor=NAVY,

                spaceBefore=2,

                spaceAfter=4

            ),


        "small":

            ParagraphStyle(

                "Small",

                parent=base["Normal"],

                fontSize=8.5,

                leading=12,

                textColor=(
                    SLATE_900
                )

            ),


        "metric_value":

            ParagraphStyle(

                "MetricValue",

                parent=base[
                    "Normal"
                ],

                fontName=(
                    "Helvetica-Bold"
                ),

                fontSize=13,

                leading=16,

                alignment=(
                    TA_CENTER
                ),

                textColor=NAVY

            ),


        "table_header":

            ParagraphStyle(

                "TableHeader",

                parent=base[
                    "Normal"
                ],

                fontSize=7.5,

                leading=9,

                textColor=WHITE

            ),


        "table_header_center":

            ParagraphStyle(

                "TableHeaderCenter",

                parent=base[
                    "Normal"
                ],

                fontSize=7.5,

                leading=9,

                textColor=WHITE,

                alignment=(
                    TA_CENTER
                )

            ),


        "table_body":

            ParagraphStyle(

                "TableBody",

                parent=base[
                    "Normal"
                ],

                fontSize=8.5,

                leading=11,

                textColor=(
                    SLATE_700
                )

            ),


        "table_total":

            ParagraphStyle(

                "TableTotal",

                parent=base[
                    "Normal"
                ],

                fontSize=8.5,

                leading=11,

                textColor=NAVY

            ),


        "table_total_center":

            ParagraphStyle(

                "TableTotalCenter",

                parent=base[
                    "Normal"
                ],

                fontSize=8.5,

                leading=11,

                alignment=(
                    TA_CENTER
                ),

                textColor=NAVY

            ),


        "legend":

            ParagraphStyle(

                "Legend",

                parent=base[
                    "Normal"
                ],

                fontSize=6.4,

                leading=8,

                alignment=(
                    TA_CENTER
                ),

                textColor=(
                    SLATE_600
                )

            ),


        "body":

            ParagraphStyle(

                "Body",

                parent=base[
                    "Normal"
                ],

                fontSize=8.5,

                leading=12.5,

                textColor=(
                    SLATE_700
                )

            ),


        "subhead_green":

            ParagraphStyle(

                "SubheadGreen",

                parent=base[
                    "Normal"
                ],

                fontSize=8,

                leading=10,

                textColor=GREEN

            ),


        "subhead_red":

            ParagraphStyle(

                "SubheadRed",

                parent=base[
                    "Normal"
                ],

                fontSize=8,

                leading=10,

                textColor=RED

            ),


        "subhead_blue":

            ParagraphStyle(

                "SubheadBlue",

                parent=base[
                    "Normal"
                ],

                fontSize=8,

                leading=10,

                textColor=BLUE

            ),


        "roadmap_number":

            ParagraphStyle(

                "RoadmapNumber",

                parent=base[
                    "Normal"
                ],

                fontSize=8,

                leading=11,

                alignment=(
                    TA_CENTER
                ),

                textColor=BLUE

            ),


        "final_label":

            ParagraphStyle(

                "FinalLabel",

                parent=base[
                    "Normal"
                ],

                fontSize=7.5,

                leading=9,

                textColor=WHITE

            ),


        "final_status":

            ParagraphStyle(

                "FinalStatus",

                parent=base[
                    "Normal"
                ],

                fontSize=10,

                leading=14,

                textColor=NAVY

            )

    }


# ============================================================
# COMPONENT HELPERS
# ============================================================

def label_value(
    label,
    value,
    styles
):

    safe_label = escape(
        str(label)
    )


    safe_value = escape(

        str(
            value
            if value not in (
                None,
                ""
            )
            else
            "N/A"
        )

    )


    return Paragraph(

        (
            f"""
            <font
                color="#64748B"
                size="7"
            >
                <b>
                    {safe_label}
                </b>
            </font>

            <br/>

            <font
                color="#0F172A"
                size="9"
            >
                <b>
                    {safe_value}
                </b>
            </font>
            """
        ),

        styles["small"]

    )


def metric_cell(
    label,
    value,
    styles
):

    return Paragraph(

        (
            f"""
            <font
                color="#64748B"
                size="6"
            >

                <b>
                    {escape(str(label))}
                </b>

            </font>

            <br/>

            <font
                color="#0B1739"
                size="12"
            >

                <b>
                    {escape(str(value))}
                </b>

            </font>
            """
        ),

        styles[
            "metric_value"
        ]

    )


def info_box(
    text,
    styles
):

    safe_text = escape(

        str(
            text
            or
            "No summary available."
        )

    )


    table = Table(

        [[

            Paragraph(
                safe_text,
                styles["body"]
            )

        ]],

        colWidths=[
            182 * mm
        ]

    )


    table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),

                colors.HexColor(
                    "#F8FAFF"
                )
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,

                colors.HexColor(
                    "#C7D2FE"
                )
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                9
            )

        ])
    )


    return table


def bullet_text(
    items,
    styles
):

    if not items:

        return Paragraph(
            "No data available.",
            styles["body"]
        )


    lines = []


    for item in items:

        lines.append(

            "- "
            +
            escape(
                str(item)
            )

        )


    return Paragraph(

        "<br/>".join(
            lines
        ),

        styles["body"]

    )


# ============================================================
# TEXT HELPERS
# ============================================================

def comma_text(
    items,
    fallback
):

    if not items:
        return fallback


    return ", ".join(

        str(item)
        for item
        in items

    )


def safe_number(
    value
):

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        return 0.0


def num_text(
    value
):

    number = safe_number(
        value
    )


    if number.is_integer():

        return str(
            int(number)
        )


    return (
        f"{number:.1f}"
        .rstrip("0")
        .rstrip(".")
    )


# ============================================================
# PERFORMANCE
# ============================================================

def percentage_value(
    score,
    max_score
):

    if not max_score:

        return 0


    return int(

        round(

            (
                safe_number(score)
                /
                safe_number(max_score)
            )
            *
            100

        )

    )


def performance_label(
    percentage
):

    if percentage >= 90:

        return "Outstanding"


    if percentage >= 80:

        return "Excellent"


    if percentage >= 70:

        return "Strong"


    if percentage >= 60:

        return "Good"


    if percentage >= 50:

        return "Average"


    return "Needs Improvement"


def performance_colors(
    percentage
):

    if percentage >= 80:

        return (
            GREEN_BG,
            GREEN
        )


    if percentage >= 60:

        return (

            colors.HexColor(
                "#EFF6FF"
            ),

            colors.HexColor(
                "#1D4ED8"
            )

        )


    if percentage >= 50:

        return (
            AMBER_BG,
            AMBER
        )


    return (
        RED_BG,
        RED
    )


def alignment_label(
    match
):

    match = safe_number(
        match
    )


    if match >= 80:

        return "Excellent Fit"


    if match >= 65:

        return "Strong Fit"


    if match >= 50:

        return "Moderate Fit"


    if match >= 35:

        return "Partial Fit"


    return "Low Fit"


def readiness_status(
    score
):

    score = safe_number(
        score
    )


    if score >= 85:

        return "HIGHLY READY"


    if score >= 75:

        return "READY TO APPLY"


    if score >= 65:

        return (
            "APPLY WITH IMPROVEMENTS"
        )


    if score >= 50:

        return (
            "NEEDS TARGETED IMPROVEMENT"
        )


    return (
        "BUILD CORE ALIGNMENT FIRST"
    )


# ============================================================
# PAGE FOOTER
# ============================================================

def draw_page_footer(
    canvas,
    doc
):

    canvas.saveState()


    width, _ = A4


    y = 9 * mm


    canvas.setStrokeColor(
        SLATE_200
    )


    canvas.setLineWidth(
        0.5
    )


    canvas.line(

        13 * mm,
        13 * mm,

        width - 13 * mm,
        13 * mm

    )


    canvas.setFont(
        "Helvetica",
        7
    )


    canvas.setFillColor(
        SLATE_500
    )


    canvas.drawString(

        13 * mm,
        y,

        (
            "ATSLens - Resume "
            "Evaluation Marksheet"
        )

    )


    canvas.drawRightString(

        width - 13 * mm,
        y,

        f"Page {doc.page}"

    )


    canvas.restoreState()