"""
State Manager

Central coordinator for the Gurbani Projection System.
Manages system state, processes STT results, drives matching,
and broadcasts updates to connected UI clients via WebSocket.
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from ..config import AppConfig, BaniType, SystemState
from .gurbani_db import GurbaniDatabase, Verse
from .matcher import GurbaniMatcher, MatchResult

logger = logging.getLogger(__name__)


@dataclass
class ProjectionState:
    """Current state broadcast to projection and admin UIs."""
    system_state: str = SystemState.IDLE.value
    current_bani: Optional[str] = None
    current_verse: Optional[dict] = None
    confidence: float = 0.0
    current_section: int = 0
    total_sections: int = 0
    total_verses: int = 0
    current_verse_index: int = 0
    audio_level: float = 0.0
    is_locked: bool = False
    last_stt_text: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def verse_to_dict(verse: Verse) -> dict:
    return {
        "id": verse.id,
        "bani": verse.bani,
        "section": verse.section,
        "line_number": verse.line_number,
        "gurmukhi": verse.gurmukhi,
        "transliteration": verse.transliteration,
        "translation_en": verse.translation_en,
        "ang": verse.ang,
    }


class StateManager:
    """
    Coordinates all system components and manages state transitions.

    Receives STT text, runs matching, updates state, and notifies
    all connected WebSocket clients.
    """

    def __init__(self, config: AppConfig, db: GurbaniDatabase):
        self.config = config
        self.db = db
        self.matcher = GurbaniMatcher(
            db=db,
            confidence_lock=config.matching.confidence_lock_threshold,
            confidence_display=config.matching.confidence_display_threshold,
            trigram_min=config.matching.trigram_min_score,
            max_candidates=config.matching.max_candidates,
            context_window=config.matching.context_window,
            sequential_bonus=config.matching.sequential_bonus,
        )

        self.state = ProjectionState()
        self._ws_clients: set = set()
        self._last_match_time: float = 0
        self._silence_start: Optional[float] = None
        self._lock: asyncio.Lock = asyncio.Lock()

    async def register_client(self, websocket):
        """Register a WebSocket client for state updates."""
        self._ws_clients.add(websocket)
        # Send current state immediately
        await self._send_to_client(websocket, self.state.to_dict())

    async def unregister_client(self, websocket):
        """Remove a WebSocket client."""
        self._ws_clients.discard(websocket)

    async def broadcast_state(self):
        """Broadcast current state to all connected clients."""
        state_dict = self.state.to_dict()
        dead_clients = set()
        for ws in self._ws_clients:
            try:
                await self._send_to_client(ws, state_dict)
            except Exception:
                dead_clients.add(ws)
        self._ws_clients -= dead_clients

    async def _send_to_client(self, websocket, data: dict):
        """Send data to a single WebSocket client."""
        try:
            await websocket.send_json({"type": "state_update", "data": data})
        except Exception as e:
            logger.warning(f"Failed to send to client: {e}")
            raise

    # --- Bani Management ---

    async def select_bani(self, bani: str):
        """Select and load a Bani for projection."""
        async with self._lock:
            self.matcher.load_bani(bani)
            verses = self.db.get_bani_verses(bani)

            sections = set()
            for v in verses:
                sections.add(v.section)

            self.state.current_bani = bani
            self.state.total_verses = len(verses)
            self.state.total_sections = len(sections)
            self.state.current_section = 0
            self.state.current_verse_index = 0
            self.state.current_verse = None
            self.state.confidence = 0.0
            self.state.is_locked = False
            self.state.system_state = SystemState.IDLE.value

            logger.info(f"Loaded Bani: {bani} ({len(verses)} verses, {len(sections)} sections)")

        await self.broadcast_state()

    # --- Listening Control ---

    async def start_listening(self):
        """Start listening for Granthi voice."""
        async with self._lock:
            if self.state.current_bani is None:
                self.state.error = "No Bani selected"
                await self.broadcast_state()
                return
            self.state.system_state = SystemState.LISTENING.value
            self.state.error = None
            self._silence_start = None

        await self.broadcast_state()

    async def stop_listening(self):
        """Stop listening."""
        async with self._lock:
            self.state.system_state = SystemState.IDLE.value
        await self.broadcast_state()

    # --- STT Processing ---

    async def process_stt_result(self, text: str, is_partial: bool = False):
        """
        Process a speech-to-text result from the audio pipeline.

        This is the main entry point for the matching pipeline.
        """
        if self.state.system_state not in (
            SystemState.LISTENING.value,
            SystemState.MATCHED.value,
        ):
            return

        async with self._lock:
            self.state.last_stt_text = text
            self._silence_start = None

            # Run matching
            result = self.matcher.match(text)

            if result is None:
                # No match found — don't change display
                if not is_partial:
                    self.state.confidence = 0.0
                await self.broadcast_state()
                return

            self.state.confidence = result.confidence

            if result.confidence >= self.config.matching.confidence_lock_threshold:
                # High confidence — lock and display
                self.matcher.lock_verse(result.verse.id)
                self.state.current_verse = verse_to_dict(result.verse)
                self.state.current_section = result.verse.section
                self.state.is_locked = True
                self.state.system_state = SystemState.MATCHED.value
                self._last_match_time = time.time()

                logger.info(
                    f"LOCKED verse {result.verse.id} "
                    f"(section {result.verse.section}, line {result.verse.line_number}) "
                    f"confidence={result.confidence:.2f}"
                )
            elif result.confidence >= self.config.matching.confidence_display_threshold:
                # Medium confidence — show but don't lock
                self.state.current_verse = verse_to_dict(result.verse)
                self.state.current_section = result.verse.section
                self.state.is_locked = False

        await self.broadcast_state()

    async def process_silence(self):
        """Called when silence is detected in audio stream."""
        if self.state.system_state != SystemState.MATCHED.value:
            return

        now = time.time()
        if self._silence_start is None:
            self._silence_start = now
            return

        silence_duration = now - self._silence_start
        if silence_duration >= self.config.audio.silence_duration_pause:
            async with self._lock:
                self.state.system_state = SystemState.PAUSED.value
                logger.info("Paused due to silence")
            await self.broadcast_state()

    async def update_audio_level(self, level: float):
        """Update audio level indicator (0.0 - 1.0)."""
        self.state.audio_level = max(0.0, min(1.0, level))
        # Don't broadcast for every audio level update — too noisy
        # Admin panel polls this separately

    # --- Manual Overrides ---

    async def jump_to_section(self, section: int):
        """Manual override: jump to a specific section."""
        async with self._lock:
            verse = self.matcher.jump_to_section(section)
            if verse:
                self.state.current_verse = verse_to_dict(verse)
                self.state.current_section = section
                self.state.is_locked = True
                self.state.confidence = 1.0
                self.state.system_state = SystemState.MANUAL_OVERRIDE.value

        await self.broadcast_state()

    async def next_verse(self):
        """Manual override: advance to next verse."""
        async with self._lock:
            verse = self.matcher.get_next_verse()
            if verse:
                self.matcher.lock_verse(verse.id)
                self.state.current_verse = verse_to_dict(verse)
                self.state.current_section = verse.section
                self.state.is_locked = True
                self.state.confidence = 1.0
                self.state.system_state = SystemState.MANUAL_OVERRIDE.value

        await self.broadcast_state()

    async def resume_listening(self):
        """Resume listening after pause or manual override."""
        async with self._lock:
            self.state.system_state = SystemState.LISTENING.value
            self._silence_start = None
        await self.broadcast_state()

    # --- Status ---

    def get_state(self) -> dict:
        """Get current state as dict."""
        return self.state.to_dict()
