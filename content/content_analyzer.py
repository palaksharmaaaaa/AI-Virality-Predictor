import re
from collections import Counter


class ContentAnalyzer:

    def __init__(self, transcript=""):

        self.transcript = (
            transcript or ""
        ).strip()

        self.words = self._get_words()

    # =====================================================
    # BASIC WORD EXTRACTION
    # =====================================================

    def _get_words(self):

        return re.findall(
            r"\b[a-zA-ZÀ-ÿ']+\b",
            self.transcript.lower()
        )

    # =====================================================
    # WORD COUNT
    # =====================================================

    def word_count(self):

        return len(self.words)

    # =====================================================
    # UNIQUE WORDS
    # =====================================================

    def unique_word_count(self):

        return len(
            set(self.words)
        )

    # =====================================================
    # VOCABULARY DIVERSITY
    # =====================================================

    def vocabulary_diversity(self):

        if not self.words:
            return 0.0

        return round(
            len(set(self.words))
            / len(self.words),
            3
        )

    # =====================================================
    # SENTENCE COUNT
    # =====================================================

    def sentence_count(self):

        if not self.transcript:
            return 0

        sentences = re.split(
            r"[.!?]+",
            self.transcript
        )

        return len([
            x for x in sentences
            if x.strip()
        ])

    # =====================================================
    # FILLER WORDS
    # =====================================================

    def filler_word_analysis(self):

        filler_words = {
            "um",
            "uh",
            "umm",
            "like",
            "actually",
            "basically",
            "you know",
            "i mean",
            "so"
        }

        text = self.transcript.lower()

        count = 0

        for filler in filler_words:

            if " " in filler:

                count += text.count(
                    filler
                )

            else:

                count += self.words.count(
                    filler
                )

        total_words = len(self.words)

        ratio = (
            count / total_words
            if total_words > 0
            else 0
        )

        return {
            "filler_word_count": count,
            "filler_word_ratio": round(
                ratio,
                3
            )
        }

    # =====================================================
    # HOOK ANALYSIS
    # =====================================================

    def hook_analysis(self):

        if not self.transcript:

            return {
                "hook_present": False,
                "hook_score": 0,
                "hook_type": "none"
            }

        first_part = " ".join(
            self.words[:30]
        )

        hook_words = [

            "how",
            "why",
            "what",
            "secret",
            "mistake",
            "learn",
            "stop",
            "never",
            "best",
            "top",
            "easy",
            "important",
            "truth",
            "problem",
            "hack",
            "tips",
            "watch",
            "wait",
            "before"
        ]

        question_words = [
            "how",
            "why",
            "what",
            "when",
            "where",
            "who"
        ]

        score = 0
        hook_type = "none"

        # Question hook
        if "?" in self.transcript[:250]:

            score += 35
            hook_type = "question"

        # Strong hook words
        found_words = [

            word
            for word in hook_words
            if word in first_part
        ]

        if found_words:

            score += min(
                len(found_words) * 15,
                45
            )

            if hook_type == "none":
                hook_type = "curiosity"

        # Number/list hook
        if re.search(
            r"\b\d+\b",
            first_part
        ):

            score += 20

            if hook_type == "none":
                hook_type = "list"

        score = min(
            score,
            100
        )

        return {
            "hook_present": score >= 30,
            "hook_score": score,
            "hook_type": hook_type
        }

    # =====================================================
    # CTA ANALYSIS
    # =====================================================

    def cta_analysis(self):

        if not self.transcript:

            return {
                "cta_present": False,
                "cta_score": 0,
                "cta_type": "none"
            }

        text = self.transcript.lower()

        cta_patterns = {

            "follow": [
                "follow me",
                "follow us",
                "follow for more"
            ],

            "like": [
                "like this video",
                "give it a like",
                "like the video"
            ],

            "comment": [
                "comment below",
                "comment your",
                "let me know"
            ],

            "share": [
                "share this",
                "share the video"
            ],

            "subscribe": [
                "subscribe",
                "subscribe to my channel"
            ],

            "save": [
                "save this",
                "save this video"
            ]
        }

        detected = []

        for cta_type, phrases in cta_patterns.items():

            for phrase in phrases:

                if phrase in text:

                    detected.append(
                        cta_type
                    )

                    break

        detected = list(
            set(detected)
        )

        score = min(
            len(detected) * 25,
            100
        )

        cta_type = (
            detected[0]
            if detected
            else "none"
        )

        return {
            "cta_present": bool(detected),
            "cta_score": score,
            "cta_type": cta_type,
            "cta_types": detected
        }

    # =====================================================
    # SENTIMENT
    # =====================================================

    def sentiment_analysis(self):

        if not self.transcript:

            return {
                "sentiment": "neutral",
                "sentiment_score": 0
            }

        try:

            from textblob import TextBlob

            polarity = TextBlob(
                self.transcript
            ).sentiment.polarity

            if polarity > 0.15:

                sentiment = "positive"

            elif polarity < -0.15:

                sentiment = "negative"

            else:

                sentiment = "neutral"

            return {
                "sentiment": sentiment,
                "sentiment_score": round(
                    polarity,
                    3
                )
            }

        except Exception:

            return {
                "sentiment": "unknown",
                "sentiment_score": 0
            }

    # =====================================================
    # TOPIC / CATEGORY
    # =====================================================

    def category_analysis(self):

        text = self.transcript.lower()

        categories = {

            "technology": [
                "python",
                "programming",
                "coding",
                "software",
                "computer",
                "ai",
                "artificial intelligence",
                "machine learning",
                "technology",
                "developer"
            ],

            "fitness": [
                "gym",
                "workout",
                "fitness",
                "exercise",
                "muscle",
                "weight loss",
                "protein"
            ],

            "education": [
                "study",
                "exam",
                "student",
                "learn",
                "course",
                "education",
                "tutorial",
                "college"
            ],

            "finance": [
                "money",
                "investment",
                "stock",
                "finance",
                "trading",
                "loan",
                "business"
            ],

            "food": [
                "recipe",
                "food",
                "cook",
                "cooking",
                "restaurant",
                "taste",
                "kitchen"
            ],

            "travel": [
                "travel",
                "trip",
                "tour",
                "hotel",
                "flight",
                "vacation",
                "destination"
            ],

            "entertainment": [
                "movie",
                "music",
                "song",
                "comedy",
                "actor",
                "celebrity",
                "dance"
            ]
        }

        scores = {}

        for category, keywords in categories.items():

            score = 0

            for keyword in keywords:

                if keyword in text:
                    score += 1

            scores[category] = score

        if not any(scores.values()):

            return {
                "category": "general",
                "category_confidence": 0,
                "category_scores": scores
            }

        best_category = max(
            scores,
            key=scores.get
        )

        total = sum(
            scores.values()
        )

        confidence = (
            scores[best_category]
            / total
        )

        return {
            "category": best_category,
            "category_confidence": round(
                confidence,
                3
            ),
            "category_scores": scores
        }

    # =====================================================
    # SENSIBILITY / QUALITY
    # =====================================================

    def transcript_quality(self):

        if not self.transcript:

            return {
                "transcript_quality": 0,
                "transcript_quality_label":
                    "no_transcript"
            }

        words = self.words

        if len(words) < 3:

            return {
                "transcript_quality": 10,
                "transcript_quality_label":
                    "too_short"
            }

        filler = self.filler_word_analysis()

        filler_ratio = filler[
            "filler_word_ratio"
        ]

        vocabulary = self.vocabulary_diversity()

        sentences = self.sentence_count()

        score = 100

        # Penalize excessive fillers
        score -= min(
            filler_ratio * 100,
            25
        )

        # Very low vocabulary diversity
        if vocabulary < 0.20:

            score -= 20

        elif vocabulary < 0.30:

            score -= 10

        # No sentence structure
        if sentences == 0:

            score -= 20

        # Repeated words
        counts = Counter(words)

        most_common = (
            counts.most_common(1)[0][1]
            if counts
            else 0
        )

        if most_common > len(words) * 0.30:

            score -= 20

        score = max(
            0,
            min(score, 100)
        )

        if score >= 75:

            label = "good"

        elif score >= 50:

            label = "moderate"

        else:

            label = "poor"

        return {
            "transcript_quality":
                round(score, 2),

            "transcript_quality_label":
                label
        }

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(self):

        filler = self.filler_word_analysis()

        hook = self.hook_analysis()

        cta = self.cta_analysis()

        sentiment = self.sentiment_analysis()

        category = self.category_analysis()

        quality = self.transcript_quality()

        return {

            "transcript": self.transcript,

            "word_count":
                self.word_count(),

            "unique_word_count":
                self.unique_word_count(),

            "sentence_count":
                self.sentence_count(),

            "vocabulary_diversity":
                self.vocabulary_diversity(),

            **filler,

            **hook,

            **cta,

            **sentiment,

            **category,

            **quality
        }