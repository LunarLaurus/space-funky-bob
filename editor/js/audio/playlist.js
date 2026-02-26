/**
 * Audio Module - Playlist Management
 * 
 * Handles playlist operations and track navigation.
 */

const AudioPlaylist = (function() {
    'use strict';

    function log(msg) {
        console.log('[Audio] ' + msg);
    }

    /**
     * Set playlist from file list
     */
    function setPlaylist(files) {
        const state = window.AudioState;
        const playlist = files.map((f, i) => ({
            index: i,
            name: f.filename || f.name || 'Unknown',
            url: f.path || f.url || '#',
            duration: 0
        }));
        state.setPlaylist(playlist);
        state.setCurrentTrackIndex(-1);
        log('Playlist set with ' + playlist.length + ' tracks');
    }

    /**
     * Get current track info
     */
    function getCurrentTrack() {
        const state = window.AudioState;
        const index = state.getCurrentTrackIndex();
        const playlist = state.getPlaylist();

        if (index < 0 || index >= playlist.length) {
            return null;
        }

        const track = playlist[index];
        return {
            ...track,
            isPlaying: state.isPlayingState(),
            isPaused: state.isPausedState(),
            position: state.isPausedState() ? 
                state.getPausedAt() : 
                (Tone.now() - state.getPlaybackStartTime()) * 1000
        };
    }

    /**
     * Play specific track
     */
    function playTrack(index, startPosition = 0) {
        const state = window.AudioState;
        const playlist = state.getPlaylist();

        if (index < 0 || index >= playlist.length) return;

        state.setCurrentTrackIndex(index);
        const track = playlist[index];
        
        // Call main playMIDI function
        if (window.AudioPlayer && window.AudioPlayer.playMIDI) {
            window.AudioPlayer.playMIDI(track.url, track.name, startPosition);
        }
    }

    /**
     * Play next track
     */
    function playNext() {
        const state = window.AudioState;
        const playlist = state.getPlaylist();
        if (playlist.length === 0) return;
        
        const nextIndex = (state.getCurrentTrackIndex() + 1) % playlist.length;
        playTrack(nextIndex);
    }

    /**
     * Play previous track
     */
    function playPrevious() {
        const state = window.AudioState;
        const playlist = state.getPlaylist();
        if (playlist.length === 0) return;
        
        const prevIndex = state.getCurrentTrackIndex() <= 0 ? 
            playlist.length - 1 : 
            state.getCurrentTrackIndex() - 1;
        playTrack(prevIndex);
    }

    /**
     * Set playback speed
     */
    function setPlaybackSpeed(speed) {
        const state = window.AudioState;

        if (speed < 0.25 || speed > 4.0) {
            log('Invalid speed: ' + speed + ' (must be 0.25-4.0)');
            return false;
        }

        const wasPlaying = state.isPlayingState();
        const wasPaused = state.isPausedState();
        const currentPosition = state.isPausedState() ? state.getPausedAt() : 
            (state.isPlayingState() ? (Tone.now() - state.getPlaybackStartTime()) * 1000 : 0);
        const currentTrackIndex = state.getCurrentTrackIndex();
        const playlist = state.getPlaylist();

        state.setPlaybackSpeed(speed);

        log('Playback speed set to ' + (speed * 100) + '%');

        // If currently playing or paused, restart at new speed from current position
        if ((wasPlaying || wasPaused) && currentTrackIndex >= 0 && playlist.length > 0) {
            const track = playlist[currentTrackIndex];
            log('Restarting playback at ' + speed + 'x speed from ' + Math.round(currentPosition) + 'ms');
            
            // Stop current playback (without resetting track index)
            if (window.Tone && Tone.Transport) {
                Tone.Transport.cancel();
            }
            state.getActiveSources().forEach(src => {
                try {
                    if (src.osc1) src.osc1.stop();
                    if (src.osc2) src.osc2.stop();
                } catch (e) {}
            });
            state.setActiveSources([]);
            state.setPlaying(false);
            
            // Small delay to ensure stop completes
            setTimeout(() => {
                // Restart at new speed
                if (window.AudioPlayer && window.AudioPlayer.playMIDI) {
                    window.AudioPlayer.playMIDI(track.url, track.name, currentPosition);
                }
            }, 50);
        }

        return true;
    }

    /**
     * Get current playback position
     */
    function getCurrentPosition() {
        const state = window.AudioState;
        
        if (state.isPausedState()) return state.getPausedAt();
        if (!state.isPlayingState()) return 0;
        
        return (Tone.now() - state.getPlaybackStartTime()) * 1000;
    }

    return {
        setPlaylist: setPlaylist,
        getCurrentTrack: getCurrentTrack,
        playTrack: playTrack,
        playNext: playNext,
        playPrevious: playPrevious,
        setPlaybackSpeed: setPlaybackSpeed,
        getCurrentPosition: getCurrentPosition
    };
})();

// Export to window
window.AudioPlaylist = AudioPlaylist;
