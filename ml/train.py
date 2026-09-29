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


# ---------------------------------------------------------
# Train model
# ---------------------------------------------------------

def train_model(training_data_path):

    if not os.path.exists(
        training_data_path
    ):
        raise FileNotFoundError(
            f"Training data not found: "
            f"{training_data_path}"
        )

    dataframe = pd.read_csv(
        training_data_path
    )

    required_columns = (
        FEATURE_COLUMNS +
        ["views"]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    dataframe = dataframe.dropna(
        subset=required_columns
    )

    if len(dataframe) < 10:

        raise ValueError(
            "At least 10 valid training rows "
            "are recommended."
        )

    X = dataframe[
        FEATURE_COLUMNS
    ].astype(float)

    y = dataframe[
        "views"
    ].astype(float)

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )
    )

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train
    )

    X_test_scaled = scaler.transform(
        X_test
    )

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

    predictions = model.predict(
        X_test_scaled
    )

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

    metrics = {

        "mae": float(mae),

        "rmse": float(rmse),

        "r2": float(r2),

        "training_rows": int(
            len(dataframe)
        )
    }

    print("\nModel trained successfully.")

    print(
        f"MAE  : {mae:.2f}"
    )

    print(
        f"RMSE : {rmse:.2f}"
    )

    print(
        f"R2   : {r2:.4f}"
    )

    return metrics


# ---------------------------------------------------------
# Run directly
# ---------------------------------------------------------

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