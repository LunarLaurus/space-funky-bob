/**
 * Toolbar UI for Space Funky B.O.B. Level Editor
 * 
 * Handles toolbar button clicks and tool selection.
 * Refactored from app.js (1186 lines → 180 lines)
 */

(function() {
    'use strict';
    
    // Toolbar state
    let currentTool = 'pencil';
    let isErasing = false;
    
    // Tool definitions
    const tools = {
        pencil: { icon: '✏️', description: 'Draw tiles' },
        eraser: { icon: '🧹', description: 'Erase tiles' },
        fill: { icon: '🪣', description: 'Fill area' },
        select: { icon: '👆', description: 'Select tiles' },
        picker: { icon: '💉', description: 'Pick tile' }
    };
    
    /**
     * Initialize toolbar event handlers
     */
    function initToolbar() {
        // Tool buttons
        document.querySelectorAll('[data-tool]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tool = e.target.dataset.tool;
                selectTool(tool);
            });
        });
        
        // Action buttons
        document.getElementById('btn-undo')?.addEventListener('click', undo);
        document.getElementById('btn-redo')?.addEventListener('click', redo);
        document.getElementById('btn-save')?.addEventListener('click', saveLevel);
        document.getElementById('btn-export')?.addEventListener('click', exportLevel);
        document.getElementById('btn-clear')?.addEventListener('click', clearLevel);
        
        // Toggle buttons
        document.getElementById('btn-grid')?.addEventListener('click', toggleGrid);
        document.getElementById('btn-snap')?.addEventListener('click', toggleSnap);
        
        updateToolbarUI();
    }
    
    /**
     * Select current tool
     * @param {string} tool - Tool name
     */
    function selectTool(tool) {
        if (!tools[tool]) {
            console.warn('Unknown tool:', tool);
            return;
        }
        
        currentTool = tool;
        isErasing = (tool === 'eraser');
        
        // Update UI
        document.querySelectorAll('[data-tool]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tool === tool);
        });
        
        // Emit tool change event
        window.dispatchEvent(new CustomEvent('toolchange', {
            detail: { tool, isErasing }
        }));
    }
    
    /**
     * Get current tool
     * @returns {string} Current tool name
     */
    function getCurrentTool() {
        return currentTool;
    }
    
    /**
     * Check if erasing
     * @returns {boolean} Is erasing mode
     */
    function isErasingMode() {
        return isErasing;
    }
    
    /**
     * Undo action
     */
    function undo() {
        if (window.History) {
            const state = window.History.undo();
            if (state && window.LevelData) {
                window.LevelData.loadLevel(state.levelData);
                window.dispatchEvent(new CustomEvent('levelchange'));
            }
        }
    }
    
    /**
     * Redo action
     */
    function redo() {
        if (window.History) {
            const state = window.History.redo();
            if (state && window.LevelData) {
                window.LevelData.loadLevel(state.levelData);
                window.dispatchEvent(new CustomEvent('levelchange'));
            }
        }
    }
    
    /**
     * Save level
     */
    function saveLevel() {
        if (window.API && window.LevelData) {
            const data = window.LevelData.getExportData();
            window.API.exportLevel(data)
                .then(result => {
                    if (result.success) {
                        Logger.log('Level saved successfully');
                    } else {
                        Logger.error('Save failed:', result.error);
                    }
                });
        }
    }
    
    /**
     * Export level
     */
    function exportLevel() {
        if (window.LevelData) {
            const data = window.LevelData.getExportData();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `level_${data.map_number}.json`;
            a.click();
            URL.revokeObjectURL(url);
        }
    }
    
    /**
     * Clear level
     */
    function clearLevel() {
        if (confirm('Clear all tiles?')) {
            if (window.LevelData) {
                window.LevelData.clearLevel();
                window.dispatchEvent(new CustomEvent('levelchange'));
            }
        }
    }
    
    /**
     * Toggle grid display
     */
    function toggleGrid() {
        const btn = document.getElementById('btn-grid');
        if (btn) {
            const show = !btn.classList.contains('active');
            btn.classList.toggle('active', show);
            
            if (window.AppState) {
                window.AppState.setState('showGrid', show);
            }
        }
    }
    
    /**
     * Toggle snap to grid
     */
    function toggleSnap() {
        const btn = document.getElementById('btn-snap');
        if (btn) {
            const snap = !btn.classList.contains('active');
            btn.classList.toggle('active', snap);
            
            if (window.AppState) {
                window.AppState.setState('snapToGrid', snap);
            }
        }
    }
    
    /**
     * Update toolbar UI based on state
     */
    function updateToolbarUI() {
        if (window.AppState) {
            const state = window.AppState.getState();
            
            const gridBtn = document.getElementById('btn-grid');
            const snapBtn = document.getElementById('btn-snap');
            
            if (gridBtn) gridBtn.classList.toggle('active', state.showGrid);
            if (snapBtn) snapBtn.classList.toggle('active', state.snapToGrid);
        }
    }
    
    // Export to window
    window.Toolbar = {
        initToolbar,
        selectTool,
        getCurrentTool,
        isErasingMode,
        updateToolbarUI
    };
    
})();
