# Gurbani Projection System - Architecture

## System Overview

An automated system that captures live Granthi voice, matches it against
canonical Gurbani scripture, and projects aligned Gurmukhi text with English
translation on a projector screen in real time.

```
+------------------+     +-------------------+     +--------------------+
|  Audio Capture   | --> | Speech Processing | --> | Phonetic Normalizer|
|  (Mic / WebAudio)|     | (Vosk/Whisper)    |     | (Gurmukhi Phonemes)|
+------------------+     +-------------------+     +--------------------+
                                                            |
                                                            v
+------------------+     +-------------------+     +--------------------+
|  Projection UI   | <-- |  State Manager    | <-- | Gurbani Matcher    |
|  (Web → HDMI)    |     | (Session + Verse) |     | (Fuzzy Index Search)|
+------------------+     +-------------------+     +--------------------+
        ^                        ^                          |
        |                        |                          v
+------------------+     +-------------------+     +--------------------+
|  Admin Panel     | --> |  WebSocket Hub    |     | SGGS Database      |
|  (Tablet/Laptop) |     | (Real-time Sync)  |     | (Pre-indexed Banis)|
+------------------+     +-------------------+     +--------------------+
```

## Component Details

### 1. Audio Capture Layer
- **Browser**: Web Audio API with MediaStream
- **Server**: PyAudio / sounddevice for direct mic access
- Streams audio chunks (16kHz, mono, 16-bit PCM) to speech processor
- Configurable buffer size for latency tuning

### 2. Speech Processing
- **Primary**: Vosk (offline, Punjabi model) for low-latency local inference
- **Fallback**: OpenAI Whisper (medium model) for higher accuracy when online
- Outputs romanized/phonetic Punjabi text segments
- Streaming partial results for faster matching

### 3. Phonetic Normalizer
- Converts STT output to standardized Gurmukhi phonemes
- Handles: nasalization, aspirated consonants, vowel length
- Maps common romanization variants to canonical forms
- Strips filler words and non-Gurbani speech

### 4. Gurbani Matcher (Core Engine)
- Pre-indexed SGGS database with phonetic keys
- Trigram index for fast fuzzy substring matching
- Confidence scoring (0-1) per verse candidate
- Lock threshold: 0.75 (configurable)
- Sequential context awareness (knows current Bani position)

### 5. State Manager
- Tracks: current Bani, current Pauri/verse, confidence, playback state
- States: IDLE, LISTENING, MATCHED, PAUSED, MANUAL_OVERRIDE
- Emits state changes via WebSocket to all connected clients
- Handles pause detection (silence > 3 seconds)

### 6. Projection UI
- Full-screen web page served to projector display
- Top: Gurmukhi text (large, Anmollipi/GurbaniAkhar font)
- Bottom: English translation (smaller, clean sans-serif)
- Dark background (#1a1a2e), high contrast text
- Smooth CSS transitions between verses (no jarring jumps)
- WebSocket connection for real-time verse updates

### 7. Admin Panel
- Tablet/laptop web interface
- Select Bani, Start/Stop listening
- Manual override: jump to specific Pauri
- Confidence meter visualization
- Audio level indicator
- Offline mode toggle

## Technology Stack

| Layer              | Technology                  | Rationale                          |
|--------------------|-----------------------------|------------------------------------|
| Backend            | Python 3.11 + FastAPI       | Async, fast, WebSocket support     |
| Speech-to-Text     | Vosk (primary)              | Offline, Punjabi support, fast     |
| Fuzzy Matching     | Custom trigram + Levenshtein| Gurbani-specific, no ML dependency |
| Real-time Comms    | WebSockets                  | Low latency, bidirectional         |
| Projection UI      | Vanilla HTML/CSS/JS         | Zero framework overhead, reliable  |
| Admin UI           | HTML/CSS/JS                 | Simple, works on any device        |
| Database           | SQLite + JSON               | No server dependency, portable     |
| Audio Processing   | sounddevice / Web Audio API | Cross-platform, low latency        |

## Data Sources

- **SGGS Text**: SikhiToTheMax open database (JSON/SQLite)
- **Translations**: Khalsa Consensus / Sant Singh Khalsa translations
- **Phonetic Index**: Pre-computed from canonical Gurmukhi text

## Latency Budget

| Stage              | Target    |
|--------------------|-----------|
| Audio capture      | ~100ms    |
| STT processing     | ~800ms    |
| Phonetic normalize | ~50ms     |
| Fuzzy matching     | ~200ms    |
| State + WebSocket  | ~50ms     |
| UI render          | ~100ms    |
| **Total**          | **~1.3s** |

## Security & Privacy

- No audio stored permanently (in-memory buffer only)
- No cloud dependency in offline mode
- Local-first architecture
- No telemetry or analytics

## Risk Analysis

| Risk                        | Impact | Mitigation                                    |
|-----------------------------|--------|-----------------------------------------------|
| Low STT accuracy            | High   | Fuzzy matching + sequential context            |
| Granthi skips verses        | Medium | Position-independent search with fallback      |
| Network failure             | Medium | Full offline mode with pre-loaded Banis        |
| Mic interference            | Medium | Audio preprocessing + directional mic support  |
| Wrong verse displayed       | High   | Confidence threshold + hold-on-uncertainty     |
| Projector disconnect        | Low    | Admin panel shows current state independently  |
