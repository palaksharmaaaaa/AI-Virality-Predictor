import cv2
import numpy as np

from config.config import HOOK_DURATION_SECONDS


def calculate_hook_intensity(video_path):

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError(
            "Could not open video for hook analysis."
        )

    fps = capture.get(
        cv2.CAP_PROP_FPS
    )

    frame_count = int(
        capture.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    if fps <= 0:
        fps = 30.0

    hook_frames = min(
        frame_count,
        int(
            fps *
            HOOK_DURATION_SECONDS
        )
    )

    if hook_frames <= 0:

        capture.release()

        return 0.0

    positions = np.linspace(
        0,
        hook_frames - 1,
        min(20, hook_frames),
        dtype=int
    )

    previous_gray = None

    motion_values = []

    contrast_values = []

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

        contrast = float(
            np.std(gray)
        )

        contrast_values.append(
            contrast
        )

        if previous_gray is not None:

            difference = cv2.absdiff(
                previous_gray,
                gray
            )

            motion_values.append(
                float(
                    np.mean(difference)
                )
            )

        previous_gray = gray

    capture.release()

    if not motion_values:
        motion_component = 0.0
    else:
        motion_component = np.mean(
            motion_values
        )

    if not contrast_values:
        contrast_component = 0.0
    else:
        contrast_component = np.mean(
            contrast_values
        )

    motion_score = (
        motion_component / 128
    ) * 100

    contrast_score = (
        contrast_component / 80
    ) * 100

    hook_score = (
        0.6 * motion_score +
        0.4 * contrast_score
    )

    return float(
        np.clip(
            hook_score,
            0,
            100
        )
    )