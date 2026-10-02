# """
# Build training_data.csv from real local videos.

# Input:
#     data/dataset_manifest.csv

# Manifest columns:
#     video_id,video_path,views,likes

# The video features are extracted automatically using
# the project's OpenCV feature extractor.
# """

# from pathlib import Path
# import pandas as pd

# from video.extractor import extract_video_features


# BASE_DIR = Path(__file__).resolve().parents[1]

# MANIFEST_PATH = BASE_DIR / "data" / "dataset_manifest.csv"
# OUTPUT_PATH = BASE_DIR / "data" / "training_data.csv"


# FEATURE_COLUMNS = [
#     "duration",
#     "fps",
#     "width",
#     "height",
#     "motion_score",
#     "scene_changes",
#     "hook_intensity",
#     "face_count",
#     "face_presence_ratio",
#     "brightness",
#     "contrast",
#     "pacing_score",
# ]


# def resolve_video_path(video_path):
#     path = Path(str(video_path))

#     if path.is_absolute():
#         return path

#     project_path = BASE_DIR / path

#     if project_path.exists():
#         return project_path

#     data_path = BASE_DIR / "data" / path

#     if data_path.exists():
#         return data_path

#     return project_path


# def main():

#     print("=" * 70)
#     print("REAL VIDEO DATASET BUILDER")
#     print("=" * 70)

#     if not MANIFEST_PATH.exists():
#         raise FileNotFoundError(
#             f"\nManifest not found:\n{MANIFEST_PATH}\n\n"
#             "Create data/dataset_manifest.csv first."
#         )

#     manifest = pd.read_csv(MANIFEST_PATH)

#     required = [
#         "video_id",
#         "video_path",
#         "views",
#     ]

#     missing = [
#         col for col in required
#         if col not in manifest.columns
#     ]

#     if missing:
#         raise ValueError(
#             f"Missing columns in manifest: {missing}\n"
#             f"Required columns: {required}"
#         )

#     print(f"\nVideos listed: {len(manifest)}")

#     rows = []

#     success_count = 0
#     skipped_count = 0

#     for index, record in manifest.iterrows():

#         video_id = str(record["video_id"]).strip()
#         video_path = resolve_video_path(record["video_path"])

#         try:
#             views = float(record["views"])
#         except (TypeError, ValueError):
#             print(f"\nSKIPPED {video_id}: invalid views")
#             skipped_count += 1
#             continue

#         print("\n" + "-" * 70)
#         print(f"Processing {index + 1}/{len(manifest)}")
#         print(f"Video ID: {video_id}")
#         print(f"File: {video_path}")
#         print(f"Actual views: {views}")

#         if not video_path.exists():
#             print("SKIPPED: Video file does not exist.")
#             skipped_count += 1
#             continue

#         try:
#             features = extract_video_features(
#                 str(video_path)
#             )

#         except Exception as exc:
#             print(
#                 f"SKIPPED: Feature extraction failed: {exc}"
#             )
#             skipped_count += 1
#             continue

#         missing_features = [
#             feature
#             for feature in FEATURE_COLUMNS
#             if feature not in features
#         ]

#         if missing_features:
#             print(
#                 "SKIPPED: Missing features:"
#             )
#             print(missing_features)
#             skipped_count += 1
#             continue

#         row = {
#             "video_id": video_id
#         }

#         valid = True

#         for feature in FEATURE_COLUMNS:

#             try:
#                 row[feature] = float(features[feature])
#             except (TypeError, ValueError, KeyError):
#                 print(
#                     f"SKIPPED: Invalid feature "
#                     f"{feature}"
#                 )
#                 valid = False
#                 break

#         if not valid:
#             skipped_count += 1
#             continue

#         # Views are the prediction target.
#         row["views"] = views

#         # Likes are kept if supplied, but NOT used as
#         # a video-input feature for prediction.
#         if "likes" in manifest.columns:
#             try:
#                 row["likes"] = float(record["likes"])
#             except (TypeError, ValueError):
#                 row["likes"] = None

#         rows.append(row)

#         success_count += 1

#         print("SUCCESS")
#         print("Extracted features:")

#         for feature in FEATURE_COLUMNS:
#             print(
#                 f"  {feature}: {row[feature]}"
#             )

#     if not rows:
#         raise RuntimeError(
#             "\nNo valid videos were processed.\n"
#             "Check your video files and manifest."
#         )

