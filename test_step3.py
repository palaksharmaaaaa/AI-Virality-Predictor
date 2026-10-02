from video.extractor import VideoFeatureExtractor
from video.transcript import TranscriptExtractor
from content.content_analyzer import ContentAnalyzer

from creator.creator_analyzer import CreatorAnalyzer
from platform.platform_analyzer import PlatformAnalyzer
from hashtag.hashtag_analyzer import HashtagAnalyzer


VIDEO_PATH = "data/videos/video001.mp4"


# =====================================================
# USER INPUT
# =====================================================

PLATFORM = "Instagram"

FOLLOWERS = 25000

FOLLOWING = 800

CREATOR_CATEGORY = "fitness"

HASHTAGS = """
#fitness
#gym
#workout
#fitnessmotivation
#viral
#reels
"""


# =====================================================
# VIDEO
# =====================================================

print("\n" + "=" * 70)
print("1. VIDEO")
print("=" * 70)

video = VideoFeatureExtractor(
    VIDEO_PATH
)

video_features = video.extract()

for key, value in video_features.items():

    print(
        f"{key}: {value}"
    )


# =====================================================
# TRANSCRIPT
# =====================================================

print("\n" + "=" * 70)
print("2. TRANSCRIPT")
print("=" * 70)

transcriber = TranscriptExtractor(
    VIDEO_PATH,
    model_size="base"
)

transcript_result = (
    transcriber.transcribe()
)

transcript = transcript_result[
    "transcript"
]

print(
    "Language:",
    transcript_result["language"]
)

print(
    "Transcript:",
    transcript
)


# =====================================================
# CONTENT
# =====================================================

print("\n" + "=" * 70)
print("3. CONTENT")
print("=" * 70)

content = ContentAnalyzer(
    transcript
)

content_features = (
    content.analyze()
)

for key, value in content_features.items():

    print(
        f"{key}: {value}"
    )


# =====================================================
# CREATOR
# =====================================================

print("\n" + "=" * 70)
print("4. CREATOR")
print("=" * 70)

creator = CreatorAnalyzer(

    followers=FOLLOWERS,

    following=FOLLOWING,

    category=CREATOR_CATEGORY
)

creator_features = creator.analyze()

for key, value in creator_features.items():

    print(
        f"{key}: {value}"
    )


# =====================================================
# PLATFORM
# =====================================================

print("\n" + "=" * 70)
print("5. PLATFORM")
print("=" * 70)

platform = PlatformAnalyzer(

    platform=PLATFORM,

    duration=video_features[
        "duration"
    ],

    width=video_features[
        "width"
    ],

    height=video_features[
        "height"
    ],

    category=CREATOR_CATEGORY
)

platform_features = platform.analyze()

for key, value in platform_features.items():

    print(
        f"{key}: {value}"
    )


# =====================================================
# HASHTAGS
# =====================================================

print("\n" + "=" * 70)
print("6. HASHTAGS")
print("=" * 70)

hashtag = HashtagAnalyzer(

    hashtags=HASHTAGS,

    content_category=CREATOR_CATEGORY
)

hashtag_features = hashtag.analyze(

    word_count=content_features[
        "word_count"
    ]
)

for key, value in hashtag_features.items():

    print(
        f"{key}: {value}"
    )


# =====================================================
# FINAL FEATURE VECTOR
# =====================================================

print("\n" + "=" * 70)
print("7. FINAL FEATURE SUMMARY")
print("=" * 70)

final_features = {

    # Video
    "duration":
        video_features["duration"],

    "fps":
        video_features["fps"],

    "width":
        video_features["width"],

    "height":
        video_features["height"],

    "aspect_ratio":
        video_features["aspect_ratio"],

    "motion_score":
        video_features["motion_score"],

    "scene_changes":
        video_features["scene_changes"],

    "face_count":
        video_features["face_count"],

    "brightness":
        video_features["brightness"],

    "contrast":
        video_features["contrast"],

    "hook_intensity":
        video_features["hook_intensity"],

    "pacing_score":
        video_features["pacing_score"],

    # Content
    "word_count":
        content_features["word_count"],

    "vocabulary_diversity":
        content_features[
            "vocabulary_diversity"
        ],

    "filler_word_ratio":
        content_features[
            "filler_word_ratio"
        ],

    "hook_score":
        content_features[
            "hook_score"
        ],

    "cta_score":
        content_features[
            "cta_score"
        ],

    "transcript_quality":
        content_features[
            "transcript_quality"
        ],

    "sentiment_score":
        content_features[
            "sentiment_score"
        ],

    # Creator
    "followers":
        creator_features["followers"],

    "following":
        creator_features["following"],

    "log_followers":
        creator_features["log_followers"],

    "follower_following_ratio":
        creator_features[
            "follower_following_ratio"
        ],

    "profile_ratio_score":
        creator_features[
            "profile_ratio_score"
        ],

    # Platform
    "format_compatibility":
        platform_features[
            "format_compatibility"
        ],

    # Hashtags
    "hashtag_count":
        hashtag_features[
            "hashtag_count"
        ],

    "hashtag_category_relevance":
        hashtag_features[
            "hashtag_category_relevance"
        ],

    "hashtag_niche_score":
        hashtag_features[
            "hashtag_niche_score"
        ],

    "hashtag_density":
        hashtag_features[
            "hashtag_density"
        ]
}


for key, value in final_features.items():

    print(
        f"{key}: {value}"
    )