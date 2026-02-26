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

    // Prevent multiple simultaneous play calls
    let isPlayingCallInProgress = false;

    /**
     * Stop all playback
     */
    function stop() {
        log('>>> stop() called (isPlayingCallInProgress=' + isPlayingCallInProgress + ')');
        log('stop() - isPlaying=' + window.AudioState.isPlayingState());
        log('stop() - currentTrack=' + window.AudioState.getCurrentTrackIndex());
        log('stop() - activeSources=' + window.AudioState.getActiveSources().length);

        // Stop progress tracking
        const interval = window.AudioState.getProgressInterval();
        if (interval) {
            log('stop() - clearing interval ' + interval);
            clearInterval(interval);
            window.AudioState.setProgressInterval(null);
        } else {
            log('stop() - no interval to clear');
        }

        // Cancel Tone.js Transport
        if (window.Tone && Tone.Transport) {
            log('stop() - cancelling Tone.Transport');
            Tone.Transport.stop();
            Tone.Transport.cancel();
        } else {
            log('stop() - Tone.Transport not available');
        }

        // Stop Tone.js playback
        const toneSynth = window.AudioState.getToneSynth();
        if (toneSynth && window.Tone) {
            log('stop() - calling toneSynth.releaseAll()');
            toneSynth.releaseAll();
        } else {
            log('stop() - toneSynth not available');
        }

        // Stop native oscillators
        const sources = window.AudioState.getActiveSources();
        const now = window.AudioState.getAudioContext() ? window.AudioState.getAudioContext().currentTime : 0;
        log('stop() - stopping ' + sources.length + ' native oscillators (currentTime: ' + now.toFixed(3) + 's)');
        sources.forEach((src, i) => {
            try {
                // Check if this oscillator is still pending or playing
                const isPending = src.startTime && src.startTime > now;
                const isPlaying = src.startTime && src.startTime <= now && src.stopTime && src.stopTime > now;
                
                if (isPending || isPlaying) {
                    log('stop() - osc1[' + i + '] startTime=' + src.startTime.toFixed(3) + 's stopTime=' + src.stopTime.toFixed(3) + 's (stopping)');
                    if (src.osc1) {
                        src.osc1.stop();
                        src.osc1.disconnect();
                    }
                    if (src.osc2) {
                        src.osc2.stop();
                        src.osc2.disconnect();
                    }
                } else {
                    log('stop() - osc1[' + i + '] already finished (startTime=' + (src.startTime ? src.startTime.toFixed(3) : 'null') + 's)');
                }
            } catch (e) {
                log('stop() - error: ' + e.message);
            }
        });
        window.AudioState.setActiveSources([]);

        window.AudioState.setPlaying(false);
        window.AudioState.setPaused(false);
        window.AudioState.setPausedAt(0);
        window.AudioState.setCurrentTrackIndex(-1);
        log('<<< stop() complete');
    }

    /**
     * Pause playback
     */
    function pause() {
        if (!window.AudioState.isPlayingState()) {
            log('pause() - not playing, ignoring');
            return;
        }

        log('>>> pause() called');

        // Stop progress tracking
        const interval = window.AudioState.getProgressInterval();
        if (interval) {
            clearInterval(interval);
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
        log('pause() - paused at ' + Math.round(window.AudioState.getPausedAt()) + 'ms');
        log('<<< pause() complete');
    }

    /**
     * Resume from pause
     */
    function resume() {
        log('>>> resume() called');
        
        if (!window.AudioState.isPausedState() || window.AudioState.getCurrentTrackIndex() < 0) {
            log('resume() - not paused or no track');
            return;
        }

        log('resume() - resuming from ' + Math.round(window.AudioState.getPausedAt()) + 'ms');

        // Resume Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.start();
        }

        const playlist = window.AudioState.getPlaylist();
        const track = playlist[window.AudioState.getCurrentTrackIndex()];
        playMIDI(track.url, track.name, window.AudioState.getPausedAt());
        log('<<< resume() complete');
    }

    /**
     * Play MIDI file
     */
    async function playMIDI(midiUrl, name, startPosition) {
        // Prevent overlapping play calls
        if (isPlayingCallInProgress) {
            log('playMIDI() - ALREADY IN PROGRESS, ignoring duplicate call');
            return false;
        }
        isPlayingCallInProgress = true;
        log('playMIDI() - call started, setting flag');

        log('========================================');
        log('>>> playMIDI() - ' + name + ' (from ' + startPosition + 'ms)');
        log('========================================');

        const state = window.AudioState;

        try {
            // Initialize engine FIRST before stop() so toneSynth exists
            let engine = state.getPreferredEngine();
            log('playMIDI() - preferred engine: ' + engine);

            if (engine === 'tone' && !window.Tone) {
                log('playMIDI() - Tone.js not available, falling back to native');
                engine = 'native';
            }

            if (engine === 'tone') {
                log('playMIDI() - initializing Tone.js...');
                await window.AudioEngine.initTone();
            } else {
                log('playMIDI() - initializing native...');
                window.AudioEngine.initNative();
            }

            log('playMIDI() - active engine: ' + state.getCurrentEngine());
            log('playMIDI() - toneSynth available: ' + !!state.getToneSynth());

            // NOW stop previous playback (toneSynth exists now)
            log('playMIDI() - calling stop() to stop previous playback');
            stop();

            if (window.Tone && Tone.Transport) {
                Tone.Transport.stop();
                Tone.Transport.cancel();
                log('playMIDI() - Tone.Transport cancelled');
            }

            log('playMIDI() - fetching: ' + midiUrl);
            const response = await fetch(midiUrl);
            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ': ' + response.statusText);
            }
            const arrayBuffer = await response.arrayBuffer();
            const midiData = new Uint8Array(arrayBuffer);
            log('playMIDI() - loaded ' + midiData.length + ' bytes');

            log('playMIDI() - validating MIDI...');
            const validation = window.AudioPlayback.validateMIDI(midiData);
            if (!validation.valid) {
                error('playMIDI() - invalid MIDI: ' + validation.errors.join(', '));
                return false;
            }
            if (validation.warnings.length > 0) {
                log('playMIDI() - warnings: ' + validation.warnings.join(', '));
            }
            log('playMIDI() - MIDI valid - Format: ' + validation.info.format + ', Division: ' + validation.info.division);

            let result = false;

            if (engine === 'tone' && state.getToneSynth()) {
                log('playMIDI() - playing via Tone.js...');
                result = await window.AudioPlayback.playViaTone(midiData, startPosition);
            } else {
                log('playMIDI() - playing via native...');
                // Parse MIDI first to get msPerTick
                const parseResult = window.AudioPlayback.parseMIDI(midiData);
                result = window.AudioPlayback.playViaNative(midiData, name, startPosition, parseResult.msPerTick);
            }

            if (result) {
                // Restore track index
                state.setCurrentTrackIndex(state.getCurrentTrackIndex() >= 0 ? state.getCurrentTrackIndex() : 0);
                log('playMIDI() - track index: ' + state.getCurrentTrackIndex());

                state.setPlaying(true);
                state.setPaused(false);
                state.setPlaybackStartTime(Tone.now() - (startPosition / 1000));

                // Calculate duration
                const parseResult = window.AudioPlayback.parseMIDI(midiData);
                if (parseResult.events && parseResult.events.length > 0) {
                    const maxTime = Math.max(...parseResult.events.map(e => e.time));
                    state.setTotalDuration(maxTime);
                } else {
                    state.setTotalDuration(60000);
                }

                log('playMIDI() - duration: ' + Math.round(state.getTotalDuration() / 1000) + 's');
                log('playMIDI() - playback started (' + state.getCurrentEngine() + ')');

                startProgressTracking();
                window.AudioUI.updatePlayerUI();
            } else {
                error('playMIDI() - playback failed');
            }

            log('<<< playMIDI() complete - result: ' + result);
            return result;
        } catch (e) {
            error('playMIDI() - exception: ' + e.message);
            error('playMIDI() - stack: ' + e.stack);
            log('<<< playMIDI() error');
            return false;
        } finally {
            isPlayingCallInProgress = false;
            log('playMIDI() - cleared flag');
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

        log('startProgressTracking() - starting interval');
        const interval = setInterval(() => {
            if (state.isPlayingState() && state.getCurrentTrackIndex() >= 0) {
                const position = window.AudioPlaylist.getCurrentPosition();
                const total = state.getTotalDuration();
                const progress = total > 0 ? (position / total) * 100 : 0;
                window.AudioUpdateProgress(position, total, progress);
            }
        }, 100);

        state.setProgressInterval(interval);
        log('startProgressTracking() - interval ' + interval + ' started');
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
