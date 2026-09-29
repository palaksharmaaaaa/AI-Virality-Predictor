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

# FEATURE_COLUMNS = [
#     "likes",
#     "dislikes",
#     "comment_count",
#     "category_id",
#     "title_length",
#     "tags_count",
#     "description_length",
#     "publish_hour",
#     "publish_day",
# ]






import glob
import os
import cv2
import numpy as np
import pandas as pd

# Mediapipe install karne ke liye: pip install mediapipe opencv-python pandas
import mediapipe as mp

# MediaPipe Face Detection Setup
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)


def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0

    prev_gray = None
    motion_scores = []
    brightness_list = []
    contrast_list = []
    face_counts = []
    scene_changes = 0

    first_3sec_frames = int(fps * 3)
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 1. Brightness & Contrast
        brightness_list.append(np.mean(gray))
        contrast_list.append(np.std(gray))

        # 2. Motion Score (Optical Flow)
        if prev_gray is not None:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            motion = np.mean(magnitude)
            motion_scores.append(motion)

            # Scene Change Threshold
            if motion > 15.0:  # Sudden spike indicates cut
                scene_changes += 1

        prev_gray = gray

        # 3. Face Detection (Har 5th frame par performance ke liye)
        if frame_idx % 5 == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb_frame)
            faces = len(results.detections) if results.detections else 0
            face_counts.append(faces)

    cap.release()

    # Derived Features
    avg_motion = np.mean(motion_scores) if motion_scores else 0
    hook_motion = (
        np.mean(motion_scores[:first_3sec_frames])
        if len(motion_scores) >= first_3sec_frames
        else avg_motion
    )
    face_presence_ratio = (
        np.sum(np.array(face_counts) > 0) / len(face_counts)
        if face_counts
        else 0
    )
    max_faces = np.max(face_counts) if face_counts else 0
    pacing_score = (scene_changes / duration * 60) if duration > 0 else 0

    return {
        "video_name": os.path.basename(video_path),
        "duration": round(duration, 2),
        "fps": round(fps, 2),
        "width": width,
        "height": height,
        "motion_score": round(avg_motion, 2),
        "scene_changes": scene_changes,
        "hook_intensity": round(hook_motion, 2),
        "face_count": max_faces,
        "face_presence_ratio": round(face_presence_ratio, 2),
        "brightness": round(np.mean(brightness_list), 2)
        if brightness_list
        else 0,
        "contrast": round(np.mean(contrast_list), 2) if contrast_list else 0,
        "pacing_score": round(pacing_score, 2),
    }


# Run Extractor on Folder
video_folder = "./videos"  # Aapke videos ka folder path
results = []

for file in glob.glob(os.path.join(video_folder, "*.mp4")):
    print(f"Processing: {file}...")
    feat = analyze_video(file)
    results.append(feat)

df = pd.DataFrame(results)
df.to_csv("video_features.csv", index=False)
print("\nExtraction Complete! Data saved in 'video_features.csv'")