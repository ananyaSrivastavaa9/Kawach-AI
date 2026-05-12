"""
toxic_words.py - Kawach AI Toxicity Detection Engine
Hindi/English/Hinglish slur dictionary, scoring, and rewrite logic.
"""

# English slurs and hate speech triggers
ENGLISH_TOXIC = [
    # General abuse
    "idiot", "stupid", "moron", "dumb", "fool", "loser", "trash", "garbage",
    "worthless", "useless", "pathetic", "disgusting", "filthy", "dirty",
    "freak", "weirdo", "psycho", "lunatic", "retard", "retarded",
    # Hate speech - religion/caste/ethnicity (sanitized references)
    "terrorist", "jihadi", "kafir", "infidel",
    "dalit", "chamar", "bhangi", "lower caste",
    "nigger", "negro", "chink", "paki", "curry muncher",
    # Violence
    "kill", "murder", "rape", "beat", "stab", "shoot", "die", "hang",
    "suicide", "attack", "bomb", "destroy",
    # Profanity
    "bitch", "bastard", "asshole", "dick", "cock", "pussy", "fuck", "shit",
    "crap", "damn", "hell", "cunt", "slut", "whore",
]

# Hindi gaaliyan and slurs (romanized)
HINDI_TOXIC = [
    # General gaaliyan
    "gandu", "madarchod", "behenchod", "bhenchod", "chutiya", "chutiye",
    "saala", "saali", "haramzada", "haramzadi", "kamina", "kamine",
    "kutte", "kutta", "suar", "suwar", "ullu", "bakwaas",
    "gadha", "gadhe", "donkey", "kambakht", "bewakoof", "pagal",
    "besharam", "nalayak", "nikamma", "nikammi", "buddhu",
    # Caste slurs
    "chamar", "bhangi", "dhed", "chandal", "neech", "adhama",
    # Religious slurs
    "kaffir", "kafir", "mlechha", "harami", "haram",
    # Body-based abuse
    "hijra", "chakka", "klinja", "randi", "randwa",
    # Violence references (Hindi)
    "maar", "maar dalo", "kaat", "jalao", "jala do", "uda do",
]

# Hinglish mixed triggers (commonly used online)
HINGLISH_TOXIC = [
    "tu kya samjhta hai", "teri maa ki", "teri bahen ki",
    "mc", "bc", "lodu", "lode", "laude", "laudu",
    "chut", "gaand", "gand", "bhosda", "bhosdi",
    "randi rona", "rona dhona", "chal hatt", "nikal yahan se",
    "bsdk", "mkc", "mkg", "lmao loser",
    "andha hai", "bahra hai", "goonga hai",
    # Caste + religion combo slurs used online
    "anti national", "deshdrohi", "urban naxal",
    "tukde tukde", "bhakt", "sickular", "libtard", "presstitute",
]

# Combine all toxic words
ALL_TOXIC_WORDS = list(set(ENGLISH_TOXIC + HINDI_TOXIC + HINGLISH_TOXIC))

HIGH_SEVERITY = [
    "madarchod", "behenchod", "bhenchod", "rape", "kill", "murder",
    "chutiya", "gandu", "randi", "terrorist", "bomb", "shoot", "stab",
    "nigger", "bhangi", "chamar", "haramzada", "bhosda", "gaand",
]

MEDIUM_SEVERITY = [
    "idiot", "stupid", "moron", "bastard", "bitch", "fuck", "shit",
    "saala", "kutte", "suar", "kambakht", "bewakoof", "pagal",
    "asshole", "dick", "pussy", "loser", "trash",
]

# Words that reduce severity (positive context indicators)
POSITIVE_CONTEXT = [
    "not", "nahi", "mat", "please", "sorry", "maafi", "forgive",
    "no", "never", "love", "pyaar", "care", "help",
]

def tokenize(text: str) -> list[str]:
    """
    Simple tokenizer - text ko words mein todna
    Handles Hinglish by splitting on spaces and punctuation.
    """
    import re
    text = text.lower()
    # Remove punctuation except apostrophes
    text = re.sub(r"[^\w\s']", " ", text)
    tokens = text.split()
    return [t.strip("'") for t in tokens if t.strip("'")]


