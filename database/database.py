
# import sqlite3
# import os
# import json

# from config.config import DATABASE_PATH


# # ---------------------------------------------------------
# # Database connection
# # ---------------------------------------------------------

# def get_connection():

#     db_directory = os.path.dirname(DATABASE_PATH)

#     if db_directory:
#         os.makedirs(
#             db_directory,
#             exist_ok=True
#         )

#     connection = sqlite3.connect(
#         DATABASE_PATH
#     )

#     connection.row_factory = sqlite3.Row

#     return connection


# # ---------------------------------------------------------
# # Initialize database
# # ---------------------------------------------------------

# def initialize_database():

#     connection = get_connection()

#     connection.execute("""
#         CREATE TABLE IF NOT EXISTS analyses (

#             id INTEGER PRIMARY KEY AUTOINCREMENT,

#             filename TEXT NOT NULL,

#             timestamp TEXT NOT NULL,

#             duration REAL,

#             fps REAL,

#             width INTEGER,

#             height INTEGER,

#             motion_score REAL,

#             scene_changes INTEGER,

#             hook_intensity REAL,

#             face_count INTEGER,

#             face_presence_ratio REAL,

#             brightness REAL,

#             contrast REAL,

#             pacing_score REAL,

#             virality_score REAL,

#             prediction_label TEXT,

#             analysis_data TEXT

#         )
#     """)


#         # -----------------------------------------------------
#     # Add analysis_data column to existing databases
#     # -----------------------------------------------------

#     columns = connection.execute(
#         "PRAGMA table_info(analyses)"
#     ).fetchall()

#     column_names = [
#         column["name"]
#         for column in columns
#     ]

#     if "analysis_data" not in column_names:

#         connection.execute(
#             """
#             ALTER TABLE analyses
#             ADD COLUMN analysis_data TEXT
#             """
#         )


#     connection.commit()

#     connection.close()


# # ---------------------------------------------------------
# # Compatibility function
# # ---------------------------------------------------------
# # app.py uses init_db()
# # ---------------------------------------------------------

# def init_db():

#     initialize_database()


# # ---------------------------------------------------------
# # Save analysis
# # ---------------------------------------------------------

# def save_analysis(
#     filename,
#     analysis_data=None,
#     timestamp=None,
#     features=None,
#     prediction=None
# ):

#     connection = get_connection()

#     # -----------------------------------------------------
#     # Current app.py format
#     # -----------------------------------------------------

#     if analysis_data is not None:

#         data = analysis_data

#         timestamp = data.get(
#             "timestamp",
#             timestamp or ""
#         )

#         # Current app.py stores video information
#         # under video_features
#         features = data.get(
#             "video_features",
#             data.get(
#                 "features",
#                 {}
#             )
#         )

#         prediction = data.get(
#             "prediction",
#             {}
#         )

#     # -----------------------------------------------------
#     # Old format compatibility
#     # -----------------------------------------------------

#     else:

#         data = {}

#         features = features or {}

#         prediction = prediction or {}

#         timestamp = timestamp or ""

#     # -----------------------------------------------------
#     # Insert analysis
#     # -----------------------------------------------------

#     cursor = connection.execute(
#         """
#         INSERT INTO analyses (

#             filename,
#             timestamp,

#             duration,
#             fps,
#             width,
#             height,

#             motion_score,
#             scene_changes,
#             hook_intensity,

#             face_count,
#             face_presence_ratio,

#             brightness,
#             contrast,
#             pacing_score,

#             virality_score,
#             prediction_label,

#             analysis_data

#         )
#         VALUES (
#             ?, ?,
#             ?, ?, ?, ?,
#             ?, ?, ?,
#             ?, ?,
#             ?, ?, ?,
#             ?, ?,
#             ?
#         )
#         """,
#         (

#             filename,

#             timestamp,

#             features.get(
#                 "duration",
#                 0
#             ),

#             features.get(
#                 "fps",
#                 0
#             ),

#             features.get(
#                 "width",
#                 0
#             ),

#             features.get(
#                 "height",
#                 0
#             ),

#             features.get(
#                 "motion_score",
#                 0
#             ),

#             features.get(
#                 "scene_changes",
#                 0
#             ),

#             features.get(
#                 "hook_intensity",
#                 0
#             ),

#             features.get(
#                 "face_count",
#                 0
#             ),

#             features.get(
#                 "face_presence_ratio",
#                 0
#             ),

#             features.get(
#                 "brightness",
#                 0
#             ),

#             features.get(
#                 "contrast",
#                 0
#             ),

#             features.get(
#                 "pacing_score",
#                 0
#             ),

#             prediction.get(
#                 "virality_score",
#                 0
#             ),

#             prediction.get(
#                 "prediction_label",
#                 "Unknown"
#             ),

#             json.dumps(
#                 data,
#                 default=str
#             )

#         )
#     )

#     # -----------------------------------------------------
#     # Get newly created ID
#     # -----------------------------------------------------

#     analysis_id = cursor.lastrowid

#     connection.commit()

