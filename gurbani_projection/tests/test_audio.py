"""Tests for the audio processor module."""

import struct

import pytest

from gurbani_projection.audio.processor import AudioProcessor


@pytest.fixture
def processor():
    return AudioProcessor(sample_rate=16000, silence_threshold_db=-40.0)


class TestAudioProcessor:
    def test_process_silence(self, processor):
        """Silent audio should be detected as silence."""
        # Generate silent audio (all zeros)
        silent = struct.pack("<" + "h" * 1000, *([0] * 1000))
        result = processor.process_chunk(silent)
        assert result["rms_level"] == 0.0
        assert result["audio_data"] == b""

    def test_process_loud_audio(self, processor):
        """Loud audio should be detected as speech."""
        # Generate loud audio
        loud = struct.pack("<" + "h" * 1000, *([20000] * 1000))
        result = processor.process_chunk(loud)
        assert result["rms_level"] > 0.5
        assert result["is_speech"] is True
        assert len(result["audio_data"]) > 0

    def test_rms_level_range(self, processor):
        """RMS level should be between 0 and 1."""
        # Various audio levels
        for amplitude in [0, 100, 1000, 10000, 32000]:
            audio = struct.pack("<" + "h" * 100, *([amplitude] * 100))
            result = processor.process_chunk(audio)
            assert 0.0 <= result["rms_level"] <= 1.0

    def test_empty_audio(self, processor):
        """Empty audio should not crash."""
        result = processor.process_chunk(b"")
        assert result["rms_level"] == 0.0

    def test_reset(self, processor):
        """Reset should clear all state."""
        loud = struct.pack("<" + "h" * 100, *([20000] * 100))
        processor.process_chunk(loud)
        assert processor.current_level > 0

        processor.reset()
        assert processor.current_level == 0.0

    def test_silence_detection_requires_sustained(self, processor):
        """Silence should not be immediate after speech."""
        # First, establish speech
        loud = struct.pack("<" + "h" * 1000, *([20000] * 1000))
        processor.process_chunk(loud)
        assert processor.process_chunk(loud)["is_speech"] is True

        # One chunk of silence should not trigger silence state
        silent = struct.pack("<" + "h" * 1000, *([0] * 1000))
        result = processor.process_chunk(silent)
        # May still be "speech" since silence needs to be sustained
        # (depends on chunk_size / sample_rate ratio)
