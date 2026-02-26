/**
 * Audio Module - UI Management
 * 
 * Handles player UI rendering and updates.
 */

const AudioUI = (function() {
    'use strict';

    function log(msg) {
        console.log('[Audio] ' + msg);
    }

    function error(msg) {
        console.error('[Audio] ERROR: ' + msg);
    }

    /**
     * Update player UI
     */
    function updatePlayerUI() {
        const state = window.AudioState;

        const playBtn = document.getElementById('btn-play-pause');
        const nowPlaying = document.getElementById('now-playing');
        const speedDisplay = document.getElementById('speed-display');

        log('updatePlayerUI called - isPlaying:' + state.isPlayingState() + ', currentTrack:' + state.getCurrentTrackIndex());

        if (playBtn) {
            if (state.isPausedState()) {
                playBtn.textContent = '▶';
                playBtn.title = 'Resume (Space)';
                playBtn.style.background = 'var(--accent)';
            } else if (state.isPlayingState()) {
                playBtn.textContent = '⏸';
                playBtn.title = 'Pause (Space)';
                playBtn.style.background = '#ff9900';
            } else {
                playBtn.textContent = '▶';
                playBtn.title = 'Play (Space)';
                playBtn.style.background = 'var(--accent)';
            }
        } else {
            log('playBtn not found');
        }

        if (nowPlaying) {
            const track = window.AudioPlaylist.getCurrentTrack();
            log('getCurrentTrack returned: ' + JSON.stringify(track));
            nowPlaying.textContent = track ? track.name : 'None';
        } else {
            log('nowPlaying element not found');
        }

        if (speedDisplay) {
            speedDisplay.textContent = state.getPlaybackSpeed().toFixed(2) + 'x';
        } else {
            log('speedDisplay element not found');
        }

        // Update playlist highlighting
        const playlist = state.getPlaylist();
        if (playlist) {
            playlist.forEach((_, i) => {
                const el = document.getElementById('track-' + i);
                if (el) {
                    if (i === state.getCurrentTrackIndex()) {
                        el.style.background = 'var(--bg-toolbar)';
                        el.style.border = '1px solid var(--accent)';
                        el.classList.add('active');
                        const indicator = el.querySelector('.play-indicator');
                        if (indicator) {
                            indicator.style.opacity = '1';
                            if (state.isPausedState()) {
                                indicator.textContent = '⏸ Paused';
                                indicator.style.color = '#ff9900';
                            } else if (state.isPlayingState()) {
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
    }

    /**
     * Initialize progress UI
     */
    function initProgressUI() {
        window.AudioUpdateProgress = function(position, total, progress) {
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
    }

    /**
     * Initialize button handlers
     */
    function initButtonHandlers() {
        let isPlayingToggle = false;

        document.getElementById('btn-play-pause')?.addEventListener('click', () => {
            if (isPlayingToggle) return;
            isPlayingToggle = true;

            const state = window.AudioState;

            if (state.isPlayingState()) {
                window.AudioPlayer.pause();
            } else if (state.isPausedState()) {
                window.AudioPlayer.resume();
            } else {
                if (state.getCurrentTrackIndex() >= 0) {
                    window.AudioPlaylist.playTrack(state.getCurrentTrackIndex());
                } else if (state.getPlaylist().length > 0) {
                    window.AudioPlaylist.playTrack(0);
                }
            }

            setTimeout(() => { isPlayingToggle = false; }, 100);
            updatePlayerUI();
        });

        document.getElementById('btn-stop')?.addEventListener('click', () => {
            window.AudioPlayer.stop();
            updatePlayerUI();
        });

        document.getElementById('btn-prev')?.addEventListener('click', () => {
            window.AudioPlaylist.playPrevious();
            updatePlayerUI();
        });

        document.getElementById('btn-next')?.addEventListener('click', () => {
            window.AudioPlaylist.playNext();
            updatePlayerUI();
        });

        // Engine toggle
        const toggleBtn = document.getElementById('btn-engine-toggle');
        if (toggleBtn) {
            toggleBtn.onclick = function(e) {
                e.stopPropagation();
                const newEngine = state.getPreferredEngine() === 'tone' ? 'native' : 'tone';
                state.setPreferredEngine(newEngine);
                toggleBtn.textContent = 'Engine: ' + (newEngine === 'tone' ? 'Tone.js' : 'Native');
                toggleBtn.style.background = newEngine === 'tone' ? 'var(--accent)' : '#444';
                toggleBtn.style.color = newEngine === 'tone' ? '#000' : '#fff';
                log('Engine switched to: ' + newEngine);
            };
        }

        // Speed control
        const speedDownBtn = document.getElementById('btn-speed-down');
        const speedUpBtn = document.getElementById('btn-speed-up');

        log('Speed buttons found: down=' + !!speedDownBtn + ', up=' + !!speedUpBtn);

        if (speedDownBtn) {
            speedDownBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                log('Speed down clicked, current: ' + state.getPlaybackSpeed());
                const newSpeed = Math.max(0.25, state.getPlaybackSpeed() - 0.25);
                window.AudioPlaylist.setPlaybackSpeed(newSpeed);
                updatePlayerUI();
            });
        } else {
            log('btn-speed-down not found');
        }

        if (speedUpBtn) {
            speedUpBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                log('Speed up clicked, current: ' + state.getPlaybackSpeed());
                const newSpeed = Math.min(4.0, state.getPlaybackSpeed() + 0.25);
                window.AudioPlaylist.setPlaybackSpeed(newSpeed);
                updatePlayerUI();
            });
        } else {
            log('btn-speed-up not found');
        }
    }

    /**
     * Render playlist UI
     */
    function renderAudioList(files) {
        const list = document.getElementById('audioList');
        if (!list) {
            error('audioList element not found!');
            return;
        }
        log('renderAudioList called with ' + (files ? files.length : 0) + ' files');

        window.AudioPlaylist.setPlaylist(files);

        let html = '<div style="color:var(--accent);padding:12px;font-size:13px;font-weight:bold;border-bottom:1px solid var(--border);">';
        html += '♫ B.O.B. Soundtrack Jukebox</div>';

        html += '<div style="padding:15px;margin:12px;background:linear-gradient(135deg,var(--bg-toolbar) 0%,var(--bg-panel) 100%);border:1px solid var(--border);border-radius:6px;">';
        html += '<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">';

        html += '<div style="display:flex;gap:6px;">';
        html += '<button type="button" id="btn-prev" title="Previous (←)" style="background:#3a3a4e;color:#fff;padding:10px 14px;cursor:pointer;border:none;border-radius:4px;font-size:14px;transition:all 0.2s;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">⏮</button>';
        html += '<button type="button" id="btn-play-pause" title="Play/Pause (Space)" style="background:var(--accent);color:#000;padding:10px 18px;cursor:pointer;border:none;border-radius:4px;font-size:16px;font-weight:bold;transition:all 0.2s;" onmouseover="this.style.background=\'#00ff99\'" onmouseout="this.style.background=\'var(--accent)\'">▶</button>';
        html += '<button type="button" id="btn-stop" title="Stop" style="background:#3a3a4e;color:#fff;padding:10px 14px;cursor:pointer;border:none;border-radius:4px;font-size:14px;transition:all 0.2s;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">⏹</button>';
        html += '<button type="button" id="btn-next" title="Next (→)" style="background:#3a3a4e;color:#fff;padding:10px 14px;cursor:pointer;border:none;border-radius:4px;font-size:14px;transition:all 0.2s;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">⏭</button>';
        html += '</div>';

        html += '<div style="flex:1;min-width:220px;margin-left:10px;">';
        html += '<div style="display:flex;align-items:center;gap:10px;">';
        html += '<div style="flex:1;min-width:0;">';
        html += '<div style="font-size:9px;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;">Now Playing</div>';
        html += '<div id="now-playing" style="font-size:12px;color:var(--accent);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">None</div>';
        html += '</div>';
        html += '<div style="text-align:right;min-width:80px;">';
        html += '<div id="time-display" style="font-size:11px;color:var(--text);font-family:monospace;">0:00 / 0:00</div>';
        html += '<div style="font-size:9px;color:var(--text-dim);margin-top:2px;" id="speed-display">1.00x</div>';
        html += '</div>';
        html += '</div>';
        html += '</div>';

        html += '<div style="display:flex;gap:4px;align-items:center;">';
        html += '<button type="button" id="btn-speed-down" title="Slower (-)" style="background:#3a3a4e;color:#fff;width:24px;height:24px;cursor:pointer;border:none;border-radius:4px;font-size:12px;font-weight:bold;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">-</button>';
        html += '<button type="button" id="btn-engine-toggle" title="Switch audio engine" style="background:#3a3a4e;color:#fff;padding:6px 10px;cursor:pointer;border:none;border-radius:4px;font-size:9px;text-transform:uppercase;letter-spacing:0.5px;transition:all 0.2s;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">Engine: Tone.js</button>';
        html += '<button type="button" id="btn-speed-up" title="Faster (+)" style="background:#3a3a4e;color:#fff;width:24px;height:24px;cursor:pointer;border:none;border-radius:4px;font-size:12px;font-weight:bold;" onmouseover="this.style.background=\'#4a4a5e\'" onmouseout="this.style.background=\'#3a3a4e\'">+</button>';
        html += '</div>';
        html += '</div>';

        html += '<div style="margin-top:12px;height:3px;background:#2a2a3e;border-radius:2px;overflow:hidden;">';
        html += '<div id="progress-bar" style="width:0%;height:100%;background:linear-gradient(90deg,var(--accent) 0%,#00ff99 100%);transition:width 0.1s;"></div>';
        html += '</div>';
        html += '</div>';

        html += '<div style="padding:8px 12px;font-size:10px;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid var(--border);">';
        html += 'Playlist (' + (files ? files.length : 0) + ' tracks)</div>';

        html += '<div style="max-height:350px;overflow-y:auto;">';
        if (!files || files.length === 0) {
            html += '<div style="padding:40px;color:var(--text-dim);text-align:center;font-size:12px;">No MIDI files found</div>';
        } else {
            files.forEach((af, index) => {
                const fileName = af.filename || af.name || 'Unknown';
                html += '<div id="track-' + index + '" style="padding:10px 12px;margin:2px 0;background:var(--bg-dark);border-radius:4px;cursor:pointer;transition:all 0.2s;display:flex;align-items:center;gap:12px;border:1px solid transparent;" onmouseover="this.style.background=\'var(--bg-toolbar)\'" onmouseout="if(!this.classList.contains(\'active\'))this.style.background=\'var(--bg-dark)\'" onclick="window.AudioPlaylist.playTrack(' + index + ')">';
                html += '<div style="width:28px;height:28px;background:linear-gradient(135deg,#2a2a3e 0%,#1a1a2e 100%);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:11px;color:var(--accent);font-weight:bold;">' + (index + 1) + '</div>';
                html += '<div style="flex:1;min-width:0;">';
                html += '<div style="color:var(--text);font-size:12px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + fileName + '</div>';
                html += '</div>';
                html += '<div style="color:var(--accent);font-size:11px;opacity:0;transition:opacity 0.2s;" class="play-indicator">▶</div>';
                html += '</div>';
            });
        }
        html += '</div>';

        html += '<div style="padding:10px 12px;margin-top:12px;background:var(--bg-dark);border-radius:4px;font-size:9px;color:var(--text-dim);border-top:1px solid var(--border);">';
        html += '<strong style="color:var(--accent);">Tone.js:</strong> High-quality synthesis | ';
        html += '<strong style="color:var(--accent);">Native:</strong> Basic synthesis';
        html += '</div>';

        list.innerHTML = html;
        log('HTML set to audioList, length: ' + html.length);

        initProgressUI();
        initButtonHandlers();

        log('Calling initial updatePlayerUI');
        updatePlayerUI();

        log('Audio player ready - waiting for user interaction');
    }

    return {
        updatePlayerUI: updatePlayerUI,
        initProgressUI: initProgressUI,
        initButtonHandlers: initButtonHandlers,
        renderAudioList: renderAudioList
    };
})();

// Export to window
window.AudioUI = AudioUI;
