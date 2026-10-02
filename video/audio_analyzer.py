import cv2
import numpy as np


class AudioAnalyzer:

    def __init__(self, video_path):

        self.video_path = video_path

    def analyze(self):

        result = {

            "has_audio": False,

            "audio_type": "unknown",

            "audio_duration": 0,

            "speech_ratio": 0,

            "silence_ratio": 0,

            "music_ratio": 0,

            "audio_quality": "unknown"
        }

        try:

            import subprocess
            import json

            command = [

                "ffprobe",

                "-v",
                "quiet",

                "-print_format",
                "json",

                "-show_streams",

                self.video_path
            ]

            process = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

            data = json.loads(
                process.stdout
            )

            streams = data.get(
                "streams",
                []
            )

            audio_streams = [

                stream
                for stream in streams
                if stream.get("codec_type")
                == "audio"
            ]

            if not audio_streams:

                return result

            audio = audio_streams[0]

            result["has_audio"] = True

            result["audio_duration"] = float(
                audio.get("duration", 0)
                or 0
            )

            sample_rate = int(
                audio.get(
                    "sample_rate",
                    0
                )
                or 0
            )

            channels = int(
                audio.get(
                    "channels",
                    0
                )
                or 0
            )

            codec = audio.get(
                "codec_name",
                "unknown"
            )

            # -------------------------
            # AUDIO QUALITY
            # -------------------------

            if sample_rate >= 48000:

                result["audio_quality"] = "high"

            elif sample_rate >= 44100:

                result["audio_quality"] = "good"

            elif sample_rate >= 22050:

                result["audio_quality"] = "medium"

            else:

                result["audio_quality"] = "low"

            # -------------------------
            # BASIC AUDIO INFORMATION
            # -------------------------

            result["sample_rate"] = sample_rate

            result["channels"] = channels

            result["codec"] = codec

            # -------------------------
            # AUDIO TYPE
            # -------------------------

            if channels == 1:

                result["audio_type"] = "mono"

            elif channels >= 2:

                result["audio_type"] = "stereo"

            else:

                result["audio_type"] = "unknown"

            return result

        except Exception as e:

            result["error"] = str(e)

            return result