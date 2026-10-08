# import os

# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import (
#     SimpleDocTemplate,
#     Paragraph,
#     Spacer,
#     Table,
#     TableStyle
# )

# from reportlab.lib import colors

# from reportlab.lib.styles import (
#     getSampleStyleSheet
# )

# from config.config import BASE_DIR


# def generate_report(analysis):

#     reports_folder = os.path.join(
#         BASE_DIR,
#         "reports",
#         "generated"
#     )

#     os.makedirs(
#         reports_folder,
#         exist_ok=True
#     )

#     analysis_id = analysis.get(
#         "id",
#         "unknown"
#     )

#     output_path = os.path.join(
#         reports_folder,
#         f"virality_report_{analysis_id}.pdf"
#     )

#     document = SimpleDocTemplate(
#         output_path,
#         pagesize=A4,
#         rightMargin=40,
#         leftMargin=40,
#         topMargin=40,
#         bottomMargin=40
#     )

#     styles = getSampleStyleSheet()

#     story = []

#     # -----------------------------------------------------
#     # Title
#     # -----------------------------------------------------

#     story.append(
#         Paragraph(
#             "AI Virality Predictor",
#             styles["Title"]
#         )
#     )

#     story.append(
#         Spacer(1, 15)
#     )

#     story.append(
#         Paragraph(
#             "Video Performance Analysis Report",
#             styles["Heading2"]
#         )
#     )

#     story.append(
#         Spacer(1, 20)
#     )

#     # -----------------------------------------------------
#     # Basic information
#     # -----------------------------------------------------

#     basic_data = [

#         ["File", analysis.get(
#             "filename",
#             "N/A"
#         )],

#         ["Analysis Time", analysis.get(
#             "timestamp",
#             "N/A"
#         )],

#         ["Virality Score", str(
#             round(
#                 float(
#                     analysis.get(
#                         "virality_score",
#                         0
#                     )
#                 ),
#                 2
#             )
#         )],

#         ["Prediction Label", analysis.get(
#             "prediction_label",
#             "N/A"
#         )]
#     ]

#     table = Table(
#         basic_data,
#         colWidths=[150, 330]
#     )

#     table.setStyle(
#         TableStyle([
#             (
#                 "BACKGROUND",
#                 (0, 0),
#                 (0, -1),
#                 colors.lightgrey
#             ),

#             (
#                 "GRID",
#                 (0, 0),
#                 (-1, -1),
#                 0.5,
#                 colors.grey
#             ),

#             (
#                 "PADDING",
#                 (0, 0),
#                 (-1, -1),
#                 8
#             )
#         ])
#     )

#     story.append(table)

#     story.append(
#         Spacer(1, 25)
#     )

#     # -----------------------------------------------------
#     # Feature section
#     # -----------------------------------------------------

#     story.append(
#         Paragraph(
#             "Video Features",
#             styles["Heading2"]
#         )
#     )

#     story.append(
#         Spacer(1, 10)
#     )

#     feature_names = [

#         ("duration", "Duration (seconds)"),

#         ("fps", "FPS"),

#         ("width", "Width"),

#         ("height", "Height"),

#         ("motion_score", "Motion Score"),

#         ("scene_changes", "Scene Changes"),

#         ("hook_intensity", "Hook Intensity"),

#         ("face_count", "Face Count"),

#         (
#             "face_presence_ratio",
#             "Face Presence (%)"
#         ),

#         ("brightness", "Brightness"),

#         ("contrast", "Contrast"),

#         ("pacing_score", "Pacing Score")
#     ]

#     feature_rows = [
#         ["Feature", "Value"]
#     ]

#     for key, label in feature_names:

#         value = analysis.get(
#             key,
#             0
#         )

#         if isinstance(
#             value,
#             float
#         ):
#             value = round(
#                 value,
#                 2
#             )

#         feature_rows.append(
#             [label, str(value)]
#         )

#     feature_table = Table(
#         feature_rows,
#         colWidths=[250, 230]
#     )

#     feature_table.setStyle(
#         TableStyle([

