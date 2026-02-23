/**
 * App State Management for Space Funky B.O.B. Level Editor
 * 
 * Centralized state management for editor application.
 * Refactored from app.js (1186 lines → 200 lines)
 */

(function() {
    'use strict';
    
    // Application state
    const state = {
        currentLevel: null,
        levelData: null,
        selectedTile: 0,
        zoom: 1,
        isDrawing: false,
        showGrid: false,
        snapToGrid: false,
        activeLayer: 'foreground'
    };
    
    // History for undo/redo
    const history = {
        past: [],
        future: [],
        maxSize: 20
    };
    
    /**
     * Get current state value
     * @param {string} key - State key
     * @returns {*} State value
     */
    function getState(key) {
        if (key === undefined) {
            return { ...state };
        }
        return state[key];
    }
    
    /**
     * Set state value and trigger change event
     * @param {string} key - State key
     * @param {*} value - New value
     */
    function setState(key, value) {
        const oldValue = state[key];
        state[key] = value;
        
        // Trigger state change event
        window.dispatchEvent(new CustomEvent('statechange', {
            detail: { key, oldValue, value }
        }));
    }
    
    /**
     * Set multiple state values at once
     * @param {Object} updates - Key-value pairs to update
     */
    function setMultipleState(updates) {
        Object.keys(updates).forEach(key => {
            state[key] = updates[key];
        });
        
        window.dispatchEvent(new CustomEvent('statechange', {
            detail: { updates }
        }));
    }
    
    /**
     * Push state to history for undo
     * @param {Object} snapshot - State snapshot to save
     */
    function pushHistory(snapshot) {
        history.past.push(snapshot);
        
        // Limit history size
        if (history.past.length > history.maxSize) {
            history.past.shift();
        }
        
        // Clear future on new action
        history.future = [];
    }
    
    /**
     * Undo last action
     * @returns {Object|null} Previous state or null
     */
    function undo() {
        if (history.past.length === 0) {
            return null;
        }
        
        const currentSnapshot = { levelData: state.levelData };
        history.future.push(currentSnapshot);
        
        const previousState = history.past.pop();
        state.levelData = previousState.levelData;
        
        window.dispatchEvent(new CustomEvent('statechange', {
            detail: { key: 'levelData', value: previousState.levelData }
        }));
        
        return previousState;
    }
    
    /**
     * Redo last undone action
     * @returns {Object|null} Next state or null
     */
    function redo() {
        if (history.future.length === 0) {
            return null;
        }
        
        const currentSnapshot = { levelData: state.levelData };
        history.past.push(currentSnapshot);
        
        const nextState = history.future.pop();
        state.levelData = nextState.levelData;
        
        window.dispatchEvent(new CustomEvent('statechange', {
            detail: { key: 'levelData', value: nextState.levelData }
        }));
        
        return nextState;
    }
    
    /**
     * Get history info
     * @returns {Object} History info
     */
    function getHistoryInfo() {
        return {
            canUndo: history.past.length > 0,
            canRedo: history.future.length > 0,
            pastCount: history.past.length,
            futureCount: history.future.length
        };
    }
    
    /**
     * Reset all state to defaults
     */
    function resetState() {
        state.currentLevel = null;
        state.levelData = null;
        state.selectedTile = 0;
        state.zoom = 1;
        state.isDrawing = false;
        state.showGrid = false;
        state.snapToGrid = false;
        state.activeLayer = 'foreground';
        
        history.past = [];
        history.future = [];
        
        window.dispatchEvent(new CustomEvent('statechange', {
            detail: { reset: true }
        }));
    }
    
    // Export to window
    window.AppState = {
        getState,
        setState,
        setMultipleState,
        pushHistory,
        undo,
        redo,
        getHistoryInfo,
        resetState
    };
    
})();
