import os


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# DIRECT CONFIG VARIABLES
# ============================================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "ai-virality-predictor-secret-key"
)


UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "data",
    "uploads"
)


MAX_CONTENT_LENGTH = 200 * 1024 * 1024


DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "virality.db"
)


MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "virality_model.joblib"
)


SCALER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "virality_scaler.joblib"
)


METADATA_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model_metadata.json"
)


ALLOWED_EXTENSIONS = {
    "mp4",
    "mov",
    "avi",
    "mkv",
    "webm",
    "m4v"
}


# ============================================================
# CONFIG CLASS
# ============================================================

class Config:

    SECRET_KEY = SECRET_KEY

    UPLOAD_FOLDER = UPLOAD_FOLDER

    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH

    DATABASE_PATH = DATABASE_PATH

    MODEL_PATH = MODEL_PATH

    SCALER_PATH = SCALER_PATH

    METADATA_PATH = METADATA_PATH

    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    os.path.dirname(DATABASE_PATH),
    exist_ok=True
)

os.makedirs(
    os.path.join(
        BASE_DIR,
        "models"
    ),
    exist_ok=True
)