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
        if (window.AudioState.getProgressInterval()) {
            clearInterval(window.AudioState.getProgressInterval());
            window.AudioState.setProgressInterval(null);
        }

        // Cancel Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.stop();
            Tone.Transport.cancel();
        }

        // Stop Tone.js playback
        const toneSynth = window.AudioState.getToneSynth();
        if (toneSynth && window.Tone) {
            toneSynth.releaseAll();
        }

        // Stop native oscillators
        window.AudioState.getActiveSources().forEach(src => {
            try {
                if (src.osc1 && src.osc1.state === 'started') src.osc1.stop();
                if (src.osc2 && src.osc2.state === 'started') src.osc2.stop();
            } catch (e) {}
        });
        window.AudioState.setActiveSources([]);

        window.AudioState.setPlaying(false);
        window.AudioState.setPaused(false);
        window.AudioState.setPausedAt(0);
        window.AudioState.setCurrentTrackIndex(-1);
        log('Playback stopped');
    }

    /**
     * Pause playback
     */
    function pause() {
        if (!window.AudioState.isPlayingState()) return;

        log('Pausing playback...');

        const state = window.AudioState;

        // Stop progress tracking
        if (window.AudioState.getProgressInterval()) {
            clearInterval(window.AudioState.getProgressInterval());
            window.AudioState.setProgressInterval(null);
        }

        // Pause Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.pause();
        }

        // Stop oscillators
        const toneSynth = window.AudioState.getToneSynth();
        if (toneSynth && window.Tone) {
            toneSynth.releaseAll();
        }

        window.AudioState.getActiveSources().forEach(src => {
            try {
                if (src.osc1 && src.osc1.state === 'started') src.osc1.stop();
                if (src.osc2 && src.osc2.state === 'started') src.osc2.stop();
            } catch (e) {}
        });
        window.AudioState.setActiveSources([]);

        // Calculate position
        if (toneSynth && window.Tone) {
            window.AudioState.setPausedAt((Tone.now() - window.AudioState.getPlaybackStartTime()) * 1000);
        }

        window.AudioState.setPaused(true);
        window.AudioState.setPlaying(false);
        log('Playback paused at ' + Math.round(window.AudioState.getPausedAt()) + 'ms');
    }

    /**
     * Resume from pause
     */
    function resume() {
        const state = window.AudioState;
        
        if (!window.AudioState.isPausedState() || window.AudioState.getCurrentTrackIndex() < 0) return;

        log('Resuming from ' + Math.round(window.AudioState.getPausedAt()) + 'ms...');

        // Resume Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.start();
        }

        const playlist = window.AudioState.getPlaylist();
        const track = playlist[window.AudioState.getCurrentTrackIndex()];
        playMIDI(track.url, track.name, window.AudioState.getPausedAt());
    }

    /**
     * Play MIDI file
     */
    async function playMIDI(midiUrl, name, startPosition) {
        log('========================================');
        log('Playing: ' + name + (startPosition > 0 ? ' (from ' + startPosition + 'ms)' : ''));
        log('========================================');

        const state = window.AudioState;

        // Save track index before stop() clears it
        const savedTrackIndex = state.getCurrentTrackIndex();

        stop();

        if (window.Tone && Tone.Transport) {
            Tone.Transport.stop();
            Tone.Transport.cancel();
        }

        try {
            let engine = window.AudioState.getPreferredEngine();

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

            log('Active engine: ' + window.AudioState.getCurrentEngine());

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

            if (engine === 'tone' && window.AudioState.getToneSynth()) {
                log('Playing via Tone.js PolySynth...');
                result = await window.AudioPlayback.playViaTone(midiData, startPosition);
            } else {
                log('Playing via native Web Audio...');
                result = window.AudioPlayback.playViaNative(midiData, name, startPosition);
            }

            if (result) {
                // Restore track index
                state.setCurrentTrackIndex(savedTrackIndex);

                window.AudioState.setPlaying(true);
                window.AudioState.setPaused(false);
                window.AudioState.setPlaybackStartTime(Tone.now() - (startPosition / 1000));

                // Calculate duration
                const events = window.AudioPlayback.parseMIDI(midiData);
                if (events && events.length > 0) {
                    const maxTime = Math.max(...events.map(e => e.time));
                    window.AudioState.setTotalDuration(maxTime);
                } else {
                    window.AudioState.setTotalDuration(60000);
                }

                log('Track duration: ' + Math.round(window.AudioState.getTotalDuration() / 1000) + 's');
                log('Playback started successfully (' + window.AudioState.getCurrentEngine() + ')');

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

        if (window.AudioState.getProgressInterval()) {
            clearInterval(window.AudioState.getProgressInterval());
        }

        const interval = setInterval(() => {
            if (window.AudioState.isPlayingState() && window.AudioState.getCurrentTrackIndex() >= 0) {
                const position = window.AudioPlaylist.getCurrentPosition();
                const total = window.AudioState.getTotalDuration();
                const progress = total > 0 ? (position / total) * 100 : 0;
                window.AudioUpdateProgress(position, total, progress);
            }
        }, 100);

        window.AudioState.setProgressInterval(interval);
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

