import os

import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.preprocessing import StandardScaler

from config.config import (
    MODEL_PATH,
    SCALER_PATH
)

from ml.features import FEATURE_COLUMNS


# =========================================================
# TRAIN MODEL
# =========================================================

# def train_model(training_data_path):

#     if not os.path.exists(training_data_path):
#         raise FileNotFoundError(
#             f"Training data not found: {training_data_path}"
#         )

#     # dataframe = pd.read_csv(training_data_path)
#     dataframe = pd.read_csv(training_data_path, low_memory=False)

#     # Remove accidental repeated header rows
#     if "video_id" in dataframe.columns:
#         dataframe = dataframe[
#             dataframe["video_id"].astype(str).str.strip().ne("video_id")
#         ]

#     # Convert all ML columns and target to numeric
#     required_columns = FEATURE_COLUMNS + ["views"]

#     for column in required_columns:
#         dataframe[column] = pd.to_numeric(
#             dataframe[column],
#             errors="coerce"
#         )

#     # Remove invalid rows
#     dataframe = dataframe.dropna(subset=required_columns).reset_index(drop=True)

#     required_columns = FEATURE_COLUMNS + ["views"]

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
#             "At least 10 valid training rows are recommended."
#         )

#     X = dataframe[
#         FEATURE_COLUMNS
#     ].astype(float)

#     y = dataframe[
#         "views"
#     ].astype(float)

#     X_train, X_test, y_train, y_test = train_test_split(
#         X,
#         y,
#         test_size=0.2,
#         random_state=42
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

#     predictions = model.predict(
#         X_test_scaled
#     )

#     mae = mean_absolute_error(
#         y_test,
#         predictions
#     )

#     rmse = mean_squared_error(
#         y_test,
#         predictions
#     ) ** 0.5

#     r2 = r2_score(
#         y_test,
#         predictions
#     )

#     model_directory = os.path.dirname(
#         MODEL_PATH
#     )

#     if model_directory:
#         os.makedirs(
#             model_directory,
#             exist_ok=True
#         )

#     scaler_directory = os.path.dirname(
#         SCALER_PATH
#     )

#     if scaler_directory:
#         os.makedirs(
#             scaler_directory,
#             exist_ok=True
#         )

#     joblib.dump(
#         model,
#         MODEL_PATH
#     )

#     joblib.dump(
#         scaler,
#         SCALER_PATH
#     )

#     metrics = {
#         "mae": float(mae),
#         "rmse": float(rmse),
#         "r2": float(r2),
#         "training_rows": int(len(dataframe))
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



def train_model(training_data_path):
    if not os.path.exists(training_data_path):
        raise FileNotFoundError(
            f"Training data not found at: {training_data_path}"
        )

    dataframe = pd.read_csv(
        training_data_path,
        low_memory=False
    )

    print(f"Original training data shape: {dataframe.shape}")

    required_columns = FEATURE_COLUMNS + ["views"]

    # Check required columns
    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # ---------------------------------------------------------
    # REMOVE ACCIDENTAL REPEATED HEADER ROWS
    # ---------------------------------------------------------

    if "video_id" in dataframe.columns:
        dataframe = dataframe[
            dataframe["video_id"].astype(str).str.strip() != "video_id"
        ]

    # ---------------------------------------------------------
    # CONVERT ML FEATURES TO NUMERIC
    # Invalid text becomes NaN
    # ---------------------------------------------------------

    for column in required_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce"
        )

    # ---------------------------------------------------------
    # REMOVE INVALID ROWS
    # ---------------------------------------------------------

    before_cleaning = len(dataframe)

    dataframe = dataframe.dropna(
        subset=required_columns
    ).reset_index(drop=True)

    removed_rows = before_cleaning - len(dataframe)

    print(f"Removed invalid rows: {removed_rows}")
    print(f"Valid training rows: {len(dataframe)}")

    # ---------------------------------------------------------
    # MINIMUM DATA CHECK
    # ---------------------------------------------------------

    if len(dataframe) < 19:
        raise ValueError(
            f"Only {len(dataframe)} valid training rows found. "
            "At least 19 valid rows are required."
        )

    # ---------------------------------------------------------
    # FEATURES / TARGET
    # ---------------------------------------------------------

    X = dataframe[FEATURE_COLUMNS].astype(float)
    y = dataframe["views"].astype(float)

    print("\nTraining features:")
    print(X.columns.tolist())

    print("\nTarget statistics:")
    print(y.describe())

    # ---------------------------------------------------------
    # TRAIN / TEST SPLIT
    # ---------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # ---------------------------------------------------------
    # SCALING
    # ---------------------------------------------------------

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ---------------------------------------------------------
    # MODEL
    # ---------------------------------------------------------

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        max_depth=12,
        min_samples_leaf=2
    )

    model.fit(
        X_train_scaled,
        y_train
    )

    # ---------------------------------------------------------
    # EVALUATION
    # ---------------------------------------------------------

    predictions = model.predict(X_test_scaled)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    print("\n==============================")
    print("MODEL TRAINING COMPLETE")
    print("==============================")
    print(f"MAE  : {mae:.2f}")
    print(f"RMSE : {rmse:.2f}")
    print(f"R2   : {r2:.4f}")

    # ---------------------------------------------------------
    # SAVE MODEL
    # ---------------------------------------------------------

    os.makedirs(
        os.path.dirname(MODEL_PATH),
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    joblib.dump(
        scaler,
        SCALER_PATH
    )

    print("\nModel saved:")
    print(MODEL_PATH)

    print("\nScaler saved:")
    print(SCALER_PATH)

    return {
        "model": model,
        "scaler": scaler,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "training_rows": len(dataframe)
    }


# =========================================================
# LOAD MODEL
# =========================================================

def load_model():

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Trained model not found. "
            "Please train the model first."
        )

    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(
            "Scaler not found. "
            "Please train the model first."
        )

    model = joblib.load(
        MODEL_PATH
    )

    scaler = joblib.load(
        SCALER_PATH
    )

    return model, scaler


