# # import cv2
# # import numpy as np

# # from video.motion import calculate_motion_score
# # from video.scenes import detect_scene_changes
# # from video.hook import calculate_hook_intensity
# # from video.face import detect_faces


# # # ---------------------------------------------------------
# # # Basic video metadata
# # # ---------------------------------------------------------

# # def get_video_metadata(video_path):

# #     capture = cv2.VideoCapture(video_path)

# #     if not capture.isOpened():
# #         raise ValueError(
# #             "Could not open the video file."
# #         )

# #     fps = capture.get(
# #         cv2.CAP_PROP_FPS
# #     )

# #     frame_count = capture.get(
# #         cv2.CAP_PROP_FRAME_COUNT
# #     )

# #     width = int(
# #         capture.get(
# #             cv2.CAP_PROP_FRAME_WIDTH
# #         )
# #     )

# #     height = int(
# #         capture.get(
# #             cv2.CAP_PROP_FRAME_HEIGHT
# #         )
# #     )

# #     if fps <= 0:
# #         fps = 30.0

# #     duration = (
# #         frame_count / fps
# #         if fps > 0
# #         else 0
# #     )

# #     capture.release()

# #     return {
# #         "duration": float(duration),
# #         "fps": float(fps),
# #         "width": width,
# #         "height": height
# #     }


# # # ---------------------------------------------------------
# # # Brightness and contrast
# # # ---------------------------------------------------------

# # def calculate_brightness_contrast(video_path):

# #     capture = cv2.VideoCapture(video_path)

# #     if not capture.isOpened():
# #         return 0.0, 0.0

# #     total_brightness = 0.0
# #     total_contrast = 0.0
# #     count = 0

# #     frame_count = int(
# #         capture.get(
# #             cv2.CAP_PROP_FRAME_COUNT
# #         )
# #     )

# #     if frame_count <= 0:
# #         capture.release()
# #         return 0.0, 0.0

# #     sample_positions = np.linspace(
# #         0,
# #         frame_count - 1,
# #         min(20, frame_count),
# #         dtype=int
# #     )

# #     for position in sample_positions:

# #         capture.set(
# #             cv2.CAP_PROP_POS_FRAMES,
# #             int(position)
# #         )

# #         success, frame = capture.read()

# #         if not success:
# #             continue

# #         gray = cv2.cvtColor(
# #             frame,
# #             cv2.COLOR_BGR2GRAY
# #         )

# #         total_brightness += float(
# #             np.mean(gray)
# #         )

# #         total_contrast += float(
# #             np.std(gray)
# #         )

# #         count += 1

# #     capture.release()

# #     if count == 0:
# #         return 0.0, 0.0

# #     return (
# #         total_brightness / count,
# #         total_contrast / count
# #     )


# # # ---------------------------------------------------------
# # # Pacing score
# # # ---------------------------------------------------------

# # def calculate_pacing_score(
# #     scene_changes,
# #     duration
# # ):

# #     if duration <= 0:
# #         return 0.0

# #     changes_per_second = (
# #         scene_changes / duration
# #     )

# #     # A moderate amount of scene change
# #     # is treated as good pacing.
# #     score = (
# #         100 *
# #         np.exp(
# #             -(
# #                 changes_per_second - 0.15
# #             ) ** 2 / 0.08
# #         )
# #     )

# #     return float(
# #         np.clip(score, 0, 100)
# #     )


# # # ---------------------------------------------------------
# # # Complete extraction pipeline
# # # ---------------------------------------------------------

# # def extract_video_features(video_path):

# #     metadata = get_video_metadata(
# #         video_path
# #     )

# #     motion_score = calculate_motion_score(
# #         video_path
# #     )

# #     scene_changes = detect_scene_changes(
# #         video_path
# #     )

# #     hook_intensity = calculate_hook_intensity(
# #         video_path
# #     )

# #     face_data = detect_faces(
# #         video_path
# #     )

# #     brightness, contrast = (
# #         calculate_brightness_contrast(
# #             video_path
# #         )
# #     )

