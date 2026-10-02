# import os

# import pandas as pd
# import numpy as np
# import json
# import joblib

# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import (
#     mean_absolute_error,
#     mean_squared_error,
#     r2_score
# )
# from sklearn.preprocessing import StandardScaler

# from config.config import (
#     MODEL_PATH,
#     SCALER_PATH
# )

# from ml.features import FEATURE_COLUMNS


# # ---------------------------------------------------------
# # Train model
# # ---------------------------------------------------------

# def train_model(training_data_path):

#     if not os.path.exists(
#         training_data_path
#     ):
#         raise FileNotFoundError(
#             f"Training data not found: "
#             f"{training_data_path}"
#         )

#     dataframe = pd.read_csv(
#         training_data_path
#     )

#     required_columns = (
#         FEATURE_COLUMNS +
#         ["views"]
#     )

#     missing_columns = [
#         column
#         for column in required_columns
#         if column not in dataframe.columns
#     ]

#     if missing_columns:

#         raise ValueError(
#             "Missing required columns: "
#             + ", ".join(missing_columns)
#         )

#     dataframe = dataframe.dropna(
#         subset=required_columns
#     )

#     if len(dataframe) < 10:

#         raise ValueError(
#             "At least 10 valid training rows "
#             "are recommended."
#         )

#     X = dataframe[
#         FEATURE_COLUMNS
#     ].astype(float)

#     y = np.log1p(
#     dataframe["views"].astype(float)
# )

#     X_train, X_test, y_train, y_test = (
#         train_test_split(
#             X,
#             y,
#             test_size=0.2,
#             random_state=42
#         )
#     )

#     scaler = StandardScaler()

#     X_train_scaled = scaler.fit_transform(
#         X_train
#     )

#     X_test_scaled = scaler.transform(
#         X_test
#     )

#     model = RandomForestRegressor(
#         n_estimators=300,
#         random_state=42,
#         n_jobs=-1,
#         max_depth=12,
#         min_samples_leaf=2
#     )

#     model.fit(
#         X_train_scaled,
#         y_train
#     )

#     # ---------------------------------------------------------
#     # EVALUATION
#     # ---------------------------------------------------------

#     predicted_log_views = model.predict(
#         X_test_scaled
#     )

#     # Convert predictions back to actual views
#     predictions = np.expm1(
#         predicted_log_views
#     )

#     # Convert actual test values back to views
#     actual_views = np.expm1(
#         y_test
#     )

#     mae = mean_absolute_error(
#         actual_views,
#         predictions
#     )

#     rmse = mean_squared_error(
#         actual_views,
#         predictions
#     ) ** 0.5

#     r2 = r2_score(
#         actual_views,
#         predictions
# )

#     os.makedirs(
#         os.path.dirname(MODEL_PATH),
#         exist_ok=True
#     )

#     joblib.dump(
#         model,
#         MODEL_PATH
#     )

#     joblib.dump(
#         scaler,
#         SCALER_PATH
#     )

#      # ---------------------------------------------------------
#     # SAVE TRAINING METADATA
#     # ---------------------------------------------------------

#     metadata = {
#         "model_type": "RandomForestRegressor",
#         "n_estimators": 300,
#         "max_depth": 12,
#         "min_samples_leaf": 2,
#         "random_state": 42,

#         "target": "log1p(views)",
#         "prediction_target": "views",

#         "feature_columns": FEATURE_COLUMNS,
#         "training_rows": len(dataframe),

#         "mae": float(mae),
#         "rmse": float(rmse),
#         "r2": float(r2)
#     }

#     metadata_path = os.path.join(
#         os.path.dirname(MODEL_PATH),
#         "model_metadata.json"
#     )

#     with open(
#         metadata_path,
#         "w",
#         encoding="utf-8"
#     ) as file:

#         json.dump(
#             metadata,
#             file,
#             indent=4
#         )

#     print("\nMetadata saved:")
#     print(metadata_path)

#     metrics = {

#         "mae": float(mae),

#         "rmse": float(rmse),

#         "r2": float(r2),

#         "training_rows": int(
#             len(dataframe)
#         )
#     }

#     print("\nModel trained successfully.")

#     print(
#         f"MAE  : {mae:.2f}"
#     )

#     print(
#         f"RMSE : {rmse:.2f}"
#     )

#     print(
#         f"R2   : {r2:.4f}"
#     )

#     return metrics


# # ---------------------------------------------------------
# # Run directly
# # ---------------------------------------------------------

# if __name__ == "__main__":

#     BASE_DIR = os.path.dirname(
#         os.path.dirname(
#             os.path.abspath(__file__)
#         )
#     )

#     training_file = os.path.join(
#         BASE_DIR,
#         "data",
#         "training_data.csv"
#     )

#     train_model(
#         training_file
#     )

# ml/train.py

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# Allow execution:
# python ml/train.py
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.feature_builder import FeatureBuilder


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "training_features.csv"
)

MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "virality_model.joblib"
)

METADATA_PATH = os.path.join(
    MODEL_DIR,
    "model_metadata.json"
)

TARGET_COLUMN = "actual_reach"


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("\n" + "=" * 70)
print("AI VIRALITY PREDICTOR - MODEL TRAINING")
print("=" * 70)

