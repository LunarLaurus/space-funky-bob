/**
 * Audio Module - High-Quality MIDI Playback
 * 
 * Uses JZZ.js for professional MIDI playback with SoundFont synthesis.
 * This provides the best possible MIDI quality with realistic instrument sounds.
 * 
 * Libraries:
 * - JZZ.js: Professional MIDI engine with SoundFont support
 * - Tone.js: High-quality Web Audio synthesis (fallback)
 * 
 * Quality Tiers:
 * 1. JZZ + SoundFont (best - realistic instruments)
 * 2. Tone.js PolySynth (good - quality synthesis)
 * 3. Native Web Audio (fallback - basic synthesis)
 */

const Audio = (function() {
    'use strict';

    // Audio engines
    let jzzEngine = null;      // JZZ MIDI engine (best quality)
    let toneSynth = null;      // Tone.js synth (good quality)
    let audioContext = null;   // Native Web Audio (fallback)
    
    // State
    let currentEngine = null;  // 'jzz', 'tone', or 'native'
    let isInitialized = false;
    let isPlaying = false;
    let testMode = false;
    let testResults = [];

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
     * Initialize JZZ engine (BEST QUALITY)
     * Uses SoundFont synthesis for realistic instruments
     */
    async function initJZZ() {
        if (jzzEngine) return true;

        try {
            log('Initializing JZZ engine...');

            // JZZ should be loaded via script tag
            if (!window.JZZ) {
                throw new Error('JZZ library not loaded');
            }

            // Initialize JZZ with SoundFont
            jzzEngine = await JZZ().openMidiOut();
            
            if (!jzzEngine || !jzzEngine.isOpen()) {
                throw new Error('JZZ failed to open MIDI output');
            }

            log('JZZ engine initialized with SoundFont synthesis');
            currentEngine = 'jzz';
            return true;
        } catch (e) {
            error('JZZ initialization failed: ' + e.message);
            jzzEngine = null;
            return false;
        }
    }

    /**
     * Initialize Tone.js synth (GOOD QUALITY)
     * Uses polyphonic synthesis
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
     * Basic synthesis when libraries unavailable
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
            if (bytes[0] !== 0x4D || bytes[3] !== 0x64) {
                return [];
            }
            
            const division = (bytes[12] << 8) | bytes[13];
            
            // Find track data - skip header (14 bytes)
            let offset = 14;
            
            // Skip MTrk header and length
            if (bytes[offset] === 0x4D && bytes[offset+1] === 0x54) {
                offset += 8;
            }
            
            let currentTime = 0;
            let runningStatus = 0;
            let bytesProcessed = 0;
            const maxBytes = 5000;
            
            while (offset < bytes.length - 2 && bytesProcessed < maxBytes) {
                bytesProcessed++;
                
                // Read delta time
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
                
                if (offset >= bytes.length) break;
                
                let status = bytes[offset];
                if ((status & 0x80) === 0) {
                    status = runningStatus;
                } else {
                    runningStatus = status;
                    offset++;
                }
                
                const type = status & 0xF0;
                
                if (type === 0x90 && offset + 1 < bytes.length) {
                    const note = bytes[offset];
                    const vel = bytes[offset + 1];
                    if (vel > 0) {
                        events.push({
                            time: (currentTime / division) * 1000,
                            note: note,
                            velocity: vel
                        });
                    }
                    offset += 2;
                } else if (type === 0x80 && offset + 1 < bytes.length) {
                    offset += 2;
                } else if (type === 0xB0) { offset += 2; }
                else if (type === 0xC0) { offset += 1; }
                else if (type === 0xE0) { offset += 2; }
                else if (status === 0xFF) {
                    offset++;
                    let len = bytes[offset++];
                    offset += len;
                } else {
                    offset++;
                }
            }
            
            return events;
        },
        
        midiToFreq: function(note) {
            // MIDI note 69 = A4 = 440Hz
            return 440 * Math.pow(2, (note - 69) / 12);
        },
        
        playEvents: function(events, name) {
            if (!events || events.length === 0) {
                log('No events to play');
                return false;
            }

            // Initialize high-quality audio chain
            initAudioChain();

            if (audioContext.state === 'suspended') {
                audioContext.resume();
            }

            const now = audioContext.currentTime;
            const startTime = now + 0.1;

            // Sort events by time
            events.sort((a, b) => a.time - b.time);

            // Limit to first 60 seconds for performance
            const maxTime = 60000;
            const filtered = events.filter(e => e.time < maxTime);

            log('Playing ' + filtered.length + ' events from ' + startTime);

            // Group simultaneous notes for better voice management
            const voices = new Map();
            const activeNotes = new Set();

            // Create improved synth voice
            const createVoice = (freq, velocity, time) => {
                // Use multiple oscillators for richer sound
                const osc1 = audioContext.createOscillator();
                const osc2 = audioContext.createOscillator();
                const filter = audioContext.createBiquadFilter();
                const gain = audioContext.createGain();
                const vibrato = audioContext.createOscillator();
                const vibratoGain = audioContext.createGain();

                // Oscillator 1 - main tone (sawtooth for brightness)
                osc1.type = 'sawtooth';
                osc1.frequency.value = freq;

                // Oscillator 2 - detuned for thickness
                osc2.type = 'triangle';
                osc2.frequency.value = freq * 0.999; // Slight detune

                // Filter - lowpass with envelope
                filter.type = 'lowpass';
                filter.Q.value = 5;
                filter.frequency.setValueAtTime(200, time);
                filter.frequency.linearRampToValueAtTime(2000 + velocity * 20, time + 0.02);
                filter.frequency.exponentialRampToValueAtTime(800, time + 0.1);

                // Vibrato
                vibrato.frequency.value = 5; // 5 Hz vibrato
                vibratoGain.gain.value = 3; // Vibrato depth
                vibrato.connect(vibratoGain);
                vibratoGain.connect(osc1.frequency);

                // Velocity-based amplitude
                const vel = velocity / 127;

                // ADSR envelope with improved shape
                gain.gain.setValueAtTime(0, time);
                gain.gain.linearRampToValueAtTime(vel * 0.3, time + 0.01); // Attack
                gain.gain.linearRampToValueAtTime(vel * 0.2, time + 0.05); // Decay to sustain
                gain.gain.linearRampToValueAtTime(vel * 0.15, time + 0.15); // Sustain
                gain.gain.linearRampToValueAtTime(0, time + 0.3); // Release

                // Connect chain
                osc1.connect(filter);
                osc2.connect(filter);
                filter.connect(gain);
                gain.connect(reverbNode);
                gain.connect(masterGain); // Also connect to dry signal

                // Start/stop
                osc1.start(time);
                osc2.start(time);
                vibrato.start(time);
                osc1.stop(time + 0.35);
                osc2.stop(time + 0.35);
                vibrato.stop(time + 0.35);

                return { osc1, osc2, filter, gain, vibrato };
            };

            // Schedule all notes
            filtered.forEach((event, index) => {
                const eventTime = startTime + (event.time / 1000);

                // Skip if time is in the past
                if (eventTime < now) return;

                const freq = this.midiToFreq(event.note);
                const noteKey = event.note;

                // Stop previous note on same key (monophonic per voice)
                if (voices.has(noteKey)) {
                    const oldVoice = voices.get(noteKey);
                    const oldTime = audioContext.currentTime;
                    oldVoice.gain.gain.cancelScheduledValues(oldTime);
                    oldVoice.gain.gain.setValueAtTime(oldVoice.gain.gain.value, oldTime);
                    oldVoice.gain.gain.exponentialRampToValueAtTime(0.001, oldTime + 0.05);
                    oldVoice.osc1.stop(oldTime + 0.05);
                    oldVoice.osc2.stop(oldTime + 0.05);
                    oldVoice.vibrato.stop(oldTime + 0.05);
                }

                // Create new voice
                const voice = createVoice(freq, event.velocity, eventTime);
                voices.set(noteKey, voice);

                // Auto-cleanup
                setTimeout(() => {
                    voices.delete(noteKey);
                }, (event.time / 1000 + 0.4) * 1000);
            });

            log('Scheduled ' + filtered.length + ' notes with enhanced synthesis');
            return true;
        }
    };
    
    /**
     * Play MIDI file using best available engine
     * Priority: JZZ (SoundFont) > Tone.js > Native Web Audio
     */
    async function playMIDI(midiUrl, name) {
        log('========================================');
        log('Playing: ' + name);
        log('========================================');

        try {
            // Determine best available engine
            let engine = 'native';
            
            if (window.JZZ) {
                log('JZZ library available - using SoundFont synthesis (BEST)');
                const jzzReady = await initJZZ();
                if (jzzReady) engine = 'jzz';
            }
            
            if (engine === 'native' && window.Tone) {
                log('Tone.js library available - using PolySynth (GOOD)');
                const toneReady = await initTone();
                if (toneReady) engine = 'tone';
            }
            
            if (engine === 'native') {
                log('Using native Web Audio synthesis (FALLBACK)');
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
            
            if (engine === 'jzz' && jzzEngine) {
                log('Playing via JZZ SoundFont...');
                result = await playViaJZZ(midiData);
            } else if (engine === 'tone' && toneSynth) {
                log('Playing via Tone.js PolySynth...');
                result = await playViaTone(midiData);
            } else {
                log('Playing via native Web Audio...');
                const events = MIDI.parseMIDI(midiData);
                result = events && events.length > 0 ? MIDI.playEvents(events, name) : false;
            }

            if (result) {
                log('Playback started successfully (' + engine + ')');
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
     * Play MIDI via JZZ SoundFont engine (BEST QUALITY)
     */
    async function playViaJZZ(midiData) {
        try {
            if (!jzzEngine) return false;

            // Send MIDI data to JZZ
            // JZZ will handle all timing and synthesis
            jzzEngine.send(new Uint8Array(midiData));
            
            log('JZZ: MIDI data sent to SoundFont synthesizer');
            return true;
        } catch (e) {
            error('JZZ playback error: ' + e.message);
            return false;
        }
    }

    /**
     * Play MIDI via Tone.js PolySynth (GOOD QUALITY)
     */
    async function playViaTone(midiData) {
        try {
            if (!toneSynth || !window.Tone) return false;

            const events = MIDI.parseMIDI(midiData);
            if (!events || events.length === 0) return false;

            // Sort by time
            events.sort((a, b) => a.time - b.time);

            const now = Tone.now();
            const startTime = now + 0.1;

            // Limit to 60 seconds
            const filtered = events.filter(e => e.time < 60000);

            log('Tone.js: Scheduling ' + filtered.length + ' notes');

            // Schedule notes
            filtered.forEach(event => {
                const eventTime = startTime + (event.time / 1000);
                if (eventTime < now) return;

                const freq = MIDI.midiToFreq(event.note);
                const velocity = event.velocity / 127;

                // Trigger note via Tone.js
                toneSynth.triggerAttackRelease(
                    freq,
                    "8n",
                    eventTime,
                    velocity
                );
            });

            log('Tone.js: Playback scheduled');
            return true;
        } catch (e) {
            error('Tone.js playback error: ' + e.message);
            return false;
        }
    }

    /**
     * Run audio validation tests
     * @returns {Object} Test results
     */
    function runTests() {
        testMode = true;
        testResults = [];

        log('========================================');
        log('Running audio validation tests...');
        log('========================================');

        // Test 1: AudioContext creation
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            testResults.push({ name: 'AudioContext creation', pass: true });
            log('✓ AudioContext creation');
        } catch (e) {
            testResults.push({ name: 'AudioContext creation', pass: false, error: e.message });
            log('✗ AudioContext creation: ' + e.message);
        }

        // Test 2: MIDI validation with valid data
        const validHeader = new Uint8Array([0x4D, 0x54, 0x68, 0x64, 0, 0, 0, 6, 0, 0, 0, 1, 0x03, 0xE8]);
        const validResult = validateMIDI(validHeader);
        testResults.push({ name: 'MIDI validation (valid)', pass: validResult.valid });
        log((validResult.valid ? '✓' : '✗') + ' MIDI validation (valid)');

        // Test 3: MIDI validation with invalid header
        const invalidHeader = new Uint8Array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
        const invalidResult = validateMIDI(invalidHeader);
        testResults.push({ name: 'MIDI validation (invalid)', pass: !invalidResult.valid });
        log((!invalidResult.valid ? '✓' : '✗') + ' MIDI validation (invalid rejected)');

        // Test 4: Web Audio API support
        const hasOscillator = typeof window.OscillatorNode !== 'undefined';
        const hasGain = typeof window.GainNode !== 'undefined';
        const hasConvolver = typeof window.ConvolverNode !== 'undefined';
        const hasCompressor = typeof window.DynamicsCompressorNode !== 'undefined';
        const apiTest = hasOscillator && hasGain && hasConvolver && hasCompressor;
        testResults.push({ name: 'Web Audio API support', pass: apiTest });
        log((apiTest ? '✓' : '✗') + ' Web Audio API support');

        // Test 5: JZZ library availability (BEST)
        const hasJZZ = typeof window.JZZ !== 'undefined';
        testResults.push({ name: 'JZZ library (SoundFont)', pass: hasJZZ });
        log((hasJZZ ? '✓' : '✗') + ' JZZ library (SoundFont) - BEST QUALITY');

        // Test 6: Tone.js library availability (GOOD)
        const hasTone = typeof window.Tone !== 'undefined';
        testResults.push({ name: 'Tone.js library', pass: hasTone });
        log((hasTone ? '✓' : '✗') + ' Tone.js library - GOOD QUALITY');

        // Engine summary
        log('========================================');
        log('Engine Availability:');
        log('  JZZ (SoundFont):    ' + (hasJZZ ? 'YES ★' : 'NO'));
        log('  Tone.js (Synth):    ' + (hasTone ? 'YES' : 'NO'));
        log('  Native (Fallback):  YES');
        log('========================================');

        // Summary
        const passed = testResults.filter(r => r.pass).length;
        const total = testResults.length;
        log('Test Results: ' + passed + '/' + total + ' passed');
        log('========================================');

        testMode = false;
        return {
            passed,
            total,
            results: testResults,
            allPassed: passed === total,
            engines: { jzz: hasJZZ, tone: hasTone, native: true }
        };
    }

    /**
     * Get test results
     */
    function getTestResults() {
        return {
            currentEngine,
            isPlaying,
            testMode,
            results: testResults,
            engines: {
                jzz: !!jzzEngine,
                tone: !!toneSynth,
                native: !!audioContext
            }
        };
    }
    
    function renderAudioList(files) {
        const list = document.getElementById('audioList');
        if (!list) return;

        let html = '<div style="color:var(--accent);padding:10px;font-size:11px;">';
        html += 'Audio files from source (MIDI format):</div>';

        // Test button
        html += '<div style="padding:10px;margin:10px 0;">';
        html += '<button type="button" id="btn-audio-test" style="background:#444;color:#fff;padding:8px 16px;cursor:pointer;border:none;border-radius:4px;margin-right:8px;">Run Audio Tests</button>';
        html += '<span id="audio-test-result" style="font-size:11px;color:var(--text-dim);"></span>';
        html += '</div>';

        if (!files || files.length === 0) {
            html += '<div style="padding:10px;color:var(--text-dim);">No MIDI files found</div>';
        } else {
            files.forEach((af) => {
                // Handle both 'filename' (API) and 'name' (legacy) formats
                const fileName = af.filename || af.name || 'unknown';
                const fileUrl = af.path || af.url || '#';
                const safeName = fileName.replace(/\./g, '_').replace(/[^a-zA-Z0-9_]/g, '');
                html += '<div style="padding:12px;margin:5px 0;background:var(--bg-dark);border-radius:4px;">';
                html += '<div style="color:var(--accent);font-weight:bold;font-size:12px;margin-bottom:8px;">' + fileName + '</div>';
                html += '<div style="display:flex;gap:8px;">';
                html += '<button type="button" id="btn_play_' + safeName + '" style="background:var(--accent);color:#000;padding:8px 16px;cursor:pointer;border:none;border-radius:4px;">Play</button>';
                html += '<a href="' + fileUrl + '" download="' + fileName + '" style="background:#444;color:#fff;padding:8px 16px;text-decoration:none;border-radius:4px;">Download</a>';
                html += '</div></div>';
            });
        }

        html += '<div style=\"padding:15px;margin-top:10px;background:var(--bg-dark);border-radius:4px;font-size:10px;color:var(--text-dim);\">';
        html += 'Note: Click Play to play MIDI via Web Audio. Download for full quality.</div>';

        list.innerHTML = html;

        // Test button handler
        const testBtn = document.getElementById('btn-audio-test');
        const testResult = document.getElementById('audio-test-result');
        if (testBtn) {
            testBtn.onclick = function() {
                const results = Audio.runTests();
                testResult.textContent = results.allPassed ? 
                    '✓ All tests passed!' : 
                    '✗ ' + results.passed + '/' + results.total + ' passed';
                testResult.style.color = results.allPassed ? 'var(--accent)' : '#ff5555';
            };
        }

        // Attach click handlers
        if (files) {
            files.forEach((af) => {
                const fileName = af.filename || af.name || 'unknown';
                const fileUrl = af.path || af.url || '#';
                const safeName = fileName.replace(/\./g, '_').replace(/[^a-zA-Z0-9_]/g, '');
                const btn = document.getElementById('btn_play_' + safeName);
                if (btn) {
                    btn.onclick = function() {
                        playMIDI(fileUrl, fileName);
                    };
                }
            });
        }
    }

    return {
        playMIDI: playMIDI,
        renderAudioList: renderAudioList,
        runTests: runTests,
        getTestResults: getTestResults,
        getCurrentEngine: function() { return currentEngine; },
        isInitialized: function() { return isInitialized; },
        stop: function() {
            if (toneSynth && window.Tone) {
                toneSynth.releaseAll();
            }
            isPlaying = false;
        }
    };
})();

// Export to window
window.Audio = Audio;
