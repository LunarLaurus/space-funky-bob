/**
 * Audio Module - High-Quality MIDI Playback
 * 
 * Uses Tone.js for professional synthesis with fallback to native Web Audio.
 * 
 * Quality Tiers (auto-selected):
 * 1. Tone.js PolySynth (BEST) - High-quality synthesis with effects
 * 2. Native Web Audio (FALLBACK) - Basic dual-oscillator synthesis
 * 
 * Note: JZZ.js removed - requires MIDI hardware which browsers don't provide.
 */

const Audio = (function() {
    'use strict';

    // Audio engines
    let toneSynth = null;      // Tone.js synth (best quality)
    let audioContext = null;   // Native Web Audio (fallback)
    
    // State
    let currentEngine = null;  // 'tone' or 'native'
    let isPlaying = false;
    let isPaused = false;
    let testMode = false;
    let testResults = [];
    let preferredEngine = 'tone'; // User preference: 'tone' or 'native'
    
    // Playlist & Playback
    let playlist = [];         // Array of MIDI files
    let currentTrackIndex = -1;
    let activeSources = [];    // Currently playing Tone.js sources
    let playbackStartTime = 0;
    let pausedAt = 0;          // Position where paused (ms)
    let totalDuration = 0;     // Total track duration (ms)
    let playbackSpeed = 1.0;   // Playback speed multiplier
    
    // Progress tracking
    let progressInterval = null;

    // Audio chain components (native fallback)
    let masterGain = null;
    let compressorNode = null;
    let reverbNode = null;

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
        
        // Stop progress tracking
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
        
        // Cancel and stop Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.stop();
            Tone.Transport.cancel();
        }
        
        // Stop Tone.js playback
        if (toneSynth && window.Tone) {
            toneSynth.releaseAll();
        }
        
        // Stop native oscillators immediately
        activeSources.forEach(src => {
            try {
                if (src.osc1) {
                    if (src.osc1.state === 'started') src.osc1.stop();
                    src.osc1.disconnect();
                }
                if (src.osc2) {
                    if (src.osc2.state === 'started') src.osc2.stop();
                    src.osc2.disconnect();
                }
            } catch (e) {}
        });
        activeSources = [];

        isPlaying = false;
        isPaused = false;
        pausedAt = 0;
        currentTrackIndex = -1;
        log('Playback stopped');
    }

    /**
     * Pause current playback
     */
    function pause() {
        if (!isPlaying) return;
        
        log('Pausing playback...');
        
        // Stop progress tracking
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
        
        // Pause Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.pause();
        }
        
        // Stop Tone.js playback
        if (toneSynth && window.Tone) {
            toneSynth.releaseAll();
        }
        
        // Stop native oscillators
        activeSources.forEach(src => {
            try {
                if (src.osc1) {
                    if (src.osc1.state === 'started') src.osc1.stop();
                    src.osc1.disconnect();
                }
                if (src.osc2) {
                    if (src.osc2.state === 'started') src.osc2.stop();
                    src.osc2.disconnect();
                }
            } catch (e) {}
        });
        activeSources = [];
        
        // Calculate current position
        if (toneSynth && window.Tone) {
            pausedAt = (Tone.now() - playbackStartTime) * 1000;
        }
        
        isPaused = true;
        isPlaying = false;
        log('Playback paused at ' + Math.round(pausedAt) + 'ms');
    }

    /**
     * Resume from pause
     */
    function resume() {
        if (!isPaused || currentTrackIndex < 0) return;
        
        log('Resuming from ' + Math.round(pausedAt) + 'ms...');
        
        // Resume Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.start();
        }
        
        const track = playlist[currentTrackIndex];
        playMIDI(track.url, track.name, pausedAt);
    }

    /**
     * Play specific track from playlist
     */
    function playTrack(index) {
        if (index < 0 || index >= playlist.length) return;
        
        currentTrackIndex = index;
        const track = playlist[index];
        playMIDI(track.url, track.name, 0);
    }

    /**
     * Play next track in playlist
     */
    function playNext() {
        if (playlist.length === 0) return;
        const nextIndex = (currentTrackIndex + 1) % playlist.length;
        playTrack(nextIndex);
    }

    /**
     * Play previous track in playlist
     */
    function playPrevious() {
        if (playlist.length === 0) return;
        const prevIndex = currentTrackIndex <= 0 ? playlist.length - 1 : currentTrackIndex - 1;
        playTrack(prevIndex);
    }

    /**
     * Set playlist
     */
    function setPlaylist(files) {
        playlist = files.map((f, i) => ({
            index: i,
            name: f.filename || f.name || 'Unknown',
            url: f.path || f.url || '#',
            duration: 0 // Could be calculated from MIDI
        }));
        currentTrackIndex = -1;
        log('Playlist set with ' + playlist.length + ' tracks');
    }

    /**
     * Get current track info
     */
    function getCurrentTrack() {
        if (currentTrackIndex < 0 || currentTrackIndex >= playlist.length) {
            return null;
        }
        return {
            ...playlist[currentTrackIndex],
            isPlaying,
            isPaused,
            position: isPaused ? pausedAt : (Tone.now() - playbackStartTime) * 1000
        };
    }

    /**
     * Get playlist
     */
    function getPlaylist() {
        return playlist.map((track, i) => ({
            ...track,
            isCurrent: i === currentTrackIndex
        }));
    }

    /**
     * Set playback speed
     * @param {number} speed - Playback speed (0.5 = 50%, 1.0 = 100%, 2.0 = 200%)
     */
    function setPlaybackSpeed(speed) {
        if (speed < 0.25 || speed > 4.0) {
            log('Invalid speed: ' + speed + ' (must be 0.25-4.0)');
            return false;
        }
        playbackSpeed = speed;
        if (window.Tone && Tone.Transport) {
            Tone.Transport.playbackRate = speed;
        }
        log('Playback speed set to ' + (speed * 100) + '%');
        return true;
    }

    /**
     * Get current playback speed
     */
    function getPlaybackSpeed() {
        return playbackSpeed;
    }

    /**
     * Get current playback position
     */
    function getCurrentPosition() {
        if (isPaused) return pausedAt;
        if (!isPlaying) return 0;
        return (Tone.now() - playbackStartTime) * 1000;
    }

    /**
     * Get total duration of current track
     */
    function getTotalDuration() {
        return totalDuration;
    }

    /**
     * Start progress tracking
     */
    function startProgressTracking() {
        // Stop any existing interval
        if (progressInterval) {
            clearInterval(progressInterval);
        }
        
        // Update progress every 100ms
        progressInterval = setInterval(() => {
            if (isPlaying && currentTrackIndex >= 0) {
                const position = getCurrentPosition();
                const progress = totalDuration > 0 ? (position / totalDuration) * 100 : 0;
                updateProgressUI(position, totalDuration, progress);
            }
        }, 100);
    }

    /**
     * Update progress UI (callback, implemented in renderAudioList)
     */
    let updateProgressUI = function(position, total, progress) {
        // Default implementation - can be overridden
    };

    /**
     * Set preferred engine (user toggle)
     * @param {string} engine - 'tone' or 'native'
     */
    function setPreferredEngine(engine) {
        if (engine === 'tone' || engine === 'native') {
            preferredEngine = engine;
            log('Preferred engine set to: ' + engine);
        }
    }

    /**
     * Get current engine status
     */
    function getEngineStatus() {
        return {
            current: currentEngine,
            preferred: preferredEngine,
            toneAvailable: !!window.Tone,
            nativeAvailable: true
        };
    }

    /**
     * Validate MIDI data structure
     */
    function validateMIDI(data) {
        const result = { valid: false, errors: [], warnings: [] };

        if (!data || data.length < 14) {
            result.errors.push('File too small for MIDI format');
            return result;
        }

        // Check header "MThd"
        if (data[0] !== 0x4D || data[1] !== 0x54 || data[2] !== 0x68 || data[3] !== 0x64) {
            result.errors.push('Invalid MIDI header (expected MThd)');
            return result;
        }

        const headerLen = (data[4] << 24) | (data[5] << 16) | (data[6] << 8) | data[7];
        if (headerLen !== 6) {
            result.warnings.push('Unusual header length: ' + headerLen);
        }

        const format = (data[8] << 8) | data[9];
        if (format > 2) {
            result.warnings.push('Unusual MIDI format: ' + format);
        }

        const division = (data[12] << 8) | data[13];
        if (division < 1 || division > 960) {
            result.warnings.push('Unusual division: ' + division);
        }

        result.valid = true;
        result.info = { format, division, headerLen };
        return result;
    }

    /**
     * Initialize Tone.js synth (BEST QUALITY)
     * Uses polyphonic synthesis with effects
     */
    async function initTone() {
        if (toneSynth) return true;

        try {
            log('Initializing Tone.js engine...');

            if (!window.Tone) {
                throw new Error('Tone.js library not loaded');
            }

            await Tone.start();

            // Create high-quality polyphonic synth
            toneSynth = new Tone.PolySynth(Tone.Synth, {
                oscillator: { type: "fatsawtooth" },
                envelope: { attack: 0.01, decay: 0.1, sustain: 0.3, release: 0.5 },
                portamento: 0.05
            }).toDestination();

            // Add effects chain
            const reverb = new Tone.Reverb({ decay: 2, wet: 0.3 }).toDestination();
            const compressor = new Tone.Compressor({ threshold: -24, ratio: 12 }).toDestination();

            toneSynth.connect(compressor);
            compressor.connect(reverb);

            log('Tone.js engine initialized');
            currentEngine = 'tone';
            return true;
        } catch (e) {
            error('Tone.js initialization failed: ' + e.message);
            toneSynth = null;
            return false;
        }
    }

    /**
     * Initialize native Web Audio (FALLBACK)
     * Basic synthesis when Tone.js unavailable
     */
    function initNative() {
        if (audioContext) return true;

        try {
            log('Initializing native Web Audio engine...');

            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            masterGain = audioContext.createGain();
            masterGain.gain.value = 0.4;

            compressorNode = audioContext.createDynamicsCompressor();
            compressorNode.threshold.value = -24;
            compressorNode.knee.value = 30;
            compressorNode.ratio.value = 12;
            compressorNode.attack.value = 0.003;
            compressorNode.release.value = 0.25;

            reverbNode = audioContext.createConvolver();
            createReverbImpulse();

            reverbNode.connect(compressorNode);
            compressorNode.connect(masterGain);
            masterGain.connect(audioContext.destination);

            const dryGain = audioContext.createGain();
            dryGain.gain.value = 0.7;
            dryGain.connect(compressorNode);

            currentEngine = 'native';
            log('Native Web Audio engine initialized');
            return true;
        } catch (e) {
            error('Native initialization failed: ' + e.message);
            return false;
        }
    }

    function createReverbImpulse() {
        if (!audioContext) return;
        const duration = 1.5, decay = 2.0, rate = audioContext.sampleRate;
        const length = rate * duration;
        const impulse = audioContext.createBuffer(2, length, rate);
        for (let ch = 0; ch < 2; ch++) {
            const data = impulse.getChannelData(ch);
            for (let i = 0; i < length; i++) {
                data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, decay);
            }
        }
        reverbNode.buffer = impulse;
    }
    
    async function loadJZZ() {
        if (window.JZZ) return true;
        
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = '/js/JZZ.js';
            script.onload = () => {
                log('JZZ library loaded');
                jzzLoaded = true;
                resolve(true);
            };
            script.onerror = () => {
                log('JZZ library failed to load');
                resolve(false);
            };
            document.head.appendChild(script);
        });
    }
    
    async function loadTone() {
        // Prefer local Tone.js if available, otherwise use Web Audio API fallback
        if (window.Tone) return true;
        if (toneLoaded) return false;
        
        // Try local first
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = '/js/Tone.js';
            script.onload = () => {
                log('Tone.js loaded (local)');
                toneLoaded = true;
                resolve(true);
            };
            script.onerror = () => {
                log('Tone.js not available - will use Web Audio API');
                toneLoaded = true;
                resolve(false);
            };
            document.head.appendChild(script);
        });
    }
    
    // Web Audio API - local fallback
    function playWebAudioDemo(name) {
        log('Playing via Web Audio API: ' + name);
        
        try {
            if (!audioContext) {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            if (audioContext.state === 'suspended') {
                audioContext.resume();
            }
            
            const now = audioContext.currentTime;
            
            const notes = [261.63, 329.63, 392.00, 493.88, 523.25, 493.88, 392.00, 329.63];
            
            notes.forEach((freq, i) => {
                const osc = audioContext.createOscillator();
                const gain = audioContext.createGain();
                
                osc.type = 'triangle';
                osc.frequency.value = freq;
                
                gain.gain.setValueAtTime(0, now + i * 0.15);
                gain.gain.linearRampToValueAtTime(0.15, now + i * 0.15 + 0.02);
                gain.gain.linearRampToValueAtTime(0.1, now + i * 0.15 + 0.1);
                gain.gain.linearRampToValueAtTime(0, now + i * 0.15 + 0.2);
                
                osc.connect(gain);
                gain.connect(audioContext.destination);
                
                osc.start(now + i * 0.15);
                osc.stop(now + i * 0.15 + 0.25);
            });
            
            log('Web Audio playing: ' + name);
            return true;
        } catch (e) {
            log('Web Audio error: ' + e.message);
            return false;
        }
    }
    
    async function loadTone() {
        if (window.Tone) return true;
        if (toneLoaded) return false;
        
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = '/js/Tone.js';
            script.onload = () => {
                log('Tone.js loaded (local)');
                toneLoaded = true;
                resolve(true);
            };
            script.onerror = () => {
                log('Tone.js failed - using Web Audio API');
                toneLoaded = true;
                resolve(false);
            };
            document.head.appendChild(script);
        });
    }
    
    async function playToneDemo(name) {
        log('Playing demo: ' + name);
        
        // Try Tone.js first (local)
        const toneReady = await loadTone();
        
        if (toneReady && window.Tone) {
            try {
                if (!audioContext) {
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                }
                
                if (audioContext.state === 'suspended') {
                    await audioContext.resume();
                }
                
                Tone.setContext(audioContext);
                
                if (!toneSynth) {
                    toneSynth = new Tone.PolySynth(Tone.Synth, {
                        oscillator: { type: "triangle" },
                        envelope: { attack: 0.01, decay: 0.1, sustain: 0.3, release: 0.4 }
                    }).toDestination();
                }
                
                const now = Tone.now();
                const melody = ["C4", "E4", "G4", "B4", "C5", "B4", "G4", "E4"];
                melody.forEach((note, i) => {
                    toneSynth.triggerAttackRelease(note, "8n", now + i * 0.15);
                });
                
                log('Tone.js playing: ' + name);
                return true;
            } catch (e) {
                log('Tone error: ' + e.message);
            }
        }
        
        // Fallback to Web Audio API
        return playWebAudioDemo(name);
    }
    
    // MIDI parser and player using Web Audio API
    const MIDI = {
        noteNames: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],

        parseMIDI: function(data) {
            const events = [];
            const bytes = new Uint8Array(data);

            // Check MIDI header "MThd"
            if (bytes[0] !== 0x4D || bytes[1] !== 0x54 || bytes[2] !== 0x68 || bytes[3] !== 0x64) {
                log('Invalid MIDI header');
                return [];
            }

            const headerLen = (bytes[4] << 24) | (bytes[5] << 16) | (bytes[6] << 8) | bytes[7];
            const format = (bytes[8] << 8) | bytes[9];
            const numTracks = (bytes[10] << 8) | bytes[11];
            const division = (bytes[12] << 8) | bytes[13];

            log('MIDI Format: ' + format + ', Tracks: ' + numTracks + ', Division: ' + division);

            let offset = 14; // Skip MThd header

            // Parse each track
            for (let track = 0; track < numTracks; track++) {
                // Check for MTrk header
                if (bytes[offset] !== 0x4D || bytes[offset+1] !== 0x54 || 
                    bytes[offset+2] !== 0x72 || bytes[offset+3] !== 0x6B) {
                    log('Invalid track header at track ' + track);
                    break;
                }

                const trackLen = (bytes[offset+4] << 24) | (bytes[offset+5] << 16) | 
                                (bytes[offset+6] << 8) | bytes[offset+7];
                const trackEnd = offset + 8 + trackLen;

                log('Parsing track ' + track + ' (' + trackLen + ' bytes)');

                offset += 8; // Skip MTrk header

                let currentTime = 0;
                let runningStatus = 0;
                let notesInTrack = 0;

                while (offset < trackEnd - 2 && offset < bytes.length) {
                    // Read delta time (variable-length)
                    let delta = 0;
                    for (let i = 0; i < 4; i++) {
                        delta = (delta << 7) | (bytes[offset] & 0x7F);
                        if ((bytes[offset] & 0x80) === 0) {
                            offset++;
                            break;
                        }
                        offset++;
                    }
                    currentTime += delta;

                    if (offset >= trackEnd) break;

                    // Read status byte
                    let status = bytes[offset];
                    if ((status & 0x80) === 0) {
                        // Running status - use previous status
                        status = runningStatus;
                    } else {
                        runningStatus = status;
                        offset++;
                    }

                    const type = status & 0xF0;

                    // Note On (0x90)
                    if (type === 0x90 && offset + 1 < trackEnd) {
                        const note = bytes[offset];
                        const vel = bytes[offset + 1];
                        if (vel > 0) {
                            events.push({
                                time: (currentTime / division) * 1000,
                                note: note,
                                velocity: vel,
                                track: track
                            });
                            notesInTrack++;
                        }
                        offset += 2;
                    }
                    // Note Off (0x80)
                    else if (type === 0x80 && offset + 1 < trackEnd) {
                        offset += 2;
                    }
                    // Control Change (0xB0)
                    else if (type === 0xB0 && offset + 1 < trackEnd) {
                        offset += 2;
                    }
                    // Program Change (0xC0)
                    else if (type === 0xC0 && offset < trackEnd) {
                        offset += 1;
                    }
                    // Pitch Bend (0xE0)
                    else if (type === 0xE0 && offset + 1 < trackEnd) {
                        offset += 2;
                    }
                    // Meta event (0xFF)
                    else if (status === 0xFF) {
                        offset++;
                        if (offset < trackEnd) {
                            let len = bytes[offset++];
                            offset += len;
                        }
                    }
                    // SysEx (0xF0, 0xF7)
                    else if (status === 0xF0 || status === 0xF7) {
                        offset++;
                        // Read variable-length length
                        let sysexLen = 0;
                        while (offset < trackEnd) {
                            sysexLen = (sysexLen << 7) | (bytes[offset] & 0x7F);
                            if ((bytes[offset] & 0x80) === 0) {
                                offset++;
                                break;
                            }
                            offset++;
                        }
                        offset += sysexLen;
                    }
                    else {
                        offset++;
                    }
                }

                log('Track ' + track + ': ' + notesInTrack + ' notes');
                offset = trackEnd; // Ensure we're at end of track
            }

            log('Total events parsed: ' + events.length);
            return events;
        },

        midiToFreq: function(note) {
            // MIDI note 69 = A4 = 440Hz
            return 440 * Math.pow(2, (note - 69) / 12);
        },
        
        playEvents: function(events, name, startPosition = 0) {
            // This is the native fallback - Tone.js is preferred
            if (!events || events.length === 0) {
                log('No events to play');
                return false;
            }

            initNative();

            if (audioContext.state === 'suspended') {
                audioContext.resume();
            }

            const now = audioContext.currentTime;
            events.sort((a, b) => a.time - b.time);
            const filtered = events.filter(e => e.time >= startPosition && e.time < 60000);

            log('Native: Scheduling ' + filtered.length + ' notes (from ' + startPosition + 'ms)');

            filtered.forEach(event => {
                const eventTime = now + 0.1 + ((event.time - startPosition) / 1000);
                if (eventTime < now) return;

                const freq = this.midiToFreq(event.note);
                const vel = event.velocity / 127;

                const osc1 = audioContext.createOscillator();
                const osc2 = audioContext.createOscillator();
                const gain = audioContext.createGain();

                osc1.type = 'sawtooth';
                osc1.frequency.value = freq;
                osc2.type = 'triangle';
                osc2.frequency.value = freq * 0.999;

                gain.gain.setValueAtTime(0, eventTime);
                gain.gain.linearRampToValueAtTime(vel * 0.3, eventTime + 0.01);
                gain.gain.linearRampToValueAtTime(0, eventTime + 0.3);

                osc1.connect(gain);
                osc2.connect(gain);
                gain.connect(masterGain);

                osc1.start(eventTime);
                osc2.start(eventTime);
                osc1.stop(eventTime + 0.35);
                osc2.stop(eventTime + 0.35);

                // Track for stop()
                activeSources.push({ osc1, osc2 });
            });

            log('Native: Playback scheduled');
            return true;
        }
    };
    
    /**
     * Play MIDI file using preferred engine
     * @param {string} midiUrl - URL to MIDI file
     * @param {string} name - Track name
     * @param {number} startPosition - Start position in ms (for resume)
     */
    async function playMIDI(midiUrl, name, startPosition = 0) {
        log('========================================');
        log('Playing: ' + name + (startPosition > 0 ? ' (from ' + startPosition + 'ms)' : ''));
        log('========================================');

        // Stop any current playback first
        stop();
        
        // Reset Tone.js Transport
        if (window.Tone && Tone.Transport) {
            Tone.Transport.stop();
            Tone.Transport.cancel();
        }

        try {
            // Determine engine based on user preference
            let engine = preferredEngine;

            // If preferred is 'tone' but Tone.js not available, fallback
            if (engine === 'tone' && !window.Tone) {
                log('Tone.js not available, falling back to native');
                engine = 'native';
            }

            // Initialize selected engine
            if (engine === 'tone') {
                log('Using Tone.js engine (preferred: ' + preferredEngine + ')');
                await initTone();
            } else {
                log('Using native Web Audio engine (preferred: ' + preferredEngine + ')');
                initNative();
            }

            log('Active engine: ' + engine);

            // Fetch MIDI file
            log('Fetching: ' + midiUrl);
            const response = await fetch(midiUrl);
            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ': ' + response.statusText);
            }
            const arrayBuffer = await response.arrayBuffer();
            const midiData = new Uint8Array(arrayBuffer);
            log('Loaded ' + midiData.length + ' bytes');

            // Validate MIDI structure
            log('Validating MIDI...');
            const validation = validateMIDI(midiData);
            if (!validation.valid) {
                error('Invalid MIDI: ' + validation.errors.join(', '));
                return false;
            }
            if (validation.warnings.length > 0) {
                log('Warnings: ' + validation.warnings.join(', '));
            }
            log('MIDI valid - Format: ' + validation.info.format + ', Division: ' + validation.info.division);

            // Play based on engine
            let result = false;

            if (engine === 'tone' && toneSynth) {
                log('Playing via Tone.js PolySynth...');
                result = await playViaTone(midiData, startPosition);
            } else {
                log('Playing via native Web Audio...');
                const events = MIDI.parseMIDI(midiData);
                result = events && events.length > 0 ? MIDI.playEvents(events, name, startPosition) : false;
            }

            if (result) {
                isPlaying = true;
                isPaused = false;
                playbackStartTime = Tone.now() - (startPosition / 1000);
                
                // Calculate total duration from events
                const events = MIDI.parseMIDI(midiData);
                if (events && events.length > 0) {
                    const maxTime = Math.max(...events.map(e => e.time));
                    totalDuration = maxTime;
                } else {
                    totalDuration = 60000; // Default 60 seconds
                }
                
                log('Track duration: ' + Math.round(totalDuration / 1000) + 's');
                log('Playback started successfully (' + engine + ')');
                
                // Start progress tracking
                startProgressTracking();
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
     * Play MIDI via Tone.js PolySynth (GOOD QUALITY)
     * @param {Uint8Array} midiData - MIDI file data
     * @param {number} startPosition - Start position in ms
     */
    async function playViaTone(midiData, startPosition = 0) {
        try {
            if (!toneSynth || !window.Tone) return false;

            // Cancel any scheduled events first
            Tone.Transport.cancel();
            
            const events = MIDI.parseMIDI(midiData);
            if (!events || events.length === 0) return false;

            // Sort by time
            events.sort((a, b) => a.time - b.time);

            // Limit to 60 seconds
            const filtered = events.filter(e => e.time >= startPosition && e.time < 60000);

            log('Tone.js: Scheduling ' + filtered.length + ' notes (from ' + startPosition + 'ms)');

            // Schedule notes using Tone.Transport (can be cancelled)
            filtered.forEach(event => {
                const eventTime = (event.time - startPosition) / 1000; // Convert to seconds
                const freq = MIDI.midiToFreq(event.note);
                const velocity = event.velocity / 127;

                // Schedule via Transport (cancellable)
                Tone.Transport.schedule((time) => {
                    toneSynth.triggerAttackRelease(freq, "8n", time, velocity);
                }, eventTime);
            });

            // Start transport
            Tone.Transport.start();
            
            log('Tone.js: Playback scheduled');
            return true;
        } catch (e) {
            error('Tone.js playback error: ' + e.message);
            return false;
        }
    }

    /**
     * Get engine status
     */
    function getEngineStatus() {
        return {
            current: currentEngine,
            preferred: preferredEngine,
            toneAvailable: !!window.Tone,
            nativeAvailable: true
        };
    }

    /**
     * Render audio playlist UI
     */
    function renderAudioList(files) {
        const list = document.getElementById('audioList');
        if (!list) return;

        // Set playlist
        setPlaylist(files);

        let html = '<div style="color:var(--accent);padding:12px;font-size:13px;font-weight:bold;border-bottom:1px solid var(--border);">';
        html += '♫ B.O.B. Soundtrack Jukebox</div>';

        // Player controls
        html += '<div style="padding:15px;margin:12px;background:linear-gradient(135deg,var(--bg-toolbar) 0%,var(--bg-panel) 100%);border:1px solid var(--border);border-radius:6px;">';
        html += '<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">';
        
        // Playback controls
        html += '<div style="display:flex;gap:6px;">';
        html += '<button type="button" id="btn-prev" title="Previous (←)" style="background:#3a3a4e;color:#fff;padding:10px 14px;cursor:pointer;border:none;border-radius:4px;font-size:14px;transition:all 0.2s;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">⏮</button>';
        html += '<button type="button" id="btn-play-pause" title="Play/Pause (Space)" style="background:var(--accent);color:#000;padding:10px 18px;cursor:pointer;border:none;border-radius:4px;font-size:16px;font-weight:bold;transition:all 0.2s;" onmouseover="this.style.background=\'#00ff99\'" onmouseout="this.style.background=\'var(--accent)\'">▶</button>';
        html += '<button type="button" id="btn-stop" title="Stop" style="background:#3a3a4e;color:#fff;padding:10px 14px;cursor:pointer;border:none;border-radius:4px;font-size:14px;transition:all 0.2s;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">⏹</button>';
        html += '<button type="button" id="btn-next" title="Next (→)" style="background:#3a3a4e;color:#fff;padding:10px 14px;cursor:pointer;border:none;border-radius:4px;font-size:14px;transition:all 0.2s;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">⏭</button>';
        html += '</div>';
        
        // Now Playing + Time Display
        html += '<div style="flex:1;min-width:220px;margin-left:10px;">';
        html += '<div style="display:flex;align-items:center;gap:10px;">';
        html += '<div style="flex:1;min-width:0;">';
        html += '<div style="font-size:9px;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;">Now Playing</div>';
        html += '<div id="now-playing" style="font-size:12px;color:var(--accent);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">None</div>';
        html += '</div>';
        html += '<div style="text-align:right;min-width:80px;">';
        html += '<div id="time-display" style="font-size:11px;color:var(--text);font-family:monospace;">0:00 / 0:00</div>';
        html += '<div style="font-size:9px;color:var(--text-dim);margin-top:2px;" id="speed-display">1.0x</div>';
        html += '</div>';
        html += '</div>';
        html += '</div>';
        
        // Engine toggle + Speed control
        html += '<div style="display:flex;gap:4px;align-items:center;">';
        html += '<button type="button" id="btn-speed-down" title="Slower (-)" style="background:#3a3a4e;color:#fff;width:24px;height:24px;cursor:pointer;border:none;border-radius:4px;font-size:12px;font-weight:bold;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">-</button>';
        html += '<button type="button" id="btn-engine-toggle" title="Switch audio engine" style="background:#3a3a4e;color:#fff;padding:6px 10px;cursor:pointer;border:none;border-radius:4px;font-size:9px;text-transform:uppercase;letter-spacing:0.5px;transition:all 0.2s;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">Engine: Tone.js</button>';
        html += '<button type="button" id="btn-speed-up" title="Faster (+)" style="background:#3a3a4e;color:#fff;width:24px;height:24px;cursor:pointer;border:none;border-radius:4px;font-size:12px;font-weight:bold;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">+</button>';
        html += '</div>';
        html += '</div>';
        
        // Progress bar
        html += '<div style="margin-top:12px;height:3px;background:#2a2a3e;border-radius:2px;overflow:hidden;">';
        html += '<div id="progress-bar" style="width:0%;height:100%;background:linear-gradient(90deg,var(--accent) 0%,#00ff99 100%);transition:width 0.1s;"></div>';
        html += '</div>';
        html += '</div>';

        // Playlist header
        html += '<div style="padding:8px 12px;font-size:10px;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid var(--border);">';
        html += 'Playlist (' + files.length + ' tracks)</div>';

        // Playlist
        html += '<div style="max-height:350px;overflow-y:auto;">';
        if (!files || files.length === 0) {
            html += '<div style="padding:40px;color:var(--text-dim);text-align:center;font-size:12px;">No MIDI files found</div>';
        } else {
            files.forEach((af, index) => {
                const fileName = af.filename || af.name || 'Unknown';
                const safeId = 'track-' + index;
                html += '<div id="' + safeId + '" style="padding:10px 12px;margin:2px 0;background:var(--bg-dark);border-radius:4px;cursor:pointer;transition:all 0.2s;display:flex;align-items:center;gap:12px;border:1px solid transparent;" onmouseover="this.style.background=\'var(--bg-toolbar)\'" onmouseout="if(!this.classList.contains(\'active\'))this.style.background=\'var(--bg-dark)\'" onclick="Audio.playTrack(' + index + ')">';
                html += '<div style="width:28px;height:28px;background:linear-gradient(135deg,#2a2a3e 0%,#1a1a2e 100%);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:11px;color:var(--accent);font-weight:bold;">' + (index + 1) + '</div>';
                html += '<div style="flex:1;min-width:0;">';
                html += '<div style="color:var(--text);font-size:12px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + fileName + '</div>';
                html += '</div>';
                html += '<div style="color:var(--accent);font-size:11px;opacity:0;transition:opacity 0.2s;" class="play-indicator">▶</div>';
                html += '</div>';
            });
        }
        html += '</div>';

        // Info footer
        html += '<div style="padding:10px 12px;margin-top:12px;background:var(--bg-dark);border-radius:4px;font-size:9px;color:var(--text-dim);border-top:1px solid var(--border);">';
        html += '<strong style="color:var(--accent);">Tone.js:</strong> High-quality synthesis | ';
        html += '<strong style="color:var(--accent);">Native:</strong> Basic synthesis';
        html += '</div>';

        list.innerHTML = html;

        // Update UI functions
        function updatePlayerUI() {
            const playBtn = document.getElementById('btn-play-pause');
            const nowPlaying = document.getElementById('now-playing');
            const speedDisplay = document.getElementById('speed-display');

            if (playBtn) {
                if (isPaused) {
                    playBtn.textContent = '▶';
                    playBtn.title = 'Resume (Space)';
                    playBtn.style.background = 'var(--accent)';
                } else if (isPlaying) {
                    playBtn.textContent = '⏸';
                    playBtn.title = 'Pause (Space)';
                    playBtn.style.background = '#ff9900';
                } else {
                    playBtn.textContent = '▶';
                    playBtn.title = 'Play (Space)';
                    playBtn.style.background = 'var(--accent)';
                }
            }

            if (nowPlaying) {
                const track = getCurrentTrack();
                nowPlaying.textContent = track ? track.name : 'None';
            }
            
            // Update speed display
            if (speedDisplay) {
                speedDisplay.textContent = playbackSpeed.toFixed(2) + 'x';
            }

            // Update playlist highlighting
            playlist.forEach((_, i) => {
                const el = document.getElementById('track-' + i);
                if (el) {
                    if (i === currentTrackIndex) {
                        el.style.background = 'var(--bg-toolbar)';
                        el.style.border = '1px solid var(--accent)';
                        el.classList.add('active');
                        const indicator = el.querySelector('.play-indicator');
                        if (indicator) {
                            indicator.style.opacity = '1';
                            if (isPaused) {
                                indicator.textContent = '⏸ Paused';
                                indicator.style.color = '#ff9900';
                            } else if (isPlaying) {
                                indicator.textContent = '♫ Playing';
                                indicator.style.color = 'var(--accent)';
                            } else {
                                indicator.textContent = '▶ Selected';
                                indicator.style.color = 'var(--text)';
                            }
                        }
                    } else {
                        el.style.background = 'var(--bg-dark)';
                        el.style.border = '1px solid transparent';
                        el.classList.remove('active');
                        const indicator = el.querySelector('.play-indicator');
                        if (indicator) indicator.style.opacity = '0';
                    }
                }
            });
        }

        // Implement progress UI update
        updateProgressUI = function(position, total, progress) {
            const timeDisplay = document.getElementById('time-display');
            const progressBar = document.getElementById('progress-bar');
            
            if (timeDisplay) {
                const posSec = Math.floor(position / 1000);
                const totalSec = Math.floor(total / 1000);
                const posMin = Math.floor(posSec / 60);
                const posRem = posSec % 60;
                const totalMin = Math.floor(totalSec / 60);
                const totalRem = totalSec % 60;
                
                timeDisplay.textContent = 
                    posMin + ':' + posRem.toString().padStart(2, '0') + ' / ' +
                    totalMin + ':' + totalRem.toString().padStart(2, '0');
            }
            
            if (progressBar) {
                progressBar.style.width = Math.min(progress, 100) + '%';
            }
        };

        // Button handlers
        let isPlayingToggle = false;  // Prevent multiple clicks
        
        document.getElementById('btn-play-pause')?.addEventListener('click', () => {
            if (isPlayingToggle) return;  // Prevent rapid clicks
            isPlayingToggle = true;
            
            if (isPlaying) {
                pause();
            } else if (isPaused) {
                resume();
            } else {
                // Play current track or first track
                if (currentTrackIndex >= 0) {
                    playTrack(currentTrackIndex);
                } else if (playlist.length > 0) {
                    playTrack(0);
                }
            }
            
            setTimeout(() => { isPlayingToggle = false; }, 100);
            updatePlayerUI();
        });

        document.getElementById('btn-stop')?.addEventListener('click', () => {
            stop();
            updatePlayerUI();
        });

        document.getElementById('btn-prev')?.addEventListener('click', () => {
            playPrevious();
            updatePlayerUI();
        });

        document.getElementById('btn-next')?.addEventListener('click', () => {
            playNext();
            updatePlayerUI();
        });

        // Engine toggle
        const toggleBtn = document.getElementById('btn-engine-toggle');
        if (toggleBtn) {
            toggleBtn.onclick = function(e) {
                e.stopPropagation();
                const newEngine = preferredEngine === 'tone' ? 'native' : 'tone';
                setPreferredEngine(newEngine);
                toggleBtn.textContent = 'Engine: ' + (newEngine === 'tone' ? 'Tone.js' : 'Native');
                toggleBtn.style.background = newEngine === 'tone' ? 'var(--accent)' : '#444';
                toggleBtn.style.color = newEngine === 'tone' ? '#000' : '#fff';
                log('Engine switched to: ' + newEngine);
            };
        }
        
        // Speed control
        document.getElementById('btn-speed-down')?.addEventListener('click', (e) => {
            e.stopPropagation();
            const newSpeed = Math.max(0.25, playbackSpeed - 0.25);
            setPlaybackSpeed(newSpeed);
            updatePlayerUI();
        });
        
        document.getElementById('btn-speed-up')?.addEventListener('click', (e) => {
            e.stopPropagation();
            const newSpeed = Math.min(4.0, playbackSpeed + 0.25);
            setPlaybackSpeed(newSpeed);
            updatePlayerUI();
        });

        // Initial UI update
        updatePlayerUI();
    }

    return {
        // Playback control
        playMIDI: playMIDI,
        playTrack: playTrack,
        playNext: playNext,
        playPrevious: playPrevious,
        pause: pause,
        resume: resume,
        stop: stop,
        
        // Playlist management
        setPlaylist: setPlaylist,
        getPlaylist: getPlaylist,
        getCurrentTrack: getCurrentTrack,
        
        // Playback speed
        setPlaybackSpeed: setPlaybackSpeed,
        getPlaybackSpeed: getPlaybackSpeed,
        
        // Settings
        setPreferredEngine: setPreferredEngine,
        getEngineStatus: getEngineStatus,
        
        // UI
        renderAudioList: renderAudioList
    };
})();

// Export to window
window.Audio = Audio;
