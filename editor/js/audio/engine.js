/**
 * Audio Module - Engine Management
 * 
 * Handles Tone.js and native Web Audio engine initialization.
 */

const AudioEngine = (function() {
    'use strict';

    function log(msg) {
        console.log('[Audio] ' + msg);
    }

    function error(msg) {
        console.error('[Audio] ERROR: ' + msg);
    }

    /**
     * Initialize Tone.js synth (DEFERRED until first user gesture)
     */
    async function initTone() {
        const state = window.AudioState;
        if (state.getToneSynth()) {
            log('Tone.js already initialized');
            return true;
        }

        try {
            log('Initializing Tone.js engine (first use)...');

            if (!window.Tone) {
                throw new Error('Tone.js library not loaded');
            }

            // This MUST be called from user gesture
            await Tone.start();
            log('Tone.AudioContext started');

            // Create high-quality polyphonic synth
            const synth = new Tone.PolySynth(Tone.Synth, {
                oscillator: { type: "fatsawtooth" },
                envelope: { attack: 0.01, decay: 0.1, sustain: 0.3, release: 0.5 },
                portamento: 0.05
            }).toDestination();

            // Add effects chain
            const reverb = new Tone.Reverb({ decay: 2, wet: 0.3 }).toDestination();
            const compressor = new Tone.Compressor({ threshold: -24, ratio: 12 }).toDestination();

            synth.connect(compressor);
            compressor.connect(reverb);

            state.setToneSynth(synth);
            state.setCurrentEngine('tone');

            log('Tone.js engine initialized');
            return true;
        } catch (e) {
            error('Tone.js initialization failed: ' + e.message);
            return false;
        }
    }

    /**
     * Initialize native Web Audio (FALLBACK)
     */
    function initNative() {
        const state = window.AudioState;
        if (state.getAudioContext()) return true;

        try {
            log('Initializing native Web Audio engine...');

            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            state.setAudioContext(ctx);

            const masterGain = ctx.createGain();
            masterGain.gain.value = 0.4;

            const compressorNode = ctx.createDynamicsCompressor();
            compressorNode.threshold.value = -24;
            compressorNode.knee.value = 30;
            compressorNode.ratio.value = 12;
            compressorNode.attack.value = 0.003;
            compressorNode.release.value = 0.25;

            const reverbNode = ctx.createConvolver();
            createReverbImpulse(ctx, reverbNode);

            reverbNode.connect(compressorNode);
            compressorNode.connect(masterGain);
            masterGain.connect(ctx.destination);

            const dryGain = ctx.createGain();
            dryGain.gain.value = 0.7;
            dryGain.connect(compressorNode);

            state.setCurrentEngine('native');
            log('Native Web Audio engine initialized');
            return true;
        } catch (e) {
            error('Native initialization failed: ' + e.message);
            return false;
        }
    }

    /**
     * Create reverb impulse response
     */
    function createReverbImpulse(ctx, reverbNode) {
        const duration = 1.5;
        const decay = 2.0;
        const rate = ctx.sampleRate;
        const length = rate * duration;
        const impulse = ctx.createBuffer(2, length, rate);

        for (let ch = 0; ch < 2; ch++) {
            const data = impulse.getChannelData(ch);
            for (let i = 0; i < length; i++) {
                data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, decay);
            }
        }
        reverbNode.buffer = impulse;
    }

    return {
        initTone: initTone,
        initNative: initNative,
        createReverbImpulse: createReverbImpulse
    };
})();

// Export to window
window.AudioEngine = AudioEngine;
