"""
Gurbani Database Engine

Manages the canonical SGGS scripture database with pre-indexed verses,
phonetic keys, and translations. Uses SQLite for persistent storage
and in-memory indexes for fast matching.
"""

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Verse:
    id: int
    bani: str
    section: int  # pauri/ashtpadi number
    line_number: int  # line within section
    gurmukhi: str
    transliteration: str  # romanized phonetic
    translation_en: str
    phonetic_key: str  # normalized phonetic representation
    ang: int  # page number in SGGS


class GurbaniDatabase:
    """
    Manages the Gurbani scripture database.

    Stores canonical text in SQLite with phonetic indexes
    for fast fuzzy matching.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self._verses_cache: dict[int, Verse] = {}

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS verses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bani TEXT NOT NULL,
                section INTEGER NOT NULL,
                line_number INTEGER NOT NULL,
                gurmukhi TEXT NOT NULL,
                transliteration TEXT NOT NULL,
                translation_en TEXT NOT NULL,
                phonetic_key TEXT NOT NULL,
                ang INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_verses_bani
                ON verses(bani);
            CREATE INDEX IF NOT EXISTS idx_verses_bani_section
                ON verses(bani, section);
            CREATE INDEX IF NOT EXISTS idx_verses_phonetic
                ON verses(phonetic_key);
        """)
        self.conn.commit()

    def load_bani_from_json(self, json_path: Path):
        """Load a Bani from a JSON file into the database."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        bani_name = data["bani"]

        # Clear existing data for this Bani
        self.conn.execute("DELETE FROM verses WHERE bani = ?", (bani_name,))

        verses = []
        for verse_data in data["verses"]:
            verses.append((
                bani_name,
                verse_data["section"],
                verse_data["line_number"],
                verse_data["gurmukhi"],
                verse_data["transliteration"],
                verse_data["translation_en"],
                verse_data["phonetic_key"],
                verse_data.get("ang", 0),
            ))

        self.conn.executemany(
            """INSERT INTO verses
               (bani, section, line_number, gurmukhi, transliteration,
                translation_en, phonetic_key, ang)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            verses,
        )
        self.conn.commit()
        self._verses_cache.clear()

    def get_verse(self, verse_id: int) -> Optional[Verse]:
        """Get a single verse by ID."""
        if verse_id in self._verses_cache:
            return self._verses_cache[verse_id]

        row = self.conn.execute(
            "SELECT * FROM verses WHERE id = ?", (verse_id,)
        ).fetchone()

        if row is None:
            return None

        verse = self._row_to_verse(row)
        self._verses_cache[verse_id] = verse
        return verse

    def get_bani_verses(self, bani: str) -> list[Verse]:
        """Get all verses for a Bani in order."""
        rows = self.conn.execute(
            "SELECT * FROM verses WHERE bani = ? ORDER BY section, line_number",
            (bani,),
        ).fetchall()
        return [self._row_to_verse(r) for r in rows]

    def get_section_verses(self, bani: str, section: int) -> list[Verse]:
        """Get all verses for a specific section (Pauri/Ashtpadi)."""
        rows = self.conn.execute(
            """SELECT * FROM verses
               WHERE bani = ? AND section = ?
               ORDER BY line_number""",
            (bani, section),
        ).fetchall()
        return [self._row_to_verse(r) for r in rows]

    def get_all_phonetic_keys(self, bani: str) -> list[tuple[int, str]]:
        """Get (verse_id, phonetic_key) pairs for building index."""
        rows = self.conn.execute(
            "SELECT id, phonetic_key FROM verses WHERE bani = ? ORDER BY section, line_number",
            (bani,),
        ).fetchall()
        return [(r["id"], r["phonetic_key"]) for r in rows]

    def get_verse_count(self, bani: str) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM verses WHERE bani = ?", (bani,)
        ).fetchone()
        return row["cnt"]

    def get_available_banis(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT bani FROM verses ORDER BY bani"
        ).fetchall()
        return [r["bani"] for r in rows]

    def search_gurmukhi(self, query: str, bani: Optional[str] = None, limit: int = 10) -> list[Verse]:
        """Simple LIKE search on Gurmukhi text."""
        if bani:
            rows = self.conn.execute(
                "SELECT * FROM verses WHERE bani = ? AND gurmukhi LIKE ? LIMIT ?",
                (bani, f"%{query}%", limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM verses WHERE gurmukhi LIKE ? LIMIT ?",
                (f"%{query}%", limit),
            ).fetchall()
        return [self._row_to_verse(r) for r in rows]

    def _row_to_verse(self, row: sqlite3.Row) -> Verse:
        return Verse(
            id=row["id"],
            bani=row["bani"],
            section=row["section"],
            line_number=row["line_number"],
            gurmukhi=row["gurmukhi"],
            transliteration=row["transliteration"],
            translation_en=row["translation_en"],
            phonetic_key=row["phonetic_key"],
            ang=row["ang"],
        )

    def close(self):
        self.conn.close()
