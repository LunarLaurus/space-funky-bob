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
        Logger.info('App', 'Initializing B.O.B. Level Editor...');

        // Initialize state management
        if (window.AppState) {
            Logger.info('App', 'State management initialized');
        }

        // Initialize level data
        if (window.LevelData) {
            window.LevelData.initLevel(80, 80);
            Logger.info('App', 'Level data initialized');
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

        Logger.info('App', 'Editor initialization complete');
    }
    
    /**
     * Initialize UI modules
     */
    async function initUIModules() {
        if (window.Toolbar) {
            window.Toolbar.initToolbar();
            Logger.info('App', 'Toolbar initialized');
        }

        if (window.Minimap) {
            window.Minimap.initMinimap('minimap');
            Logger.info('App', 'Minimap initialized');
        }

        if (window.TilesetPanel) {
            await window.TilesetPanel.initTilesetPanel('tileset');
            Logger.info('App', 'Tileset panel initialized');
        }

        if (window.BossViewer) {
            await window.BossViewer.initBossViewer('boss-viewer');
            Logger.info('App', 'Boss viewer initialized');
        }
    }
    
    /**
     * Initialize event handlers
     */
    function initEventHandlers() {
        if (window.CanvasEvents) {
            window.CanvasEvents.initCanvasEvents('levelCanvas');
            Logger.info('App', 'Canvas events initialized');
        }

        if (window.KeyboardEvents) {
            window.KeyboardEvents.initKeyboardEvents();
            Logger.info('App', 'Keyboard events initialized');
        }

        // Initialize Renderer
        if (window.Renderer) {
            window.Renderer.init('levelCanvas', 'minimap');
            Logger.info('App', 'Renderer initialized');
        }

        // State change listener
        window.addEventListener('statechange', (e) => {
            Logger.debug('App', 'State changed: ' + JSON.stringify(e.detail));
        });

        // Level change listener - render main canvas
        window.addEventListener('levelchange', () => {
            if (window.Renderer) {
                const state = window.AppState.getState();
                const levelData = window.LevelData.getData();
                window.Renderer.renderCanvas(levelData, {
                    zoom: state.zoom,
                    showGrid: state.showGrid,
                    snapToGrid: state.snapToGrid,
                    currentLayer: state.activeLayer,
                    showEnemies: state.showEnemies
                }, [], []);
            }
            if (window.Minimap) window.Minimap.renderMinimap();
            if (window.History) {
                const snapshot = window.History.createSnapshot({
                    levelData: window.LevelData?.getData()
                });
                window.History.saveState(snapshot);
            }
        });

        // Initialize data reference click handlers
        initDataReference();
    }

    function initFeatures() {
        if (window.PasswordGenerator) {
            window.PasswordGenerator.initPasswordGenerator('password-generator');
            Logger.info('App', 'Password generator initialized');
        }

        if (window.LevelSequenceViewer) {
            window.LevelSequenceViewer.initLevelSequenceViewer('sequence-viewer');
            Logger.info('App', 'Level sequence viewer initialized');
        }
    }
    
    function initFeatureNavigation() {
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                showFeature(tab.dataset.feature);
            });
        });
        Logger.info('App', 'Feature navigation initialized');
    }

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
            Logger.info('App', 'Feature switched: ' + feature);

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

        Logger.info('App', 'Level exported: ' + data.map_number);
    }

    /**
     * Initialize data reference click handlers
     */
    function initDataReference() {
        const dataList = document.getElementById('dataList');
        if (!dataList) return;

        dataList.querySelectorAll('li').forEach(li => {
            li.style.cursor = 'pointer';
            li.onclick = async () => {
                const filename = li.dataset.file;
                const viewer = document.getElementById('dataViewer');
                const title = document.getElementById('dataTitle');
                const content = document.getElementById('dataContent');

                // Highlight selected
                dataList.querySelectorAll('li').forEach(l => {
                    l.style.background = '';
                    l.style.color = '';
                });
                li.style.background = 'var(--accent)';
                li.style.color = '#000';

                // Show viewer
                viewer.style.display = 'block';
                title.textContent = filename;
                content.innerHTML = '<div style="color:var(--accent)">Loading...</div>';

                try {
                    const data = await window.API.getDataFile(filename);
                    let items = Array.isArray(data) ? data : (data.tiles || data.enemies || data.worlds || data.tilesets || []);

                    // Simple display based on file type
                    let html = '<div style="max-height:200px;overflow-y:auto;">';
                    if (filename === 'ENEMIES.json') {
                        html += '<table style="width:100%;font-size:9px;border-collapse:collapse;">';
                        html += '<tr style="background:var(--bg-toolbar);"><th>ID</th><th>Name</th><th>Category</th></tr>';
                        items.forEach(item => {
                            html += '<tr style="border-bottom:1px solid var(--border);">' +
                                '<td style="padding:4px;">' + (item.id || '-') + '</td>' +
                                '<td style="padding:4px;">' + (item.name || '-') + '</td>' +
                                '<td style="padding:4px;">' + (item.category || '-') + '</td></tr>';
                        });
                        html += '</table>';
                    } else if (filename === 'TILES.json') {
                        html += '<table style="width:100%;font-size:9px;border-collapse:collapse;">';
                        html += '<tr style="background:var(--bg-toolbar);"><th>ID</th><th>Name</th><th>Type</th></tr>';
                        items.forEach(item => {
                            html += '<tr style="border-bottom:1px solid var(--border);">' +
                                '<td style="padding:4px;">' + (item.id || '-') + '</td>' +
                                '<td style="padding:4px;">' + (item.name || '-') + '</td>' +
                                '<td style="padding:4px;">' + (item.type || '-') + '</td></tr>';
                        });
                        html += '</table>';
                    } else if (filename === 'LEVELS.json') {
                        html += '<pre style="font-size:9px;margin:0;">' + JSON.stringify(data, null, 2) + '</pre>';
                    } else if (filename === 'TILESETS.json') {
                        html += '<table style="width:100%;font-size:9px;border-collapse:collapse;">';
                        html += '<tr style="background:var(--bg-toolbar);"><th>ID</th><th>Name</th><th>Tiles</th></tr>';
                        items.forEach(item => {
                            html += '<tr style="border-bottom:1px solid var(--border);">' +
                                '<td style="padding:4px;">' + (item.id || '-') + '</td>' +
                                '<td style="padding:4px;">' + (item.name || '-') + '</td>' +
                                '<td style="padding:4px;">' + (item.num_tiles || '-') + '</td></tr>';
                        });
                        html += '</table>';
                    }
                    html += '</div>';
                    content.innerHTML = html;
                } catch (e) {
                    content.innerHTML = '<div style="color:red">Error: ' + e.message + '</div>';
                }
            };
        });
    }

    // Export to window
    window.App = {
        initEditor,
        exportLevel
    };

    // Export feature navigation globally
    window.initFeatureNavigation = initFeatureNavigation;
    window.showFeature = showFeature;

    // Export data reference init globally
    window.initDataReference = initDataReference;

    // Auto-initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEditor);
    } else {
        initEditor();
    }

})();
