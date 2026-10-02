import sqlite3
import os

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

            prediction_label TEXT

        )
    """)

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# Compatibility function
# ---------------------------------------------------------
# app.py uses init_db()
# ---------------------------------------------------------

def init_db():
    initialize_database()


# ---------------------------------------------------------
# Save analysis
# ---------------------------------------------------------

def save_analysis(
    filename,
    timestamp,
    features,
    prediction
):

    connection = get_connection()

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
            prediction_label
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            filename,
            timestamp,

            features.get("duration", 0),
            features.get("fps", 0),
            features.get("width", 0),
            features.get("height", 0),

            features.get("motion_score", 0),
            features.get("scene_changes", 0),
            features.get("hook_intensity", 0),

            features.get("face_count", 0),
            features.get("face_presence_ratio", 0),

            features.get("brightness", 0),
            features.get("contrast", 0),

            features.get("pacing_score", 0),

            prediction.get("virality_score", 0),
            prediction.get("prediction_label", "Unknown")
        )
    )

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
# Compatibility function
# ---------------------------------------------------------
# app.py uses get_analysis_by_id()
# ---------------------------------------------------------

def get_analysis_by_id(analysis_id):
    return get_analysis(analysis_id)


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