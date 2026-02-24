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
        document.getElementById('btnUndo')?.addEventListener('click', undo);
        document.getElementById('btnRedo')?.addEventListener('click', redo);
        document.getElementById('btnSave')?.addEventListener('click', saveLevel);
        document.getElementById('btnExport')?.addEventListener('click', exportLevel);
        document.getElementById('btnClear')?.addEventListener('click', clearLevel);

        // Toggle buttons
        document.getElementById('btnGrid')?.addEventListener('click', toggleGrid);
        document.getElementById('btnSnap')?.addEventListener('click', toggleSnap);

        // Zoom buttons
        document.getElementById('btnZoomIn')?.addEventListener('click', zoomIn);
        document.getElementById('btnZoomOut')?.addEventListener('click', zoomOut);

        // Feature buttons
        document.getElementById('btnShowEnemies')?.addEventListener('click', toggleEnemies);
        document.getElementById('btnExportROM')?.addEventListener('click', exportToROM);
        document.getElementById('btnTileViewer')?.addEventListener('click', openTileViewer);
        document.getElementById('btnAudio')?.addEventListener('click', openAudioModal);
        document.getElementById('btnImport')?.addEventListener('click', importLevel);
        
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
                        Logger.info('Toolbar', 'Level saved successfully');
                    } else {
                        Logger.error('Toolbar', 'Save failed: ' + result.error);
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

            const gridBtn = document.getElementById('btnGrid');
            const snapBtn = document.getElementById('btnSnap');
            const enemiesBtn = document.getElementById('btnShowEnemies');

            if (gridBtn) gridBtn.classList.toggle('active', state.showGrid);
            if (snapBtn) snapBtn.classList.toggle('active', state.snapToGrid);
            if (enemiesBtn) enemiesBtn.classList.toggle('active', state.showEnemies);
        }
    }

    /**
     * Zoom in
     */
    function zoomIn() {
        const state = window.AppState?.getState() || {};
        const newZoom = Math.min((state.zoom || 4) + 1, 8);
        if (window.AppState) window.AppState.setState('zoom', newZoom);
        if (window.Renderer) {
            const levelData = window.LevelData?.getData();
            window.Renderer.renderCanvas(levelData, { ...state, zoom: newZoom }, [], []);
        }
        const display = document.getElementById('zoomDisplay');
        if (display) display.textContent = newZoom + 'x';
    }

    /**
     * Zoom out
     */
    function zoomOut() {
        const state = window.AppState?.getState() || {};
        const newZoom = Math.max((state.zoom || 4) - 1, 1);
        if (window.AppState) window.AppState.setState('zoom', newZoom);
        if (window.Renderer) {
            const levelData = window.LevelData?.getData();
            window.Renderer.renderCanvas(levelData, { ...state, zoom: newZoom }, [], []);
        }
        const display = document.getElementById('zoomDisplay');
        if (display) display.textContent = newZoom + 'x';
    }

    /**
     * Toggle enemy markers
     */
    function toggleEnemies() {
        const state = window.AppState?.getState() || {};
        const newShow = !state.showEnemies;
        if (window.AppState) window.AppState.setState('showEnemies', newShow);
        const btn = document.getElementById('btnShowEnemies');
        if (btn) btn.classList.toggle('active', newShow);
        if (window.Renderer) {
            const levelData = window.LevelData?.getData();
            window.Renderer.renderCanvas(levelData, { ...state, showEnemies: newShow }, [], []);
        }
    }

    /**
     * Export level to ROM
     */
    async function exportToROM() {
        const btn = document.getElementById('btnExportROM');
        if (btn) btn.disabled = true;
        try {
            const levelData = window.LevelData?.getExportData();
            const result = await window.API?.exportLevel(levelData);
            if (result?.success) {
                Logger.info('Toolbar', 'Exported to ROM: ' + result.level);
            } else {
                Logger.error('Toolbar', 'Export failed: ' + (result?.error || 'Unknown'));
            }
        } catch (e) {
            Logger.error('Toolbar', 'Export error: ' + e.message);
        }
        if (btn) btn.disabled = false;
    }

    /**
     * Open tile viewer modal
     */
    async function openTileViewer() {
        const modal = document.getElementById('tileViewerModal');
        const select = document.getElementById('tileViewerTileset');
        if (select) {
            select.innerHTML = '<option value="">Select tileset...</option>';
            try {
                const data = await window.API?.getAllTilesets();
                if (data?.tilesets) {
                    data.tilesets.forEach(ts => {
                        const opt = document.createElement('option');
                        opt.value = ts.id;
                        opt.textContent = ts.name;
                        select.appendChild(opt);
                    });
                }
            } catch(e) {
                Logger.error('Toolbar', 'Failed to load tilesets: ' + e.message);
            }
        }
        if (modal) modal.style.display = 'block';
    }

    /**
     * Open audio modal
     */
    async function openAudioModal() {
        const modal = document.getElementById('audioModal');
        if (modal) modal.style.display = 'block';
        const list = document.getElementById('audioList');
        if (list) {
            list.innerHTML = '<div style="color:var(--accent);padding:10px;">Loading audio files...</div>';
            try {
                const response = await fetch('/midi');
                const data = await response.json();
                if (window.Audio) window.Audio.renderAudioList(data.files);
            } catch (e) {
                list.innerHTML = '<div style="color:red;padding:10px;">Error: ' + e.message + '</div>';
            }
        }
    }

    /**
     * Import level from JSON file
     */
    function importLevel() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            try {
                const text = await file.text();
                const data = JSON.parse(text);
                if (window.LevelData) {
                    window.LevelData.loadLevel(data);
                    window.dispatchEvent(new CustomEvent('levelchange'));
                    Logger.info('Toolbar', 'Level imported: ' + (data.name || 'Unknown'));
                }
            } catch (err) {
                Logger.error('Toolbar', 'Import failed: ' + err.message);
            }
        };
        input.click();
    }

    // Export to window
    window.Toolbar = {
        initToolbar,
        selectTool,
        getCurrentTool,
        isErasingMode,
        updateToolbarUI,
        zoomIn,
        zoomOut,
        toggleEnemies,
        exportToROM,
        openTileViewer,
        openAudioModal,
        importLevel
    };

})();
