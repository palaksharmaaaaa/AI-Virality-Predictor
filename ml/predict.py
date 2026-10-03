import os
import json
import numpy as np
import pandas as pd
import joblib

from ml.feature_builder import FeatureBuilder


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "virality_model.joblib"
)

METADATA_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model_metadata.json"
)


# ============================================================
# VIRALITY PREDICTOR
# ============================================================

class ViralityPredictor:

    def __init__(self):

        self.pipeline = None
        self.metadata = {}

        self.model_available = False

        # ----------------------------------------------------
        # Load trained model
        # ----------------------------------------------------

        if os.path.exists(MODEL_PATH):

            try:
                self.pipeline = joblib.load(MODEL_PATH)
                self.model_available = True

            except Exception as e:

                print("ERROR loading virality model:", e)
                self.pipeline = None
                self.model_available = False

        else:

            print("WARNING: Virality model not found:")
            print(MODEL_PATH)

        # ----------------------------------------------------
        # Load metadata
        # ----------------------------------------------------

        if os.path.exists(METADATA_PATH):

            try:

                with open(
                    METADATA_PATH,
                    "r",
                    encoding="utf-8"
                ) as f:

                    self.metadata = json.load(f)

            except Exception as e:

                print("WARNING: Could not load model metadata:", e)
                self.metadata = {}

    # ========================================================
    # PREPARE FEATURES
    # ========================================================

    def prepare_features(self, features):

        """
        Convert input features into the exact dataframe
        expected by the trained ML pipeline.
        """

        # ----------------------------------------------------
        # Dictionary
        # ----------------------------------------------------

        if isinstance(features, dict):

            df = pd.DataFrame([features])

        # ----------------------------------------------------
        # DataFrame
        # ----------------------------------------------------

        elif isinstance(features, pd.DataFrame):

            df = features.copy()

        # ----------------------------------------------------
        # Series
        # ----------------------------------------------------

        elif isinstance(features, pd.Series):

            df = pd.DataFrame([features.to_dict()])

        # ----------------------------------------------------
        # Other
        # ----------------------------------------------------

        else:

            raise TypeError(
                "Features must be a dictionary, pandas DataFrame "
                "or pandas Series."
            )

        # ----------------------------------------------------
        # Expected feature columns
        # ----------------------------------------------------

        expected_columns = FeatureBuilder.get_feature_columns()

        # ----------------------------------------------------
        # Add missing columns
        # ----------------------------------------------------

        for column in expected_columns:

            if column not in df.columns:

                df[column] = np.nan

        # ----------------------------------------------------
        # Keep only expected columns
        # ----------------------------------------------------

        df = df[expected_columns].copy()

        # ----------------------------------------------------
        # Numeric columns
        # ----------------------------------------------------

        numeric_columns = FeatureBuilder.NUMERIC_FEATURES

        for column in numeric_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        # ----------------------------------------------------
        # Categorical columns
        # ----------------------------------------------------

        categorical_columns = FeatureBuilder.CATEGORICAL_FEATURES

        for column in categorical_columns:

            df[column] = df[column].fillna("unknown")

            df[column] = df[column].astype(str)

        return df

    # ========================================================
    # PREDICT REACH
    # ========================================================

    def predict_reach(self, features):

        """
        Predict actual reach using trained RandomForest model.
        """

        if not self.model_available:

            return 0.0

        X = self.prepare_features(features)

        try:

            predicted_log = self.pipeline.predict(X)

            predicted_log = float(predicted_log[0])

            # Model was trained using log1p(actual_reach)
            predicted_reach = np.expm1(predicted_log)

            # Prevent negative reach
            predicted_reach = max(
                float(predicted_reach),
                0.0
            )

            return predicted_reach

        except Exception as e:

            print("ERROR during reach prediction:")
            print(e)

            return 0.0

    # ========================================================
    # VIRALITY SCORE
    # ========================================================

    def calculate_virality_score(
        self,
        predicted_reach,
        features
    ):

        """
        Convert predicted reach into a 0-100 virality score.

        IMPORTANT:
        This is a rule-based score derived from the ML predicted
        reach. It is NOT the RandomForest model's direct output.
        """

        # ----------------------------------------------------
        # Get followers
        # ----------------------------------------------------

        try:

            if isinstance(features, pd.DataFrame):

                followers = float(
                    features.iloc[0].get(
                        "followers",
                        0
                    )
                )

            elif isinstance(features, dict):

                followers = float(
                    features.get(
                        "followers",
                        0
                    )
                )

            else:

                followers = 0.0

        except (TypeError, ValueError):

            followers = 0.0

        # ----------------------------------------------------
        # Clean values
        # ----------------------------------------------------

        predicted_reach = max(
            float(predicted_reach),
            0.0
        )

        followers = max(
            followers,
            0.0
        )

        # ----------------------------------------------------
        # CASE 1
        # Followers available
        # ----------------------------------------------------

        if followers > 0:

            reach_ratio = (
                predicted_reach / followers
            )

            # No predicted reach
            if reach_ratio <= 0:

                return 0.0

            # -----------------------------------------------
            # Smooth logarithmic scoring
            # -----------------------------------------------

            log_ratio = np.log10(
                max(reach_ratio, 1e-6)
            )

            score = 100 / (
                1 + np.exp(
                    -1.5 * log_ratio
                )
            )

        # ----------------------------------------------------
        # CASE 2
        # Followers missing
        # ----------------------------------------------------

        else:

            """
            If the user does not provide follower count,
            we cannot calculate reach/follower ratio.

            Therefore use predicted reach itself.

            This prevents the old code from returning 20
            for every video.
            """

            reference_reach = 1_000_000

            score = (
                np.log1p(predicted_reach)
                /
                np.log1p(reference_reach)
            ) * 100

        # ----------------------------------------------------
        # Clamp score
        # ----------------------------------------------------

        score = max(
            0.0,
            min(
                100.0,
                score
            )
        )

        return round(
            float(score),
            2
        )

    # ========================================================
    # COMPLETE PREDICTION
    # ========================================================

    def predict(self, features):

        """
        Complete prediction.

        Returns:
            predicted reach
            estimated views
            virality score
            model information
        """

        # ----------------------------------------------------
        # Prepare features
        # ----------------------------------------------------

        prepared_features = self.prepare_features(
            features
        )

        # ----------------------------------------------------
        # Predict reach
        # ----------------------------------------------------

        predicted_reach = self.predict_reach(
            prepared_features
        )

        # ----------------------------------------------------
        # Calculate score
        # ----------------------------------------------------

        virality_score = self.calculate_virality_score(
            predicted_reach,
            prepared_features
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
            0
        )

        metrics = self.metadata.get(
            "metrics",
            {}
        )

        model_r2 = metrics.get(
            "r2",
            None
        )

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {

            "predicted_reach": round(
                predicted_reach,
                2
            ),

            "estimated_views": int(
                round(predicted_reach)
            ),

            "virality_score": round(
                virality_score,
                2
            ),

            "model_type": model_type,

            "training_rows": training_rows,

            "model_r2": model_r2,

            "is_model_available":
                self.model_available
        }


# ============================================================
# SIMPLE HELPER FUNCTION
# ============================================================

def predict_virality(features):

    predictor = ViralityPredictor()

    return predictor.predict(
        features
    )