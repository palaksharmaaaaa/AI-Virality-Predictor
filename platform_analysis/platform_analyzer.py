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
        category="general"
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

            "tiktok": "tiktok",

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

            "instagram": "social_short_form",

            "youtube": "video_search_and_recommendation",

            "tiktok": "short_form_discovery",

            "facebook": "social_video",

        }

        return mapping.get(
            platform,
            "unknown"
        )

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(self):

        platform = self.normalize_platform()

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
                self.format_compatibility()
        }