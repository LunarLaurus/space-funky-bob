/**
 * Space Funky B.O.B. Level Editor - Main Application
 * 
 * Refactored: 1186 lines → 150 lines
 * Architecture: Modular (state/, ui/, events/, features/)
 */

(function() {
    'use strict';
    
    // Configuration
    window.APP_CONFIG = {
        MAP_WIDTH: 80,
        MAP_HEIGHT: 80,
        TILE_SIZE: 8,
        MAX_HISTORY: 20
    };
    
    /**
     * Initialize editor application
     */
    async function initEditor() {
        Logger.log('Initializing B.O.B. Level Editor...');

        // Initialize state management
        if (window.AppState) {
            Logger.log('State management initialized');
        }

        // Initialize level data
        if (window.LevelData) {
            window.LevelData.initLevel(80, 80);
            Logger.log('Level data initialized');
        }

        // Initialize UI modules
        await initUIModules();

        // Initialize event handlers
        initEventHandlers();

        // Initialize features
        initFeatures();

        // Initialize feature navigation
        if (typeof initFeatureNavigation === 'function') {
            initFeatureNavigation();
        }

        // Load default level
        await loadDefaultLevel();

        Logger.log('Editor initialization complete');
    }
    
    /**
     * Initialize UI modules
     */
    async function initUIModules() {
        if (window.Toolbar) {
            window.Toolbar.initToolbar();
            Logger.log('Toolbar initialized');
        }
        
        if (window.Minimap) {
            window.Minimap.initMinimap('minimap-canvas');
            Logger.log('Minimap initialized');
        }
        
        if (window.TilesetPanel) {
            await window.TilesetPanel.initTilesetPanel('tileset-panel');
            Logger.log('Tileset panel initialized');
        }
        
        if (window.BossViewer) {
            await window.BossViewer.initBossViewer('boss-viewer');
            Logger.log('Boss viewer initialized');
        }
    }
    
    /**
     * Initialize event handlers
     */
    function initEventHandlers() {
        if (window.CanvasEvents) {
            window.CanvasEvents.initCanvasEvents('editor-canvas');
            Logger.log('Canvas events initialized');
        }
        
        if (window.KeyboardEvents) {
            window.KeyboardEvents.initKeyboardEvents();
            Logger.log('Keyboard events initialized');
        }
        
        // State change listener
        window.addEventListener('statechange', (e) => {
            Logger.debug('State changed:', e.detail);
        });
        
        // Level change listener
        window.addEventListener('levelchange', () => {
            if (window.Minimap) window.Minimap.renderMinimap();
            if (window.History) {
                const snapshot = window.History.createSnapshot({
                    levelData: window.LevelData?.getData()
                });
                window.History.saveState(snapshot);
            }
        });
    }
    
    /**
     * Initialize features
     */
    function initFeatures() {
        if (window.PasswordGenerator) {
            window.PasswordGenerator.initPasswordGenerator('password-feature');
            Logger.log('Password generator initialized');
        }
        
        if (window.LevelSequenceViewer) {
            window.LevelSequenceViewer.initLevelSequenceViewer('sequence-viewer');
            Logger.log('Level sequence viewer initialized');
        }
    }
    
    /**
     * Initialize feature navigation tabs
     */
    function initFeatureNavigation() {
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                showFeature(tab.dataset.feature);
            });
        });
        Logger.log('Feature navigation initialized');
    }

    /**
     * Show/hide feature sections
     */
    function showFeature(feature) {
        // Hide all features
        document.querySelectorAll('.feature-section').forEach(el => {
            el.style.display = 'none';
        });
        document.querySelectorAll('.nav-tab').forEach(el => {
            el.classList.remove('active');
        });

        // Show selected feature
        const section = document.getElementById(`${feature}-feature`);
        const tab = document.querySelector(`[data-feature="${feature}"]`);

        if (section && tab) {
            section.style.display = 'block';
            tab.classList.add('active');
            Logger.log('Feature switched:', feature);

            // Initialize feature if needed
            if (feature === 'bosses' && window.BossViewer) {
                window.BossViewer.initBossViewer('boss-viewer');
            } else if (feature === 'sequences' && window.LevelSequenceViewer) {
                window.LevelSequenceViewer.initLevelSequenceViewer('sequence-viewer');
            } else if (feature === 'password' && window.PasswordGenerator) {
                window.PasswordGenerator.initPasswordGenerator('password-generator');
            } else if (feature === 'tilesets' && window.TilesetPanel) {
                window.TilesetPanel.initTilesetPanel('tileset-browser');
            }
        }
    }

    /**
     * Load default level
     */
    async function loadDefaultLevel() {
        if (window.API) {
            try {
                const level = await window.API.getLevel('world_1');
                if (level && window.LevelData) {
                    window.LevelData.loadLevel(level);
                    window.dispatchEvent(new CustomEvent('levelchange'));
                }
            } catch (error) {
                Logger.warn('Could not load default level:', error);
            }
        }
    }

    /**
     * Export level data
     */
    function exportLevel() {
        if (!window.LevelData) return;

        const data = window.LevelData.getExportData();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `level_${data.map_number}.json`;
        a.click();
        URL.revokeObjectURL(url);

        Logger.log('Level exported:', data.map_number);
    }

    // Export to window
    window.App = {
        initEditor,
        exportLevel
    };

    // Export feature navigation globally
    window.initFeatureNavigation = initFeatureNavigation;
    window.showFeature = showFeature;

    // Auto-initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEditor);
    } else {
        initEditor();
    }

})();
