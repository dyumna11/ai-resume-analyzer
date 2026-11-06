from typing import List, Dict, Any, Union
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def create_report(
    filename: str,
    ats_score: Union[int, float],
    section_scores: Dict[str, Any],
    missing_skills: List[str],
    suggestions: List[str],
    questions: List[str]
) -> str:
    """Generate a structured PDF report using ReportLab and save to filename."""
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(
        Paragraph("AI Resume Analysis Report", styles["Title"])
    )
    elements.append(Spacer(1, 14))

    # Overall ATS Score
    elements.append(
        Paragraph(f"Overall ATS Score: {ats_score}%", styles["Heading2"])
    )
    elements.append(Spacer(1, 12))

    # Section-wise Scores
    elements.append(
        Paragraph("Section-wise Breakdown", styles["Heading2"])
    )
    elements.append(Spacer(1, 6))

    if section_scores:
        for section, score in section_scores.items():
            elements.append(
                Paragraph(f"<b>{section}:</b> {score}%", styles["BodyText"])
            )
    else:
        elements.append(Paragraph("No section breakdown available.", styles["BodyText"]))

    elements.append(Spacer(1, 14))

    # Missing Skills
    elements.append(
        Paragraph("Identified Missing Skills", styles["Heading2"])
    )
    elements.append(Spacer(1, 6))

    if missing_skills:
        for skill in missing_skills:
            elements.append(
                Paragraph(f"• {skill}", styles["BodyText"])
            )
    else:
        elements.append(
            Paragraph("• No critical skills missing for this job description!", styles["BodyText"])
        )

    elements.append(Spacer(1, 14))

    # Suggestions
    elements.append(
        Paragraph("Improvement Recommendations", styles["Heading2"])
    )
    elements.append(Spacer(1, 6))

    if suggestions:
        for item in suggestions:
            elements.append(
                Paragraph(f"• {item}", styles["BodyText"])
            )
    else:
        elements.append(
            Paragraph("• Resume is well-aligned with job requirements.", styles["BodyText"])
        )

    elements.append(PageBreak())

    # Interview Questions
    elements.append(
        Paragraph("Recommended Interview Preparation Questions", styles["Heading2"])
    )
    elements.append(Spacer(1, 10))

    if questions:
        for q in questions:
            elements.append(
                Paragraph(q, styles["BodyText"])
            )
            elements.append(Spacer(1, 6))
    else:
        elements.append(
            Paragraph("No interview questions generated.", styles["BodyText"])
        )

    doc.build(elements)
    return filename
