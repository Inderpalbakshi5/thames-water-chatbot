"""
Gurbani Matcher Engine

The core matching engine that takes normalized phonetic input from STT
and finds the best matching verse in the canonical Gurbani database.

Uses a combination of:
1. Trigram index for fast candidate retrieval
2. Edit distance for precise scoring
3. Sequential context bonus for expected next verses
4. Confidence thresholds for display/lock decisions
"""

from dataclasses import dataclass
from typing import Optional

from .gurbani_db import GurbaniDatabase, Verse
from .phonetic import (
    extract_trigrams,
    normalize_stt_output,
    normalized_edit_similarity,
    trigram_similarity,
)


@dataclass
class MatchResult:
    verse: Verse
    confidence: float
    trigram_score: float
    edit_score: float
    context_bonus: float


class GurbaniMatcher:
    """
    Matches STT output against pre-indexed Gurbani verses.

    Maintains awareness of current position within a Bani
    to provide sequential context bonuses and improve accuracy.
    """

    def __init__(
        self,
        db: GurbaniDatabase,
        confidence_lock: float = 0.75,
        confidence_display: float = 0.60,
        trigram_min: float = 0.3,
        max_candidates: int = 10,
        context_window: int = 5,
        sequential_bonus: float = 0.15,
    ):
        self.db = db
        self.confidence_lock = confidence_lock
        self.confidence_display = confidence_display
        self.trigram_min = trigram_min
        self.max_candidates = max_candidates
        self.context_window = context_window
        self.sequential_bonus = sequential_bonus

        # Current state
        self.current_bani: Optional[str] = None
        self.current_verse_id: Optional[int] = None
        self.verse_sequence: list[tuple[int, str]] = []  # (id, phonetic_key)
        self.current_index: int = -1  # index in verse_sequence

        # Trigram index: trigram -> set of (verse_id, phonetic_key) indices
        self._trigram_index: dict[str, set[int]] = {}

    def load_bani(self, bani: str):
        """Load a Bani and build the trigram index for matching."""
        self.current_bani = bani
        self.current_verse_id = None
        self.current_index = -1
        self.verse_sequence = self.db.get_all_phonetic_keys(bani)

        # Build trigram index
        self._trigram_index.clear()
        for idx, (verse_id, phonetic_key) in enumerate(self.verse_sequence):
            for trigram in extract_trigrams(phonetic_key):
                if trigram not in self._trigram_index:
                    self._trigram_index[trigram] = set()
                self._trigram_index[trigram].add(idx)

    def match(self, stt_text: str) -> Optional[MatchResult]:
        """
        Match STT output against the loaded Bani.

        Returns the best matching verse with confidence score,
        or None if no match exceeds the display threshold.
        """
        if not self.verse_sequence:
            return None

        # Normalize the STT output
        normalized = normalize_stt_output(stt_text)
        if not normalized or len(normalized) < 3:
            return None

        # Phase 1: Fast candidate retrieval via trigram index
        candidate_scores: dict[int, int] = {}
        query_trigrams = extract_trigrams(normalized)

        for trigram in query_trigrams:
            if trigram in self._trigram_index:
                for idx in self._trigram_index[trigram]:
                    candidate_scores[idx] = candidate_scores.get(idx, 0) + 1

        if not candidate_scores:
            return None

        # Filter to top candidates by trigram hit count
        sorted_candidates = sorted(
            candidate_scores.items(), key=lambda x: x[1], reverse=True
        )[:self.max_candidates * 2]

        # Phase 2: Detailed scoring
        results: list[MatchResult] = []

        for idx, _hit_count in sorted_candidates:
            verse_id, phonetic_key = self.verse_sequence[idx]

            # Trigram similarity
            tri_score = trigram_similarity(normalized, phonetic_key)
            if tri_score < self.trigram_min:
                continue

            # Edit distance similarity
            edit_score = normalized_edit_similarity(normalized, phonetic_key)

            # Sequential context bonus
            context_bonus = 0.0
            if self.current_index >= 0:
                distance = abs(idx - (self.current_index + 1))
                if distance == 0:
                    # This is the exact next expected verse
                    context_bonus = self.sequential_bonus
                elif distance <= self.context_window:
                    # Close to expected position
                    context_bonus = self.sequential_bonus * (1.0 - distance / self.context_window) * 0.5

            # Combined confidence
            confidence = (tri_score * 0.4 + edit_score * 0.6) + context_bonus
            confidence = min(confidence, 1.0)

            verse = self.db.get_verse(verse_id)
            if verse is None:
                continue

            results.append(MatchResult(
                verse=verse,
                confidence=confidence,
                trigram_score=tri_score,
                edit_score=edit_score,
                context_bonus=context_bonus,
            ))

        if not results:
            return None

        # Sort by confidence, return best
        results.sort(key=lambda r: r.confidence, reverse=True)
        best = results[0]

        # Only return if above display threshold
        if best.confidence < self.confidence_display:
            return None

        return best

    def lock_verse(self, verse_id: int):
        """
        Lock onto a verse — confirms it as the current position.
        Updates sequential context for future matching.
        """
        self.current_verse_id = verse_id
        for idx, (vid, _) in enumerate(self.verse_sequence):
            if vid == verse_id:
                self.current_index = idx
                break

    def get_next_verse(self) -> Optional[Verse]:
        """Get the next verse in sequence after current position."""
        if self.current_index < 0:
            return None
        next_idx = self.current_index + 1
        if next_idx >= len(self.verse_sequence):
            return None
        verse_id = self.verse_sequence[next_idx][0]
        return self.db.get_verse(verse_id)

    def get_current_verse(self) -> Optional[Verse]:
        """Get the currently locked verse."""
        if self.current_verse_id is None:
            return None
        return self.db.get_verse(self.current_verse_id)

    def jump_to_section(self, section: int):
        """Manual override: jump to a specific section (Pauri)."""
        for idx, (verse_id, _) in enumerate(self.verse_sequence):
            verse = self.db.get_verse(verse_id)
            if verse and verse.section == section and verse.line_number == 1:
                self.current_index = idx
                self.current_verse_id = verse_id
                return verse
        return None

    def reset(self):
        """Reset matcher state."""
        self.current_verse_id = None
        self.current_index = -1
