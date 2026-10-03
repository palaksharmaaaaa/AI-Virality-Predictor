import re
from collections import Counter


# ============================================================
# CTA PATTERNS - ENGLISH + HINDI + HINGLISH
# ============================================================

CTA_PATTERNS = [
    # English
    r"\bfollow\b",
    r"\bsubscribe\b",
    r"\blike\b",
    r"\bcomment\b",
    r"\bshare\b",
    r"\bsave\b",
    r"\bclick\b",
    r"\blink in bio\b",
    r"\bcheck out\b",
    r"\blet me know\b",
    r"\bjoin\b",
    r"\bdownload\b",
    r"\btry\b",
    r"\bvisit\b",
    r"\bwatch\b",
    r"\bcheck\b",

    # Hindi
    r"फॉलो",
    r"फॉलो करें",
    r"सब्सक्राइब",
    r"सब्सक्राइब करें",
    r"लाइक",
    r"लाइक करें",
    r"कमेंट",
    r"कमेंट करें",
    r"शेयर",
    r"शेयर करें",
    r"सेव",
    r"सेव करें",
    r"डाउनलोड",
    r"चेक करें",
    r"बताएं",
    r"बताइए",
    r"जुड़ें",
    r"देखें",
    r"जरूर देखें",

    # Common Hinglish
    r"\blike karo\b",
    r"\blike karna\b",
    r"\bcomment karo\b",
    r"\bcomment karna\b",
    r"\bshare karo\b",
    r"\bshare karna\b",
    r"\bfollow karo\b",
    r"\bfollow karna\b",
    r"\bsubscribe karo\b",
    r"\bsubscribe karna\b",
    r"\bchannel ko subscribe\b",
]


# ============================================================
# FILLER WORDS - ENGLISH + HINDI + HINGLISH
# ============================================================

FILLER_WORDS = {
    # English
    "um",
    "uh",
    "erm",
    "hmm",
    "like",
    "you know",
    "basically",
    "actually",
    "literally",

    # Hindi
    "उम",
    "अं",
    "हम्म",
    "मतलब",
    "यानि",
    "यानी",
    "असल में",

    # Hinglish
    "matlab",
    "yaani",
    "basically",
    "actually",
}


# ============================================================
# STOPWORDS - ENGLISH + HINDI
# ============================================================