if not os.path.exists(DATA_PATH):
    print("\nERROR:")
    print(f"Training dataset not found:")
    print(DATA_PATH)

    print("\nCreate:")
    print("data/training_features.csv")

    sys.exit(1)


df = pd.read_csv(DATA_PATH)

print(f"\nDataset shape: {df.shape}")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# DATA VALIDATION
# ============================================================

if TARGET_COLUMN not in df.columns:
    print(
        f"\nERROR: Target column '{TARGET_COLUMN}' "
        f"does not exist."
    )

    print("\nAvailable columns:")
    print(df.columns.tolist())

    sys.exit(1)


# ============================================================
# DATASET SIZE CHECK
# ============================================================

if len(df) < 20:
    print("\nWARNING:")
    print(
        f"Only {len(df)} training rows found."
    )
    print(
        "This dataset is suitable only for "
        "development/testing."
    )
    print(
        "For a reliable production model, collect "
        "substantially more labeled videos."
    )

if len(df) < 10:
    print(
        "\nERROR: Dataset is too small even for "
        "development training."
    )
    print(
        "Minimum development requirement: 10 rows."
    )
    sys.exit(1)


# ============================================================
# REMOVE INVALID TARGETS
# ============================================================

df[TARGET_COLUMN] = pd.to_numeric(
    df[TARGET_COLUMN],
    errors="coerce"
)

df = df.dropna(
    subset=[TARGET_COLUMN]
)

df = df[
    df[TARGET_COLUMN] >= 0
].copy()


if len(df) < 10:
    print(
        "\nERROR: Not enough valid target values "
        "after cleaning."
    )
    sys.exit(1)


# ============================================================
# FEATURE LIST
# ============================================================

numeric_features = FeatureBuilder.NUMERIC_FEATURES
categorical_features = FeatureBuilder.CATEGORICAL_FEATURES

feature_columns = (
    numeric_features +
    categorical_features
)


# ============================================================
# CHECK MISSING FEATURES
# ============================================================

missing_features = [
    col
    for col in feature_columns
    if col not in df.columns
]

if missing_features:
    print("\nERROR: Missing feature columns:")

    for column in missing_features:
        print(" -", column)

    print(
        "\nYour training CSV must contain all "
        "feature columns."
    )

    sys.exit(1)


# ============================================================
# FEATURES / TARGET
# ============================================================

X = df[feature_columns].copy()

y = df[TARGET_COLUMN].astype(float)


# ============================================================
# LOG TRANSFORM TARGET
# ============================================================

"""
Social reach/views are usually heavily skewed.

Example:
1000
3000
8000
50000
500000
5000000

Training directly on these values can make the model
over-focus on extremely large accounts.

log1p makes the target easier for the model to learn.
"""

y_log = np.log1p(y)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_log,
    test_size=0.20,
    random_state=42
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# NUMERIC PIPELINE
# ============================================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]
)


# ============================================================
# CATEGORICAL PIPELINE
# ============================================================

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            )
        )
    ]
)


# ============================================================
# PREPROCESSOR
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_pipeline,
            numeric_features
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ],
    remainder="drop"
)


# ============================================================
# MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=400,
    max_depth=18,
    min_samples_split=4,
    min_samples_leaf=2,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1
)


# ============================================================
# COMPLETE PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            model
        )
    ]
)


# ============================================================
# TRAIN
# ============================================================

print("\nTraining model...")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed.")


# ============================================================
# PREDICTION
# ============================================================

predicted_log = pipeline.predict(
    X_test
)

predicted_reach = np.maximum(
    np.expm1(predicted_log),
    0
)

actual_reach = np.maximum(
    np.expm1(y_test),
    0
)


# ============================================================
# METRICS
# ============================================================

mae = mean_absolute_error(
    actual_reach,
    predicted_reach
)

rmse = np.sqrt(
    mean_squared_error(
        actual_reach,
        predicted_reach
    )
)

r2 = r2_score(
    actual_reach,
    predicted_reach
)


print("\n" + "=" * 70)
print("MODEL PERFORMANCE")
print("=" * 70)

print(
    f"\nMAE  : {mae:,.2f}"
)

print(
    f"RMSE : {rmse:,.2f}"
)

print(
    f"R²   : {r2:.4f}"
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    pipeline,
    MODEL_PATH
)


# ============================================================
# SAVE MODEL METADATA
# ============================================================

metadata = {
    "model_type": "RandomForestRegressor",
    "target": TARGET_COLUMN,
    "target_transform": "log1p",
    "n_estimators": 400,
    "feature_count": len(feature_columns),
    "numeric_features": numeric_features,
    "categorical_features": categorical_features,
    "training_rows": int(len(X_train)),
    "testing_rows": int(len(X_test)),
    "metrics": {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    },
    "platforms": [
        "instagram",
        "youtube",
        "tiktok",
        "facebook"
    ]
}

with open(
    METADATA_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        metadata,
        file,
        indent=4
    )


print("\n" + "=" * 70)
print("MODEL SAVED")
print("=" * 70)

print(
    f"\nModel:"
    f"\n{MODEL_PATH}"
)

print(
    f"\nMetadata:"
    f"\n{METADATA_PATH}"
)

print("\nTraining finished successfully.")