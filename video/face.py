import cv2
import numpy as np
import mediapipe as mp


# ---------------------------------------------------------
# MediaPipe Face Detection
# ---------------------------------------------------------

mp_face_detection = mp.solutions.face_detection


def detect_faces(video_path):

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError(
            "Could not open video for face detection."
        )

    frame_count = int(
        capture.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    frame_width = int(
        capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    frame_height = int(
        capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    if frame_count <= 0:
        capture.release()

        return {
            "face_count": 0,
            "face_presence_ratio": 0.0
        }

    # -----------------------------------------------------
    # Sample frames
    # -----------------------------------------------------

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

    frames_with_faces = 0

    max_faces_in_frame = 0

    total_valid_detections = 0

    # -----------------------------------------------------
    # MediaPipe detector
    #
    # model_selection=0:
    # short-range model, suitable for faces
    # relatively close to camera.
    #
    # min_detection_confidence:
    # higher = fewer false positives.
    # -----------------------------------------------------

    with mp_face_detection.FaceDetection(
        model_selection=1,
        min_detection_confidence=0.60
    ) as detector:

        for position in positions:

            capture.set(
                cv2.CAP_PROP_POS_FRAMES,
                int(position)
            )

            success, frame = capture.read()

            if not success:
                continue

            if frame is None:
                continue

            # -------------------------------------------------
            # Convert BGR -> RGB
            # -------------------------------------------------

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            # -------------------------------------------------
            # Run MediaPipe face detection
            # -------------------------------------------------

            results = detector.process(
                rgb_frame
            )

            valid_faces = []

            if results.detections:

                for detection in results.detections:

                    # -----------------------------------------
                    # Detection confidence
                    # -----------------------------------------

                    confidence = float(
                        detection.score[0]
                    )

                    if confidence < 0.60:
                        continue

                    # -----------------------------------------
                    # Bounding box
                    # -----------------------------------------

                    bbox = detection.location_data.relative_bounding_box

                    x = int(
                        bbox.xmin * frame_width
                    )

                    y = int(
                        bbox.ymin * frame_height
                    )

                    w = int(
                        bbox.width * frame_width
                    )

                    h = int(
                        bbox.height * frame_height
                    )

                    # -----------------------------------------
                    # Clamp coordinates
                    # -----------------------------------------

                    x = max(
                        0,
                        x
                    )

                    y = max(
                        0,
                        y
                    )

                    w = min(
                        w,
                        frame_width - x
                    )

                    h = min(
                        h,
                        frame_height - y
                    )

                    # -----------------------------------------
                    # Invalid bounding box
                    # -----------------------------------------

                    if w <= 0 or h <= 0:
                        continue

                    # -----------------------------------------
                    # Minimum face size
                    #
                    # Allows children but removes tiny
                    # object-like detections.
                    # -----------------------------------------

                    min_dimension = min(
                        frame_width,
                        frame_height
                    )

                    minimum_face_size = max(
                        35,
                        int(
                            min_dimension * 0.035
                        )
                    )

                    if w < minimum_face_size:
                        continue

                    if h < minimum_face_size:
                        continue

                    # -----------------------------------------
                    # Face aspect ratio
                    # -----------------------------------------

                    aspect_ratio = w / float(h)

                    if (
                        aspect_ratio < 0.55
                        or aspect_ratio > 1.80
                    ):
                        continue

                    # -----------------------------------------
                    # Face should have reasonable area
                    # -----------------------------------------

                    face_area = w * h

                    frame_area = (
                        frame_width *
                        frame_height
                    )

                    face_area_ratio = (
                        face_area /
                        float(frame_area)
                    )

                    # Reject extremely tiny detections
                    if face_area_ratio < 0.001:
                        continue

                    valid_faces.append(
                        {
                            "x": x,
                            "y": y,
                            "w": w,
                            "h": h,
                            "confidence": confidence
                        }
                    )

            # -------------------------------------------------
            # Frame result
            # -------------------------------------------------

            faces_in_frame = len(
                valid_faces
            )

            if faces_in_frame > 0:

                frames_with_faces += 1

                total_valid_detections += (
                    faces_in_frame
                )

                max_faces_in_frame = max(
                    max_faces_in_frame,
                    faces_in_frame
                )

    capture.release()

    # ---------------------------------------------------------
    # Face presence ratio
    # ---------------------------------------------------------

    actual_samples = len(
        positions
    )

    if actual_samples > 0:

        face_presence_ratio = (
            frames_with_faces /
            actual_samples
        ) * 100

    else:

        face_presence_ratio = 0.0

    # ---------------------------------------------------------
    # IMPORTANT:
    #
    # face_count represents the maximum number of faces
    # detected simultaneously in a sampled frame.
    #
    # This prevents the same person being counted again
    # and again across multiple frames.
    # ---------------------------------------------------------

    face_count = max_faces_in_frame

    return {
        "face_count": int(
            face_count
        ),

        "face_presence_ratio": round(
            float(
                face_presence_ratio
            ),
            2
        )
    }