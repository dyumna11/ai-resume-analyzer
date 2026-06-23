from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

def create_report(
    filename,
    ats_score,
    section_scores,
    missing_skills,
    suggestions,
    questions
):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "AI Resume Analysis Report",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            f"ATS Score: {ats_score}%",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            "Section-wise Scores",
            styles["Heading2"]
        )
    )

    for section, score in section_scores.items():

        elements.append(
            Paragraph(
                f"{section}: {score}%",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            "Missing Skills",
            styles["Heading2"]
        )
    )

    for skill in missing_skills:

        elements.append(
            Paragraph(
                f"• {skill}",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            "Suggestions",
            styles["Heading2"]
        )
    )

    for item in suggestions:

        elements.append(
            Paragraph(
                f"• {item}",
                styles["BodyText"]
            )
        )

    elements.append(PageBreak())

    elements.append(
        Paragraph(
            "Interview Questions",
            styles["Heading2"]
        )
    )

    for q in questions:

        elements.append(
            Paragraph(
                q,
                styles["BodyText"]
            )
        )

    doc.build(elements)