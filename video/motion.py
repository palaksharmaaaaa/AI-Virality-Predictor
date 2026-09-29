import cv2
import numpy as np


def calculate_motion_score(video_path):

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError(
            "Could not open video for motion analysis."
        )

    previous_gray = None

    differences = []

    frame_count = int(
        capture.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    if frame_count <= 0:

        capture.release()

        return 0.0

    sample_count = min(
        30,
        frame_count
    )

    positions = np.linspace(
        0,
        frame_count - 1,
        sample_count,
        dtype=int
    )

    for position in positions:

        capture.set(
            cv2.CAP_PROP_POS_FRAMES,
            int(position)
        )

        success, frame = capture.read()

        if not success:
            continue

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        gray = cv2.resize(
            gray,
            (320, 240)
        )

        if previous_gray is not None:

            diff = cv2.absdiff(
                previous_gray,
                gray
            )

            score = float(
                np.mean(diff)
            )

            differences.append(score)

        previous_gray = gray

    capture.release()

    if not differences:
        return 0.0

    raw_score = float(
        np.mean(differences)
    )

    # Normalize approximately to 0-100.
    normalized_score = (
        raw_score / 128.0
    ) * 100

    return float(
        np.clip(
            normalized_score,
            0,
            100
        )
    )