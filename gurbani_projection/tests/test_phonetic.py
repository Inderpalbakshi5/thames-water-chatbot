"""Tests for the phonetic normalizer module."""

import pytest
from gurbani_projection.core.phonetic import (
    compute_phonetic_key,
    extract_trigrams,
    gurmukhi_to_phonetic,
    levenshtein_distance,
    normalize_stt_output,
    normalized_edit_similarity,
    trigram_similarity,
)


class TestGurmukhiToPhonetic:
    def test_basic_gurmukhi(self):
        # ਸ=s, ਤ=t, ਿ=i → "sti"
        result = gurmukhi_to_phonetic("ਸਤਿ")
        assert result == "sti"

    def test_empty_string(self):
        assert gurmukhi_to_phonetic("") == ""

    def test_spaces_preserved(self):
        result = gurmukhi_to_phonetic("ਸਤਿ ਨਾਮੁ")
        assert " " in result

    def test_punctuation_removed(self):
        result = gurmukhi_to_phonetic("ਸਤਿ;")
        assert ";" not in result


class TestNormalizeSttOutput:
    def test_lowercase(self):
        # Double consonants are collapsed by normalization
        assert normalize_stt_output("HELLO") == "helo"

    def test_remove_filler(self):
        result = normalize_stt_output("um sat naam ji")
        assert "um" not in result
        assert "ji" not in result

    def test_remove_punctuation(self):
        result = normalize_stt_output("sat, naam.")
        assert "," not in result
        assert "." not in result

    def test_empty_string(self):
        assert normalize_stt_output("") == ""

    def test_normalize_whitespace(self):
        result = normalize_stt_output("sat   naam")
        assert "  " not in result


class TestTrigrams:
    def test_extract_trigrams(self):
        trigrams = extract_trigrams("abcde")
        assert "abc" in trigrams
        assert "bcd" in trigrams
        assert "cde" in trigrams

    def test_short_string(self):
        trigrams = extract_trigrams("ab")
        assert trigrams == {"ab"}

    def test_empty_string(self):
        assert extract_trigrams("") == set()

    def test_spaces_removed(self):
        trigrams = extract_trigrams("a b c d e")
        assert "abc" in trigrams

    def test_similarity_identical(self):
        assert trigram_similarity("hello", "hello") == 1.0

    def test_similarity_different(self):
        score = trigram_similarity("hello", "world")
        assert score < 0.5

    def test_similarity_similar(self):
        score = trigram_similarity("anand", "anandh")
        assert score > 0.5

    def test_similarity_empty(self):
        assert trigram_similarity("", "") == 0.0


class TestLevenshtein:
    def test_identical(self):
        assert levenshtein_distance("hello", "hello") == 0

    def test_one_edit(self):
        assert levenshtein_distance("hello", "hallo") == 1

    def test_empty(self):
        assert levenshtein_distance("", "hello") == 5
        assert levenshtein_distance("hello", "") == 5

    def test_completely_different(self):
        assert levenshtein_distance("abc", "xyz") == 3


class TestNormalizedEditSimilarity:
    def test_identical(self):
        assert normalized_edit_similarity("hello", "hello") == 1.0

    def test_empty_both(self):
        assert normalized_edit_similarity("", "") == 1.0

    def test_completely_different(self):
        score = normalized_edit_similarity("abc", "xyz")
        assert score == 0.0

    def test_partial_match(self):
        score = normalized_edit_similarity("anand", "anandh")
        assert 0.5 < score < 1.0
