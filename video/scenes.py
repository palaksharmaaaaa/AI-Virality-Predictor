import cv2
import numpy as np


def detect_scene_changes(video_path, threshold=30.0):
    """
    Detect scene changes using frame-to-frame visual differences.

    Parameters
    ----------
    video_path : str
        Path to the video file.

    threshold : float
        Mean grayscale difference required to consider
        a frame transition a scene change.

    Returns
    -------
    int
        Number of detected scene changes.
    """

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError(
            "Could not open video for scene-change detection."
        )

    frame_count = int(
        capture.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    if frame_count <= 0:
        capture.release()
        return 0

    # Sample frames instead of processing every frame.
    sample_count = min(60, frame_count)

    positions = np.linspace(
        0,
        frame_count - 1,
        sample_count,
        dtype=int
    )

    previous_gray = None
    scene_changes = 0

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

            difference = cv2.absdiff(
                previous_gray,
                gray
            )

            mean_difference = float(
                np.mean(difference)
            )

            if mean_difference >= threshold:
                scene_changes += 1

        previous_gray = gray

    capture.release()

    return int(scene_changes)