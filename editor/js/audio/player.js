/**
 * Audio Module - Main Player
 * 
 * Orchestrates playback, connects all sub-modules.
 */

const AudioPlayer = (function() {
    'use strict';

    function log(msg) {
        console.log('[Audio] ' + msg);
    }

    function error(msg) {
        console.error('[Audio] ERROR: ' + msg);
    }

    /**
     * Stop all playback
     */
    function stop() {
        log('Stopping playback...');

        const state = window.AudioState;

        // Stop progress tracking
        if (state.getProgressInterval()) {
            clearInterval(state.getProgressInterval());
            state.setProgressInterval(null);
        }

        // Cancel Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.stop();
            Tone.Transport.cancel();
        }

        // Stop Tone.js playback
        const toneSynth = state.getToneSynth();
        if (toneSynth && window.Tone) {
            toneSynth.releaseAll();
        }

        // Stop native oscillators
        state.getActiveSources().forEach(src => {
            try {
                if (src.osc1 && src.osc1.state === 'started') src.osc1.stop();
                if (src.osc2 && src.osc2.state === 'started') src.osc2.stop();
            } catch (e) {}
        });
        state.setActiveSources([]);

        state.setPlaying(false);
        state.setPaused(false);
        state.setPausedAt(0);
        state.setCurrentTrackIndex(-1);
        log('Playback stopped');
    }

    /**
     * Pause playback
     */
    function pause() {
        if (!state.isPlayingState()) return;

        log('Pausing playback...');

        const state = window.AudioState;

        // Stop progress tracking
        if (state.getProgressInterval()) {
            clearInterval(state.getProgressInterval());
            state.setProgressInterval(null);
        }

        // Pause Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.pause();
        }

        // Stop oscillators
        const toneSynth = state.getToneSynth();
        if (toneSynth && window.Tone) {
            toneSynth.releaseAll();
        }

        state.getActiveSources().forEach(src => {
            try {
                if (src.osc1 && src.osc1.state === 'started') src.osc1.stop();
                if (src.osc2 && src.osc2.state === 'started') src.osc2.stop();
            } catch (e) {}
        });
        state.setActiveSources([]);

        // Calculate position
        if (toneSynth && window.Tone) {
            state.setPausedAt((Tone.now() - state.getPlaybackStartTime()) * 1000);
        }

        state.setPaused(true);
        state.setPlaying(false);
        log('Playback paused at ' + Math.round(state.getPausedAt()) + 'ms');
    }

    /**
     * Resume from pause
     */
    function resume() {
        const state = window.AudioState;
        
        if (!state.isPausedState() || state.getCurrentTrackIndex() < 0) return;

        log('Resuming from ' + Math.round(state.getPausedAt()) + 'ms...');

        // Resume Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.start();
        }

        const playlist = state.getPlaylist();
        const track = playlist[state.getCurrentTrackIndex()];
        playMIDI(track.url, track.name, state.getPausedAt());
    }

    /**
     * Play MIDI file
     */
    async function playMIDI(midiUrl, name, startPosition) {
        log('========================================');
        log('Playing: ' + name + (startPosition > 0 ? ' (from ' + startPosition + 'ms)' : ''));
        log('========================================');

        const state = window.AudioState;

        stop();

        if (window.Tone && Tone.Transport) {
            Tone.Transport.stop();
            Tone.Transport.cancel();
        }

        try {
            let engine = state.getPreferredEngine();

            if (engine === 'tone' && !window.Tone) {
                log('Tone.js not available, falling back to native');
                engine = 'native';
            }

            if (engine === 'tone') {
                log('Using Tone.js engine (preferred: ' + engine + ')');
                await window.AudioEngine.initTone();
            } else {
                log('Using native Web Audio engine (preferred: ' + engine + ')');
                window.AudioEngine.initNative();
            }

            log('Active engine: ' + state.getCurrentEngine());

            log('Fetching: ' + midiUrl);
            const response = await fetch(midiUrl);
            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ': ' + response.statusText);
            }
            const arrayBuffer = await response.arrayBuffer();
            const midiData = new Uint8Array(arrayBuffer);
            log('Loaded ' + midiData.length + ' bytes');

            log('Validating MIDI...');
            const validation = window.AudioPlayback.validateMIDI(midiData);
            if (!validation.valid) {
                error('Invalid MIDI: ' + validation.errors.join(', '));
                return false;
            }
            if (validation.warnings.length > 0) {
                log('Warnings: ' + validation.warnings.join(', '));
            }
            log('MIDI valid - Format: ' + validation.info.format + ', Division: ' + validation.info.division);

            let result = false;

            if (engine === 'tone' && state.getToneSynth()) {
                log('Playing via Tone.js PolySynth...');
                result = await window.AudioPlayback.playViaTone(midiData, startPosition);
            } else {
                log('Playing via native Web Audio...');
                result = window.AudioPlayback.playViaNative(midiData, name, startPosition);
            }

            if (result) {
                state.setPlaying(true);
                state.setPaused(false);
                state.setPlaybackStartTime(Tone.now() - (startPosition / 1000));

                // Calculate duration
                const events = window.AudioPlayback.parseMIDI(midiData);
                if (events && events.length > 0) {
                    const maxTime = Math.max(...events.map(e => e.time));
                    state.setTotalDuration(maxTime);
                } else {
                    state.setTotalDuration(60000);
                }

                log('Track duration: ' + Math.round(state.getTotalDuration() / 1000) + 's');
                log('Playback started successfully (' + state.getCurrentEngine() + ')');

                startProgressTracking();
                window.AudioUI.updatePlayerUI();
            } else {
                error('Playback failed');
            }

            return result;
        } catch (e) {
            error('playMIDI exception: ' + e.message);
            error('Stack: ' + e.stack);
            return false;
        }
    }

    /**
     * Start progress tracking
     */
    function startProgressTracking() {
        const state = window.AudioState;

        if (state.getProgressInterval()) {
            clearInterval(state.getProgressInterval());
        }

        const interval = setInterval(() => {
            if (state.isPlayingState() && state.getCurrentTrackIndex() >= 0) {
                const position = window.AudioPlaylist.getCurrentPosition();
                const total = state.getTotalDuration();
                const progress = total > 0 ? (position / total) * 100 : 0;
                window.AudioUpdateProgress(position, total, progress);
            }
        }, 100);

        state.setProgressInterval(interval);
    }

    return {
        playMIDI: playMIDI,
        stop: stop,
        pause: pause,
        resume: resume,
        startProgressTracking: startProgressTracking
    };
})();

// Export to window
window.AudioPlayer = AudioPlayer;
