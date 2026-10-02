import re


class HashtagAnalyzer:

    def __init__(
        self,
        hashtags="",
        content_category="general"
    ):

        self.raw_hashtags = (
            hashtags or ""
        )

        self.content_category = (
            str(
                content_category
                or "general"
            )
            .strip()
            .lower()
        )

    # =====================================================
    # EXTRACT HASHTAGS
    # =====================================================

    def extract_hashtags(self):

        hashtags = re.findall(
            r"#([A-Za-z0-9_]+)",
            self.raw_hashtags.lower()
        )

        # Remove duplicates
        return list(
            dict.fromkeys(
                hashtags
            )
        )

    # =====================================================
    # CATEGORY KEYWORDS
    # =====================================================

    CATEGORY_KEYWORDS = {

        "technology": [
            "technology",
            "tech",
            "python",
            "coding",
            "programming",
            "ai",
            "machinelearning",
            "artificialintelligence",
            "developer"
        ],

        "fitness": [
            "fitness",
            "gym",
            "workout",
            "fitnessmotivation",
            "exercise",
            "muscle",
            "weightloss"
        ],

        "education": [
            "education",
            "study",
            "student",
            "learning",
            "exam",
            "tutorial",
            "college"
        ],

        "finance": [
            "finance",
            "money",
            "investment",
            "stocks",
            "trading",
            "business"
        ],

        "food": [
            "food",
            "recipe",
            "cooking",
            "foodie",
            "restaurant"
        ],

        "travel": [
            "travel",
            "traveling",
            "vacation",
            "tourism",
            "trip",
            "travelblogger"
        ],

        "entertainment": [
            "entertainment",
            "comedy",
            "music",
            "dance",
            "movie",
            "celebrity"
        ]
    }

    # =====================================================
    # CATEGORY RELEVANCE
    # =====================================================

    def category_relevance(self, hashtags):

        if not hashtags:

            return 0

        keywords = self.CATEGORY_KEYWORDS.get(
            self.content_category,
            []
        )

        if not keywords:

            return 0

        matches = 0

        for hashtag in hashtags:

            if hashtag in keywords:

                matches += 1

        return round(
            matches / len(hashtags),
            3
        )

    # =====================================================
    # GENERIC HASHTAGS
    # =====================================================

    def generic_hashtag_count(
        self,
        hashtags
    ):

        generic = {

            "viral",
            "fyp",
            "foryou",
            "foryoupage",
            "trending",
            "explore",
            "explorepage",
            "reels",
            "shorts"
        }

        return sum(
            1
            for hashtag in hashtags
            if hashtag in generic
        )

    # =====================================================
    # NICHE HASHTAG SCORE
    # =====================================================

    def niche_score(self, hashtags):

        if not hashtags:

            return 0

        generic_count = (
            self.generic_hashtag_count(
                hashtags
            )
        )

        niche_count = (
            len(hashtags)
            - generic_count
        )

        return round(
            niche_count /
            len(hashtags),
            3
        )

    # =====================================================
    # HASHTAG DENSITY
    # =====================================================

    def hashtag_density(
        self,
        word_count
    ):

        hashtags = self.extract_hashtags()

        if word_count <= 0:

            return 0

        return round(
            len(hashtags)
            / word_count,
            3
        )

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(
        self,
        word_count=0
    ):

        hashtags = (
            self.extract_hashtags()
        )

        relevance = (
            self.category_relevance(
                hashtags
            )
        )

        generic_count = (
            self.generic_hashtag_count(
                hashtags
            )
        )

        niche_score = (
            self.niche_score(
                hashtags
            )
        )

        return {

            "hashtags": hashtags,

            "hashtag_count":
                len(hashtags),

            "unique_hashtag_count":
                len(set(hashtags)),

            "generic_hashtag_count":
                generic_count,

            "niche_hashtag_count":
                max(
                    len(hashtags)
                    - generic_count,
                    0
                ),

            "hashtag_category_relevance":
                relevance,

            "hashtag_niche_score":
                niche_score,

            "hashtag_density":
                self.hashtag_density(
                    word_count
                )
        }