STOPWORDS = {
    # English
    "the", "a", "an", "is", "are", "was", "were",
    "to", "of", "and", "or", "in", "on", "for",
    "with", "this", "that", "you", "your", "it",
    "i", "we", "they", "he", "she", "her",
    "his", "their", "my", "our", "me", "be",
    "been", "from", "as", "at", "by", "but",
    "if", "then", "so", "than", "about", "into",
    "can", "will", "would", "could", "should",
    "do", "does", "did",

    # Hindi
    "का", "के", "की", "को", "से", "में", "पर",
    "और", "या", "यह", "वह", "ये", "वे",
    "मैं", "हम", "आप", "तुम", "मुझे", "हमें",
    "आपको", "तुम्हें", "था", "थी", "थे",
    "है", "हैं", "हो", "कर", "करना", "करते",
    "एक", "इस", "उस", "तो", "भी", "ही",
    "जो", "कि", "नहीं", "अगर", "जब", "तक",
    "लेकिन", "अब", "बहुत", "साथ",
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    if not text:
        return ""

    text = str(text)

    # Remove Qwen / model special tokens
    special_tokens = [
        "<|im_end|>",
        "<|endoftext|>",
        "<|im_start|>",
        "<|end|>",
    ]

    for token in special_tokens:
        text = text.replace(token, " ")

    # Normalize excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# WORD TOKENIZATION
# ============================================================

def split_words(text):
    """
    Unicode-aware tokenizer.

    Supports:
    - English
    - Hindi
    - Hinglish
    - Other Unicode languages
    - Numbers
    - Apostrophes / hyphens inside words
    """

    if not text:
        return []

    return re.findall(
        r"[^\W\d_]+(?:['’-][^\W\d_]+)*|\d+(?:\.\d+)?",
        text.lower(),
        flags=re.UNICODE,
    )


# ============================================================
# CTA DETECTION
# ============================================================

def detect_cta(text):

    if not text:
        return []

    text_lower = text.lower()

    found = []

    for pattern in CTA_PATTERNS:

        if re.search(
            pattern,
            text_lower,
            flags=re.UNICODE
        ):
            clean_pattern = pattern

            clean_pattern = clean_pattern.replace(
                r"\b",
                ""
            )

            found.append(clean_pattern)

    return list(dict.fromkeys(found))


def calculate_cta_score(text):

    if not text:
        return 0.0

    ctas = detect_cta(text)

    if not ctas:
        return 0.0

    # Maximum score = 100
    score = min(len(ctas) * 20, 100)

    return float(score)


# ============================================================
# SPEECH DENSITY
# ============================================================

def calculate_speech_density(text, duration):

    if duration <= 0:
        return 0.0

    words = split_words(text)

    if not words:
        return 0.0

    words_per_second = len(words) / duration

    return round(words_per_second, 3)


# ============================================================
# HOOK DETECTION
# ============================================================

def detect_hook(text):

    if not text:
        return {
            "has_hook": False,
            "hook_score": 0
        }

    # First ~30 words are treated as opening/hook
    first_part = " ".join(
        text.split()[:30]
    ).lower()

    hook_patterns = [

        # English
        r"\bhow\b",
        r"\bwhy\b",
        r"\bwhat if\b",
        r"\bdid you know\b",
        r"\bsecret\b",
        r"\bmistake\b",
        r"\bstop\b",
        r"\bnever\b",
        r"\byou need to\b",
        r"\bhere's\b",
        r"\btoday\b",
        r"\bwatch\b",
        r"\blearn\b",
        r"\bdiscover\b",
        r"\bimportant\b",
        r"\bproblem\b",
        r"\bsolution\b",
        r"\bwait\b",
        r"\bbefore\b",

        # Hindi
        r"कैसे",
        r"क्यों",
        r"क्या होगा",
        r"क्या आप जानते",
        r"क्या आपको पता",
        r"राज",
        r"गलती",
        r"रुकिए",
        r"कभी नहीं",
        r"आपको जरूर",
        r"आज",
        r"देखिए",
        r"सीखिए",
        r"जानिए",
        r"महत्वपूर्ण",
        r"समस्या",
        r"समाधान",
        r"पहले",
        r"ध्यान दें",

        # Hinglish
        r"\bkaise\b",
        r"\bkyun\b",
        r"\bkya\b",
        r"\bsecret\b",
        r"\bmistake\b",
        r"\bdekho\b",
        r"\bsuno\b",
        r"\bjaaniye\b",
        r"\bseekhiye\b",
        r"\bimportant\b",
    ]

    matches = 0

    for pattern in hook_patterns:

        if re.search(
            pattern,
            first_part,
            flags=re.UNICODE
        ):
            matches += 1

    # Question in opening is also a hook signal
    if "?" in first_part or "?" in text[:200]:
        matches += 1

    score = min(matches * 20, 100)

    return {
        "has_hook": matches > 0,
        "hook_score": score
    }


# ============================================================
# SENTIMENT
# ============================================================

def detect_sentiment(text):

    positive_words = {
        # English
        "amazing",
        "great",
        "best",
        "love",
        "happy",
        "exciting",
        "awesome",
        "beautiful",
        "success",
        "successful",
        "good",
        "perfect",
        "wonderful",
        "excellent",
        "fun",
        "win",
        "winning",

        # Hindi
        "अच्छा",
        "अच्छी",
        "अच्छे",
        "बेहतरीन",
        "शानदार",
        "कमाल",
        "अद्भुत",
        "खुश",
        "खुशी",
        "सफलता",
        "सफल",
        "प्यार",
        "सुंदर",
        "मजेदार",
        "जीत",

        # Hinglish
        "accha",
        "achha",
        "best",
        "shandar",
        "kamal",
        "zabardast",
        "khush",
        "success",
        "successful",
        "maza",
    }

    negative_words = {
        # English
        "bad",
        "worst",
        "hate",
        "sad",
        "problem",
        "fail",
        "failure",
        "wrong",
        "danger",
        "dangerous",
        "poor",
        "terrible",
        "horrible",
        "mistake",
        "loss",
        "losing",

        # Hindi
        "बुरा",
        "बुरी",
        "बुरे",
        "खराब",
        "नफरत",
        "दुख",
        "दुखी",
        "समस्या",
        "असफल",
        "गलत",
        "खतरा",
        "खतरनाक",
        "भयानक",
        "गलती",
        "नुकसान",
        "हार",

        # Hinglish
        "bura",
        "kharab",
        "galat",
        "problem",
        "danger",
        "dangerous",
        "failure",
        "loss",
        "haar",
        "nuksan",
    }

    words = set(split_words(text))

    positive = len(
        words & positive_words
    )

    negative = len(
        words & negative_words
    )

    total = positive + negative

    if positive > negative:
        sentiment = "positive"

    elif negative > positive:
        sentiment = "negative"

    else:
        sentiment = "neutral"

    if total == 0:
        sentiment_score = 0.0

    else:
        sentiment_score = round(
            ((positive - negative) / total) * 100,
            2
        )

    return {
        "label": sentiment,
        "positive_count": positive,
        "negative_count": negative,
        "score": sentiment_score,
    }


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

def extract_keywords(text, top_n=10):

    words = split_words(text)

    filtered = [
        word
        for word in words
        if (
            word not in STOPWORDS
            and len(word) > 2
            and not word.isdigit()
        )
    ]

    counts = Counter(filtered)

    return [
        word
        for word, count in counts.most_common(top_n)
    ]


# ============================================================
# FILLER WORD RATIO
# ============================================================

def calculate_filler_ratio(text):

    words = split_words(text)

    if not words:
        return 0.0

    filler_count = 0

    text_lower = text.lower()

    for filler in FILLER_WORDS:

        if " " in filler:

            filler_count += len(
                re.findall(
                    re.escape(filler),
                    text_lower,
                    flags=re.UNICODE
                )
            )

        else:

            filler_count += sum(
                1
                for word in words
                if word == filler
            )

    ratio = (
        filler_count / len(words)
    ) * 100

    return round(ratio, 2)


# ============================================================
# SENTENCE COUNT
# ============================================================

def count_sentences(text):

    if not text:
        return 0

    # Handles ., !, ?, Hindi danda । and double danda ॥
    sentences = re.findall(
        r"[^.!?।！？]+[.!?।！？]+",
        text
    )

    if not sentences and text.strip():
        return 1

    return len(sentences)


# ============================================================
# VOCABULARY DIVERSITY
# ============================================================

def calculate_vocabulary_diversity(words):

    if not words:
        return 0.0

    unique_words = len(set(words))

    diversity = unique_words / len(words)

    return round(diversity, 2)


# ============================================================
# QUESTION DETECTION
# ============================================================

def count_questions(text):

    if not text:
        return 0

    return len(
        re.findall(
            r"[?？]",
            text
        )
    )


# ============================================================
# TRANSCRIPT QUALITY
# ============================================================

def calculate_transcript_quality(text):

    if not text:
        return 0.0

    words = split_words(text)

    if not words:
        return 0.0

    score = 100.0

    # Very short transcript
    if len(words) < 5:
        score -= 30

    elif len(words) < 10:
        score -= 15

    # Repeated same word excessively
    counts = Counter(words)

    most_common_count = (
        counts.most_common(1)[0][1]
        if counts
        else 0
    )

    if len(words) > 0:

        repetition_ratio = (
            most_common_count / len(words)
        )

        if repetition_ratio > 0.70:
            score -= 30

        elif repetition_ratio > 0.50:
            score -= 15

    return round(
        max(0.0, min(100.0, score)),
        2
    )


# ============================================================
# MAIN CONTENT ANALYSIS FUNCTION
# ============================================================

def analyze_content(text, duration=0):

    text = clean_text(text)

    words = split_words(text)

    hook = detect_hook(text)

    cta = detect_cta(text)

    cta_score = calculate_cta_score(text)

    sentiment = detect_sentiment(text)

    keywords = extract_keywords(text)

    speech_density = calculate_speech_density(
        text,
        duration
    )

    questions = count_questions(text)

    filler_ratio = calculate_filler_ratio(text)

    sentence_count = count_sentences(text)

    vocabulary_diversity = (
        calculate_vocabulary_diversity(words)
    )

    transcript_quality = (
        calculate_transcript_quality(text)
    )

    return {

        "transcript": text,

        "word_count": len(words),

        "unique_words": len(set(words)),

        "character_count": len(text),

        "sentence_count": sentence_count,

        "vocabulary_diversity": vocabulary_diversity,

        "filler_word_ratio": filler_ratio,

        "hook_score": hook["hook_score"],

        "has_hook": hook["has_hook"],

        "cta_detected": len(cta) > 0,

        "cta_score": cta_score,

        "cta_types": cta,

        "question_count": questions,

        "sentiment": sentiment["label"],

        "sentiment_score": sentiment["score"],

        "positive_words": sentiment["positive_count"],

        "negative_words": sentiment["negative_count"],

        "keywords": keywords,

        "speech_density": speech_density,

        "transcript_quality": transcript_quality,

    }


# ============================================================
# CONTENT ANALYZER CLASS
# Compatible with app.py
# ============================================================

class ContentAnalyzer:

    def __init__(self, transcript="", duration=0):

        self.transcript = transcript or ""

        self.duration = duration or 0

    def analyze(self):

        return analyze_content(
            self.transcript,
            self.duration
        )