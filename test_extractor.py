from video.extractor import VideoFeatureExtractor
from video.audio_analyzer import AudioAnalyzer
from video.transcript import TranscriptExtractor

from content.content_analyzer import ContentAnalyzer


VIDEO_PATH = "data/videos/video001.mp4"


# =====================================================
# VIDEO
# =====================================================

print("\n" + "=" * 60)
print("VIDEO ANALYSIS")
print("=" * 60)

video_extractor = VideoFeatureExtractor(
    VIDEO_PATH
)

video_features = video_extractor.extract()

for key, value in video_features.items():

    print(
        f"{key}: {value}"
    )


# =====================================================
# AUDIO
# =====================================================

print("\n" + "=" * 60)
print("AUDIO ANALYSIS")
print("=" * 60)

audio_analyzer = AudioAnalyzer(
    VIDEO_PATH
)

audio_features = audio_analyzer.analyze()

for key, value in audio_features.items():

    print(
        f"{key}: {value}"
    )


# =====================================================
# TRANSCRIPT
# =====================================================

print("\n" + "=" * 60)
print("TRANSCRIPT")
print("=" * 60)

transcript_extractor = TranscriptExtractor(
    VIDEO_PATH,
    model_size="base"
)

transcript_result = (
    transcript_extractor.transcribe()
)

print(
    "Success:",
    transcript_result["success"]
)

print(
    "Language:",
    transcript_result["language"]
)

print(
    "Transcript:",
    transcript_result["transcript"]
)


# =====================================================
# CONTENT ANALYSIS
# =====================================================

print("\n" + "=" * 60)
print("CONTENT ANALYSIS")
print("=" * 60)

content_analyzer = ContentAnalyzer(
    transcript_result["transcript"]
)

content_features = (
    content_analyzer.analyze()
)

for key, value in content_features.items():

    print(
        f"{key}: {value}"
    )