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
        
        state.setPlaybackSpeed(speed);
        
        if (window.Tone && Tone.Transport) {
            Tone.Transport.playbackRate = speed;
        }
        
        log('Playback speed set to ' + (speed * 100) + '%');
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
