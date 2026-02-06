/**
 * Gurbani Projection Display
 *
 * Connects to the server via WebSocket and renders verses
 * with smooth transitions. Designed for projector output.
 */

(function () {
    'use strict';

    const RECONNECT_DELAY_MS = 2000;
    const TRANSITION_MS = 600;

    // DOM elements
    const idleDisplay = document.getElementById('idle-display');
    const verseDisplay = document.getElementById('verse-display');
    const gurmukhiVerse = document.getElementById('gurmukhi-verse');
    const translationVerse = document.getElementById('translation-verse');
    const transliterationVerse = document.getElementById('transliteration-verse');
    const sectionIndicator = document.getElementById('section-indicator');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const confidenceFill = document.getElementById('confidence-fill');

    let ws = null;
    let currentVerseId = null;
    let isTransitioning = false;

    /**
     * Connect to WebSocket server.
     */
    function connect() {
        const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${location.host}/ws/projection`;

        ws = new WebSocket(wsUrl);

        ws.onopen = function () {
            console.log('Projection connected');
            updateStatus('idle', 'Connected');
        };

        ws.onclose = function () {
            console.log('Projection disconnected, reconnecting...');
            updateStatus('', 'Reconnecting...');
            setTimeout(connect, RECONNECT_DELAY_MS);
        };

        ws.onerror = function (err) {
            console.error('WebSocket error:', err);
            ws.close();
        };

        ws.onmessage = function (event) {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'state_update') {
                    handleStateUpdate(msg.data);
                }
            } catch (e) {
                console.error('Failed to parse message:', e);
            }
        };
    }

    /**
     * Handle a state update from the server.
     */
    function handleStateUpdate(state) {
        updateStatus(state.system_state, state.system_state);
        updateConfidence(state.confidence);

        if (state.system_state === 'idle' && !state.current_verse) {
            showIdle();
            return;
        }

        if (state.current_verse) {
            showVerse(state.current_verse, state);
        }
    }

    /**
     * Show the idle display.
     */
    function showIdle() {
        idleDisplay.style.display = 'flex';
        verseDisplay.style.display = 'none';
        sectionIndicator.textContent = '';
        currentVerseId = null;
    }

    /**
     * Display a verse with smooth transition.
     */
    function showVerse(verse, state) {
        if (verse.id === currentVerseId) {
            // Same verse, just update confidence
            return;
        }

        if (isTransitioning) {
            return;
        }

        idleDisplay.style.display = 'none';
        verseDisplay.style.display = 'block';

        // Transition out
        isTransitioning = true;
        gurmukhiVerse.classList.add('transitioning');
        translationVerse.classList.add('transitioning');

        setTimeout(function () {
            // Update content
            gurmukhiVerse.textContent = verse.gurmukhi;
            translationVerse.textContent = verse.translation_en;

            if (verse.transliteration) {
                transliterationVerse.textContent = verse.transliteration;
            }

            // Update section indicator
            if (state.current_section > 0) {
                sectionIndicator.textContent =
                    'Section ' + state.current_section +
                    (state.total_sections ? ' / ' + state.total_sections : '');
            }

            // Transition in
            gurmukhiVerse.classList.remove('transitioning');
            translationVerse.classList.remove('transitioning');

            currentVerseId = verse.id;
            isTransitioning = false;
        }, TRANSITION_MS);
    }

    /**
     * Update the status indicator.
     */
    function updateStatus(state, text) {
        statusDot.className = 'status-dot';
        if (state === 'listening') {
            statusDot.classList.add('listening');
        } else if (state === 'matched' || state === 'manual_override') {
            statusDot.classList.add('matched');
        } else if (state === 'paused') {
            statusDot.classList.add('paused');
        }
        statusText.textContent = text || '';
    }

    /**
     * Update confidence bar.
     */
    function updateConfidence(confidence) {
        confidenceFill.style.width = (confidence * 100) + '%';
    }

    // Handle keyboard shortcuts for manual control
    document.addEventListener('keydown', function (e) {
        if (!ws || ws.readyState !== WebSocket.OPEN) return;

        switch (e.key) {
            case 'ArrowRight':
            case ' ':
                // Next verse
                ws.send(JSON.stringify({ action: 'next_verse' }));
                e.preventDefault();
                break;
            case 'ArrowLeft':
                // Previous (no-op for now, could implement)
                break;
            case 'f':
            case 'F':
                // Toggle fullscreen
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                } else {
                    document.exitFullscreen();
                }
                break;
            case 't':
            case 'T':
                // Toggle translation
                translationVerse.classList.toggle('hidden');
                break;
        }
    });

    // Start connection
    connect();
})();