#     dataset = pd.DataFrame(rows)

#     # Keep training features + target.
#     output_columns = [
#         "video_id",
#         *FEATURE_COLUMNS,
#         "views",
#     ]

#     dataset = dataset[output_columns]

#     for column in FEATURE_COLUMNS + ["views"]:
#         dataset[column] = pd.to_numeric(
#             dataset[column],
#             errors="coerce"
#         )

#     before = len(dataset)

#     dataset = dataset.dropna(
#         subset=FEATURE_COLUMNS + ["views"]
#     )

#     removed = before - len(dataset)

#     if removed:
#         print(
#             f"\nRemoved invalid rows: {removed}"
#         )

#     OUTPUT_PATH.parent.mkdir(
#         parents=True,
#         exist_ok=True
#     )

#     dataset.to_csv(
#         OUTPUT_PATH,
#         index=False
#     )

#     print("\n" + "=" * 70)
#     print("DATASET BUILD COMPLETE")
#     print("=" * 70)

#     print(f"Successful videos: {success_count}")
#     print(f"Skipped videos: {skipped_count}")
#     print(f"Final rows: {len(dataset)}")

#     print(f"\nSaved:")
#     print(OUTPUT_PATH)

#     print("\nDataset:")
#     print(dataset.to_string(index=False))

#     print("\nView statistics:")
#     print(dataset["views"].describe())

#     print("=" * 70)


# if __name__ == "__main__":
#     main()

# scripts/build_training_dataset.py

# scripts/build_training_dataset.py

import os
import sys
import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

from video.extractor import VideoFeatureExtractor
from video.transcript import TranscriptExtractor
from content.content_analyzer import ContentAnalyzer
from creator.creator_analyzer import CreatorAnalyzer
from platform_analysis.platform_analyzer import PlatformAnalyzer
from hashtag.hashtag_analyzer import HashtagAnalyzer
from ml.feature_builder import FeatureBuilder


# ============================================================
# FILE PATHS
# ============================================================

LABEL_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "video_labels.csv"
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "training_features.csv"
)


# ============================================================
# DEFAULT CREATOR / PLATFORM DATA
# ============================================================

DEFAULT_PLATFORM = "instagram"

DEFAULT_FOLLOWERS = 25000

DEFAULT_FOLLOWING = 800

DEFAULT_CREATOR_CATEGORY = "general"

DEFAULT_HASHTAGS = ""


# ============================================================
# NUMBER PARSER
# ============================================================

def parse_number(value):

    if pd.isna(value):
        return 0.0

    value = str(value).strip().lower()

    if value == "":
        return 0.0

    multiplier = 1

    if value.endswith("k"):
        multiplier = 1000
        value = value[:-1]

    elif value.endswith("m"):
        multiplier = 1000000
        value = value[:-1]

    elif value.endswith("b"):
        multiplier = 1000000000
        value = value[:-1]

    try:

        return float(value) * multiplier

    except ValueError:

        return 0.0


# ============================================================
# PROCESS ONE VIDEO
# ============================================================