# #     pacing_score = calculate_pacing_score(
# #         scene_changes,
# #         metadata["duration"]
# #     )

# #     features = {

# #         "duration": metadata["duration"],

# #         "fps": metadata["fps"],

# #         "width": metadata["width"],

# #         "height": metadata["height"],

# #         "motion_score": motion_score,

# #         "scene_changes": scene_changes,

# #         "hook_intensity": hook_intensity,

# #         "face_count": face_data["face_count"],

# #         "face_presence_ratio": (
# #             face_data["face_presence_ratio"]
# #         ),

# #         "brightness": brightness,

# #         "contrast": contrast,

# #         "pacing_score": pacing_score
# #     }

# #     return features

# import cv2
# import numpy as np
# import os


# class VideoFeatureExtractor:

#     def __init__(self, video_path):
#         self.video_path = video_path

#     def extract(self):

#         cap = cv2.VideoCapture(self.video_path)

#         if not cap.isOpened():
#             raise ValueError("Unable to open video file.")

#         # -----------------------------
#         # BASIC VIDEO INFORMATION
#         # -----------------------------

#         fps = cap.get(cv2.CAP_PROP_FPS)

#         frame_count = int(
#             cap.get(cv2.CAP_PROP_FRAME_COUNT)
#         )

#         width = int(
#             cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#         )

#         height = int(
#             cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#         )

#         if fps <= 0:
#             fps = 30

#         duration = frame_count / fps if fps > 0 else 0

#         # -----------------------------
#         # RESOLUTION
#         # -----------------------------

#         resolution = f"{width}x{height}"

#         # -----------------------------
#         # ASPECT RATIO
#         # -----------------------------

#         aspect_ratio = (
#             width / height
#             if height > 0
#             else 0
#         )

#         aspect_ratio_name = self.get_aspect_ratio(
#             width,
#             height
#         )

#         # -----------------------------
#         # VIDEO QUALITY
#         # -----------------------------

#         if width >= 1920 and height >= 1080:
#             resolution_category = "1080p_or_higher"

#         elif width >= 1280 and height >= 720:
#             resolution_category = "720p"

#         elif width >= 854 and height >= 480:
#             resolution_category = "480p"

#         else:
#             resolution_category = "low_resolution"

#         # -----------------------------
#         # FILE INFORMATION
#         # -----------------------------

#         file_size_bytes = os.path.getsize(
#             self.video_path
#         )

#         file_size_mb = (
#             file_size_bytes / (1024 * 1024)
#         )

#         # -----------------------------
#         # ANALYSIS VARIABLES
#         # -----------------------------

#         brightness_values = []
#         contrast_values = []
#         motion_values = []

#         frame_brightness = []
#         frame_contrast = []

#         scene_changes = 0

#         previous_gray = None
#         previous_histogram = None

#         sampled_frames = 0

#         # -----------------------------
#         # FACE DETECTOR
#         # -----------------------------

#         face_cascade = cv2.CascadeClassifier(
#             cv2.data.haarcascades +
#             "haarcascade_frontalface_default.xml"
#         )

#         face_counts = []

#         # -----------------------------
#         # FRAME SAMPLING
#         # -----------------------------

#         sample_interval = max(
#             int(fps),
#             1
#         )

#         frame_index = 0

#         while True:

#             ret, frame = cap.read()

#             if not ret:
#                 break

#             if frame_index % sample_interval != 0:
#                 frame_index += 1
#                 continue

#             sampled_frames += 1

#             # Resize for faster analysis
#             frame = cv2.resize(
#                 frame,
#                 (640, 360)
#             )

#             gray = cv2.cvtColor(
#                 frame,
#                 cv2.COLOR_BGR2GRAY
#             )

#             # -----------------------------
#             # BRIGHTNESS
#             # -----------------------------

#             brightness = float(
#                 np.mean(gray)
#             )

#             brightness_values.append(
#                 brightness
#             )

