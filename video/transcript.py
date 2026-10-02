# import os
# import subprocess
# import tempfile


# class TranscriptExtractor:

#     def __init__(self, video_path, model_size="base"):
#         self.video_path = video_path
#         self.model_size = model_size
#         self.model = None

#     # =====================================================
#     # LOAD WHISPER
#     # =====================================================

#     def _load_model(self):

#         if self.model is not None:
#             return self.model

#         try:
#             import whisper

#             self.model = whisper.load_model(
#                 self.model_size
#             )

#             return self.model

#         except ImportError:

#             raise ImportError(
#                 "Whisper is not installed. "
#                 "Run: pip install openai-whisper"
#             )

#     # =====================================================
#     # EXTRACT AUDIO FROM VIDEO
#     # =====================================================

#     def _extract_audio(self):

#         temp_dir = tempfile.mkdtemp()

#         audio_path = os.path.join(
#             temp_dir,
#             "audio.wav"
#         )

#         command = [
#             "ffmpeg",
#             "-y",
#             "-i",
#             self.video_path,
#             "-vn",
#             "-acodec",
#             "pcm_s16le",
#             "-ar",
#             "16000",
#             "-ac",
#             "1",
#             audio_path
#         ]

#         result = subprocess.run(
#             command,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )

#         if result.returncode != 0:

#             raise RuntimeError(
#                 "FFmpeg could not extract audio.\n"
#                 + result.stderr[-1000:]
#             )

#         return audio_path

#     # =====================================================
#     # TRANSCRIBE
#     # =====================================================

#     def transcribe(self):

#         try:

#             model = self._load_model()

#             audio_path = self._extract_audio()

#             result = model.transcribe(
#                 audio_path,
#                 fp16=False,
#                 verbose=False
#             )

#             transcript = (
#                 result.get("text", "")
#                 .strip()
#             )

#             language = result.get(
#                 "language",
#                 "unknown"
#             )

#             segments = result.get(
#                 "segments",
#                 []
#             )

#             return {
#                 "transcript": transcript,
#                 "language": language,
#                 "segments": segments,
#                 "success": True,
#                 "error": None
#             }

#         except Exception as e:

#             return {
#                 "transcript": "",
#                 "language": "unknown",
#                 "segments": [],
#                 "success": False,
#                 "error": str(e)
#             }


import os
import subprocess
import tempfile
import wave
import numpy as np
import imageio_ffmpeg
import whisper


# Bundled FFmpeg path
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# Also add FFmpeg folder to PATH
FFMPEG_DIR = os.path.dirname(FFMPEG_PATH)
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")


class TranscriptAnalyzer:

    def __init__(self, model_name="small"):
        self.model_name = model_name
        self.model = None

    def load_model(self):
        if self.model is None:
            print(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)

    def has_audio_stream(self, video_path):

        try:
            result = subprocess.run(
                [
                    FFMPEG_PATH,
                    "-i",
                    video_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                errors="ignore"
            )

            output = result.stderr.lower()

            return "audio:" in output

        except Exception as e:
            print("Audio stream detection error:", e)
            return False

    def extract_audio(self, video_path):

        wav_path = os.path.join(
            tempfile.gettempdir(),
            "virality_whisper_audio.wav"
        )

        command = [
            FFMPEG_PATH,
            "-y",
            "-i",
            video_path,
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-acodec",
            "pcm_s16le",
            wav_path
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="ignore"
        )

        if result.returncode != 0:
            raise RuntimeError(
                "FFmpeg audio extraction failed:\n"
                + result.stderr[-3000:]
            )

        if not os.path.exists(wav_path):
            raise RuntimeError("WAV file was not created.")

        return wav_path

    def load_wav_as_numpy(self, wav_path):

        with wave.open(wav_path, "rb") as wf:

            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frames = wf.getnframes()

            audio_bytes = wf.readframes(frames)

        if sample_width != 2:
            raise RuntimeError(
                f"Unexpected WAV sample width: {sample_width}"
            )

        audio = np.frombuffer(
            audio_bytes,
            dtype=np.int16
        ).astype(np.float32)

        # Normalize int16 → float32
        audio = audio / 32768.0

        # Mono conversion if necessary
        if channels > 1:
            audio = audio.reshape(-1, channels)
            audio = audio.mean(axis=1)

        return audio, sample_rate

    def transcribe(self, video_path):

        result = {
            "success": False,
            "transcript": "",
            "language": "",
            "segments": [],
            "error": ""
        }

        try:

            if not os.path.exists(video_path):
                result["error"] = "Video file does not exist."
                return result

            print("Video:", video_path)
            print("FFmpeg:", FFMPEG_PATH)

            # Check audio
            if not self.has_audio_stream(video_path):

                result["error"] = "No audio stream found in video."
                return result

            print("Audio stream detected.")

            # Extract audio
            wav_path = self.extract_audio(video_path)

            print("Audio extracted:", wav_path)

            # Load WAV directly into numpy
            # This avoids Whisper calling external ffmpeg again.
            audio, sample_rate = self.load_wav_as_numpy(wav_path)

            print(
                f"Audio loaded: {len(audio)} samples @ {sample_rate} Hz"
            )

            # Load Whisper
            self.load_model()

            print("Transcribing...")

            whisper_result = self.model.transcribe(
                audio,
                language="hi",
                task="transcribe",
                fp16=False
            )

            transcript = whisper_result.get(
                "text",
                ""
            ).strip()

            segments = whisper_result.get(
                "segments",
                []
            )

            language = whisper_result.get(
                "language",
                ""
            )

            result["success"] = True
            result["transcript"] = transcript
            result["language"] = language
            result["segments"] = segments

            print("Transcription completed.")
            print("Language:", language)
            print("Transcript:", transcript)

            # Cleanup
            try:
                os.remove(wav_path)
            except Exception:
                pass

            return result

        except Exception as e:

            result["error"] = str(e)

            print("TRANSCRIPTION ERROR:")
            print(e)

            return result


# Compatibility function
def transcribe_video(video_path, model_name="small"):

    analyzer = TranscriptAnalyzer(model_name)

    return analyzer.transcribe(video_path)