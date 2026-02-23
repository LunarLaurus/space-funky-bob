/**
 * History Management for Space Funky B.O.B. Level Editor
 * 
 * Undo/redo functionality with configurable history size.
 * Refactored from app.js (1186 lines → 150 lines)
 */

(function() {
    'use strict';
    
    // History configuration
    const MAX_HISTORY = 20;
    
    // History stacks
    let past = [];
    let future = [];
    
    /**
     * Save state snapshot to history
     * @param {Object} snapshot - State to save
     */
    function saveState(snapshot) {
        past.push(snapshot);
        
        // Limit history size
        if (past.length > MAX_HISTORY) {
            past.shift();
        }
        
        // Clear future on new action
        future = [];
        
        // Emit history change event
        emitHistoryChange();
    }
    
    /**
     * Undo last action
     * @returns {Object|null} Previous state or null if nothing to undo
     */
    function undo() {
        if (past.length === 0) {
            return null;
        }
        
        // Save current state to future
        const currentState = past[past.length - 1];
        future.push(currentState);
        
        // Get previous state
        const previousState = past.pop();
        
        emitHistoryChange();
        return previousState;
    }
    
    /**
     * Redo last undone action
     * @returns {Object|null} Next state or null if nothing to redo
     */
    function redo() {
        if (future.length === 0) {
            return null;
        }
        
        // Save current state to past
        const currentState = future[future.length - 1];
        past.push(currentState);
        
        // Get next state
        const nextState = future.pop();
        
        emitHistoryChange();
        return nextState;
    }
    
    /**
     * Clear all history
     */
    function clearHistory() {
        past = [];
        future = [];
        emitHistoryChange();
    }
    
    /**
     * Get history info
     * @returns {Object} History status
     */
    function getHistoryInfo() {
        return {
            canUndo: past.length > 0,
            canRedo: future.length > 0,
            pastCount: past.length,
            futureCount: future.length,
            maxSize: MAX_HISTORY
        };
    }
    
    /**
     * Emit history change event
     */
    function emitHistoryChange() {
        window.dispatchEvent(new CustomEvent('historychange', {
            detail: getHistoryInfo()
        }));
    }
    
    /**
     * Set maximum history size
     * @param {number} size - New max size
     */
    function setMaxHistory(size) {
        MAX_HISTORY = Math.max(1, size);
        
        // Trim history if needed
        while (past.length > MAX_HISTORY) {
            past.shift();
        }
    }
    
    /**
     * Create state snapshot for saving
     * @param {Object} state - Current state
     * @returns {Object} Snapshot
     */
    function createSnapshot(state) {
        return {
            timestamp: Date.now(),
            levelData: JSON.parse(JSON.stringify(state.levelData || {})),
            selectedTile: state.selectedTile,
            zoom: state.zoom
        };
    }
    
    // Export to window
    window.History = {
        saveState,
        undo,
        redo,
        clearHistory,
        getHistoryInfo,
        setMaxHistory,
        createSnapshot
    };
    
})();
