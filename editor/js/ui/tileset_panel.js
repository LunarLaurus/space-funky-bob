/**
 * Tileset Panel for Space Funky B.O.B. Level Editor
 * 
 * Displays 12 tilesets with selection UI.
 * Refactored from app.js (1186 lines → 200 lines)
 */

(function() {
    'use strict';
    
    // All 12 tileset types from source
    const TILESETS = [
        { id: 'borg', name: 'Borg Factory', offset: '0x008000' },
        { id: 'bug', name: 'Bug Planet', offset: '0x008800' },
        { id: 'ancient', name: 'Ancient Ruins', offset: '0x009000' },
        { id: 'lava', name: 'Lava World', offset: '0x009800' },
        { id: 'ultra', name: 'Ultra Force', offset: '0x00A000' },
        { id: 'bubble', name: 'Bubble Forest', offset: '0x00A800' },
        { id: 'borg2', name: 'Borg Variant 2', offset: '0x00B000' },
        { id: 'borg3', name: 'Borg Variant 3', offset: '0x00B800' },
        { id: 'world', name: 'World Map', offset: '0x00C000' },
        { id: 'borg4', name: 'Borg Door', offset: '0x00C800' },
        { id: 'main_graphics_1', name: 'Main Graphics 1', offset: '0x035800' },
        { id: 'main_graphics_2', name: 'Main Graphics 2', offset: '0x03D800' }
    ];
    
    let currentTileset = 'borg';
    let selectedTile = 0;
    
    /**
     * Initialize tileset panel
     * @param {string} containerId - Container element ID
     */
    async function initTilesetPanel(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn('Tileset panel container not found:', containerId);
            return;
        }
        
        // Create tileset selector
        const selector = document.createElement('select');
        selector.id = 'tileset-selector';
        selector.className = 'tileset-selector';
        
        TILESETS.forEach(ts => {
            const option = document.createElement('option');
            option.value = ts.id;
            option.textContent = `${ts.name} (${ts.offset})`;
            selector.appendChild(option);
        });
        
        selector.addEventListener('change', (e) => {
            loadTileset(e.target.value);
        });
        
        container.appendChild(selector);
        
        // Create tile grid
        const tileGrid = document.createElement('div');
        tileGrid.id = 'tile-grid';
        tileGrid.className = 'tile-grid';
        container.appendChild(tileGrid);
        
        // Load default tileset
        await loadTileset('borg');
    }
    
    /**
     * Load tileset data
     * @param {string} tilesetId - Tileset ID
     */
    async function loadTileset(tilesetId) {
        currentTileset = tilesetId;
        
        if (window.API) {
            try {
                const data = await window.API.getTileset(tilesetId);
                renderTileGrid(data);
                
                window.dispatchEvent(new CustomEvent('tilesetchange', {
                    detail: { tilesetId, data }
                }));
            } catch (error) {
                console.error('Failed to load tileset:', error);
            }
        }
    }
    
    /**
     * Render tile grid
     * @param {Object} data - Tileset data
     */
    function renderTileGrid(data) {
        const grid = document.getElementById('tile-grid');
        if (!grid) return;
        
        grid.innerHTML = '';
        
        if (!data || !data.tiles) {
            grid.textContent = 'No tile data available';
            return;
        }
        
        // Render 256 tiles (16x16 grid)
        for (let i = 0; i < 256; i++) {
            const tile = document.createElement('div');
            tile.className = 'tile';
            tile.dataset.tileId = i;
            
            // Simple placeholder rendering
            tile.style.width = '32px';
            tile.style.height = '32px';
            tile.style.display = 'inline-block';
            tile.style.border = '1px solid #333';
            tile.style.background = `hsl(${i * 1.4}, 50%, 50%)`;
            
            tile.addEventListener('click', () => selectTile(i));
            
            grid.appendChild(tile);
        }
    }
    
    /**
     * Select tile
     * @param {number} tileId - Tile ID
     */
    function selectTile(tileId) {
        selectedTile = tileId;
        
        // Update UI
        document.querySelectorAll('.tile').forEach(tile => {
            tile.classList.toggle('selected', parseInt(tile.dataset.tileId) === tileId);
        });
        
        // Emit selection event
        window.dispatchEvent(new CustomEvent('tileselect', {
            detail: { tileId, tileset: currentTileset }
        }));
        
        // Update app state
        if (window.AppState) {
            window.AppState.setState('selectedTile', tileId);
        }
    }
    
    /**
     * Get current tileset
     * @returns {string} Current tileset ID
     */
    function getCurrentTileset() {
        return currentTileset;
    }
    
    /**
     * Get selected tile
     * @returns {number} Selected tile ID
     */
    function getSelectedTile() {
        return selectedTile;
    }
    
    /**
     * Get all tilesets
     * @returns {Array} Tileset list
     */
    function getAllTilesets() {
        return TILESETS;
    }

    /**
     * Load all tilesets from ROM
     */
    async function loadAllTilesets() {
        Logger.info('TilesetPanel', 'Scanning ROM for tilesets...');
        
        if (window.API) {
            try {
                const data = await window.API.getAllTilesets();
                Logger.info('TilesetPanel', 'Found ' + (data.tilesets?.length || 0) + ' tilesets');
                
                // Update tileset list
                TILESETS.length = 0;
                if (data.tilesets) {
                    data.tilesets.forEach(ts => {
                        TILESETS.push({
                            id: ts.id,
                            name: ts.name,
                            offset: ts.rom_offset
                        });
                    });
                }
                
                // Re-render tile grid with first tileset
                if (TILESETS.length > 0) {
                    await loadTileset(TILESETS[0].id);
                }
            } catch (error) {
                Logger.error('TilesetPanel', 'Failed to load tilesets: ' + error.message);
            }
        }
    }

    // Export to window
    window.TilesetPanel = {
        initTilesetPanel,
        loadTileset,
        renderTileGrid,
        selectTile,
        getCurrentTileset,
        getSelectedTile,
        getAllTilesets,
        loadAllTilesets
    };

    // Export loadAllTilesets globally for onclick handler
    window.loadAllTilesets = loadAllTilesets;

})();
