import cv2
import os


def generate_thumbnail(
    video_path,
    output_path
):

    capture = cv2.VideoCapture(
        video_path
    )

    if not capture.isOpened():
        return False

    frame_count = int(
        capture.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    if frame_count <= 0:

        capture.release()

        return False

    middle_frame = frame_count // 2

    capture.set(
        cv2.CAP_PROP_POS_FRAMES,
        middle_frame
    )

    success, frame = capture.read()

    capture.release()

    if not success:
        return False

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    return bool(
        cv2.imwrite(
            output_path,
            frame
        )
    )