"""
Phonetic Normalizer for Gurbani

Converts romanized Punjabi/Hindi STT output into normalized phonetic keys
that can be compared against the canonical Gurbani phonetic index.

Handles:
- Multiple romanization schemes
- Aspirated consonants
- Nasalization
- Vowel length variations
- Common STT transcription errors
"""

import re
import unicodedata


# Gurmukhi to phonetic mapping for building index from canonical text
GURMUKHI_TO_PHONETIC = {
    # Vowels
    "\u0a05": "a", "\u0a06": "aa", "\u0a07": "i", "\u0a08": "ee",
    "\u0a09": "u", "\u0a0a": "oo", "\u0a0f": "e", "\u0a10": "ai",
    "\u0a13": "o", "\u0a14": "au",
    # Vowel signs
    "\u0a3e": "aa", "\u0a3f": "i", "\u0a40": "ee", "\u0a41": "u",
    "\u0a42": "oo", "\u0a47": "e", "\u0a48": "ai", "\u0a4b": "o",
    "\u0a4c": "au",
    # Consonants
    "\u0a38": "s", "\u0a39": "h", "\u0a15": "k", "\u0a16": "kh",
    "\u0a17": "g", "\u0a18": "gh", "\u0a19": "ng",
    "\u0a1a": "ch", "\u0a1b": "chh", "\u0a1c": "j", "\u0a1d": "jh",
    "\u0a1e": "ny",
    "\u0a1f": "t", "\u0a20": "th", "\u0a21": "d", "\u0a22": "dh",
    "\u0a23": "n",
    "\u0a24": "t", "\u0a25": "th", "\u0a26": "d", "\u0a27": "dh",
    "\u0a28": "n",
    "\u0a2a": "p", "\u0a2b": "ph", "\u0a2c": "b", "\u0a2d": "bh",
    "\u0a2e": "m",
    "\u0a2f": "y", "\u0a30": "r", "\u0a32": "l", "\u0a35": "v",
    "\u0a5c": "r",  # rra
    # Special
    "\u0a70": "n",  # tippi (nasalization)
    "\u0a02": "n",  # bindi
    "\u0a71": "",   # addak (gemination marker)
    "\u0a4d": "",   # virama (halant)
    "\u0a3c": "",   # nukta
    "\u0a73": "u",  # ura
    "\u0a72": "i",  # iri
}

# Romanization normalization: common variants → canonical form
ROMANIZATION_NORMALIZATIONS = [
    # Long vowels
    (r"aa+", "aa"),
    (r"ee+", "ee"),
    (r"oo+", "oo"),
    (r"ii+", "ee"),
    (r"uu+", "oo"),
    # Aspirated consonants
    (r"kh", "kh"),
    (r"gh", "gh"),
    (r"chh?", "ch"),
    (r"jh", "jh"),
    (r"th", "th"),
    (r"dh", "dh"),
    (r"ph", "ph"),
    (r"bh", "bh"),
    # Common STT variants
    (r"sh", "sh"),
    (r"shh", "sh"),
    (r"w", "v"),
    (r"x", "ksh"),
    (r"q", "k"),
    (r"z", "j"),
    (r"f", "ph"),
    # Remove double consonants (except aspirated pairs)
    (r"([^aeiou])\1", r"\1"),
]

# Words that are typically filler/non-Gurbani in speech
FILLER_WORDS = {
    "um", "uh", "hmm", "ah", "oh", "ji", "sahib",
    "waheguru", "bole", "so", "nihal", "sat", "sri",
    "akal", "the", "is", "and", "of", "in", "to",
}


def gurmukhi_to_phonetic(gurmukhi_text: str) -> str:
    """
    Convert Gurmukhi script to normalized phonetic key.

    Used for building the phonetic index from canonical SGGS text.
    """
    result = []
    for char in gurmukhi_text:
        if char in GURMUKHI_TO_PHONETIC:
            result.append(GURMUKHI_TO_PHONETIC[char])
        elif char == " ":
            result.append(" ")
        elif char == ";" or char == "," or char == ".":
            continue
        elif unicodedata.category(char).startswith("N"):
            # Keep numbers (for verse references)
            result.append(char)

    phonetic = "".join(result)
    # Normalize spaces
    phonetic = re.sub(r"\s+", " ", phonetic).strip()
    return phonetic.lower()


def normalize_stt_output(text: str) -> str:
    """
    Normalize STT romanized output into a canonical phonetic form
    suitable for matching against the Gurbani phonetic index.
    """
    text = text.lower().strip()

    # Remove punctuation except spaces
    text = re.sub(r"[^\w\s]", "", text)

    # Remove filler words
    words = text.split()
    words = [w for w in words if w not in FILLER_WORDS]
    text = " ".join(words)

    # Apply romanization normalizations
    for pattern, replacement in ROMANIZATION_NORMALIZATIONS:
        text = re.sub(pattern, replacement, text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def compute_phonetic_key(gurmukhi_text: str) -> str:
    """
    Compute a phonetic key for a Gurmukhi verse.
    This is stored in the database for matching.
    """
    return gurmukhi_to_phonetic(gurmukhi_text)


def extract_trigrams(text: str) -> set[str]:
    """
    Extract character trigrams from text for fuzzy matching.
    Trigrams enable fast approximate string matching.
    """
    text = text.replace(" ", "")
    if len(text) < 3:
        return {text} if text else set()
    return {text[i:i+3] for i in range(len(text) - 2)}


def trigram_similarity(text1: str, text2: str) -> float:
    """
    Compute trigram similarity between two strings.
    Returns 0.0-1.0 where 1.0 is identical.
    """
    trigrams1 = extract_trigrams(text1)
    trigrams2 = extract_trigrams(text2)

    if not trigrams1 or not trigrams2:
        return 0.0

    intersection = trigrams1 & trigrams2
    union = trigrams1 | trigrams2

    return len(intersection) / len(union)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    prev_row = list(range(len(s2) + 1))

    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def normalized_edit_similarity(s1: str, s2: str) -> float:
    """
    Compute normalized similarity based on edit distance.
    Returns 0.0-1.0 where 1.0 is identical.
    """
    if not s1 and not s2:
        return 1.0
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    distance = levenshtein_distance(s1, s2)
    return 1.0 - (distance / max_len)
