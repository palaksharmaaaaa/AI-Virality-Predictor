# import cv2
# import numpy as np

# from video.motion import calculate_motion_score
# from video.scenes import detect_scene_changes
# from video.hook import calculate_hook_intensity
# from video.face import detect_faces


# # ---------------------------------------------------------
# # Basic video metadata
# # ---------------------------------------------------------

# def get_video_metadata(video_path):

#     capture = cv2.VideoCapture(video_path)

#     if not capture.isOpened():
#         raise ValueError(
#             "Could not open the video file."
#         )

#     fps = capture.get(
#         cv2.CAP_PROP_FPS
#     )

#     frame_count = capture.get(
#         cv2.CAP_PROP_FRAME_COUNT
#     )

#     width = int(
#         capture.get(
#             cv2.CAP_PROP_FRAME_WIDTH
#         )
#     )

#     height = int(
#         capture.get(
#             cv2.CAP_PROP_FRAME_HEIGHT
#         )
#     )

#     if fps <= 0:
#         fps = 30.0

#     duration = (
#         frame_count / fps
#         if fps > 0
#         else 0
#     )

#     capture.release()

#     return {
#         "duration": float(duration),
#         "fps": float(fps),
#         "width": width,
#         "height": height
#     }


# # ---------------------------------------------------------
# # Brightness and contrast
# # ---------------------------------------------------------

# def calculate_brightness_contrast(video_path):

#     capture = cv2.VideoCapture(video_path)

#     if not capture.isOpened():
#         return 0.0, 0.0

#     total_brightness = 0.0
#     total_contrast = 0.0
#     count = 0

#     frame_count = int(
#         capture.get(
#             cv2.CAP_PROP_FRAME_COUNT
#         )
#     )

#     if frame_count <= 0:
#         capture.release()
#         return 0.0, 0.0

#     sample_positions = np.linspace(
#         0,
#         frame_count - 1,
#         min(20, frame_count),
#         dtype=int
#     )

#     for position in sample_positions:

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

#         total_brightness += float(
#             np.mean(gray)
#         )

#         total_contrast += float(
#             np.std(gray)
#         )

#         count += 1

#     capture.release()

#     if count == 0:
#         return 0.0, 0.0

#     return (
#         total_brightness / count,
#         total_contrast / count
#     )


# # ---------------------------------------------------------
# # Pacing score
# # ---------------------------------------------------------

# def calculate_pacing_score(
#     scene_changes,
#     duration
# ):

#     if duration <= 0:
#         return 0.0

#     changes_per_second = (
#         scene_changes / duration
#     )

#     # A moderate amount of scene change
#     # is treated as good pacing.
#     score = (
#         100 *
#         np.exp(
#             -(
#                 changes_per_second - 0.15
#             ) ** 2 / 0.08
#         )
#     )

#     return float(
#         np.clip(score, 0, 100)
#     )


# # ---------------------------------------------------------
# # Complete extraction pipeline
# # ---------------------------------------------------------

# def extract_video_features(video_path):

#     metadata = get_video_metadata(
#         video_path
#     )

#     motion_score = calculate_motion_score(
#         video_path
#     )

#     scene_changes = detect_scene_changes(
#         video_path
#     )

#     hook_intensity = calculate_hook_intensity(
#         video_path
#     )

#     face_data = detect_faces(
#         video_path
#     )

#     brightness, contrast = (
#         calculate_brightness_contrast(
#             video_path
#         )
#     )

#     pacing_score = calculate_pacing_score(
#         scene_changes,
#         metadata["duration"]
#     )

#     features = {

#         "duration": metadata["duration"],

#         "fps": metadata["fps"],

#         "width": metadata["width"],

#         "height": metadata["height"],

#         "motion_score": motion_score,

#         "scene_changes": scene_changes,

#         "hook_intensity": hook_intensity,

#         "face_count": face_data["face_count"],

#         "face_presence_ratio": (
#             face_data["face_presence_ratio"]
#         ),

