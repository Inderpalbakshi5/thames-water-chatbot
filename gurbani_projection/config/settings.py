"""
Configuration settings for the Gurbani Projection System.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class SystemState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    MATCHED = "matched"
    PAUSED = "paused"
    MANUAL_OVERRIDE = "manual_override"


class BaniType(Enum):
    SUKHMANI_SAHIB = "sukhmani_sahib"
    ANAND_SAHIB = "anand_sahib"
    JAPJI_SAHIB = "japji_sahib"
    REHRAS_SAHIB = "rehras_sahib"
    FULL_SGGS = "full_sggs"


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 4096
    format_bits: int = 16
    silence_threshold_db: float = -40.0
    silence_duration_pause: float = 3.0  # seconds of silence before pause state
    buffer_max_seconds: float = 30.0


@dataclass
class MatchingConfig:
    confidence_lock_threshold: float = 0.75
    confidence_display_threshold: float = 0.60
    trigram_min_score: float = 0.3
    max_candidates: int = 10
    context_window: int = 5  # verses ahead/behind current position
    sequential_bonus: float = 0.15  # bonus for next expected verse


@dataclass
class ProjectionConfig:
    gurmukhi_font_size: str = "3.5rem"
    translation_font_size: str = "1.5rem"
    background_color: str = "#1a1a2e"
    gurmukhi_color: str = "#f5f0e1"
    translation_color: str = "#b8b5a8"
    transition_duration: str = "0.6s"
    show_translation: bool = True
    show_transliteration: bool = False


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    ws_ping_interval: int = 20
    ws_ping_timeout: int = 20


@dataclass
class AppConfig:
    audio: AudioConfig = field(default_factory=AudioConfig)
    matching: MatchingConfig = field(default_factory=MatchingConfig)
    projection: ProjectionConfig = field(default_factory=ProjectionConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    data_dir: Path = Path(__file__).parent.parent / "data"
    vosk_model_path: str = "vosk-model-small-hi-0.22"  # Hindi/Punjabi model
    offline_mode: bool = False
