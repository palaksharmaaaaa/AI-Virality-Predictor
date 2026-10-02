# ml/feature_builder.py

import math
import pandas as pd


class FeatureBuilder:
    """
    Converts video, content, creator, platform and hashtag
    analysis dictionaries into one ML-ready feature dictionary.
    """

    CATEGORICAL_FEATURES = [
        "platform",
        "orientation",
        "format_type",
        "video_format",
        "category",
        "creator_category",
    ]

    NUMERIC_FEATURES = [
        # Video
        "duration",
        "fps",
        "width",
        "height",
        "aspect_ratio",
        "motion_score",
        "scene_changes",
        "scene_change_rate",
        "face_count",
        "face_presence_ratio",
        "brightness",
        "contrast",
        "hook_intensity",
        "pacing_score",

        # Audio
        "has_audio",
        "speech_ratio",
        "silence_ratio",
        "music_ratio",

        # Content
        "word_count",
        "unique_word_count",
        "sentence_count",
        "vocabulary_diversity",
        "filler_word_ratio",
        "hook_score",
        "cta_score",
        "transcript_quality",
        "sentiment_score",

        # Creator
        "followers",
        "following",
        "log_followers",
        "follower_following_ratio",
        "profile_ratio_score",

        # Platform
        "format_compatibility",

        # Hashtags
        "hashtag_count",
        "unique_hashtag_count",
        "generic_hashtag_count",
        "niche_hashtag_count",
        "hashtag_category_relevance",
        "hashtag_niche_score",
        "hashtag_density",
    ]

    def _safe_float(self, value, default=0.0):
        try:
            if value is None:
                return default

            value = float(value)

            if not math.isfinite(value):
                return default

            return value

        except (TypeError, ValueError):
            return default

    def _safe_int(self, value, default=0):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default

    def _safe_text(self, value, default="unknown"):
        if value is None:
            return default

        value = str(value).strip().lower()

        return value if value else default

    def build(
        self,
        video_features=None,
        audio_features=None,
        content_features=None,
        creator_features=None,
        platform_features=None,
        hashtag_features=None,
    ):
        video_features = video_features or {}
        audio_features = audio_features or {}
        content_features = content_features or {}
        creator_features = creator_features or {}
        platform_features = platform_features or {}
        hashtag_features = hashtag_features or {}

        features = {}

        # =========================================================
        # VIDEO FEATURES
        # =========================================================

        features["duration"] = self._safe_float(
            video_features.get("duration")
        )

        features["fps"] = self._safe_float(
            video_features.get("fps")
        )

        features["width"] = self._safe_int(
            video_features.get("width")
        )

        features["height"] = self._safe_int(
            video_features.get("height")
        )

        features["aspect_ratio"] = self._safe_float(
            video_features.get("aspect_ratio")
        )

        features["motion_score"] = self._safe_float(
            video_features.get("motion_score")
        )

        features["scene_changes"] = self._safe_int(
            video_features.get("scene_changes")
        )

        features["scene_change_rate"] = self._safe_float(
            video_features.get("scene_change_rate")
        )

        features["face_count"] = self._safe_int(
            video_features.get("face_count")
        )

        features["face_presence_ratio"] = self._safe_float(
            video_features.get("face_presence_ratio")
        )

        features["brightness"] = self._safe_float(
            video_features.get("brightness")
        )

        features["contrast"] = self._safe_float(
            video_features.get("contrast")
        )

        features["hook_intensity"] = self._safe_float(
            video_features.get("hook_intensity")
        )

        features["pacing_score"] = self._safe_float(
            video_features.get("pacing_score")
        )

        features["video_format"] = self._safe_text(
            video_features.get("video_format"),
            "unknown"
        )

        # =========================================================
        # AUDIO FEATURES
        # =========================================================

        features["has_audio"] = int(
            bool(audio_features.get("has_audio", False))
        )

        features["speech_ratio"] = self._safe_float(
            audio_features.get("speech_ratio")
        )

        features["silence_ratio"] = self._safe_float(
            audio_features.get("silence_ratio")
        )

        features["music_ratio"] = self._safe_float(
            audio_features.get("music_ratio")
        )

        # =========================================================
        # CONTENT FEATURES
        # =========================================================

        features["word_count"] = self._safe_int(
            content_features.get("word_count")
        )

        features["unique_word_count"] = self._safe_int(
            content_features.get("unique_word_count")
        )

        features["sentence_count"] = self._safe_int(
            content_features.get("sentence_count")
        )

        features["vocabulary_diversity"] = self._safe_float(
            content_features.get("vocabulary_diversity")
        )

        features["filler_word_ratio"] = self._safe_float(
            content_features.get("filler_word_ratio")
        )

        features["hook_score"] = self._safe_float(
            content_features.get("hook_score")
        )

        features["cta_score"] = self._safe_float(
            content_features.get("cta_score")
        )

        features["transcript_quality"] = self._safe_float(
            content_features.get("transcript_quality")
        )

        features["sentiment_score"] = self._safe_float(
            content_features.get("sentiment_score")
        )

        features["category"] = self._safe_text(
            content_features.get("category"),
            "general"
        )

        # =========================================================
        # CREATOR FEATURES
        # =========================================================

        features["followers"] = self._safe_float(
            creator_features.get("followers")
        )

        features["following"] = self._safe_float(
            creator_features.get("following")
        )

        features["log_followers"] = self._safe_float(
            creator_features.get("log_followers")
        )

        features["follower_following_ratio"] = self._safe_float(
            creator_features.get("follower_following_ratio")
        )

        features["profile_ratio_score"] = self._safe_float(
            creator_features.get("profile_ratio_score")
        )

        features["creator_category"] = self._safe_text(
            creator_features.get("creator_category"),
            "general"
        )

        # =========================================================
        # PLATFORM FEATURES
        # =========================================================

        features["platform"] = self._safe_text(
            platform_features.get("platform"),
            "instagram"
        )

        features["orientation"] = self._safe_text(
            platform_features.get("orientation"),
            "unknown"
        )

        features["format_type"] = self._safe_text(
            platform_features.get("format_type"),
            "unknown"
        )

        features["format_compatibility"] = self._safe_float(
            platform_features.get("format_compatibility")
        )

        # =========================================================
        # HASHTAG FEATURES
        # =========================================================

        features["hashtag_count"] = self._safe_int(
            hashtag_features.get("hashtag_count")
        )

        features["unique_hashtag_count"] = self._safe_int(
            hashtag_features.get("unique_hashtag_count")
        )

        features["generic_hashtag_count"] = self._safe_int(
            hashtag_features.get("generic_hashtag_count")
        )

        features["niche_hashtag_count"] = self._safe_int(
            hashtag_features.get("niche_hashtag_count")
        )

        features["hashtag_category_relevance"] = self._safe_float(
            hashtag_features.get("hashtag_category_relevance")
        )

        features["hashtag_niche_score"] = self._safe_float(
            hashtag_features.get("hashtag_niche_score")
        )

        features["hashtag_density"] = self._safe_float(
            hashtag_features.get("hashtag_density")
        )

        return features

    @classmethod
    def get_feature_columns(cls):
        return cls.NUMERIC_FEATURES + cls.CATEGORICAL_FEATURES

    @classmethod
    def dataframe_from_features(cls, features):
        """
        Converts one feature dictionary into a pandas DataFrame.
        """
        row = {}

        for column in cls.get_feature_columns():
            row[column] = features.get(column, 0)

        return pd.DataFrame([row])