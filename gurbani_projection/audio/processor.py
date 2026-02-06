"""
Audio Processor

Handles audio capture from microphone, preprocessing (noise reduction,
level detection), and streaming to the speech-to-text engine.

Supports two modes:
1. Server-side: PyAudio/sounddevice capture on the host machine
2. Browser-side: Web Audio API streams audio via WebSocket

The browser-side mode is preferred for simplicity (no server mic access needed).
"""

import asyncio
import logging
import math
import struct
from typing import Optional

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Processes audio chunks from either server mic or browser WebSocket.

    Responsibilities:
    - Compute audio level (RMS) for UI feedback
    - Detect silence for pause detection
    - Buffer audio for STT engine
    - Basic noise gate
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        silence_threshold_db: float = -40.0,
        chunk_size: int = 4096,
    ):
        self.sample_rate = sample_rate
        self.silence_threshold_db = silence_threshold_db
        self.chunk_size = chunk_size
        self._audio_buffer: bytearray = bytearray()
        self._is_speech: bool = False
        self._silence_frames: int = 0
        self._speech_frames: int = 0
        self._rms_level: float = 0.0

    def process_chunk(self, audio_data: bytes) -> dict:
        """
        Process a chunk of 16-bit PCM audio data.

        Returns:
            dict with keys:
            - rms_level: float (0.0 - 1.0) normalized audio level
            - is_speech: bool - whether speech is detected
            - is_silence: bool - whether this is a silence period
            - audio_data: bytes - the processed audio data (for STT)
        """
        rms = self._compute_rms(audio_data)
        rms_db = 20 * math.log10(max(rms, 1e-10))
        self._rms_level = min(1.0, max(0.0, (rms_db + 60) / 60))

        is_above_threshold = rms_db > self.silence_threshold_db

        if is_above_threshold:
            self._speech_frames += 1
            self._silence_frames = 0
            self._is_speech = True
        else:
            self._silence_frames += 1
            # Require sustained silence before marking as silent
            silence_duration = self._silence_frames * self.chunk_size / self.sample_rate
            if silence_duration > 1.0:
                self._is_speech = False

        return {
            "rms_level": self._rms_level,
            "is_speech": self._is_speech,
            "is_silence": not self._is_speech,
            "audio_data": audio_data if self._is_speech else b"",
        }

    def _compute_rms(self, audio_data: bytes) -> float:
        """Compute RMS of 16-bit PCM audio."""
        if len(audio_data) < 2:
            return 0.0

        n_samples = len(audio_data) // 2
        if n_samples == 0:
            return 0.0

        try:
            samples = struct.unpack(f"<{n_samples}h", audio_data[:n_samples * 2])
            sum_sq = sum(s * s for s in samples)
            return math.sqrt(sum_sq / n_samples) / 32768.0
        except struct.error:
            return 0.0

    @property
    def current_level(self) -> float:
        return self._rms_level

    def reset(self):
        self._audio_buffer.clear()
        self._is_speech = False
        self._silence_frames = 0
        self._speech_frames = 0
        self._rms_level = 0.0


class STTEngine:
    """
    Speech-to-text engine abstraction.

    Supports Vosk (offline) and Whisper (online) backends.
    The actual engine is selected at initialization based on availability.
    """

    def __init__(self, engine_type: str = "vosk", model_path: Optional[str] = None):
        self.engine_type = engine_type
        self.model_path = model_path
        self._model = None
        self._recognizer = None
        self._initialized = False

    async def initialize(self):
        """Initialize the STT engine. Call once at startup."""
        if self.engine_type == "vosk":
            await self._init_vosk()
        elif self.engine_type == "whisper":
            await self._init_whisper()
        elif self.engine_type == "browser":
            # Browser-based Web Speech API — no server-side init needed
            self._initialized = True
            logger.info("Using browser-based speech recognition")
        else:
            raise ValueError(f"Unknown STT engine: {self.engine_type}")

    async def _init_vosk(self):
        """Initialize Vosk STT engine."""
        try:
            from vosk import KaldiRecognizer, Model

            logger.info(f"Loading Vosk model from {self.model_path}")
            self._model = Model(self.model_path)
            self._recognizer = KaldiRecognizer(self._model, 16000)
            self._recognizer.SetWords(True)
            self._initialized = True
            logger.info("Vosk model loaded successfully")
        except ImportError:
            logger.warning("Vosk not installed. Install with: pip install vosk")
            raise
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            raise

    async def _init_whisper(self):
        """Initialize Whisper STT engine."""
        try:
            import whisper

            logger.info("Loading Whisper model (medium)")
            self._model = whisper.load_model("medium")
            self._initialized = True
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.warning("Whisper not installed. Install with: pip install openai-whisper")
            raise

    async def transcribe(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio data to text.

        For browser-based STT, this is a no-op (browser sends text directly).
        """
        if not self._initialized:
            return None

        if self.engine_type == "vosk":
            return await self._transcribe_vosk(audio_data)
        elif self.engine_type == "whisper":
            return await self._transcribe_whisper(audio_data)
        elif self.engine_type == "browser":
            # Browser sends transcribed text directly
            return None

        return None

    async def _transcribe_vosk(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using Vosk."""
        import json as json_mod

        loop = asyncio.get_event_loop()

        def _recognize():
            if self._recognizer.AcceptWaveform(audio_data):
                result = json_mod.loads(self._recognizer.Result())
                return result.get("text", "")
            else:
                partial = json_mod.loads(self._recognizer.PartialResult())
                return partial.get("partial", "")

        text = await loop.run_in_executor(None, _recognize)
        return text if text else None

    async def _transcribe_whisper(self, audio_data: bytes) -> Optional[str]:
        """Transcribe using Whisper."""
        import io

        import numpy as np

        loop = asyncio.get_event_loop()

        def _recognize():
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            result = self._model.transcribe(
                audio_np,
                language="pa",  # Punjabi
                task="transcribe",
            )
            return result.get("text", "")

        text = await loop.run_in_executor(None, _recognize)
        return text if text else None

    def reset(self):
        """Reset recognizer state."""
        if self.engine_type == "vosk" and self._recognizer:
            self._recognizer.Reset()
