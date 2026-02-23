/**
 * Keyboard Events for Space Funky B.O.B. Level Editor
 * 
 * Handles keyboard shortcuts.
 * Refactored from app.js (1186 lines → 150 lines)
 */

(function() {
    'use strict';
    
    // Keyboard shortcuts
    const SHORTCUTS = {
        'Ctrl+S': 'save',
        'Ctrl+Z': 'undo',
        'Ctrl+Y': 'redo',
        'Ctrl+G': 'toggleGrid',
        'Ctrl+Shift+G': 'toggleSnap',
        '+': 'zoomIn',
        '-': 'zoomOut',
        '0': 'selectTile0',
        '1': 'selectTile1',
        '2': 'selectTile2',
        '3': 'selectTile3',
        '4': 'selectTile4',
        '5': 'selectTile5',
        '6': 'selectTile6',
        '7': 'selectTile7',
        '8': 'selectTile8',
        '9': 'selectTile9',
        'R': 'rotateTile',
        'G': 'toggleGrid',
        'S': 'toggleSnap'
    };
    
    /**
     * Initialize keyboard event handlers
     */
    function initKeyboardEvents() {
        document.addEventListener('keydown', onKeyDown);
    }
    
    /**
     * Key down handler
     * @param {KeyboardEvent} e - Keyboard event
     */
    function onKeyDown(e) {
        // Build shortcut key
        let shortcut = '';
        if (e.ctrlKey || e.metaKey) shortcut += 'Ctrl+';
        if (e.shiftKey) shortcut += 'Shift+';
        shortcut += e.key.toUpperCase();
        
        // Check for matching shortcut
        const action = SHORTCUTS[shortcut];
        if (action) {
            e.preventDefault();
            handleShortcut(action, e);
        }
    }
    
    /**
     * Handle keyboard shortcut
     * @param {string} action - Action name
     * @param {KeyboardEvent} e - Original event
     */
    function handleShortcut(action, e) {
        switch (action) {
            case 'save':
                if (window.Toolbar) window.Toolbar.saveLevel();
                break;
            
            case 'undo':
                if (window.Toolbar) window.Toolbar.undo();
                break;
            
            case 'redo':
                if (window.Toolbar) window.Toolbar.redo();
                break;
            
            case 'toggleGrid':
                if (window.Toolbar) window.Toolbar.toggleGrid();
                break;
            
            case 'toggleSnap':
                if (window.Toolbar) window.Toolbar.toggleSnap();
                break;
            
            case 'zoomIn':
                adjustZoom(0.5);
                break;
            
            case 'zoomOut':
                adjustZoom(-0.5);
                break;
            
            case 'selectTile0':
            case 'selectTile1':
            case 'selectTile2':
            case 'selectTile3':
            case 'selectTile4':
            case 'selectTile5':
            case 'selectTile6':
            case 'selectTile7':
            case 'selectTile8':
            case 'selectTile9':
                selectQuickTile(parseInt(action.slice(-1)));
                break;
            
            case 'rotateTile':
                rotateSelectedTile();
                break;
        }
    }
    
    /**
     * Adjust zoom level
     * @param {number} delta - Zoom change
     */
    function adjustZoom(delta) {
        if (window.AppState) {
            const state = window.AppState.getState();
            const newZoom = Math.max(0.5, Math.min(4, state.zoom + delta));
            window.AppState.setState('zoom', newZoom);
            
            window.dispatchEvent(new CustomEvent('zoomchange', {
                detail: { zoom: newZoom }
            }));
        }
    }
    
    /**
     * Quick tile selection (0-9)
     * @param {number} tileId - Tile ID
     */
    function selectQuickTile(tileId) {
        if (window.AppState) {
            window.AppState.setState('selectedTile', tileId);
            
            window.dispatchEvent(new CustomEvent('tileselect', {
                detail: { tileId }
            }));
        }
    }
    
    /**
     * Rotate selected tile
     */
    function rotateSelectedTile() {
        // Placeholder for tile rotation
        console.log('Rotate tile');
    }
    
    /**
     * Register custom shortcut
     * @param {string} key - Key combination
     * @param {Function} handler - Handler function
     */
    function registerShortcut(key, handler) {
        SHORTCUTS[key] = handler;
    }
    
    // Export to window
    window.KeyboardEvents = {
        initKeyboardEvents,
        handleShortcut,
        adjustZoom,
        selectQuickTile,
        registerShortcut
    };
    
})();