def process_video(
    video_path,
    actual_reach,
    platform="instagram",
    followers=25000,
    following=800,
    creator_category="general",
    hashtags=""
):
    """
    Extract all features for one video and attach actual reach.
    """

    # =========================================================
    # 1. VIDEO FEATURES
    # =========================================================

    extractor = VideoFeatureExtractor(video_path)

    video_features = extractor.extract()

    # =========================================================
    # 2. TRANSCRIPT
    # =========================================================

    transcript = ""

    try:

        transcript_extractor = TranscriptExtractor(
            video_path
        )

        transcript_result = (
            transcript_extractor.transcribe()
        )

        if isinstance(
            transcript_result,
            dict
        ):

            transcript = transcript_result.get(
                "transcript",
                ""
            )

        elif isinstance(
            transcript_result,
            str
        ):

            transcript = transcript_result

    except Exception as e:

        print(
            f"  Transcript warning: {e}"
        )

    # =========================================================
    # 3. CONTENT FEATURES
    # =========================================================

    content_analyzer = ContentAnalyzer(
        transcript
    )

    content_features = (
        content_analyzer.analyze()
    )

    # =========================================================
    # 4. CREATOR FEATURES
    # =========================================================

    creator_analyzer = CreatorAnalyzer(
        followers=followers,
        following=following,
        category=creator_category
    )

    creator_features = (
        creator_analyzer.analyze()
    )

    # =========================================================
    # 5. PLATFORM FEATURES
    # =========================================================

    platform_analyzer = PlatformAnalyzer(
        platform=platform,
        duration=video_features.get(
            "duration",
            0
        ),
        width=video_features.get(
            "width",
            0
        ),
        height=video_features.get(
            "height",
            0
        ),
        category=creator_category
    )

    platform_features = (
        platform_analyzer.analyze()
    )

    # =========================================================
    # 6. HASHTAG FEATURES
    # =========================================================

    word_count = content_features.get(
        "word_count",
        0
    )

    hashtag_analyzer = HashtagAnalyzer(
        hashtags=hashtags,
        content_category=creator_category
    )

    hashtag_features = (
        hashtag_analyzer.analyze(
            word_count=word_count
        )
    )

    # =========================================================
    # 7. BUILD FINAL FEATURES
    # =========================================================

    feature_builder = FeatureBuilder()

    features = feature_builder.build(
        video_features=video_features,
        audio_features={},
        content_features=content_features,
        creator_features=creator_features,
        platform_features=platform_features,
        hashtag_features=hashtag_features
    )

    # =========================================================
    # 8. TARGET VARIABLE
    # =========================================================

    features["actual_reach"] = float(
        actual_reach
    )

    return features

# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("TRAINING DATASET BUILDER")
    print("=" * 70)

    # ========================================================
    # CHECK LABEL FILE
    # ========================================================

    if not os.path.exists(LABEL_FILE):

        print(
            "\nERROR:"
        )

        print(
            "video_labels.csv not found:"
        )

        print(
            LABEL_FILE
        )

        return

    # ========================================================
    # LOAD LABELS
    # ========================================================

    labels = pd.read_csv(
        LABEL_FILE
    )

    print(
        f"\nLabel rows: {len(labels)}"
    )

    # ========================================================
    # REQUIRED COLUMNS
    # ========================================================

    required_columns = [
        "video_id",
        "video_path",
        "views",
        "likes"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in labels.columns
    ]

    if missing_columns:

        print(
            "\nERROR: Missing columns:"
        )

        for column in missing_columns:

            print(
                f"  - {column}"
            )

        return

    # ========================================================
    # PROCESS EACH ROW
    # ========================================================

    rows = []

    for _, row in labels.iterrows():

        video_id = str(
            row["video_id"]
        ).strip()

        relative_path = str(
            row["video_path"]
        ).strip()

        # ----------------------------------------------------
        # CONVERT PATH
        # ----------------------------------------------------

        relative_path = relative_path.replace(
            "/",
            os.sep
        )

        video_path = os.path.join(
            PROJECT_ROOT,
            relative_path
        )

        # ----------------------------------------------------
        # CHECK VIDEO
        # ----------------------------------------------------

        if not os.path.exists(video_path):

            print(
                f"\nWARNING: Video not found:"
            )

            print(
                video_path
            )

            continue

        # ----------------------------------------------------
        # PARSE VIEWS
        # ----------------------------------------------------

        views = parse_number(
            row["views"]
        )

        if views <= 0:

            print(
                f"\nWARNING: Invalid views:"
                f" {video_id}"
            )

            continue

        # ----------------------------------------------------
        # PROCESS
        # ----------------------------------------------------

        try:

            features = process_video(
                video_path,
                views
            )

            # ------------------------------------------------
            # ADD NON-MODEL METADATA
            # ------------------------------------------------

            features["video_id"] = video_id

            features["likes"] = parse_number(
                row["likes"]
            )

            rows.append(
                features
            )

            print(
                f"  ✓ {video_id}"
                f" | views={views:,.0f}"
            )

        except Exception as error:

            print(
                f"\n  ✗ {video_id}"
            )

            print(
                f"    Error: {error}"
            )

    # ========================================================
    # CHECK RESULT
    # ========================================================

    if not rows:

        print(
            "\nERROR: No rows were generated."
        )

        return

    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        rows
    )

    # ========================================================
    # SAVE
    # ========================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("TRAINING DATASET CREATED")
    print("=" * 70)

    print(
        f"\nRows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print(
        f"\nSaved:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nViews statistics:"
    )

    print(
        df["actual_reach"].describe()
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()