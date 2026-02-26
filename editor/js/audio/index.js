/**
 * Audio Module - Main Entry Point
 * 
 * Loads all sub-modules and provides unified API.
 * 
 * Module Structure:
 * - state.js: Centralized state management
 * - engine.js: Tone.js and native Web Audio initialization
 * - playback.js: MIDI parsing and playback
 * - playlist.js: Playlist management and navigation
 * - ui.js: UI rendering and updates
 * - player.js: Main playback orchestration
 */

// Load order matters - dependencies first
document.write('<script src="js/audio/state.js"><\/script>');
document.write('<script src="js/audio/engine.js"><\/script>');
document.write('<script src="js/audio/playback.js"><\/script>');
document.write('<script src="js/audio/playlist.js"><\/script>');
document.write('<script src="js/audio/ui.js"><\/script>');
document.write('<script src="js/audio/player.js"><\/script>');

// Main Audio API (backward compatibility)
window.Audio = {
    // Playback control
    playMIDI: (url, name, pos) => {
        console.log('[Audio] Audio.playMIDI wrapper called -> AudioPlayer.playMIDI');
        return window.AudioPlayer.playMIDI(url, name, pos);
    },
    playTrack: (index) => {
        console.log('[Audio] Audio.playTrack(' + index + ')');
        return window.AudioPlaylist.playTrack(index);
    },
    playNext: () => window.AudioPlaylist.playNext(),
    playPrevious: () => window.AudioPlaylist.playPrevious(),
    pause: () => window.AudioPlayer.pause(),
    resume: () => window.AudioPlayer.resume(),
    stop: () => {
        console.log('[Audio] Audio.stop() called');
        return window.AudioPlayer.stop();
    },

    // Playlist management
    setPlaylist: (files) => window.AudioPlaylist.setPlaylist(files),
    getPlaylist: () => window.AudioPlaylist.getPlaylist(),
    getCurrentTrack: () => window.AudioPlaylist.getCurrentTrack(),

    // Playback speed
    setPlaybackSpeed: (speed) => {
        console.log('[Audio] Audio.setPlaybackSpeed(' + speed + ')');
        return window.AudioPlaylist.setPlaybackSpeed(speed);
    },
    getPlaybackSpeed: () => window.AudioPlaylist.getPlaybackSpeed(),

    // Settings
    setPreferredEngine: (engine) => window.AudioState.setPreferredEngine(engine),
    getEngineStatus: () => ({
        current: window.AudioState.getCurrentEngine(),
        preferred: window.AudioState.getPreferredEngine(),
        toneAvailable: !!window.Tone,
        nativeAvailable: true
    }),

    // UI
    renderAudioList: (files) => window.AudioUI.renderAudioList(files)
};

console.log('[Audio] Module loaded - split into 6 sub-modules');