#     connection.close()

#     return analysis_id


# # ---------------------------------------------------------
# # Get one analysis
# # ---------------------------------------------------------

# def get_analysis(analysis_id):

#     connection = get_connection()

#     result = connection.execute(
#         """
#         SELECT *
#         FROM analyses
#         WHERE id = ?
#         """,
#         (analysis_id,)
#     ).fetchone()

#     connection.close()

#     return result


# # ---------------------------------------------------------
# # Compatibility function
# # ---------------------------------------------------------
# # app.py uses get_analysis_by_id()
# # ---------------------------------------------------------

# def get_analysis_by_id(analysis_id):

#     result = get_analysis(
#         analysis_id
#     )

#     if result is None:
#         return None

#     # -----------------------------------------------------
#     # Current analysis data
#     # -----------------------------------------------------

#     if result["analysis_data"]:

#         try:

#             analysis_data = json.loads(
#                 result["analysis_data"]
#             )

#             return {
#                 "id": result["id"],
#                 "filename": result["filename"],
#                 "timestamp": result["timestamp"],
#                 "analysis_data": analysis_data
#             }

#         except (
#             json.JSONDecodeError,
#             TypeError
#         ):

#             pass

#     # -----------------------------------------------------
#     # Compatibility for old database records
#     # -----------------------------------------------------

#     return {
#         "id": result["id"],
#         "filename": result["filename"],
#         "timestamp": result["timestamp"],

#         "analysis_data": {

#             "video_features": {

#                 "duration": result["duration"] or 0,

#                 "fps": result["fps"] or 0,

#                 "width": result["width"] or 0,

#                 "height": result["height"] or 0,

#                 "motion_score": (
#                     result["motion_score"] or 0
#                 ),

#                 "scene_changes": (
#                     result["scene_changes"] or 0
#                 ),

#                 "hook_intensity": (
#                     result["hook_intensity"] or 0
#                 ),

#                 "face_count": (
#                     result["face_count"] or 0
#                 ),

#                 "face_presence_ratio": (
#                     result["face_presence_ratio"] or 0
#                 ),

#                 "brightness": (
#                     result["brightness"] or 0
#                 ),

#                 "contrast": (
#                     result["contrast"] or 0
#                 ),

#                 "pacing_score": (
#                     result["pacing_score"] or 0
#                 )

#             },

#             "prediction": {

#                 "virality_score": (
#                     result["virality_score"] or 0
#                 ),

#                 "prediction_label": (
#                     result["prediction_label"]
#                     or "Unknown"
#                 )

#             }

#         }
#     }


# # ---------------------------------------------------------
# # Get all analyses
# # ---------------------------------------------------------

# def get_all_analyses():

#     connection = get_connection()

#     results = connection.execute(
#         """
#         SELECT *
#         FROM analyses
#         ORDER BY id DESC
#         """
#     ).fetchall()

#     connection.close()

#     return results

import sqlite3
import os
import json

from config.config import DATABASE_PATH


# ---------------------------------------------------------
# Database connection
# ---------------------------------------------------------

def get_connection():

    db_directory = os.path.dirname(DATABASE_PATH)

    if db_directory:

        os.makedirs(
            db_directory,
            exist_ok=True
        )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ---------------------------------------------------------
# Initialize database
# ---------------------------------------------------------

