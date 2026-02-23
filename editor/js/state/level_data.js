/**
 * Level Data Management for Space Funky B.O.B. Level Editor
 * 
 * Manages level tile data structure (80x80 tiles).
 * Refactored from app.js (1186 lines → 200 lines)
 */

(function() {
    'use strict';
    
    // Level data structure
    let levelData = {
        mapNumber: 0,
        name: '',
        width: 80,
        height: 80,
        tiles: []  // 2D array: tiles[x][y] = { tileId, properties }
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
            tiles: []
        };
        
        // Initialize 2D tile array
        for (let x = 0; x < width; x++) {
            levelData.tiles[x] = [];
            for (let y = 0; y < height; y++) {
                levelData.tiles[x][y] = {
                    tileId: 0,
                    properties: {}
                };
            }
        }
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
        
        // Load tiles (sparse format: only non-zero tiles)
        levelData.tiles = [];
        for (let x = 0; x < levelData.width; x++) {
            levelData.tiles[x] = [];
            for (let y = 0; y < levelData.height; y++) {
                levelData.tiles[x][y] = {
                    tileId: 0,
                    properties: {}
                };
            }
        }
        
        // Apply tile data
        if (data.tiles) {
            data.tiles.forEach(tile => {
                if (tile.x >= 0 && tile.x < levelData.width &&
                    tile.y >= 0 && tile.y < levelData.height) {
                    levelData.tiles[tile.x][tile.y] = {
                        tileId: tile.tile || tile.tileId || 0,
                        properties: tile.properties || {}
                    };
                }
            });
        }
        
        return true;
    }
    
    /**
     * Get tile at position
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @returns {Object} Tile data
     */
    function getTile(x, y) {
        if (x < 0 || x >= levelData.width || y < 0 || y >= levelData.height) {
            return null;
        }
        return levelData.tiles[x][y];
    }
    
    /**
     * Set tile at position
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     * @param {number} tileId - Tile ID
     */
    function setTile(x, y, tileId) {
        if (x < 0 || x >= levelData.width || y < 0 || y >= levelData.height) {
            return;
        }
        levelData.tiles[x][y].tileId = tileId;
    }
    
    /**
     * Get all non-zero tiles (sparse format)
     * @returns {Array} Array of tile objects
     */
    function getNonZeroTiles() {
        const tiles = [];
        for (let x = 0; x < levelData.width; x++) {
            for (let y = 0; y < levelData.height; y++) {
                if (levelData.tiles[x][y].tileId !== 0) {
                    tiles.push({
                        x,
                        y,
                        tile: levelData.tiles[x][y].tileId
                    });
                }
            }
        }
        return tiles;
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
            tiles: getNonZeroTiles()
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
            totalTiles: levelData.width * levelData.height,
            nonZeroTiles: getNonZeroTiles().length
        };
    }
    
    /**
     * Clear all tiles
     */
    function clearLevel() {
        for (let x = 0; x < levelData.width; x++) {
            for (let y = 0; y < levelData.height; y++) {
                levelData.tiles[x][y].tileId = 0;
                levelData.tiles[x][y].properties = {};
            }
        }
    }
    
    // Export to window
    window.LevelData = {
        initLevel,
        loadLevel,
        getTile,
        setTile,
        getNonZeroTiles,
        getExportData,
        getMetadata,
        clearLevel,
        getData: () => levelData
    };
    
})();
