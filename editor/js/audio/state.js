/**
 * Audio Module - State Management
 * 
 * Centralized state for audio playback.
 */

const AudioState = (function() {
    'use strict';

    // Audio engines
    let toneSynth = null;
    let audioContext = null;

    // Playback state
    let currentEngine = null;
    let isPlaying = false;
    let isPaused = false;
    let preferredEngine = 'tone';

    // Playlist & Playback tracking
    let playlist = [];
    let currentTrackIndex = -1;
    let activeSources = [];
    let playbackStartTime = 0;
    let pausedAt = 0;
    let totalDuration = 0;
    let playbackSpeed = 1.0;

    // Progress tracking
    let progressInterval = null;

    return {
        // Engines
        getToneSynth: () => toneSynth,
        setToneSynth: (val) => { toneSynth = val; },
        getAudioContext: () => audioContext,
        setAudioContext: (val) => { audioContext = val; },

        // State
        getCurrentEngine: () => currentEngine,
        setCurrentEngine: (val) => { currentEngine = val; },
        isPlayingState: () => isPlaying,
        setPlaying: (val) => { isPlaying = val; },
        isPausedState: () => isPaused,
        setPaused: (val) => { isPaused = val; },
        getPreferredEngine: () => preferredEngine,
        setPreferredEngine: (val) => { preferredEngine = val; },

        // Playlist
        getPlaylist: () => playlist,
        setPlaylist: (val) => { playlist = val; },
        getCurrentTrackIndex: () => currentTrackIndex,
        setCurrentTrackIndex: (val) => { currentTrackIndex = val; },

        // Playback tracking
        getActiveSources: () => activeSources,
        setActiveSources: (val) => { activeSources = val; },
        getPlaybackStartTime: () => playbackStartTime,
        setPlaybackStartTime: (val) => { playbackStartTime = val; },
        getPausedAt: () => pausedAt,
        setPausedAt: (val) => { pausedAt = val; },
        getTotalDuration: () => totalDuration,
        setTotalDuration: (val) => { totalDuration = val; },
        getPlaybackSpeed: () => playbackSpeed,
        setPlaybackSpeed: (val) => { playbackSpeed = val; },

        // Progress
        getProgressInterval: () => progressInterval,
        setProgressInterval: (val) => { progressInterval = val; }
    };
})();

// Export to window
window.AudioState = AudioState;