# =========================================================
# PREDICT VIRALITY
# =========================================================

def predict_virality(features):

    """
    Predict expected video views / virality score.

    Parameters
    ----------
    features : dict or pandas.DataFrame

        Video features generated by extract_video_features().

    Returns
    -------
    dict

        Contains predicted views and a normalized
        virality score.
    """

    model, scaler = load_model()

    # -----------------------------------------------------
    # Convert input into DataFrame
    # -----------------------------------------------------

    if isinstance(features, dict):

        input_data = {
            column: features.get(column, 0.0)
            for column in FEATURE_COLUMNS
        }

        dataframe = pd.DataFrame(
            [input_data]
        )

    elif isinstance(features, pd.DataFrame):

        dataframe = features.copy()

        missing_columns = [
            column
            for column in FEATURE_COLUMNS
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing prediction features: "
                + ", ".join(missing_columns)
            )

        dataframe = dataframe[
            FEATURE_COLUMNS
        ]

    else:

        raise TypeError(
            "features must be a dictionary "
            "or pandas DataFrame."
        )

    # -----------------------------------------------------
    # Ensure numeric values
    # -----------------------------------------------------

    dataframe = dataframe[
        FEATURE_COLUMNS
    ].astype(float)

    # -----------------------------------------------------
    # Scale features
    # -----------------------------------------------------

    scaled_features = scaler.transform(
        dataframe
    )

    # -----------------------------------------------------
    # Predict views
    # -----------------------------------------------------

    predicted_views = model.predict(
        scaled_features
    )

    predicted_views = float(
        max(
            0,
            predicted_views[0]
        )
    )

    # -----------------------------------------------------
    # Convert prediction into a 0-100 score
    #
    # This is NOT the model's actual probability.
    # It is a presentation score based on predicted views.
    # -----------------------------------------------------

    virality_score = calculate_virality_score(
        predicted_views
    )

    return {
        "predicted_views": predicted_views,
        "virality_score": virality_score,
        "is_model_available": True,
        "prediction_mode": "ML Model"
    }


# =========================================================
# VIRALITY SCORE 
# =========================================================

def calculate_virality_score(predicted_views):

    """
    Convert predicted views into a 0-100 presentation score.

    The score is logarithmically scaled so that very large
    view counts do not completely dominate the UI.
    """

    import math

    if predicted_views <= 0:
        return 0.0

    # Reference points:
    # 1,000 views  -> approximately low score
    # 1,000,000 views -> high score

    minimum_views = 1_000
    reference_views = 1_000_000

    log_min = math.log10(
        minimum_views
    )

    log_reference = math.log10(
        reference_views
    )

    log_views = math.log10(
        max(
            predicted_views,
            minimum_views
        )
    )

    score = (
        (log_views - log_min)
        /
        (log_reference - log_min)
    ) * 100

    return round(
    float(
        max(
            0,
            min(
                100,
                score
            )
        )
    ),
    2
)


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    training_file = os.path.join(
        BASE_DIR,
        "data",
        "training_data.csv"
    )

    train_model(
        training_file
    )