#             # -----------------------------
#             # CONTRAST
#             # -----------------------------

#             contrast = float(
#                 np.std(gray)
#             )

#             contrast_values.append(
#                 contrast
#             )

#             # -----------------------------
#             # MOTION
#             # -----------------------------

#             if previous_gray is not None:

#                 diff = cv2.absdiff(
#                     previous_gray,
#                     gray
#                 )

#                 motion = float(
#                     np.mean(diff)
#                 )

#                 motion_values.append(
#                     motion
#                 )

#             previous_gray = gray.copy()

#             # -----------------------------
#             # SCENE CHANGE
#             # -----------------------------

#             histogram = cv2.calcHist(
#                 [gray],
#                 [0],
#                 None,
#                 [32],
#                 [0, 256]
#             )

#             cv2.normalize(
#                 histogram,
#                 histogram
#             )

#             if previous_histogram is not None:

#                 correlation = cv2.compareHist(
#                     previous_histogram,
#                     histogram,
#                     cv2.HISTCMP_CORREL
#                 )

#                 if correlation < 0.65:
#                     scene_changes += 1

#             previous_histogram = histogram

#             # -----------------------------
#             # FACE DETECTION
#             # -----------------------------

#             faces = face_cascade.detectMultiScale(
#                 gray,
#                 scaleFactor=1.1,
#                 minNeighbors=5,
#                 minSize=(30, 30)
#             )

#             face_counts.append(
#                 len(faces)
#             )

#             frame_index += 1

#         cap.release()

#         # -----------------------------
#         # FINAL FEATURES
#         # -----------------------------

#         avg_brightness = (
#             float(np.mean(brightness_values))
#             if brightness_values
#             else 0
#         )

#         avg_contrast = (
#             float(np.mean(contrast_values))
#             if contrast_values
#             else 0
#         )

#         motion_score = (
#             float(np.mean(motion_values))
#             if motion_values
#             else 0
#         )

#         face_count = (
#             int(max(face_counts))
#             if face_counts
#             else 0
#         )

#         face_presence_ratio = (
#             float(
#                 sum(
#                     1 for x in face_counts
#                     if x > 0
#                 ) / len(face_counts)
#             )
#             if face_counts
#             else 0
#         )

#         # -----------------------------
#         # PACING SCORE
#         # -----------------------------

#         if duration > 0:

#             scene_change_rate = (
#                 scene_changes / duration
#             )

#         else:

#             scene_change_rate = 0

#         pacing_score = min(
#             scene_change_rate * 10,
#             100
#         )

#         # -----------------------------
#         # HOOK INTENSITY
#         # -----------------------------

#         hook_intensity = self.calculate_hook(
#             motion_score,
#             scene_change_rate,
#             brightness_values
#         )

#         # -----------------------------
#         # VIDEO TAXONOMY
#         # -----------------------------

#         video_type = self.classify_video_format(
#             duration,
#             width,
#             height
#         )

#         # -----------------------------
#         # RETURN ALL FEATURES
#         # -----------------------------

#         return {

#             # Basic
#             "duration": round(duration, 2),
#             "fps": round(fps, 2),
#             "frame_count": frame_count,

#             # Dimensions
#             "width": width,
#             "height": height,
#             "resolution": resolution,
#             "resolution_category":
#                 resolution_category,

#             # Aspect ratio
#             "aspect_ratio":
#                 round(aspect_ratio, 3),

#             "aspect_ratio_name":
#                 aspect_ratio_name,

#             # File
#             "file_size_mb":
#                 round(file_size_mb, 2),

#             # Visual
#             "brightness":
#                 round(avg_brightness, 2),

#             "contrast":
#                 round(avg_contrast, 2),

#             "motion_score":
#                 round(motion_score, 2),

#             "scene_changes":
#                 scene_changes,

#             "scene_change_rate":
#                 round(scene_change_rate, 3),

#             # Faces
#             "face_count":
#                 face_count,

#             "face_presence_ratio":
#                 round(face_presence_ratio, 3),

