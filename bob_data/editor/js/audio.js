/**
 * Audio Module - MIDI Playback
 * Handles loading and playing MIDI files from the game
 */

const Audio = (function() {
    'use strict';
    
    let jzzLoaded = false;
    let toneLoaded = false;
    let toneSynth = null;
    let audioContext = null;
    
    function log(msg) {
        console.log('[Audio] ' + msg);
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
            
            if (!audioContext) {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            if (audioContext.state === 'suspended') {
                audioContext.resume();
            }
            
            const now = audioContext.currentTime;
            const startTime = now + 0.05;
            
            // Sort events by time
            events.sort((a, b) => a.time - b.time);
            
            // Limit to first 30 seconds
            const maxTime = 30000;
            const filtered = events.filter(e => e.time < maxTime);
            
            log('Playing ' + filtered.length + ' events from ' + startTime);
            
            // Create a simple synth for each note
            filtered.forEach((event) => {
                const eventTime = startTime + (event.time / 1000);
                
                // Skip if time is in the past
                if (eventTime < now) return;
                
                const osc = audioContext.createOscillator();
                const gain = audioContext.createGain();
                
                osc.type = 'triangle';
                osc.frequency.value = this.midiToFreq(event.note);
                
                const vel = (event.velocity || 100) / 127;
                
                // ADSR envelope
                gain.gain.setValueAtTime(0, eventTime);
                gain.gain.linearRampToValueAtTime(vel * 0.2, eventTime + 0.01);
                gain.gain.linearRampToValueAtTime(vel * 0.15, eventTime + 0.1);
                gain.gain.linearRampToValueAtTime(vel * 0.1, eventTime + 0.2);
                gain.gain.linearRampToValueAtTime(0, eventTime + 0.3);
                
                osc.connect(gain);
                gain.connect(audioContext.destination);
                
                osc.start(eventTime);
                osc.stop(eventTime + 0.35);
            });
            
            log('Scheduled ' + filtered.length + ' notes');
            return true;
        }
    };
    
    async function playMIDI(midiUrl, name) {
        log('playMIDI: ' + name);
        
        try {
            const response = await fetch(midiUrl);
            if (!response.ok) throw new Error('Fetch failed');
            const arrayBuffer = await response.arrayBuffer();
            const midiData = new Uint8Array(arrayBuffer);
            
            log('Parsing MIDI...');
            const events = MIDI.parseMIDI(midiData);
            
            if (!events || events.length === 0) {
                log('No events parsed');
                return false;
            }
            
            log('Playing ' + events.length + ' events');
            return MIDI.playEvents(events, name);
            
        } catch (e) {
            log('Error: ' + e.message);
            return false;
        }
    }
    
    function renderAudioList(files) {
        const list = document.getElementById('audioList');
        if (!list) return;
        
        let html = '<div style="color:var(--accent);padding:10px;font-size:11px;">';
        html += 'Audio files from source (MIDI format):</div>';
        
        if (!files || files.length === 0) {
            html += '<div style="padding:10px;color:var(--text-dim);">No MIDI files found</div>';
        } else {
            files.forEach((af) => {
                const safeName = af.name.replace(/\./g, '_');
                html += '<div style="padding:12px;margin:5px 0;background:var(--bg-dark);border-radius:4px;">';
                html += '<div style="color:var(--accent);font-weight:bold;font-size:12px;margin-bottom:8px;">' + af.name + '</div>';
                html += '<div style="display:flex;gap:8px;">';
                html += '<button type="button" id="btn_play_' + safeName + '" style="background:var(--accent);color:#000;padding:8px 16px;cursor:pointer;border:none;border-radius:4px;">Play</button>';
                html += '<a href="' + af.url + '" download="' + af.name + '" style="background:#444;color:#fff;padding:8px 16px;text-decoration:none;border-radius:4px;">Download</a>';
                html += '</div></div>';
            });
        }
        
        html += '<div style=\"padding:15px;margin-top:10px;background:var(--bg-dark);border-radius:4px;font-size:10px;color:var(--text-dim);\">';
        html += 'Note: Click Play to play MIDI via Web Audio. Download for full quality.</div>';
        
        list.innerHTML = html;
        
        // Attach click handlers
        if (files) {
            files.forEach((af) => {
                const safeName = af.name.replace(/\./g, '_');
                const btn = document.getElementById('btn_play_' + safeName);
                if (btn) {
                    btn.onclick = function() {
                        playMIDI(af.url, af.name);
                    };
                }
            });
        }
    }
    
    return {
        playMIDI: playMIDI,
        renderAudioList: renderAudioList
    };
})();
