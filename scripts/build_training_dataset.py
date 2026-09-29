"""
Build training_data.csv from real local videos.

Input:
    data/dataset_manifest.csv

Manifest columns:
    video_id,video_path,views,likes

The video features are extracted automatically using
the project's OpenCV feature extractor.
"""

from pathlib import Path
import pandas as pd

from video.extractor import extract_video_features


BASE_DIR = Path(__file__).resolve().parents[1]

MANIFEST_PATH = BASE_DIR / "data" / "dataset_manifest.csv"
OUTPUT_PATH = BASE_DIR / "data" / "training_data.csv"


FEATURE_COLUMNS = [
    "duration",
    "fps",
    "width",
    "height",
    "motion_score",
    "scene_changes",
    "hook_intensity",
    "face_count",
    "face_presence_ratio",
    "brightness",
    "contrast",
    "pacing_score",
]


def resolve_video_path(video_path):
    path = Path(str(video_path))

    if path.is_absolute():
        return path

    project_path = BASE_DIR / path

    if project_path.exists():
        return project_path

    data_path = BASE_DIR / "data" / path

    if data_path.exists():
        return data_path

    return project_path


def main():

    print("=" * 70)
    print("REAL VIDEO DATASET BUILDER")
    print("=" * 70)

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"\nManifest not found:\n{MANIFEST_PATH}\n\n"
            "Create data/dataset_manifest.csv first."
        )

    manifest = pd.read_csv(MANIFEST_PATH)

    required = [
        "video_id",
        "video_path",
        "views",
    ]

    missing = [
        col for col in required
        if col not in manifest.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in manifest: {missing}\n"
            f"Required columns: {required}"
        )

    print(f"\nVideos listed: {len(manifest)}")

    rows = []

    success_count = 0
    skipped_count = 0

    for index, record in manifest.iterrows():

        video_id = str(record["video_id"]).strip()
        video_path = resolve_video_path(record["video_path"])

        try:
            views = float(record["views"])
        except (TypeError, ValueError):
            print(f"\nSKIPPED {video_id}: invalid views")
            skipped_count += 1
            continue

        print("\n" + "-" * 70)
        print(f"Processing {index + 1}/{len(manifest)}")
        print(f"Video ID: {video_id}")
        print(f"File: {video_path}")
        print(f"Actual views: {views}")

        if not video_path.exists():
            print("SKIPPED: Video file does not exist.")
            skipped_count += 1
            continue

        try:
            features = extract_video_features(
                str(video_path)
            )

        except Exception as exc:
            print(
                f"SKIPPED: Feature extraction failed: {exc}"
            )
            skipped_count += 1
            continue

        missing_features = [
            feature
            for feature in FEATURE_COLUMNS
            if feature not in features
        ]

        if missing_features:
            print(
                "SKIPPED: Missing features:"
            )
            print(missing_features)
            skipped_count += 1
            continue

        row = {
            "video_id": video_id
        }

        valid = True

        for feature in FEATURE_COLUMNS:

            try:
                row[feature] = float(features[feature])
            except (TypeError, ValueError, KeyError):
                print(
                    f"SKIPPED: Invalid feature "
                    f"{feature}"
                )
                valid = False
                break

        if not valid:
            skipped_count += 1
            continue

        # Views are the prediction target.
        row["views"] = views

        # Likes are kept if supplied, but NOT used as
        # a video-input feature for prediction.
        if "likes" in manifest.columns:
            try:
                row["likes"] = float(record["likes"])
            except (TypeError, ValueError):
                row["likes"] = None

        rows.append(row)

        success_count += 1

        print("SUCCESS")
        print("Extracted features:")

        for feature in FEATURE_COLUMNS:
            print(
                f"  {feature}: {row[feature]}"
            )

    if not rows:
        raise RuntimeError(
            "\nNo valid videos were processed.\n"
            "Check your video files and manifest."
        )

    dataset = pd.DataFrame(rows)

    # Keep training features + target.
    output_columns = [
        "video_id",
        *FEATURE_COLUMNS,
        "views",
    ]

    dataset = dataset[output_columns]

    for column in FEATURE_COLUMNS + ["views"]:
        dataset[column] = pd.to_numeric(
            dataset[column],
            errors="coerce"
        )

    before = len(dataset)

    dataset = dataset.dropna(
        subset=FEATURE_COLUMNS + ["views"]
    )

    removed = before - len(dataset)

    if removed:
        print(
            f"\nRemoved invalid rows: {removed}"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataset.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n" + "=" * 70)
    print("DATASET BUILD COMPLETE")
    print("=" * 70)

    print(f"Successful videos: {success_count}")
    print(f"Skipped videos: {skipped_count}")
    print(f"Final rows: {len(dataset)}")

    print(f"\nSaved:")
    print(OUTPUT_PATH)

    print("\nDataset:")
    print(dataset.to_string(index=False))

    print("\nView statistics:")
    print(dataset["views"].describe())

    print("=" * 70)


if __name__ == "__main__":
    main()