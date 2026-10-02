import math


class CreatorAnalyzer:

    def __init__(
        self,
        followers=0,
        following=0,
        category="general"
    ):

        self.followers = max(
            float(followers or 0),
            0
        )

        self.following = max(
            float(following or 0),
            0
        )

        self.category = (
            str(category or "general")
            .strip()
            .lower()
        )

    # =====================================================
    # FOLLOWER / FOLLOWING RATIO
    # =====================================================

    def follower_following_ratio(self):

        if self.following <= 0:

            return self.followers

        return self.followers / self.following

    # =====================================================
    # LOG FOLLOWER COUNT
    # =====================================================

    def log_followers(self):

        return round(
            math.log10(
                self.followers + 1
            ),
            4
        )

    # =====================================================
    # CREATOR SIZE
    # =====================================================

    def account_size(self):

        if self.followers < 1_000:

            return "nano"

        elif self.followers < 10_000:

            return "micro"

        elif self.followers < 100_000:

            return "mid"

        elif self.followers < 1_000_000:

            return "macro"

        else:

            return "mega"

    # =====================================================
    # FOLLOWER RANGE
    # =====================================================

    def follower_range(self):

        if self.followers < 1_000:
            return "0-1K"

        elif self.followers < 10_000:
            return "1K-10K"

        elif self.followers < 100_000:
            return "10K-100K"

        elif self.followers < 1_000_000:
            return "100K-1M"

        else:
            return "1M+"

    # =====================================================
    # FOLLOWING RATIO QUALITY
    # =====================================================

    def profile_ratio_score(self):

        ratio = self.follower_following_ratio()

        if ratio >= 100:
            return 100

        elif ratio >= 50:
            return 90

        elif ratio >= 20:
            return 75

        elif ratio >= 10:
            return 60

        elif ratio >= 5:
            return 45

        elif ratio >= 1:
            return 30

        else:
            return 15

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(self):

        ratio = self.follower_following_ratio()

        return {

            "followers": self.followers,

            "following": self.following,

            "log_followers":
                self.log_followers(),

            "follower_following_ratio":
                round(ratio, 4),

            "profile_ratio_score":
                self.profile_ratio_score(),

            "account_size":
                self.account_size(),

            "follower_range":
                self.follower_range(),

            "creator_category":
                self.category
        }