#             # Engagement-related visual features
#             "hook_intensity":
#                 round(hook_intensity, 2),

#             "pacing_score":
#                 round(pacing_score, 2),

#             # Taxonomy
#             "video_format":
#                 video_type,

#             # Sampling
#             "sampled_frames":
#                 sampled_frames
#         }

#     # =====================================================
#     # ASPECT RATIO CLASSIFICATION
#     # =====================================================

#     def get_aspect_ratio(self, width, height):

#         if height == 0:
#             return "unknown"

#         ratio = width / height

#         # Vertical
#         if ratio < 0.8:
#             return "vertical"

#         # Square
#         elif 0.95 <= ratio <= 1.05:
#             return "square"

#         # Standard landscape
#         elif 1.3 <= ratio <= 1.4:
#             return "4:3"

#         # Widescreen
#         elif 1.7 <= ratio <= 1.85:
#             return "16:9"

#         else:
#             return "other"

#     # =====================================================
#     # VIDEO FORMAT CLASSIFICATION
#     # =====================================================

#     def classify_video_format(
#         self,
#         duration,
#         width,
#         height
#     ):

#         if height == 0:
#             return "unknown"

#         ratio = width / height

#         # Vertical short form
#         if ratio < 0.8 and duration <= 90:
#             return "short_form_vertical"

#         # Vertical long form
#         elif ratio < 0.8:
#             return "long_form_vertical"

#         # Square content
#         elif 0.95 <= ratio <= 1.05:
#             return "square_video"

#         # Landscape short
#         elif duration <= 90:
#             return "short_form_landscape"

#         # Landscape long
#         else:
#             return "long_form_landscape"

#     # =====================================================
#     # HOOK SCORE
#     # =====================================================

#     def calculate_hook(
#         self,
#         motion_score,
#         scene_change_rate,
#         brightness_values
#     ):

#         motion_component = min(
#             motion_score * 2,
#             50
#         )

#         scene_component = min(
#             scene_change_rate * 20,
#             30
#         )

#         brightness_component = 0

#         if brightness_values:

#             avg_brightness = np.mean(
#                 brightness_values
#             )

#             if 40 <= avg_brightness <= 220:
#                 brightness_component = 20

#         return min(
#             motion_component +
#             scene_component +
#             brightness_component,
#             100
#         )


import cv2
import numpy as np
import os
import torch
import torchvision

from PIL import Image

from torchvision.models.detection import (
    ssdlite320_mobilenet_v3_large,
    SSDLite320_MobileNet_V3_Large_Weights
)


