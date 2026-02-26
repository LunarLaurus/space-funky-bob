/**
 * Audio Module - MIDI Playback
 * 
 * Handles MIDI parsing and playback via Tone.js or native Web Audio.
 */

const AudioPlayback = (function() {
    'use strict';

    function log(msg) {
        console.log('[Audio] ' + msg);
    }

    function error(msg) {
        console.error('[Audio] ERROR: ' + msg);
    }

    /**
     * Validate MIDI data
     */
    function validateMIDI(data) {
        const result = { valid: false, errors: [], warnings: [] };

        if (!data || data.length < 14) {
            result.errors.push('File too small for MIDI format');
            return result;
        }

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
     * Parse MIDI file
     * @returns {Object} { events, msPerTick }
     */
    function parseMIDI(data) {
        const events = [];
        const bytes = new Uint8Array(data);

        if (bytes[0] !== 0x4D || bytes[1] !== 0x54 || bytes[2] !== 0x68 || bytes[3] !== 0x64) {
            log('Invalid MIDI header');
            return { events: [], msPerTick: 1.0 };
        }

        const format = (bytes[8] << 8) | bytes[9];
        const numTracks = (bytes[10] << 8) | bytes[11];
        const division = (bytes[12] << 8) | bytes[13];

        log('MIDI Format: ' + format + ', Tracks: ' + numTracks + ', Division: ' + division);

        // Default tempo: 120 BPM = 500000 microseconds per quarter note
        let tempo = 500000;
        let ticksPerBeat = division;
        let msPerTick = tempo / (ticksPerBeat * 1000);
        
        log('parseMIDI() - default tempo: 120 BPM (' + tempo + ' µs/beat)');
        log('parseMIDI() - msPerTick: ' + msPerTick.toFixed(4));

        let offset = 14;

        for (let track = 0; track < numTracks; track++) {
            if (bytes[offset] !== 0x4D || bytes[offset+1] !== 0x54 ||
                bytes[offset+2] !== 0x72 || bytes[offset+3] !== 0x6B) {
                log('Invalid track header at track ' + track);
                break;
            }

            const trackLen = (bytes[offset+4] << 24) | (bytes[offset+5] << 16) |
                            (bytes[offset+6] << 8) | bytes[offset+7];
            const trackEnd = offset + 8 + trackLen;

            log('Parsing track ' + track + ' (' + trackLen + ' bytes, offset=' + offset + ', trackEnd=' + trackEnd + ')');
            offset += 8;

            let currentTime = 0;
            let runningStatus = 0;
            let notesInTrack = 0;
            let eventsChecked = 0;

            while (offset < trackEnd - 2 && offset < bytes.length) {
                let delta = 0;
                for (let i = 0; i < 4; i++) {
                    if (offset >= trackEnd) break;
                    delta = (delta << 7) | (bytes[offset] & 0x7F);
                    if ((bytes[offset] & 0x80) === 0) {
                        offset++;
                        break;
                    }
                    offset++;
                }
                currentTime += delta;

                if (offset >= trackEnd) {
                    log('parseMIDI() - reached trackEnd after delta, offset=' + offset + ' trackEnd=' + trackEnd);
                    break;
                }

                let status = bytes[offset];
                if ((status & 0x80) === 0) {
                    status = runningStatus;
                } else {
                    runningStatus = status;
                    offset++;
                }

                const type = status & 0xF0;
                eventsChecked++;

                // Note On (0x90-0x9F)
                if (type === 0x90 && offset + 1 < trackEnd) {
                    const note = bytes[offset];
                    const vel = bytes[offset + 1];
                    if (vel > 0) {
                        // Convert ticks to milliseconds using tempo
                        const timeMs = currentTime * msPerTick;
                        events.push({
                            time: timeMs,
                            note: note,
                            velocity: vel,
                            track: track
                        });
                        notesInTrack++;
                    }
                    offset += 2;
                }
                // Note Off (0x80-0x8F)
                else if (type === 0x80 && offset + 1 < trackEnd) {
                    offset += 2;
                }
                // Control Change (0xB0-0xBF)
                else if (type === 0xB0 && offset + 1 < trackEnd) {
                    offset += 2;
                }
                // Program Change (0xC0-0xCF)
                else if (type === 0xC0 && offset < trackEnd) {
                    offset += 1;
                }
                // Pitch Bend (0xE0-0xEF)
                else if (type === 0xE0 && offset + 1 < trackEnd) {
                    offset += 2;
                }
                // Meta event (0xFF)
                else if (status === 0xFF) {
                    offset++;
                    if (offset < trackEnd) {
                        const metaType = bytes[offset++];
                        // Read length as SINGLE BYTE (standard MIDI format)
                        let len = 0;
                        if (offset < trackEnd) {
                            len = bytes[offset++];
                        }
                        
                        // Tempo meta event (0x51): 3 bytes, microseconds per quarter note
                        if (metaType === 0x51 && len === 3 && offset + 3 <= trackEnd) {
                            tempo = (bytes[offset] << 16) | (bytes[offset+1] << 8) | bytes[offset+2];
                            msPerTick = tempo / (ticksPerBeat * 1000);
                            const bpm = 60000000 / tempo;
                            log('parseMIDI() - tempo change: ' + bpm.toFixed(1) + ' BPM');
                        }
                        
                        // Skip the meta event data
                        offset += len;
                        
                        // Safety check - don't go past trackEnd
                        if (offset > trackEnd) {
                            offset = trackEnd;
                        }
                    }
                }
                // SYSEX event (0xF0 or 0xF7)
                else if (status === 0xF0 || status === 0xF7) {
                    offset++;
                    // Read SYSEX length (variable-length)
                    let sysexLen = 0;
                    while (offset < trackEnd) {
                        const byte = bytes[offset++];
                        sysexLen = (sysexLen << 7) | (byte & 0x7F);
                        if (!(byte & 0x80)) break;
                    }
                    log('parseMIDI() - sysex len=' + sysexLen);
                    offset += sysexLen;
                }
                // Unknown/running status - skip
                else {
                    offset++;
                }
            }

            log('Track ' + track + ': ' + notesInTrack + ' notes');
            offset = trackEnd;
        }

        log('Total events parsed: ' + events.length);
        return { events, msPerTick };
    }

    /**
     * Convert MIDI note to frequency
     */
    function midiToFreq(note) {
        return 440 * Math.pow(2, (note - 69) / 12);
    }

    /**
     * Play via Tone.js
     */
    async function playViaTone(midiData, startPosition) {
        const state = window.AudioState;
        const toneSynth = state.getToneSynth();

        if (!toneSynth || !window.Tone) {
            log('playViaTone() - toneSynth not available');
            return false;
        }

        // Get current playback speed
        const speed = state.getPlaybackSpeed();
        log('playViaTone() - playback speed: ' + speed + 'x');

        log('playViaTone() - cancelling Tone.Transport');
        Tone.Transport.cancel();

        // Parse MIDI and get events with correct tempo
        const parseResult = parseMIDI(midiData);
        const events = parseResult.events;
        
        if (!events || events.length === 0) {
            log('playViaTone() - no events');
            return false;
        }

        events.sort((a, b) => a.time - b.time);
        const filtered = events.filter(e => e.time >= startPosition && e.time < 60000);

        log('playViaTone() - scheduling ' + filtered.length + ' notes from ' + startPosition + 'ms (msPerTick: ' + parseResult.msPerTick.toFixed(4) + ')');

        // Schedule notes
        const now = Tone.now();
        log('playViaTone() - Tone.now() = ' + now);

        let scheduledCount = 0;
        filtered.forEach((event, i) => {
            // Apply speed: faster speed = shorter time between notes
            const eventTime = now + (((event.time - startPosition) / 1000) / speed);
            const freq = midiToFreq(event.note);
            const velocity = event.velocity / 127;

            // Log first few and last few events
            if (i < 5 || i >= filtered.length - 5) {
                log('playViaTone() - note[' + i + '] freq=' + freq + 'Hz time=' + eventTime.toFixed(3) + 's (speed: ' + speed + 'x)');
            } else if (i === 5) {
                log('playViaTone() - ... (' + (filtered.length - 10) + ' more notes) ...');
            }

            try {
                toneSynth.triggerAttackRelease(freq, "8n", eventTime, velocity);
                scheduledCount++;
            } catch (e) {
                log('playViaTone() - error scheduling note ' + i + ': ' + e.message);
            }
        });

        log('playViaTone() - scheduled ' + scheduledCount + '/' + filtered.length + ' notes');
        log('playViaTone() - playback scheduled at ' + speed + 'x speed');
        return true;
    }

    /**
     * Play via native Web Audio
     */
    function playViaNative(midiData, name, startPosition, msPerTick) {
        const state = window.AudioState;
        const ctx = state.getAudioContext();
        
        if (!ctx) {
            log('playViaNative() - audioContext not available');
            return false;
        }

        const parseResult = parseMIDI(midiData);
        const events = parseResult.events;
        
        // Use provided msPerTick or fall back to parsed value
        const tempoMsPerTick = msPerTick || parseResult.msPerTick;
        
        if (!events || events.length === 0) {
            log('playViaNative() - no events');
            return false;
        }

        const now = ctx.currentTime;
        const filtered = events.filter(e => e.time >= startPosition && e.time < 60000);

        log('playViaNative() - scheduling ' + filtered.length + ' notes');

        filtered.forEach(event => {
            const eventTime = now + 0.1 + ((event.time - startPosition) / 1000);
            if (eventTime < now) return;

            const freq = midiToFreq(event.note);
            const vel = event.velocity / 127;

            const osc1 = ctx.createOscillator();
            const osc2 = ctx.createOscillator();
            const gain = ctx.createGain();

            osc1.type = 'sawtooth';
            osc1.frequency.value = freq;
            osc2.type = 'triangle';
            osc2.frequency.value = freq * 0.999;

            gain.gain.setValueAtTime(0, eventTime);
            gain.gain.linearRampToValueAtTime(vel * 0.3, eventTime + 0.01);
            gain.gain.linearRampToValueAtTime(0, eventTime + 0.3);

            osc1.connect(gain);
            osc2.connect(gain);
            gain.connect(ctx.destination);

            osc1.start(eventTime);
            osc2.start(eventTime);
            osc1.stop(eventTime + 0.35);
            osc2.stop(eventTime + 0.35);

            state.getActiveSources().push({ osc1, osc2, startTime: eventTime, stopTime: eventTime + 0.35 });
        });

        log('playViaNative() - playback scheduled');
        return true;
    }

    return {
        validateMIDI: validateMIDI,
        parseMIDI: parseMIDI,
        midiToFreq: midiToFreq,
        playViaTone: playViaTone,
        playViaNative: playViaNative
    };
})();

// Export to window
window.AudioPlayback = AudioPlayback;
