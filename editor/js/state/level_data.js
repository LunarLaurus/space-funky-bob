/**
 * Level Data Management for Space Funky B.O.B. Level Editor
 * 
 * Manages level tile data structure (80x80 tiles).
 * Refactored from app.js (1186 lines → 200 lines)
 */

(function() {
    'use strict';
    
    // Level data structure - matches renderer expectations
    let levelData = {
        mapNumber: 0,
        name: '',
        width: 80,
        height: 80,
        background: [],  // Array of {x, y, tile} objects
        foreground: [],   // Array of {x, y, tile} objects
        enemies: []       // Array of {x, y, type, id} objects
    };
    
    /**
     * Initialize empty level data
     * @param {number} width - Level width (default 80)
     * @param {number} height - Level height (default 80)
     */
    function initLevel(width = 80, height = 80) {
        levelData = {
            mapNumber: 0,
            name: '',
            width,
            height,
            background: [],
            foreground: [],
            enemies: []
        };
    }
    
    /**
     * Load level data from server response
     * @param {Object} data - Level data from API
     */
    function loadLevel(data) {
        if (!data) {
            console.error('No level data provided');
            return false;
        }

        levelData.mapNumber = data.map_number || 0;
        levelData.name = data.name || '';
        levelData.width = data.width || 80;
        levelData.height = data.height || 80;

        // Initialize empty background and foreground arrays
        levelData.background = [];
        levelData.foreground = [];
        levelData.enemies = data.enemies || [];

        // Load tiles - convert from 2D array or sparse format to {x, y, tile} objects
        if (data.tiles && Array.isArray(data.tiles)) {
            // Sparse format: tiles is array of {x, y, tile} objects
            data.tiles.forEach(tile => {
                const tileObj = {
                    x: tile.x || 0,
                    y: tile.y || 0,
                    tile: tile.tile || tile.tileId || 0
                };
                // Assume layer property or default to background
                if (tile.layer === 'foreground') {
                    levelData.foreground.push(tileObj);
                } else {
                    levelData.background.push(tileObj);
                }
            });
        } else if (data.background) {
            // Already in correct format
            levelData.background = data.background;
            levelData.foreground = data.foreground || [];
        }

        return true;
    }
    
    /**
     * Get tile at position
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @param {string} layer - Layer ('background' or 'foreground', default 'background')
     * @returns {Object} Tile data {x, y, tile}
     */
    function getTile(x, y, layer = 'background') {
        if (x < 0 || x >= levelData.width || y < 0 || y >= levelData.height) {
            return null;
        }
        const tiles = layer === 'foreground' ? levelData.foreground : levelData.background;
        return tiles.find(t => t.x === x && t.y === y) || null;
    }

    /**
     * Set tile at position
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @param {number} tileId - Tile ID
     * @param {string} layer - Layer ('background' or 'foreground', default 'background')
     */
    function setTile(x, y, tileId, layer = 'background') {
        if (x < 0 || x >= levelData.width || y < 0 || y >= levelData.height) {
            return;
        }
        const tiles = layer === 'foreground' ? levelData.foreground : levelData.background;
        
        // Remove existing tile at this position
        const existingIndex = tiles.findIndex(t => t.x === x && t.y === y);
        if (existingIndex !== -1) {
            tiles.splice(existingIndex, 1);
        }
        
        // Add new tile if tileId is non-zero
        if (tileId !== 0) {
            tiles.push({ x, y, tile: tileId });
        }
    }

    /**
     * Get all tiles (both layers)
     * @returns {Object} Object with background and foreground arrays
     */
    function getAllTiles() {
        return {
            background: levelData.background,
            foreground: levelData.foreground,
            enemies: levelData.enemies
        };
    }

    /**
     * Get level data for export
     * @returns {Object} Complete level data
     */
    function getExportData() {
        return {
            map_number: levelData.mapNumber,
            name: levelData.name,
            width: levelData.width,
            height: levelData.height,
            background: levelData.background,
            foreground: levelData.foreground,
            enemies: levelData.enemies
        };
    }

    /**
     * Get level metadata
     * @returns {Object} Level metadata
     */
    function getMetadata() {
        return {
            mapNumber: levelData.mapNumber,
            name: levelData.name,
            width: levelData.width,
            height: levelData.height,
            backgroundTiles: levelData.background.length,
            foregroundTiles: levelData.foreground.length,
            enemies: levelData.enemies.length
        };
    }

    /**
     * Clear all tiles
     */
    function clearLevel() {
        levelData.background = [];
        levelData.foreground = [];
        levelData.enemies = [];
    }
    
    // Export to window
    window.LevelData = {
        initLevel,
        loadLevel,
        getTile,
        setTile,
        getAllTiles,
        getExportData,
        getMetadata,
        clearLevel,
        getData: () => levelData
    };

})();
