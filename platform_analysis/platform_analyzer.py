# class PlatformAnalyzer:

#     SUPPORTED_PLATFORMS = [
#         "instagram",
#         "youtube",
#         "tiktok",
#         "facebook"
#     ]

#     def __init__(
#         self,
#         platform,
#         duration,
#         width,
#         height,
#         category="general"
#     ):

#         self.platform = (
#             str(platform or "instagram")
#             .strip()
#             .lower()
#         )

#         self.duration = float(
#             duration or 0
#         )

#         self.width = int(
#             width or 0
#         )

#         self.height = int(
#             height or 0
#         )

#         self.category = (
#             str(category or "general")
#             .strip()
#             .lower()
#         )

#     # =====================================================
#     # PLATFORM NORMALIZATION
#     # =====================================================

#     def normalize_platform(self):

#         aliases = {

#             "ig": "instagram",

#             "insta": "instagram",

#             "instagram reels": "instagram",

#             "yt": "youtube",

#             "youtube shorts": "youtube",

#             "shorts": "youtube",

#             "tiktok": "tiktok",

#             "fb": "facebook",

#             "facebook reels": "facebook"
#         }

#         return aliases.get(
#             self.platform,
#             self.platform
#         )

#     # =====================================================
#     # VIDEO ORIENTATION
#     # =====================================================

#     def orientation(self):

#         if self.width <= 0 or self.height <= 0:

#             return "unknown"

#         ratio = self.width / self.height

#         if ratio < 0.8:

#             return "vertical"

#         elif 0.95 <= ratio <= 1.05:

#             return "square"

#         else:

#             return "landscape"

#     # =====================================================
#     # FORMAT
#     # =====================================================

#     def format_type(self):

#         orientation = self.orientation()

#         if orientation == "vertical":

#             if self.duration <= 90:

#                 return "vertical_short"

#             return "vertical_long"

#         elif orientation == "square":

#             return "square"

#         else:

#             if self.duration <= 90:

#                 return "landscape_short"

#             return "landscape_long"

#     # =====================================================
#     # PLATFORM FORMAT COMPATIBILITY
#     # =====================================================

#     def format_compatibility(self):

#         platform = self.normalize_platform()

#         orientation = self.orientation()

#         duration = self.duration

#         score = 50

#         # -----------------------------------------------
#         # Instagram
#         # -----------------------------------------------

#         if platform == "instagram":

#             if orientation == "vertical":

#                 score += 40

#             elif orientation == "square":

#                 score += 20

#             if duration <= 90:

#                 score += 10

#         # -----------------------------------------------
#         # YouTube
#         # -----------------------------------------------

#         elif platform == "youtube":

#             if orientation == "vertical":

#                 score += 25

#             elif orientation == "landscape":

#                 score += 30

#             if duration <= 60:

#                 score += 10

#         # -----------------------------------------------
#         # TikTok
#         # -----------------------------------------------

#         elif platform == "tiktok":

#             if orientation == "vertical":

#                 score += 40

#             if duration <= 90:

#                 score += 10

#         # -----------------------------------------------
#         # Facebook
#         # -----------------------------------------------

#         elif platform == "facebook":

#             if orientation == "vertical":

#                 score += 30

#             elif orientation == "square":

#                 score += 20

#             if duration <= 90:

#                 score += 10

#         return min(
#             max(score, 0),
#             100
#         )

#     # =====================================================
#     # PLATFORM CATEGORY
#     # =====================================================

#     def platform_category(self):

#         platform = self.normalize_platform()

#         mapping = {

#             "instagram": "social_short_form",

#             "youtube": "video_search_and_recommendation",

#             "tiktok": "short_form_discovery",

#             "facebook": "social_video",

#         }

#         return mapping.get(
#             platform,
#             "unknown"
#         )

#     # =====================================================
#     # MAIN ANALYSIS
#     # =====================================================

#     def analyze(self):

#         platform = self.normalize_platform()

#         return {

#             "platform": platform,

#             "platform_supported":
#                 platform in self.SUPPORTED_PLATFORMS,

#             "orientation":
#                 self.orientation(),

#             "format_type":
#                 self.format_type(),

#             "platform_category":
#                 self.platform_category(),

