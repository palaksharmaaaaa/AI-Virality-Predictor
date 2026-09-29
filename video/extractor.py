import cv2
import numpy as np

from video.motion import calculate_motion_score
from video.scenes import detect_scene_changes
from video.hook import calculate_hook_intensity
from video.face import detect_faces


# ---------------------------------------------------------
# Basic video metadata
# ---------------------------------------------------------

def get_video_metadata(video_path):

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError(
            "Could not open the video file."
        )

    fps = capture.get(
        cv2.CAP_PROP_FPS
    )

    frame_count = capture.get(
        cv2.CAP_PROP_FRAME_COUNT
    )

    width = int(
        capture.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        capture.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    if fps <= 0:
        fps = 30.0

    duration = (
        frame_count / fps
        if fps > 0
        else 0
    )

    capture.release()

    return {
        "duration": float(duration),
        "fps": float(fps),
        "width": width,
        "height": height
    }


# ---------------------------------------------------------
# Brightness and contrast
# ---------------------------------------------------------

def calculate_brightness_contrast(video_path):

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        return 0.0, 0.0

    total_brightness = 0.0
    total_contrast = 0.0
    count = 0

    frame_count = int(
        capture.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    if frame_count <= 0:
        capture.release()
        return 0.0, 0.0

    sample_positions = np.linspace(
        0,
        frame_count - 1,
        min(20, frame_count),
        dtype=int
    )

    for position in sample_positions:

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

        total_brightness += float(
            np.mean(gray)
        )

        total_contrast += float(
            np.std(gray)
        )

        count += 1

    capture.release()

    if count == 0:
        return 0.0, 0.0

    return (
        total_brightness / count,
        total_contrast / count
    )


# ---------------------------------------------------------
# Pacing score
# ---------------------------------------------------------

def calculate_pacing_score(
    scene_changes,
    duration
):

    if duration <= 0:
        return 0.0

    changes_per_second = (
        scene_changes / duration
    )

    # A moderate amount of scene change
    # is treated as good pacing.
    score = (
        100 *
        np.exp(
            -(
                changes_per_second - 0.15
            ) ** 2 / 0.08
        )
    )

    return float(
        np.clip(score, 0, 100)
    )


# ---------------------------------------------------------
# Complete extraction pipeline
# ---------------------------------------------------------

def extract_video_features(video_path):

    metadata = get_video_metadata(
        video_path
    )

    motion_score = calculate_motion_score(
        video_path
    )

    scene_changes = detect_scene_changes(
        video_path
    )

    hook_intensity = calculate_hook_intensity(
        video_path
    )

    face_data = detect_faces(
        video_path
    )

    brightness, contrast = (
        calculate_brightness_contrast(
            video_path
        )
    )

    pacing_score = calculate_pacing_score(
        scene_changes,
        metadata["duration"]
    )

    features = {

        "duration": metadata["duration"],

        "fps": metadata["fps"],

        "width": metadata["width"],

        "height": metadata["height"],

        "motion_score": motion_score,

        "scene_changes": scene_changes,

        "hook_intensity": hook_intensity,

        "face_count": face_data["face_count"],

        "face_presence_ratio": (
            face_data["face_presence_ratio"]
        ),

        "brightness": brightness,

        "contrast": contrast,

        "pacing_score": pacing_score
    }

    return features