class VideoFeatureExtractor:

    def __init__(self, video_path):

        self.video_path = video_path

        # =================================================
        # DEVICE
        # =================================================

        # CPU is intentionally used because the project
        # should work without requiring a GPU.
        self.device = torch.device("cpu")

        # =================================================
        # SSDLITE320 PERSON DETECTOR
        # =================================================

        print("=" * 60)
        print("Loading SSDLite320 MobileNetV3-Large...")
        print("Device:", self.device)
        print("=" * 60)

        weights = (
            SSDLite320_MobileNet_V3_Large_Weights.DEFAULT
        )

        self.person_model = (
            ssdlite320_mobilenet_v3_large(
                weights=weights
            )
        )

        self.person_model.to(self.device)
        self.person_model.eval()

        self.categories = weights.meta["categories"]

        print(
            "SSDLite320 loaded successfully."
        )

        # =================================================
        # HAAR FACE VERIFICATION
        # =================================================

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        self.profile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_profileface.xml"
        )

        # Verify cascade files loaded correctly
        if self.face_cascade.empty():
            print(
                "WARNING: Frontal face cascade could not be loaded."
            )

        if self.profile_cascade.empty():
            print(
                "WARNING: Profile face cascade could not be loaded."
            )

    # =====================================================
    # MAIN FEATURE EXTRACTION
    # =====================================================

    def extract(self):

        cap = cv2.VideoCapture(
            self.video_path
        )

        if not cap.isOpened():
            raise ValueError(
                "Unable to open video file."
            )

        # =================================================
        # BASIC VIDEO INFORMATION
        # =================================================

        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        frame_count = int(
            cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        width = int(
            cap.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )

        height = int(
            cap.get(
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

        # =================================================
        # RESOLUTION
        # =================================================

        resolution = (
            f"{width}x{height}"
        )

        # =================================================
        # ASPECT RATIO
        # =================================================

        aspect_ratio = (
            width / height
            if height > 0
            else 0
        )

        aspect_ratio_name = (
            self.get_aspect_ratio(
                width,
                height
            )
        )

        # =================================================
        # VIDEO QUALITY
        # =================================================

        if width >= 1920 and height >= 1080:

            resolution_category = (
                "1080p_or_higher"
            )

        elif width >= 1280 and height >= 720:

            resolution_category = (
                "720p"
            )

        elif width >= 854 and height >= 480:

            resolution_category = (
                "480p"
            )

        else:

            resolution_category = (
                "low_resolution"
            )

        # =================================================
        # FILE INFORMATION
        # =================================================

        try:

            file_size_bytes = os.path.getsize(
                self.video_path
            )

        except OSError:

            file_size_bytes = 0

        file_size_mb = (
            file_size_bytes /
            (1024 * 1024)
        )

        # =================================================
        # ANALYSIS VARIABLES
        # =================================================

        brightness_values = []
        contrast_values = []
        motion_values = []

        scene_changes = 0

        previous_gray = None
        previous_histogram = None

        sampled_frames = 0

        # =================================================
        # FACE / PERSON COUNTS
        # =================================================

        face_counts = []
        person_counts = []

        # =================================================
        # FRAME SAMPLING
        # =================================================

        # Approximately one frame per second.
        sample_interval = max(
            int(fps),
            1
        )

        frame_index = 0

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            # ---------------------------------------------
            # SAMPLE FRAME
            # ---------------------------------------------

            if (
                frame_index %
                sample_interval != 0
            ):

                frame_index += 1
                continue

            sampled_frames += 1

            # ---------------------------------------------
            # Resize for faster processing
            # ---------------------------------------------

            frame = cv2.resize(
                frame,
                (640, 360),
                interpolation=cv2.INTER_AREA
            )

            # =================================================
            # GRAYSCALE
            # =================================================

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            # =================================================
            # BRIGHTNESS
            # =================================================

            brightness = float(
                np.mean(gray)
            )

            brightness_values.append(
                brightness
            )

            # =================================================
            # CONTRAST
            # =================================================

            contrast = float(
                np.std(gray)
            )

            contrast_values.append(
                contrast
            )

            # =================================================
            # MOTION
            # =================================================

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

            # =================================================
            # SCENE CHANGE
            # =================================================

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

                correlation = (
                    cv2.compareHist(
                        previous_histogram,
                        histogram,
                        cv2.HISTCMP_CORREL
                    )
                )

                if correlation < 0.65:

                    scene_changes += 1

            previous_histogram = histogram

            # =================================================
            # PERSON + FACE DETECTION
            # =================================================

            person_count, face_count = (
                self.detect_persons_and_faces(
                    frame
                )
            )

            person_counts.append(
                person_count
            )

            face_counts.append(
                face_count
            )

            # ---------------------------------------------
            # Move to next frame
            # ---------------------------------------------

            frame_index += 1

        cap.release()

        # =================================================
        # FINAL BRIGHTNESS
        # =================================================

        avg_brightness = (

            float(
                np.mean(
                    brightness_values
                )
            )

            if brightness_values

            else 0.0
        )

        # =================================================
        # FINAL CONTRAST
        # =================================================

        avg_contrast = (

            float(
                np.mean(
                    contrast_values
                )
            )

            if contrast_values

            else 0.0
        )

        # =================================================
        # MOTION SCORE
        # =================================================

        motion_score = (

            float(
                np.mean(
                    motion_values
                )
            )

            if motion_values

            else 0.0
        )

        # =================================================
        # PERSON COUNT
        # =================================================

        person_count = (

            int(
                max(
                    person_counts
                )
            )

            if person_counts

            else 0
        )

        # =================================================
        # FACE COUNT
        # =================================================

        # Maximum number of simultaneously detected faces
        # in any sampled frame.

        face_count = (

            int(
                max(
                    face_counts
                )
            )

            if face_counts

            else 0
        )

        # Safety constraint:
        # faces cannot be greater than detected persons.

        face_count = min(
            face_count,
            person_count
        )

        # =================================================
        # FACE PRESENCE RATIO
        # =================================================

        face_presence_ratio = (

            float(
                sum(
                    1
                    for x in face_counts
                    if x > 0
                )
                /
                len(face_counts)
            )

            if face_counts

            else 0.0
        )

        # =================================================
        # PERSON PRESENCE RATIO
        # =================================================

        person_presence_ratio = (

            float(
                sum(
                    1
                    for x in person_counts
                    if x > 0
                )
                /
                len(person_counts)
            )

            if person_counts

            else 0.0
        )

        # =================================================
        # PACING SCORE
        # =================================================

        if duration > 0:

            scene_change_rate = (
                scene_changes /
                duration
            )

        else:

            scene_change_rate = 0.0

        pacing_score = min(
            scene_change_rate * 10,
            100
        )

        # =================================================
        # HOOK INTENSITY
        # =================================================

        hook_intensity = (
            self.calculate_hook(
                motion_score,
                scene_change_rate,
                brightness_values
            )
        )

        # =================================================
        # VIDEO TAXONOMY
        # =================================================

        video_type = (
            self.classify_video_format(
                duration,
                width,
                height
            )
        )

        # =================================================
        # RETURN FEATURES
        # =================================================

        return {

            # -------------------------------------------------
            # Basic
            # -------------------------------------------------

            "duration":
                round(
                    duration,
                    2
                ),

            "fps":
                round(
                    fps,
                    2
                ),

            "frame_count":
                frame_count,

            # -------------------------------------------------
            # Dimensions
            # -------------------------------------------------

            "width":
                width,

            "height":
                height,

            "resolution":
                resolution,

            "resolution_category":
                resolution_category,

            # -------------------------------------------------
            # Aspect ratio
            # -------------------------------------------------

            "aspect_ratio":
                round(
                    aspect_ratio,
                    3
                ),

            "aspect_ratio_name":
                aspect_ratio_name,

            # -------------------------------------------------
            # File
            # -------------------------------------------------

            "file_size_mb":
                round(
                    file_size_mb,
                    2
                ),

            # -------------------------------------------------
            # Visual
            # -------------------------------------------------

            "brightness":
                round(
                    avg_brightness,
                    2
                ),

            "contrast":
                round(
                    avg_contrast,
                    2
                ),

            "motion_score":
                round(
                    motion_score,
                    2
                ),

            # -------------------------------------------------
            # Scene
            # -------------------------------------------------

            "scene_changes":
                scene_changes,

            "scene_change_rate":
                round(
                    scene_change_rate,
                    3
                ),

            # -------------------------------------------------
            # Person
            # -------------------------------------------------

            "person_count":
                person_count,

            "person_presence_ratio":
                round(
                    person_presence_ratio,
                    3
                ),

            # -------------------------------------------------
            # Face
            # -------------------------------------------------

            "face_count":
                face_count,

            "face_presence_ratio":
                round(
                    face_presence_ratio,
                    3
                ),

            # -------------------------------------------------
            # Engagement-related visual features
            # -------------------------------------------------

            "hook_intensity":
                round(
                    hook_intensity,
                    2
                ),

            "pacing_score":
                round(
                    pacing_score,
                    2
                ),

            # -------------------------------------------------
            # Taxonomy
            # -------------------------------------------------

            "video_format":
                video_type,

            # -------------------------------------------------
            # Sampling
            # -------------------------------------------------

            "sampled_frames":
                sampled_frames
        }

    # =====================================================
    # PERSON + FACE DETECTION
    # =====================================================

    def detect_persons_and_faces(
        self,
        frame
    ):

        if frame is None:
            return 0, 0

        if frame.size == 0:
            return 0, 0

        # =================================================
        # BGR -> RGB
        # =================================================

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # =================================================
        # PIL IMAGE
        # =================================================

        image = Image.fromarray(
            rgb
        )

        # =================================================
        # IMAGE -> TENSOR
        # =================================================

        tensor = (
            torchvision
            .transforms
            .functional
            .to_tensor(
                image
            )
            .unsqueeze(0)
        )

        tensor = tensor.to(
            self.device
        )

        # =================================================
        # SSDLITE INFERENCE
        # =================================================

        with torch.no_grad():

            prediction = (
                self.person_model(
                    tensor
                )[0]
            )

        boxes = prediction[
            "boxes"
        ]

        labels = prediction[
            "labels"
        ]

        scores = prediction[
            "scores"
        ]

        # =================================================
        # DETECT PERSONS
        # =================================================

        persons = []

        for (
            box,
            label,
            score
        ) in zip(
            boxes,
            labels,
            scores
        ):

            confidence = float(
                score.cpu().item()
            )

            # ---------------------------------------------
            # Confidence threshold
            # ---------------------------------------------

            if confidence < 0.40:
                continue

            label_id = int(
                label.cpu().item()
            )

            if (
                label_id < 0
                or
                label_id >= len(
                    self.categories
                )
            ):
                continue

            category = (
                self.categories[
                    label_id
                ]
            )

            # ---------------------------------------------
            # Only PERSON
            # ---------------------------------------------

            if category != "person":
                continue

            # ---------------------------------------------
            # Bounding box
            # ---------------------------------------------

            box_values = (
                box
                .detach()
                .cpu()
                .numpy()
                .astype(int)
            )

            x1, y1, x2, y2 = (
                box_values
            )

            # ---------------------------------------------
            # Clamp coordinates
            # ---------------------------------------------

            frame_height, frame_width = (
                frame.shape[:2]
            )

            x1 = max(
                0,
                min(
                    x1,
                    frame_width - 1
                )
            )

            y1 = max(
                0,
                min(
                    y1,
                    frame_height - 1
                )
            )

            x2 = max(
                0,
                min(
                    x2,
                    frame_width
                )
            )

            y2 = max(
                0,
                min(
                    y2,
                    frame_height
                )
            )

            # ---------------------------------------------
            # Validate box
            # ---------------------------------------------

            if x2 <= x1:
                continue

            if y2 <= y1:
                continue

            person_width = (
                x2 - x1
            )

            person_height = (
                y2 - y1
            )

            if person_width < 20:
                continue

            if person_height < 30:
                continue

            persons.append(
                (
                    x1,
                    y1,
                    x2,
                    y2,
                    confidence
                )
            )

        # =================================================
        # PERSON COUNT
        # =================================================

        person_count = len(
            persons
        )

        # =================================================
        # FACE VERIFICATION
        # =================================================

        face_count = 0

        for (
            x1,
            y1,
            x2,
            y2,
            confidence
        ) in persons:

            person_height = (
                y2 - y1
            )

            # ---------------------------------------------
            # Top 45% of person box
            # ---------------------------------------------

            head_y2 = (
                y1 +
                int(
                    person_height *
                    0.45
                )
            )

            head_y2 = max(
                y1 + 1,
                min(
                    head_y2,
                    frame.shape[0]
                )
            )

            # ---------------------------------------------
            # Crop head region
            # ---------------------------------------------

            head_crop = frame[
                y1:head_y2,
                x1:x2
            ]

            if (
                head_crop.size == 0
            ):
                continue

            # ---------------------------------------------
            # Convert to grayscale
            # ---------------------------------------------

            head_gray = cv2.cvtColor(
                head_crop,
                cv2.COLOR_BGR2GRAY
            )

            # ---------------------------------------------
            # Improve local contrast
            # ---------------------------------------------

            head_gray = cv2.equalizeHist(
                head_gray
            )

            # ---------------------------------------------
            # Minimum crop size
            # ---------------------------------------------

            if (
                head_gray.shape[0] < 20
                or
                head_gray.shape[1] < 20
            ):
                continue

            # =================================================
            # FRONTAL FACE DETECTION
            # =================================================

            detected_faces = (
                self.face_cascade.detectMultiScale(
                    head_gray,
                    scaleFactor=1.08,
                    minNeighbors=4,
                    minSize=(15, 15)
                )
            )

            if len(
                detected_faces
            ) > 0:

                face_count += 1

                continue

            # =================================================
            # PROFILE FACE FALLBACK
            # =================================================

            profile_faces = (
                self.profile_cascade.detectMultiScale(
                    head_gray,
                    scaleFactor=1.08,
                    minNeighbors=4,
                    minSize=(15, 15)
                )
            )

            if len(
                profile_faces
            ) > 0:

                face_count += 1

        # =================================================
        # SAFETY CONSTRAINT
        # =================================================

        face_count = min(
            face_count,
            person_count
        )

        return (
            person_count,
            face_count
        )

    # =====================================================
    # ASPECT RATIO CLASSIFICATION
    # =====================================================

    def get_aspect_ratio(
        self,
        width,
        height
    ):

        if height == 0:
            return "unknown"

        ratio = (
            width /
            height
        )

        # Vertical
        if ratio < 0.8:

            return "vertical"

        # Square
        elif (
            0.95 <= ratio <= 1.05
        ):

            return "square"

        # Standard landscape
        elif (
            1.3 <= ratio <= 1.4
        ):

            return "4:3"

        # Widescreen
        elif (
            1.7 <= ratio <= 1.85
        ):

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

        ratio = (
            width /
            height
        )

        # ---------------------------------------------
        # Vertical short form
        # ---------------------------------------------

        if (
            ratio < 0.8
            and
            duration <= 90
        ):

            return (
                "short_form_vertical"
            )

        # ---------------------------------------------
        # Vertical long form
        # ---------------------------------------------

        elif ratio < 0.8:

            return (
                "long_form_vertical"
            )

        # ---------------------------------------------
        # Square
        # ---------------------------------------------

        elif (
            0.95 <= ratio <= 1.05
        ):

            return (
                "square_video"
            )

        # ---------------------------------------------
        # Landscape short
        # ---------------------------------------------

        elif duration <= 90:

            return (
                "short_form_landscape"
            )

        # ---------------------------------------------
        # Landscape long
        # ---------------------------------------------

        else:

            return (
                "long_form_landscape"
            )

    # =====================================================
    # HOOK SCORE
    # =====================================================

    def calculate_hook(
        self,
        motion_score,
        scene_change_rate,
        brightness_values
    ):

        # ---------------------------------------------
        # Motion component
        # ---------------------------------------------

        motion_component = min(
            motion_score * 2,
            50
        )

        # ---------------------------------------------
        # Scene component
        # ---------------------------------------------

        scene_component = min(
            scene_change_rate * 20,
            30
        )

        # ---------------------------------------------
        # Brightness component
        # ---------------------------------------------

        brightness_component = 0

        if brightness_values:

            avg_brightness = (
                np.mean(
                    brightness_values
                )
            )

            if (
                40 <= avg_brightness <= 220
            ):

                brightness_component = 20

        # ---------------------------------------------
        # Final hook score
        # ---------------------------------------------

        return min(
            motion_component +
            scene_component +
            brightness_component,
            100
        )


# =========================================================
# BACKWARD-COMPATIBLE FUNCTION
# =========================================================
#
# If any existing code does:
#
#     from video.extractor import extract_video_features
#
# this function will continue to work.
# =========================================================

def extract_video_features(
    video_path
):

    extractor = (
        VideoFeatureExtractor(
            video_path
        )
    )

    return extractor.extract()