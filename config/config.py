import os


# ---------------------------------------------------------
# Base directory
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ---------------------------------------------------------
# Project directories
# ---------------------------------------------------------

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

THUMBNAIL_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "thumbnails"
)

MODEL_FOLDER = os.path.join(
    BASE_DIR,
    "models"
)

DATABASE_FOLDER = os.path.join(
    BASE_DIR,
    "database"
)


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

DATABASE_PATH = os.path.join(
    DATABASE_FOLDER,
    "virality.db"
)


# ---------------------------------------------------------
# Machine learning model
# ---------------------------------------------------------

MODEL_PATH = os.path.join(
    MODEL_FOLDER,
    "virality_model.joblib"
)

SCALER_PATH = os.path.join(
    MODEL_FOLDER,
    "virality_scaler.joblib"
)


# ---------------------------------------------------------
# Allowed videos
# ---------------------------------------------------------

ALLOWED_EXTENSIONS = {
    "mp4",
    "mov",
    "avi",
    "mkv"
}


# ---------------------------------------------------------
# Upload limit
# ---------------------------------------------------------

MAX_CONTENT_LENGTH = (
    200 * 1024 * 1024
)


# ---------------------------------------------------------
# Video analysis configuration
# ---------------------------------------------------------

FRAME_SAMPLE_COUNT = 30

SCENE_CHANGE_THRESHOLD = 35.0

BLUR_THRESHOLD = 80.0

HOOK_DURATION_SECONDS = 3

FACE_DETECTION_SCALE = 1.1

FACE_DETECTION_NEIGHBORS = 5