#             "format_compatibility":
#                 self.format_compatibility()
#         }


class PlatformAnalyzer:

    SUPPORTED_PLATFORMS = [
        "instagram",
        "youtube",
        "tiktok",
        "facebook"
    ]

    def __init__(
        self,
        platform,
        duration,
        width,
        height,
        category="general",
        base_virality_score=0
    ):

        self.platform = (
            str(platform or "instagram")
            .strip()
            .lower()
        )

        self.duration = float(
            duration or 0
        )

        self.width = int(
            width or 0
        )

        self.height = int(
            height or 0
        )

        self.category = (
            str(category or "general")
            .strip()
            .lower()
        )

        # Overall ML prediction score will be used
        # as the base for platform-wise prediction.
        self.base_virality_score = float(
            base_virality_score or 0
        )

    # =====================================================
    # PLATFORM NORMALIZATION
    # =====================================================

    def normalize_platform(self):

        aliases = {

            "ig": "instagram",
            "insta": "instagram",
            "instagram reels": "instagram",

            "yt": "youtube",
            "youtube shorts": "youtube",
            "shorts": "youtube",

            "fb": "facebook",
            "facebook reels": "facebook"
        }

        return aliases.get(
            self.platform,
            self.platform
        )

    # =====================================================
    # VIDEO ORIENTATION
    # =====================================================

    def orientation(self):

        if self.width <= 0 or self.height <= 0:
            return "unknown"

        ratio = self.width / self.height

        if ratio < 0.8:
            return "vertical"

        elif 0.95 <= ratio <= 1.05:
            return "square"

        else:
            return "landscape"

    # =====================================================
    # FORMAT
    # =====================================================

    def format_type(self):

        orientation = self.orientation()

        if orientation == "vertical":

            if self.duration <= 90:
                return "vertical_short"

            return "vertical_long"

        elif orientation == "square":

            return "square"

        else:

            if self.duration <= 90:
                return "landscape_short"

            return "landscape_long"

    # =====================================================
    # PLATFORM FORMAT COMPATIBILITY
    # =====================================================

    def format_compatibility(self):

        platform = self.normalize_platform()

        orientation = self.orientation()

        duration = self.duration

        score = 50

        # -----------------------------------------------
        # Instagram
        # -----------------------------------------------

        if platform == "instagram":

            if orientation == "vertical":
                score += 40

            elif orientation == "square":
                score += 20

            if duration <= 90:
                score += 10

        # -----------------------------------------------
        # YouTube
        # -----------------------------------------------

        elif platform == "youtube":

            if orientation == "vertical":
                score += 25

            elif orientation == "landscape":
                score += 30

            if duration <= 60:
                score += 10

        # -----------------------------------------------
        # TikTok
        # -----------------------------------------------

        elif platform == "tiktok":

            if orientation == "vertical":
                score += 40

            if duration <= 90:
                score += 10

        # -----------------------------------------------
        # Facebook
        # -----------------------------------------------

        elif platform == "facebook":

            if orientation == "vertical":
                score += 30

            elif orientation == "square":
                score += 20

            if duration <= 90:
                score += 10

        return min(
            max(score, 0),
            100
        )

    # =====================================================
    # PLATFORM CATEGORY
    # =====================================================

    def platform_category(self):

        platform = self.normalize_platform()

        mapping = {

            "instagram":
                "social_short_form",

            "youtube":
                "video_search_and_recommendation",

            "tiktok":
                "short_form_discovery",

            "facebook":
                "social_video",

        }

        return mapping.get(
            platform,
            "unknown"
        )

    # =====================================================
    # PLATFORM VIRALITY ADJUSTMENT
    # =====================================================

    def platform_score_adjustment(self):

        """
        Platform-specific adjustment.

        This does NOT replace the ML model.
        It adapts the overall prediction according
        to the video's compatibility with each platform.
        """

        platform = self.normalize_platform()

        orientation = self.orientation()
        duration = self.duration

        adjustment = 0

        # -------------------------------------------------
        # Instagram
        # -------------------------------------------------

        if platform == "instagram":

            if orientation == "vertical":
                adjustment += 8

            elif orientation == "square":
                adjustment += 3

            elif orientation == "landscape":
                adjustment -= 5

            if duration <= 90:
                adjustment += 3

            elif duration > 180:
                adjustment -= 5

        # -------------------------------------------------
        # YouTube
        # -------------------------------------------------

        elif platform == "youtube":

            if orientation == "vertical":
                adjustment += 5

            elif orientation == "landscape":
                adjustment += 7

            if duration <= 60:
                adjustment += 3

            elif duration > 300:
                adjustment += 2

        # -------------------------------------------------
        # TikTok
        # -------------------------------------------------

        elif platform == "tiktok":

            if orientation == "vertical":
                adjustment += 10

            elif orientation == "square":
                adjustment -= 2

            elif orientation == "landscape":
                adjustment -= 8

            if duration <= 90:
                adjustment += 3

            elif duration > 180:
                adjustment -= 7

        # -------------------------------------------------
        # Facebook
        # -------------------------------------------------

        elif platform == "facebook":

            if orientation == "vertical":
                adjustment += 6

            elif orientation == "square":
                adjustment += 4

            elif orientation == "landscape":
                adjustment += 1

            if duration <= 90:
                adjustment += 2

        return adjustment

    # =====================================================
    # PLATFORM VIRALITY SCORE
    # =====================================================

    def virality_score(self):

        compatibility = self.format_compatibility()

        adjustment = self.platform_score_adjustment()

        # Base ML prediction
        base_score = self.base_virality_score

        # Compatibility contribution
        compatibility_effect = (
            (compatibility - 50) * 0.20
        )

        score = (
            base_score
            + compatibility_effect
            + adjustment
        )

        return round(
            min(max(score, 0), 100),
            1
        )

    # =====================================================
    # VIRALITY LABEL
    # =====================================================

    def virality_label(self, score):

        if score >= 80:
            return "Very High Viral Potential"

        elif score >= 65:
            return "High Viral Potential"

        elif score >= 50:
            return "Moderate Viral Potential"

        elif score >= 30:
            return "Low Viral Potential"

        return "Very Low Viral Potential"

    # =====================================================
    # ESTIMATED REACH
    # =====================================================

    def estimated_reach(
        self,
        overall_estimated_views
    ):

        """
        Estimates platform-specific reach using
        the overall ML estimated views as baseline.

        This is a derived estimate, not a platform API forecast.
        """

        base_views = float(
            overall_estimated_views or 0
        )

        compatibility = self.format_compatibility()

        score = self.virality_score()

        # Platform compatibility multiplier
        compatibility_multiplier = (
            0.70 +
            (compatibility / 100) * 0.60
        )

        # Virality multiplier
        virality_multiplier = (
            0.70 +
            (score / 100) * 0.60
        )

        estimated = (
            base_views
            * compatibility_multiplier
            * virality_multiplier
        )

        return max(
            0,
            round(estimated)
        )

    # =====================================================
    # PLATFORM ANALYSIS
    # =====================================================

    def analyze(
        self,
        overall_estimated_views=0
    ):

        platform = self.normalize_platform()

        compatibility = self.format_compatibility()

        score = self.virality_score()

        return {

            "platform": platform,

            "platform_supported":
                platform in self.SUPPORTED_PLATFORMS,

            "orientation":
                self.orientation(),

            "format_type":
                self.format_type(),

            "platform_category":
                self.platform_category(),

            "format_compatibility":
                compatibility,

            "virality_score":
                score,

            "virality_label":
                self.virality_label(score),

            "estimated_reach":
                self.estimated_reach(
                    overall_estimated_views
                )
        }


# =========================================================
# ALL PLATFORM ANALYSIS
# =========================================================

def analyze_all_platforms(
    duration,
    width,
    height,
    base_virality_score,
    overall_estimated_views=0,
    category="general"
):

    results = {}

    for platform in PlatformAnalyzer.SUPPORTED_PLATFORMS:

        analyzer = PlatformAnalyzer(

            platform=platform,

            duration=duration,

            width=width,

            height=height,

            category=category,

            base_virality_score=base_virality_score
        )

        results[platform] = analyzer.analyze(
            overall_estimated_views=
            overall_estimated_views
        )

    return results
