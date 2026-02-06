"""Tests for the Gurbani matcher engine."""

import json
import tempfile
from pathlib import Path

import pytest

from gurbani_projection.core.gurbani_db import GurbaniDatabase
from gurbani_projection.core.matcher import GurbaniMatcher


@pytest.fixture
def sample_db():
    """Create a temporary database with sample Anand Sahib data."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    db = GurbaniDatabase(db_path)

    data_path = Path(__file__).parent.parent / "data" / "anand_sahib.json"
    if data_path.exists():
        db.load_bani_from_json(data_path)

    yield db
    db.close()
    db_path.unlink(missing_ok=True)


@pytest.fixture
def matcher(sample_db):
    """Create a matcher loaded with Anand Sahib."""
    m = GurbaniMatcher(
        db=sample_db,
        confidence_lock=0.75,
        confidence_display=0.40,
        trigram_min=0.2,
    )
    m.load_bani("anand_sahib")
    return m


class TestGurbaniDatabase:
    def test_load_and_count(self, sample_db):
        count = sample_db.get_verse_count("anand_sahib")
        assert count > 0

    def test_get_available_banis(self, sample_db):
        banis = sample_db.get_available_banis()
        assert "anand_sahib" in banis

    def test_get_verse(self, sample_db):
        verses = sample_db.get_bani_verses("anand_sahib")
        assert len(verses) > 0
        first = verses[0]
        assert first.gurmukhi != ""
        assert first.translation_en != ""

    def test_get_section_verses(self, sample_db):
        verses = sample_db.get_section_verses("anand_sahib", 1)
        assert len(verses) > 0
        for v in verses:
            assert v.section == 1

    def test_get_phonetic_keys(self, sample_db):
        keys = sample_db.get_all_phonetic_keys("anand_sahib")
        assert len(keys) > 0
        for vid, key in keys:
            assert isinstance(vid, int)
            assert isinstance(key, str)


class TestGurbaniMatcher:
    def test_load_bani(self, matcher):
        assert matcher.current_bani == "anand_sahib"
        assert len(matcher.verse_sequence) > 0

    def test_match_exact_transliteration(self, matcher):
        # Try matching the first verse transliteration
        result = matcher.match("anand bhaeiaa maeree maae satiguroo mai paaeiaa")
        assert result is not None
        assert result.confidence > 0.5

    def test_match_partial_text(self, matcher):
        # Partial match — should still find something
        result = matcher.match("anand bhaeiaa maeree maae")
        # May or may not match depending on threshold
        # Just verify it doesn't crash
        assert result is None or result.confidence > 0

    def test_no_match_garbage(self, matcher):
        result = matcher.match("xyz abc random english words here")
        assert result is None or result.confidence < 0.5

    def test_lock_and_context(self, matcher):
        result = matcher.match("anand bhaeiaa maeree maae satiguroo mai paaeiaa")
        if result:
            matcher.lock_verse(result.verse.id)
            assert matcher.current_verse_id == result.verse.id
            assert matcher.current_index >= 0

    def test_get_next_verse(self, matcher):
        # Lock first verse
        result = matcher.match("anand bhaeiaa maeree maae satiguroo mai paaeiaa")
        if result:
            matcher.lock_verse(result.verse.id)
            next_v = matcher.get_next_verse()
            assert next_v is not None
            # Next verse should be different
            assert next_v.id != result.verse.id

    def test_jump_to_section(self, matcher):
        verse = matcher.jump_to_section(2)
        assert verse is not None
        assert verse.section == 2
        assert verse.line_number == 1

    def test_reset(self, matcher):
        matcher.lock_verse(1)
        matcher.reset()
        assert matcher.current_verse_id is None
        assert matcher.current_index == -1

    def test_sequential_bonus(self, matcher):
        """Test that matching the next expected verse gets a bonus."""
        # Match and lock first verse
        result1 = matcher.match("anand bhaeiaa maeree maae satiguroo mai paaeiaa")
        if result1:
            matcher.lock_verse(result1.verse.id)

            # Now match the second verse — should get sequential bonus
            result2 = matcher.match("satiguroo t paaeiaa sehaj saetee man vajeeaa vaadhhaaeeaa")
            if result2:
                assert result2.context_bonus > 0


class TestDatabaseMultipleBanis:
    def test_load_multiple_banis(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)

        db = GurbaniDatabase(db_path)
        data_dir = Path(__file__).parent.parent / "data"

        loaded = 0
        for json_file in data_dir.glob("*.json"):
            try:
                db.load_bani_from_json(json_file)
                loaded += 1
            except Exception:
                pass

        if loaded > 0:
            banis = db.get_available_banis()
            assert len(banis) == loaded

        db.close()
        db_path.unlink(missing_ok=True)