def find_trigger_words(text: str) -> list[str]:
    """
    Text mein toxic words dhundna.
    Returns list of matched toxic words found.
    """
    tokens = tokenize(text)
    text_lower = text.lower()
    found = []

    for word in ALL_TOXIC_WORDS:
        word_lower = word.lower()
        # Check multi-word phrases
        if " " in word_lower:
            if word_lower in text_lower:
                found.append(word)
        else:
            # Single word match
            if word_lower in tokens:
                found.append(word)

    return list(set(found))


def calculate_toxicity_score(text: str) -> dict:
    """
    Toxicity score calculate karna (0-100).

    Scoring logic:
    - Base: (toxic_word_count / total_word_count) * 100
    - High severity words = 3x weight
    - Medium severity words = 1.5x weight
    - Positive context words reduce score slightly
    - Max capped at 100
    """
    if not text or not text.strip():
        return {
            "score": 0,
            "label": "Safe",
            "triggers": [],
            "explanation": "No text provided.",
            "rewrite": "",
        }

    tokens = tokenize(text)
    total_words = max(len(tokens), 1)
    triggers = find_trigger_words(text)

    if not triggers:
        return {
            "score": 0,
            "label": "Safe",
            "triggers": [],
            "explanation": "No harmful language detected. ✅",
            "rewrite": text,
        }

    # Weighted score calculation
    weighted_count = 0
    for word in triggers:
        if word.lower() in [w.lower() for w in HIGH_SEVERITY]:
            weighted_count += 3  # High severity = 3x weight
        elif word.lower() in [w.lower() for w in MEDIUM_SEVERITY]:
            weighted_count += 1.5
        else:
            weighted_count += 1

    # Positive context reduces score
    positive_hits = sum(1 for w in POSITIVE_CONTEXT if w in tokens)
    reduction = positive_hits * 5

    raw_score = (weighted_count / total_words) * 100
    score = max(0, min(100, raw_score - reduction))
    score = round(score)

    # Classification
    if score < 25:
        label = "Safe"
    elif score < 55:
        label = "Moderate"
    else:
        label = "Toxic"

    explanation = _generate_explanation(triggers, score)
    rewrite = _generate_rewrite(text, triggers)

    return {
        "score": score,
        "label": label,
        "triggers": triggers,
        "explanation": explanation,
        "rewrite": rewrite,
    }


def _generate_explanation(triggers: list[str], score: int) -> str:
    """Human-readable explanation generate karna"""
    if not triggers:
        return "This text appears safe."

    # Categorize triggers
    has_religious = any(w in ["kafir", "kaffir", "jihadi", "terrorist", "mlechha", "haram"] for w in triggers)
    has_caste = any(w in ["chamar", "bhangi", "dhed", "chandal", "neech"] for w in triggers)
    has_sexual = any(w in ["rape", "randi", "bhosda", "chut", "pussy", "dick", "cock", "slut", "whore"] for w in triggers)
    has_violence = any(w in ["kill", "murder", "shoot", "stab", "bomb", "maar", "kaat"] for w in triggers)
    has_gaali = any(w in HINDI_TOXIC for w in triggers)

    parts = []
    if has_violence:
        parts.append("contains violent/threatening language")
    if has_sexual:
        parts.append("contains sexually explicit or objectifying language")
    if has_religious:
        parts.append("contains religion-based hate speech")
    if has_caste:
        parts.append("contains caste-based discrimination")
    if has_gaali:
        parts.append("contains abusive Hindi language (gaaliyan)")
    if not parts:
        parts.append("contains offensive/abusive language")

    trigger_str = ", ".join([f'"{t}"' for t in triggers[:3]])
    return f"This text {' and '.join(parts)}. Detected words: {trigger_str}."


def _generate_rewrite(text: str, triggers: list[str]) -> str:
    """
    Polite rewrite: triggers ko [removed] se replace karna.
    Also suggest a gentler alternative opening.
    """
    result = text
    for word in triggers:
        import re
        # Case-insensitive replacement
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        result = pattern.sub("[removed]", result)

    # Add a polite prefix suggestion if text is short enough
    if len(result.split()) < 20 and "[removed]" in result:
        result = result + "\n\n💡 Try rephrasing: Express your concern without harmful words."

    return result


def analyze_batch(texts: list[str]) -> list[dict]:
    """
    Multiple texts ko analyze karna (CSV batch processing).
    Returns list of result dicts.
    """
    results = []
    for text in texts:
        result = calculate_toxicity_score(str(text) if text else "")
        results.append(result)
    return results
