
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "virality_model.joblib"
)

METADATA_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "model_metadata.json"
)


# ============================================================
# PREDICTOR CLASS
# ============================================================

class ViralityPredictor:

    def __init__(
        self,
        model_path=MODEL_PATH,
        metadata_path=METADATA_PATH
    ):
        self.model_path = model_path
        self.metadata_path = metadata_path

        self.pipeline = None
        self.metadata = {}

        self.load_model()
        self.load_metadata()


    # ========================================================
    # LOAD MODEL
    # ========================================================

    def load_model(self):

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                "Trained virality model was not found.\n"
                f"Expected location:\n{self.model_path}\n\n"
                "Train the model first using:\n"
                "python ml/train.py"
            )

        try:
            self.pipeline = joblib.load(
                self.model_path
            )

        except Exception as e:
            raise RuntimeError(
                "Unable to load the virality model.\n"
                f"Error: {e}"
            )


    # ========================================================
    # LOAD METADATA
    # ========================================================

    def load_metadata(self):

        if not os.path.exists(
            self.metadata_path
        ):
            self.metadata = {}
            return

        try:
            with open(
                self.metadata_path,
                "r",
                encoding="utf-8"
            ) as file:

                self.metadata = json.load(file)

        except Exception:
            self.metadata = {}


    # ========================================================
    # PREPARE FEATURES
    # ========================================================

   
    def prepare_features(
        self,
        features
    ):

        if features is None:
            raise ValueError(
                "Prediction features cannot be None."
            )

        # ========================================================
        # ACCEPT DIFFERENT FEATURE FORMATS
        # ========================================================

        # Dictionary
        if isinstance(features, dict):

            df = pd.DataFrame(
                [features]
            )

        # DataFrame
        elif isinstance(features, pd.DataFrame):

            df = features.copy()

        # Series
        elif isinstance(features, pd.Series):

            df = pd.DataFrame(
                [features.to_dict()]
            )

        # List / tuple
        elif isinstance(features, (list, tuple)):

            df = pd.DataFrame(
                features
            )

        else:

            # Try converting unknown feature objects
            try:

                if hasattr(features, "to_dict"):

                    converted = features.to_dict()

                    if isinstance(converted, dict):

                        df = pd.DataFrame(
                            [converted]
                        )

                    else:

                        df = pd.DataFrame(
                            converted
                        )

                else:

                    df = pd.DataFrame(
                        [features]
                    )

            except Exception as e:

                raise TypeError(
                    "Unable to convert prediction "
                    "features into a DataFrame.\n"
                    f"Received type: {type(features)}\n"
                    f"Error: {e}"
                )


        # ========================================================
        # EXPECTED MODEL FEATURES
        # ========================================================

        try:

            from ml.feature_builder import (
                FeatureBuilder
            )

            expected_columns = (
                FeatureBuilder.NUMERIC_FEATURES
                +
                FeatureBuilder.CATEGORICAL_FEATURES
            )

        except Exception as e:

            raise RuntimeError(
                "Unable to load FeatureBuilder.\n"
                f"Error: {e}"
            )


        # ========================================================
        # ADD MISSING FEATURES
        # ========================================================

        for column in expected_columns:

            if column not in df.columns:

                df[column] = np.nan


        # ========================================================
        # KEEP ONLY MODEL FEATURES
        # ========================================================

        df = df[
            expected_columns
        ].copy()


        # ========================================================
        # CLEAN NUMERIC VALUES
        # ========================================================

        for column in FeatureBuilder.NUMERIC_FEATURES:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )


        # ========================================================
        # RETURN
        # ========================================================

        return df




    # ========================================================
    # RAW REACH PREDICTION
    # ========================================================

    def predict_reach(
        self,
        features
    ):

        X = self.prepare_features(
            features
        )

        try:

            predicted_log = self.pipeline.predict(
                X
            )

        except Exception as e:

            raise RuntimeError(
                "Prediction failed.\n"
                f"Error: {e}"
            )


        # ----------------------------------------------------
        # Model was trained using log1p(target)
        # ----------------------------------------------------

        predicted_reach = np.expm1(
            predicted_log
        )

        predicted_reach = np.maximum(
            predicted_reach,
            0
        )


        return float(
            predicted_reach[0]
        )


    # ========================================================
    # VIRALITY SCORE
    # ========================================================

    def calculate_virality_score(
        self,
        predicted_reach,
        features
    ):

        """
        Converts predicted reach into a 0-100
        virality score.

        This is a product score, not a direct
        platform algorithm score.
        """

        if predicted_reach <= 0:
            return 0.0


        # ----------------------------------------------------
        # Extract followers
        # ----------------------------------------------------

        if isinstance(
            features,
            pd.DataFrame
        ):

            followers = features.iloc[0].get(
                "followers",
                0
            )

        else:

            followers = features.get(
                "followers",
                0
            )


        try:
            followers = float(
                followers or 0
            )

        except Exception:
            followers = 0


        # ----------------------------------------------------
        # Reach multiplier
        # ----------------------------------------------------

        if followers > 0:

            reach_ratio = (
                predicted_reach
                / followers
            )

        else:

            reach_ratio = 0


        # ----------------------------------------------------
        # Convert reach ratio to score
        # ----------------------------------------------------

        if reach_ratio >= 20:
            score = 100

        elif reach_ratio >= 10:
            score = 90

        elif reach_ratio >= 5:
            score = 80

        elif reach_ratio >= 3:
            score = 70

        elif reach_ratio >= 2:
            score = 60

        elif reach_ratio >= 1:
            score = 50

        elif reach_ratio >= 0.5:
            score = 35

        else:
            score = 20


        return float(
            min(
                max(score, 0),
                100
            )
        )


    # ========================================================
    # COMPLETE PREDICTION
    # ========================================================

    def predict(
        self,
        features
    ):

        predicted_reach = (
            self.predict_reach(
                features
            )
        )

        virality_score = (
            self.calculate_virality_score(
                predicted_reach,
                features
            )
        )


        # ----------------------------------------------------
        # Estimated views
        # ----------------------------------------------------

        estimated_views = int(
            round(
                predicted_reach
            )
        )


        # ----------------------------------------------------
        # Model information
        # ----------------------------------------------------

        model_type = self.metadata.get(
            "model_type",
            "RandomForestRegressor"
        )

        training_rows = self.metadata.get(
            "training_rows",
            None
        )

        r2 = self.metadata.get(
            "metrics",
            {}
        ).get(
            "r2",
            None
        )


        return {

            "predicted_reach":
                round(
                    predicted_reach,
                    2
                ),

            "estimated_views":
                estimated_views,

            "virality_score":
                round(
                    virality_score,
                    2
                ),

            "model_type":
                model_type,

            "training_rows":
                training_rows,

            "model_r2":
                r2,

            "is_model_available":
                True
        }


# ============================================================
# SIMPLE FUNCTION API
# ============================================================

def predict_virality(
    features
):
    """
    Simple helper function for app.py.

    Example:

        result = predict_virality(
            feature_dict
        )
    """

    predictor = ViralityPredictor()

    return predictor.predict(
        features
    )


# ============================================================
# COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print(
        "AI VIRALITY PREDICTOR - "
        "PREDICTION TEST"
    )
    print("=" * 70)


    try:

        predictor = ViralityPredictor()

        print("\nModel loaded successfully.")

        print(
            "\nModel:",
            predictor.metadata.get(
                "model_type",
                "Unknown"
            )
        )

        print(
            "Training rows:",
            predictor.metadata.get(
                "training_rows",
                "Unknown"
            )
        )

        print(
            "\nPrediction system is ready."
        )

        print(
            "\nUse predict_virality(features)"
            " from app.py."
        )


    except Exception as e:

        print(
            "\nERROR:"
        )

        print(e)

