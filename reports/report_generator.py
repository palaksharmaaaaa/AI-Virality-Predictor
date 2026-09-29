import os

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from config.config import BASE_DIR


def generate_report(analysis):

    reports_folder = os.path.join(
        BASE_DIR,
        "reports",
        "generated"
    )

    os.makedirs(
        reports_folder,
        exist_ok=True
    )

    analysis_id = analysis.get(
        "id",
        "unknown"
    )

    output_path = os.path.join(
        reports_folder,
        f"virality_report_{analysis_id}.pdf"
    )

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    story = []

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "AI Virality Predictor",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    story.append(
        Paragraph(
            "Video Performance Analysis Report",
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # -----------------------------------------------------
    # Basic information
    # -----------------------------------------------------

    basic_data = [

        ["File", analysis.get(
            "filename",
            "N/A"
        )],

        ["Analysis Time", analysis.get(
            "timestamp",
            "N/A"
        )],

        ["Virality Score", str(
            round(
                float(
                    analysis.get(
                        "virality_score",
                        0
                    )
                ),
                2
            )
        )],

        ["Prediction Label", analysis.get(
            "prediction_label",
            "N/A"
        )]
    ]

    table = Table(
        basic_data,
        colWidths=[150, 330]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    story.append(table)

    story.append(
        Spacer(1, 25)
    )

    # -----------------------------------------------------
    # Feature section
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Video Features",
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 10)
    )

    feature_names = [

        ("duration", "Duration (seconds)"),

        ("fps", "FPS"),

        ("width", "Width"),

        ("height", "Height"),

        ("motion_score", "Motion Score"),

        ("scene_changes", "Scene Changes"),

        ("hook_intensity", "Hook Intensity"),

        ("face_count", "Face Count"),

        (
            "face_presence_ratio",
            "Face Presence (%)"
        ),

        ("brightness", "Brightness"),

        ("contrast", "Contrast"),

        ("pacing_score", "Pacing Score")
    ]

    feature_rows = [
        ["Feature", "Value"]
    ]

    for key, label in feature_names:

        value = analysis.get(
            key,
            0
        )

        if isinstance(
            value,
            float
        ):
            value = round(
                value,
                2
            )

        feature_rows.append(
            [label, str(value)]
        )

    feature_table = Table(
        feature_rows,
        colWidths=[250, 230]
    )

    feature_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(
        feature_table
    )

    story.append(
        Spacer(1, 25)
    )

    story.append(
        Paragraph(
            "Note: Virality predictions depend on the "
            "training data used by the model. Feature-based "
            "fallback scores are not equivalent to validated "
            "machine-learning predictions.",
            styles["BodyText"]
        )
    )

    document.build(
        story
    )

    return output_path