#             (
#                 "BACKGROUND",
#                 (0, 0),
#                 (-1, 0),
#                 colors.lightgrey
#             ),

#             (
#                 "GRID",
#                 (0, 0),
#                 (-1, -1),
#                 0.5,
#                 colors.grey
#             ),

#             (
#                 "PADDING",
#                 (0, 0),
#                 (-1, -1),
#                 7
#             )
#         ])
#     )

#     story.append(
#         feature_table
#     )

#     story.append(
#         Spacer(1, 25)
#     )

#     story.append(
#         Paragraph(
#             "Note: Virality predictions depend on the "
#             "training data used by the model. Feature-based "
#             "fallback scores are not equivalent to validated "
#             "machine-learning predictions.",
#             styles["BodyText"]
#         )
#     )

#     document.build(
#         story
#     )

#     return output_path


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

    # =========================================================
    # GET STORED ANALYSIS DATA
    # =========================================================

    analysis_data = analysis.get(
        "analysis_data",
        {}
    )

    if not isinstance(analysis_data, dict):
        analysis_data = {}

    video_features = analysis_data.get(
        "video_features",
        {}
    )

    audio_features = analysis_data.get(
        "audio_features",
        {}
    )

    content_features = analysis_data.get(
        "content_features",
        {}
    )

    prediction = analysis_data.get(
        "prediction",
        {}
    )

    transcript_result = analysis_data.get(
        "transcript_result",
        {}
    )

    # =========================================================
    # PDF DOCUMENT
    # =========================================================

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

    # =========================================================
    # TITLE
    # =========================================================

    story.append(
        Paragraph(
            "AI Virality Predictor",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 10)
    )

    story.append(
        Paragraph(
            "Video Analysis Report",
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # =========================================================
    # BASIC INFORMATION
    # =========================================================

    basic_data = [
        [
            "File",
            analysis.get("filename", "N/A")
        ],
        [
            "Analysis Time",
            analysis.get("timestamp", "N/A") or "N/A"
        ],
        [
            "Analysis ID",
            str(analysis_id)
        ],
        [
            "Virality Score",
            str(
                round(
                    float(
                        prediction.get(
                            "virality_score",
                            0
                        ) or 0
                    ),
                    2
                )
            )
        ],
        [
            "Prediction Label",
            prediction.get(
                "prediction_label",
                "N/A"
            )
        ],
        [
            "Estimated Views",
            f"{int(float(prediction.get('estimated_views', 0) or 0)):,}"
        ],
        [
            "Model",
            prediction.get(
                "model_type",
                "N/A"
            )
        ]
    ]

    table = Table(
        basic_data,
        colWidths=[160, 320]
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

    # =========================================================
    # VIDEO FEATURES
    # =========================================================

    story.append(
        Paragraph(
            "Video Analysis",
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
        ("scene_change_rate", "Scene Change Rate"),
        ("hook_intensity", "Hook Intensity"),
        ("person_count", "Person Count"),
        ("face_count", "Face Count"),
        ("face_presence_ratio", "Face Presence"),
        ("brightness", "Brightness"),
        ("contrast", "Contrast"),
        ("pacing_score", "Pacing Score")
    ]

    feature_rows = [
        ["Feature", "Value"]
    ]

    for key, label in feature_names:

        value = video_features.get(
            key,
            0
        )

        if isinstance(value, float):
            value = round(value, 2)

        feature_rows.append(
            [
                label,
                str(value)
            ]
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

    # =========================================================
    # AUDIO ANALYSIS
    # =========================================================

    story.append(
        Paragraph(
            "Audio Analysis",
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 10)
    )

    audio_rows = [
        ["Feature", "Value"],
        [
            "Audio Available",
            "Yes"
            if audio_features.get(
                "has_audio",
                0
            )
            else "No"
        ],
        [
            "Audio Duration",
            str(
                round(
                    float(
                        audio_features.get(
                            "audio_duration",
                            0
                        ) or 0
                    ),
                    2
                )
            )
        ],
        [
            "Speech Ratio",
            str(
                round(
                    float(
                        audio_features.get(
                            "speech_ratio",
                            0
                        ) or 0
                    ),
                    2
                )
            )
        ],
        [
            "Silence Ratio",
            str(
                round(
                    float(
                        audio_features.get(
                            "silence_ratio",
                            0
                        ) or 0
                    ),
                    2
                )
            )
        ],
        [
            "Music Ratio",
            str(
                round(
                    float(
                        audio_features.get(
                            "music_ratio",
                            0
                        ) or 0
                    ),
                    2
                )
            )
        ]
    ]

    audio_table = Table(
        audio_rows,
        colWidths=[250, 230]
    )

    audio_table.setStyle(
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
        audio_table
    )

    story.append(
        Spacer(1, 25)
    )

    # =========================================================
    # CONTENT / TRANSCRIPT
    # =========================================================

    story.append(
        Paragraph(
            "Content & Transcript Analysis",
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 10)
    )

    content_rows = [
        ["Feature", "Value"],
        [
            "Word Count",
            str(
                content_features.get(
                    "word_count",
                    0
                )
            )
        ],
        [
            "Sentence Count",
            str(
                content_features.get(
                    "sentence_count",
                    0
                )
            )
        ],
        [
            "Vocabulary Diversity",
            str(
                round(
                    float(
                        content_features.get(
                            "vocabulary_diversity",
                            0
                        ) or 0
                    ),
                    2
                )
            )
        ],
        [
            "Hook Score",
            str(
                round(
                    float(
                        content_features.get(
                            "hook_score",
                            0
                        ) or 0
                    ),
                    2
                )
            )
        ],
        [
            "CTA Score",
            str(
                round(
                    float(
                        content_features.get(
                            "cta_score",
                            0
                        ) or 0
                    ),
                    2
                )
            )
        ],
        [
            "Sentiment Score",
            str(
                round(
                    float(
                        content_features.get(
                            "sentiment_score",
                            0
                        ) or 0
                    ),
                    2
                )
            )
        ],
        [
            "Transcript Quality",
            str(
                round(
                    float(
                        content_features.get(
                            "transcript_quality",
                            0
                        ) or 0
                    ),
                    2
                )
            ]
        ]
    ]

    content_table = Table(
        content_rows,
        colWidths=[250, 230]
    )

    content_table.setStyle(
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
        content_table
    )

    story.append(
        Spacer(1, 25)
    )

    # =========================================================
    # TRANSCRIPT
    # =========================================================

    transcript = analysis_data.get(
        "transcript",
        ""
    )

    if not transcript:
        transcript = transcript_result.get(
            "transcript",
            ""
        )

    if transcript:

        story.append(
            Paragraph(
                "Transcript",
                styles["Heading2"]
            )
        )

        story.append(
            Spacer(1, 8)
        )

        story.append(
            Paragraph(
                str(transcript),
                styles["BodyText"]
            )
        )

        story.append(
            Spacer(1, 20)
        )

    # =========================================================
    # MODEL INFORMATION
    # =========================================================

    story.append(
        Paragraph(
            "Model Information",
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(1, 8)
    )

    model_rows = [
        ["Property", "Value"],
        [
            "Model Type",
            prediction.get(
                "model_type",
                "N/A"
            )
        ],
        [
            "Training Rows",
            str(
                prediction.get(
                    "training_rows",
                    "N/A"
                )
            )
        ],
        [
            "Model R²",
            str(
                round(
                    float(
                        prediction.get(
                            "model_r2",
                            0
                        ) or 0
                    ),
                    4
                )
            )
        ],
        [
            "Model Available",
            "Yes"
            if prediction.get(
                "is_model_available",
                False
            )
            else "No"
        ]
    ]

    model_table = Table(
        model_rows,
        colWidths=[250, 230]
    )

    model_table.setStyle(
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
        model_table
    )

    story.append(
        Spacer(1, 20)
    )

    # =========================================================
    # NOTE
    # =========================================================

    story.append(
        Paragraph(
            "Note: Virality predictions depend on the "
            "training data and machine-learning model used "
            "by the application.",
            styles["BodyText"]
        )
    )

    # =========================================================
    # BUILD PDF
    # =========================================================

    document.build(
        story
    )

    return output_path