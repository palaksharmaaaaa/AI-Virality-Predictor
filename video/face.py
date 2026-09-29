# import cv2
# import numpy as np


# def detect_faces(video_path):

#     cascade_path = cv2.data.haarcascades + (
#         "haarcascade_frontalface_default.xml"
#     )

#     face_detector = cv2.CascadeClassifier(
#         cascade_path
#     )

#     capture = cv2.VideoCapture(video_path)

#     if not capture.isOpened():
#         raise ValueError(
#             "Could not open video for face detection."
#         )

#     frame_count = int(
#         capture.get(
#             cv2.CAP_PROP_FRAME_COUNT
#         )
#     )

#     if frame_count <= 0:

#         capture.release()

#         return {
#             "face_count": 0,
#             "face_presence_ratio": 0.0
#         }

#     sample_count = min(
#         30,
#         frame_count
#     )

#     positions = np.linspace(
#         0,
#         frame_count - 1,
#         sample_count,
#         dtype=int
#     )

#     total_faces = 0

#     frames_with_faces = 0

#     for position in positions:

#         capture.set(
#             cv2.CAP_PROP_POS_FRAMES,
#             int(position)
#         )

#         success, frame = capture.read()

#         if not success:
#             continue

#         gray = cv2.cvtColor(
#             frame,
#             cv2.COLOR_BGR2GRAY
#         )

#         faces = face_detector.detectMultiScale(
#             gray,
#             scaleFactor=1.1,
#             minNeighbors=5,
#             minSize=(30, 30)
#         )

#         if len(faces) > 0:

#             frames_with_faces += 1

#             total_faces += len(faces)

#     capture.release()

#     actual_samples = len(positions)

#     if actual_samples == 0:
#         presence_ratio = 0.0
#     else:
#         presence_ratio = (
#             frames_with_faces /
#             actual_samples
#         ) * 100

#     return {
#         "face_count": int(total_faces),

#         "face_presence_ratio": float(
#             presence_ratio
#         )
#     }

import cv2
import numpy as np


def detect_faces(video_path):

    cascade_path = cv2.data.haarcascades + (
        "haarcascade_frontalface_default.xml"
    )

    face_detector = cv2.CascadeClassifier(
        cascade_path
    )

    if face_detector.empty():
        raise ValueError(
            "Could not load Haar Cascade face detector."
        )

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError(
            "Could not open video for face detection."
        )

    frame_count = int(
        capture.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    if frame_count <= 0:
        capture.release()

        return {
            "face_count": 0,
            "face_presence_ratio": 0.0
        }

    # Maximum 30 frames are sampled.
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

    total_faces = 0
    frames_with_faces = 0

    # A detection must be reasonably large
    # to be considered a real face.
    frame_width = int(
        capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    frame_height = int(
        capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    min_face_width = max(
        50,
        int(frame_width * 0.06)
    )

    min_face_height = max(
        50,
        int(frame_height * 0.06)
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

        # Improve detection consistency.
        gray = cv2.equalizeHist(gray)

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=8,
            minSize=(
                min_face_width,
                min_face_height
            )
        )

        valid_faces = []

        for (x, y, w, h) in faces:

            # Reject very small detections.
            if w < min_face_width:
                continue

            if h < min_face_height:
                continue

            # Reject extremely unusual face shapes.
            aspect_ratio = w / float(h)

            if aspect_ratio < 0.65 or aspect_ratio > 1.5:
                continue

            valid_faces.append(
                (x, y, w, h)
            )

        if len(valid_faces) > 0:

            frames_with_faces += 1

            total_faces += len(
                valid_faces
            )

    capture.release()

    actual_samples = len(positions)

    if actual_samples == 0:
        presence_ratio = 0.0
    else:
        presence_ratio = (
            frames_with_faces /
            actual_samples
        ) * 100

    return {
        "face_count": int(total_faces),

        "face_presence_ratio": round(
            float(presence_ratio),
            2
        )
    }