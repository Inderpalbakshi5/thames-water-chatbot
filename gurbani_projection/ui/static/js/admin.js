/**
 * Admin Control Panel
 *
 * Manages Bani selection, listening controls, manual overrides,
 * and displays real-time state from the server.
 * Optionally provides browser-based speech recognition as fallback.
 */

(function () {
    'use strict';

    const RECONNECT_DELAY_MS = 2000;

    // DOM elements
    const connectionDot = document.getElementById('connection-dot');
    const connectionText = document.getElementById('connection-text');
    const baniSelect = document.getElementById('bani-select');
    const btnLoadBani = document.getElementById('btn-load-bani');
    const btnStart = document.getElementById('btn-start');
    const btnStop = document.getElementById('btn-stop');
    const btnNext = document.getElementById('btn-next');
    const btnResume = document.getElementById('btn-resume');
    const btnJump = document.getElementById('btn-jump');
    const sectionInput = document.getElementById('section-input');
    const stateBadge = document.getElementById('state-badge');
    const confidenceValue = document.getElementById('confidence-value');
    const confidenceFill = document.getElementById('confidence-fill');
    const audioBars = document.getElementById('audio-bars').children;
    const sttOutput = document.getElementById('stt-output');
    const currentSection = document.getElementById('current-section');
    const totalSections = document.getElementById('total-sections');
    const totalVerses = document.getElementById('total-verses');
    const previewGurmukhi = document.getElementById('preview-gurmukhi');
    const previewTranslation = document.getElementById('preview-translation');
    const previewMeta = document.getElementById('preview-meta');
    const btnBrowserStt = document.getElementById('btn-browser-stt');
    const browserSttStatus = document.getElementById('browser-stt-status');

    let ws = null;
    let browserSttActive = false;
    let recognition = null;

    /**
     * Connect to WebSocket server.
     */
    function connect() {
        const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${location.host}/ws/admin`;

        ws = new WebSocket(wsUrl);

        ws.onopen = function () {
            connectionDot.classList.add('connected');
            connectionText.textContent = 'Connected';
            enableControls(true);
        };

        ws.onclose = function () {
            connectionDot.classList.remove('connected');
            connectionText.textContent = 'Disconnected';
            enableControls(false);
            setTimeout(connect, RECONNECT_DELAY_MS);
        };

        ws.onerror = function () {
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
     * Send a command to the server.
     */
    function sendCommand(action, params) {
        if (!ws || ws.readyState !== WebSocket.OPEN) return;
        ws.send(JSON.stringify({ action: action, ...params }));
    }

    /**
     * Handle state update from server.
     */
    function handleStateUpdate(state) {
        // State badge
        stateBadge.className = 'state-badge ' + state.system_state;
        stateBadge.textContent = formatState(state.system_state);

        // Confidence
        const confPct = Math.round(state.confidence * 100);
        confidenceValue.textContent = confPct + '%';
        confidenceFill.style.width = confPct + '%';
        confidenceFill.className = 'confidence-fill';
        if (confPct >= 75) confidenceFill.classList.add('high');
        else if (confPct >= 50) confidenceFill.classList.add('medium');

        // Audio level
        updateAudioBars(state.audio_level);

        // STT output
        if (state.last_stt_text) {
            sttOutput.textContent = state.last_stt_text;
        }

        // Section info
        currentSection.textContent = state.current_section || '-';
        totalSections.textContent = state.total_sections || '-';
        totalVerses.textContent = state.total_verses || '-';

        // Current verse preview
        if (state.current_verse) {
            previewGurmukhi.textContent = state.current_verse.gurmukhi;
            previewTranslation.textContent = state.current_verse.translation_en;
            previewMeta.textContent =
                'Section ' + state.current_verse.section +
                ', Line ' + state.current_verse.line_number +
                (state.current_verse.ang ? ' | Ang ' + state.current_verse.ang : '') +
                (state.is_locked ? ' | LOCKED' : '');
        } else {
            previewGurmukhi.textContent = 'No verse selected';
            previewTranslation.textContent = '';
            previewMeta.textContent = '';
        }

        // Button states
        updateButtonStates(state.system_state, state.current_bani);
    }

    function formatState(state) {
        const map = {
            idle: 'Idle',
            listening: 'Listening',
            matched: 'Matched',
            paused: 'Paused',
            manual_override: 'Manual',
        };
        return map[state] || state;
    }

    function updateAudioBars(level) {
        const barCount = audioBars.length;
        const activeCount = Math.round(level * barCount);
        for (let i = 0; i < barCount; i++) {
            const height = 5 + (i + 1) * 2.5;
            audioBars[i].style.height = height + 'px';
            if (i < activeCount) {
                audioBars[i].classList.add('active');
            } else {
                audioBars[i].classList.remove('active');
            }
        }
    }

    function updateButtonStates(state, currentBani) {
        btnLoadBani.disabled = !baniSelect.value;
        btnStart.disabled = !currentBani || state === 'listening' || state === 'matched';
        btnStop.disabled = state === 'idle';
        btnNext.disabled = !currentBani;
        btnResume.disabled = state !== 'paused' && state !== 'manual_override';
        btnJump.disabled = !currentBani;
    }

    function enableControls(enabled) {
        if (!enabled) {
            btnLoadBani.disabled = true;
            btnStart.disabled = true;
            btnStop.disabled = true;
            btnNext.disabled = true;
            btnResume.disabled = true;
            btnJump.disabled = true;
        }
    }

    // --- Event Handlers ---

    baniSelect.addEventListener('change', function () {
        btnLoadBani.disabled = !this.value;
    });

    btnLoadBani.addEventListener('click', function () {
        if (baniSelect.value) {
            sendCommand('select_bani', { bani: baniSelect.value });
        }
    });

    btnStart.addEventListener('click', function () {
        sendCommand('start_listening');
    });

    btnStop.addEventListener('click', function () {
        sendCommand('stop_listening');
    });

    btnNext.addEventListener('click', function () {
        sendCommand('next_verse');
    });

    btnResume.addEventListener('click', function () {
        sendCommand('resume_listening');
    });

    btnJump.addEventListener('click', function () {
        const section = parseInt(sectionInput.value, 10);
        if (section > 0) {
            sendCommand('jump_to_section', { section: section });
        }
    });

    // --- Browser Speech Recognition (Fallback) ---

    btnBrowserStt.addEventListener('click', function () {
        if (browserSttActive) {
            stopBrowserStt();
        } else {
            startBrowserStt();
        }
    });

    function startBrowserStt() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            browserSttStatus.textContent = 'Speech recognition not supported in this browser.';
            return;
        }

        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'pa-IN'; // Punjabi

        recognition.onstart = function () {
            browserSttActive = true;
            btnBrowserStt.textContent = 'Disable Browser STT';
            btnBrowserStt.classList.remove('btn-secondary');
            btnBrowserStt.classList.add('btn-danger');
            browserSttStatus.textContent = 'Listening via browser...';
        };

        recognition.onresult = function (event) {
            let transcript = '';
            let isFinal = false;

            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    isFinal = true;
                }
            }

            if (transcript) {
                // Send transcription to server for matching
                sendCommand('stt_result', {
                    text: transcript,
                    is_partial: !isFinal,
                });
            }
        };

        recognition.onerror = function (event) {
            browserSttStatus.textContent = 'Error: ' + event.error;
            if (event.error === 'not-allowed') {
                stopBrowserStt();
            }
        };

        recognition.onend = function () {
            // Restart if still active (browser stops after silence)
            if (browserSttActive) {
                recognition.start();
            }
        };

        recognition.start();
    }

    function stopBrowserStt() {
        browserSttActive = false;
        if (recognition) {
            recognition.stop();
            recognition = null;
        }
        btnBrowserStt.textContent = 'Enable Browser STT';
        btnBrowserStt.classList.remove('btn-danger');
        btnBrowserStt.classList.add('btn-secondary');
        browserSttStatus.textContent = 'Stopped.';
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function (e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;

        switch (e.key) {
            case 'ArrowRight':
                btnNext.click();
                break;
            case 's':
            case 'S':
                if (btnStart.disabled) {
                    btnStop.click();
                } else {
                    btnStart.click();
                }
                break;
        }
    });

    // Start connection
    connect();
})();