def initialize_database():

    connection = get_connection()

    # -----------------------------------------------------
    # Create table if it does not exist
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS analyses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT NOT NULL,

            timestamp TEXT NOT NULL,

            duration REAL,

            fps REAL,

            width INTEGER,

            height INTEGER,

            motion_score REAL,

            scene_changes INTEGER,

            hook_intensity REAL,

            face_count INTEGER,

            face_presence_ratio REAL,

            brightness REAL,

            contrast REAL,

            pacing_score REAL,

            virality_score REAL,

            prediction_label TEXT,

            analysis_data TEXT

        )
    """)

    # -----------------------------------------------------
    # Update old database if analysis_data is missing
    # -----------------------------------------------------

    columns = connection.execute(
        "PRAGMA table_info(analyses)"
    ).fetchall()

    column_names = [
        column["name"]
        for column in columns
    ]

    if "analysis_data" not in column_names:

        connection.execute(
            """
            ALTER TABLE analyses
            ADD COLUMN analysis_data TEXT
            """
        )

    connection.commit()

    connection.close()


# ---------------------------------------------------------
# Compatibility function
# ---------------------------------------------------------

def init_db():

    initialize_database()


# ---------------------------------------------------------
# Save analysis
# ---------------------------------------------------------

def save_analysis(
    filename,
    analysis_data=None,
    timestamp=None,
    features=None,
    prediction=None
):

    connection = get_connection()

    # -----------------------------------------------------
    # Current app.py format
    # -----------------------------------------------------

    if analysis_data is not None:

        data = analysis_data

        # Timestamp
        timestamp = data.get(
            "timestamp",
            timestamp or ""
        )

        # -------------------------------------------------
        # IMPORTANT:
        # Current app.py uses "video_features"
        # -------------------------------------------------

        features = data.get(
            "video_features",
            data.get(
                "features",
                {}
            )
        )

        # Prediction
        prediction = data.get(
            "prediction",
            {}
        )

    # -----------------------------------------------------
    # Old format compatibility
    # -----------------------------------------------------

    else:

        data = {}

        features = features or {}

        prediction = prediction or {}

        timestamp = timestamp or ""

    # -----------------------------------------------------
    # Save complete analysis as JSON
    # -----------------------------------------------------

    analysis_json = json.dumps(
        data,
        default=str
    )

    # -----------------------------------------------------
    # Insert analysis
    # -----------------------------------------------------

    cursor = connection.execute(
        """
        INSERT INTO analyses (

            filename,
            timestamp,

            duration,
            fps,
            width,
            height,

            motion_score,
            scene_changes,
            hook_intensity,

            face_count,
            face_presence_ratio,

            brightness,
            contrast,
            pacing_score,

            virality_score,
            prediction_label,

            analysis_data

        )

        VALUES (
            ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?,
            ?, ?, ?,
            ?, ?,
            ?
        )
        """,

        (

            filename,

            timestamp,

            features.get(
                "duration",
                0
            ),

            features.get(
                "fps",
                0
            ),

            features.get(
                "width",
                0
            ),

            features.get(
                "height",
                0
            ),

            features.get(
                "motion_score",
                0
            ),

            features.get(
                "scene_changes",
                0
            ),

            features.get(
                "hook_intensity",
                0
            ),

            features.get(
                "face_count",
                0
            ),

            features.get(
                "face_presence_ratio",
                0
            ),

            features.get(
                "brightness",
                0
            ),

            features.get(
                "contrast",
                0
            ),

            features.get(
                "pacing_score",
                0
            ),

            prediction.get(
                "virality_score",
                0
            ),

            prediction.get(
                "prediction_label",
                "Unknown"
            ),

            analysis_json

        )
    )

    # -----------------------------------------------------
    # Get new ID
    # -----------------------------------------------------

    analysis_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return analysis_id


# ---------------------------------------------------------
# Get one analysis
# ---------------------------------------------------------

def get_analysis(analysis_id):

    connection = get_connection()

    result = connection.execute(
        """
        SELECT *
        FROM analyses
        WHERE id = ?
        """,
        (analysis_id,)
    ).fetchone()

    connection.close()

    return result


# ---------------------------------------------------------
# Get one analysis by ID
# ---------------------------------------------------------

def get_analysis_by_id(analysis_id):

    result = get_analysis(
        analysis_id
    )

    if result is None:
        return None

    # -----------------------------------------------------
    # Convert SQLite row to normal dictionary
    # -----------------------------------------------------

    row = dict(result)

    # -----------------------------------------------------
    # Current complete analysis
    # -----------------------------------------------------

    analysis_json = row.get(
        "analysis_data"
    )

    if analysis_json:

        try:

            analysis_data = json.loads(
                analysis_json
            )

            return {
                "id": row.get(
                    "id"
                ),

                "filename": row.get(
                    "filename"
                ),

                "timestamp": row.get(
                    "timestamp"
                ),

                "analysis_data": analysis_data
            }

        except (
            json.JSONDecodeError,
            TypeError
        ):

            pass

    # -----------------------------------------------------
    # Old records compatibility
    # -----------------------------------------------------

    return {

        "id": row.get(
            "id"
        ),

        "filename": row.get(
            "filename"
        ),

        "timestamp": row.get(
            "timestamp"
        ),

        "analysis_data": {

            "video_features": {

                "duration": row.get(
                    "duration",
                    0
                ) or 0,

                "fps": row.get(
                    "fps",
                    0
                ) or 0,

                "width": row.get(
                    "width",
                    0
                ) or 0,

                "height": row.get(
                    "height",
                    0
                ) or 0,

                "motion_score": row.get(
                    "motion_score",
                    0
                ) or 0,

                "scene_changes": row.get(
                    "scene_changes",
                    0
                ) or 0,

                "hook_intensity": row.get(
                    "hook_intensity",
                    0
                ) or 0,

                "face_count": row.get(
                    "face_count",
                    0
                ) or 0,

                "face_presence_ratio": row.get(
                    "face_presence_ratio",
                    0
                ) or 0,

                "brightness": row.get(
                    "brightness",
                    0
                ) or 0,

                "contrast": row.get(
                    "contrast",
                    0
                ) or 0,

                "pacing_score": row.get(
                    "pacing_score",
                    0
                ) or 0

            },

            "prediction": {

                "virality_score": row.get(
                    "virality_score",
                    0
                ) or 0,

                "prediction_label": row.get(
                    "prediction_label",
                    "Unknown"
                ) or "Unknown"

            }

        }
    }


# ---------------------------------------------------------
# Get all analyses
# ---------------------------------------------------------

def get_all_analyses():

    connection = get_connection()

    results = connection.execute(
        """
        SELECT *
        FROM analyses
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return results