#         "brightness": brightness,

#         "contrast": contrast,

#         "pacing_score": pacing_score
#     }

#     return features

import cv2
import numpy as np
import os


class VideoFeatureExtractor:

    def __init__(self, video_path):
        self.video_path = video_path

    def extract(self):

        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            raise ValueError("Unable to open video file.")

        # -----------------------------
        # BASIC VIDEO INFORMATION
        # -----------------------------

        fps = cap.get(cv2.CAP_PROP_FPS)

        frame_count = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        width = int(
            cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        height = int(
            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        if fps <= 0:
            fps = 30

        duration = frame_count / fps if fps > 0 else 0

        # -----------------------------
        # RESOLUTION
        # -----------------------------

        resolution = f"{width}x{height}"

        # -----------------------------
        # ASPECT RATIO
        # -----------------------------

        aspect_ratio = (
            width / height
            if height > 0
            else 0
        )

        aspect_ratio_name = self.get_aspect_ratio(
            width,
            height
        )

        # -----------------------------
        # VIDEO QUALITY
        # -----------------------------

        if width >= 1920 and height >= 1080:
            resolution_category = "1080p_or_higher"

        elif width >= 1280 and height >= 720:
            resolution_category = "720p"

        elif width >= 854 and height >= 480:
            resolution_category = "480p"

        else:
            resolution_category = "low_resolution"

        # -----------------------------
        # FILE INFORMATION
        # -----------------------------

        file_size_bytes = os.path.getsize(
            self.video_path
        )

        file_size_mb = (
            file_size_bytes / (1024 * 1024)
        )

        # -----------------------------
        # ANALYSIS VARIABLES
        # -----------------------------

        brightness_values = []
        contrast_values = []
        motion_values = []

        frame_brightness = []
        frame_contrast = []

        scene_changes = 0

        previous_gray = None
        previous_histogram = None

        sampled_frames = 0

        # -----------------------------
        # FACE DETECTOR
        # -----------------------------

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        face_counts = []

        # -----------------------------
        # FRAME SAMPLING
        # -----------------------------

        sample_interval = max(
            int(fps),
            1
        )

        frame_index = 0

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            if frame_index % sample_interval != 0:
                frame_index += 1
                continue

            sampled_frames += 1

            # Resize for faster analysis
            frame = cv2.resize(
                frame,
                (640, 360)
            )

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            # -----------------------------
            # BRIGHTNESS
            # -----------------------------

            brightness = float(
                np.mean(gray)
            )

            brightness_values.append(
                brightness
            )

            # -----------------------------
            # CONTRAST
            # -----------------------------

            contrast = float(
                np.std(gray)
            )

            contrast_values.append(
                contrast
            )

            # -----------------------------
            # MOTION
            # -----------------------------

            if previous_gray is not None:

                diff = cv2.absdiff(
                    previous_gray,
                    gray
                )

                motion = float(
                    np.mean(diff)
                )

                motion_values.append(
                    motion
                )

            previous_gray = gray.copy()

            # -----------------------------
            # SCENE CHANGE
            # -----------------------------

            histogram = cv2.calcHist(
                [gray],
                [0],
                None,
                [32],
                [0, 256]
            )

            cv2.normalize(
                histogram,
                histogram
            )

            if previous_histogram is not None:

                correlation = cv2.compareHist(
                    previous_histogram,
                    histogram,
                    cv2.HISTCMP_CORREL
                )

                if correlation < 0.65:
                    scene_changes += 1

            previous_histogram = histogram

            # -----------------------------
            # FACE DETECTION
            # -----------------------------

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            face_counts.append(
                len(faces)
            )

            frame_index += 1

        cap.release()

        # -----------------------------
        # FINAL FEATURES
        # -----------------------------

        avg_brightness = (
            float(np.mean(brightness_values))
            if brightness_values
            else 0
        )

        avg_contrast = (
            float(np.mean(contrast_values))
            if contrast_values
            else 0
        )

        motion_score = (
            float(np.mean(motion_values))
            if motion_values
            else 0
        )

        face_count = (
            int(max(face_counts))
            if face_counts
            else 0
        )

        face_presence_ratio = (
            float(
                sum(
                    1 for x in face_counts
                    if x > 0
                ) / len(face_counts)
            )
            if face_counts
            else 0
        )

        # -----------------------------
        # PACING SCORE
        # -----------------------------

        if duration > 0:

            scene_change_rate = (
                scene_changes / duration
            )

        else:

            scene_change_rate = 0

        pacing_score = min(
            scene_change_rate * 10,
            100
        )

        # -----------------------------
        # HOOK INTENSITY
        # -----------------------------

        hook_intensity = self.calculate_hook(
            motion_score,
            scene_change_rate,
            brightness_values
        )

        # -----------------------------
        # VIDEO TAXONOMY
        # -----------------------------

        video_type = self.classify_video_format(
            duration,
            width,
            height
        )

        # -----------------------------
        # RETURN ALL FEATURES
        # -----------------------------

        return {

            # Basic
            "duration": round(duration, 2),
            "fps": round(fps, 2),
            "frame_count": frame_count,

            # Dimensions
            "width": width,
            "height": height,
            "resolution": resolution,
            "resolution_category":
                resolution_category,

            # Aspect ratio
            "aspect_ratio":
                round(aspect_ratio, 3),

            "aspect_ratio_name":
                aspect_ratio_name,

            # File
            "file_size_mb":
                round(file_size_mb, 2),

            # Visual
            "brightness":
                round(avg_brightness, 2),

            "contrast":
                round(avg_contrast, 2),

            "motion_score":
                round(motion_score, 2),

            "scene_changes":
                scene_changes,

            "scene_change_rate":
                round(scene_change_rate, 3),

            # Faces
            "face_count":
                face_count,

            "face_presence_ratio":
                round(face_presence_ratio, 3),

            # Engagement-related visual features
            "hook_intensity":
                round(hook_intensity, 2),

            "pacing_score":
                round(pacing_score, 2),

            # Taxonomy
            "video_format":
                video_type,

            # Sampling
            "sampled_frames":
                sampled_frames
        }

    # =====================================================
    # ASPECT RATIO CLASSIFICATION
    # =====================================================

    def get_aspect_ratio(self, width, height):

        if height == 0:
            return "unknown"

        ratio = width / height

        # Vertical
        if ratio < 0.8:
            return "vertical"

        # Square
        elif 0.95 <= ratio <= 1.05:
            return "square"

        # Standard landscape
        elif 1.3 <= ratio <= 1.4:
            return "4:3"

        # Widescreen
        elif 1.7 <= ratio <= 1.85:
            return "16:9"

        else:
            return "other"

    # =====================================================
    # VIDEO FORMAT CLASSIFICATION
    # =====================================================

    def classify_video_format(
        self,
        duration,
        width,
        height
    ):

        if height == 0:
            return "unknown"

        ratio = width / height

        # Vertical short form
        if ratio < 0.8 and duration <= 90:
            return "short_form_vertical"

        # Vertical long form
        elif ratio < 0.8:
            return "long_form_vertical"

        # Square content
        elif 0.95 <= ratio <= 1.05:
            return "square_video"

        # Landscape short
        elif duration <= 90:
            return "short_form_landscape"

        # Landscape long
        else:
            return "long_form_landscape"

    # =====================================================
    # HOOK SCORE
    # =====================================================

    def calculate_hook(
        self,
        motion_score,
        scene_change_rate,
        brightness_values
    ):

        motion_component = min(
            motion_score * 2,
            50
        )

        scene_component = min(
            scene_change_rate * 20,
            30
        )

        brightness_component = 0

        if brightness_values:

            avg_brightness = np.mean(
                brightness_values
            )

            if 40 <= avg_brightness <= 220:
                brightness_component = 20

        return min(
            motion_component +
            scene_component +
            brightness_component,
            100
        )