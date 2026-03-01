/**
 * Renderer Module - Canvas Drawing
 * 
 * Handles all canvas rendering for the level editor:
 * - Main level canvas (tile rendering)
 * - Minimap overview
 * - Tile palette
 * - Enemy markers
 * 
 * Files linking:
 *   - app.js imports and calls Renderer methods
 *   - Depends on: logger.js (global Logger), config (global constants)
 * 
 * Rendering flow:
 *   1. renderCanvas() - Main level view
 *   2. renderMinimap() - Overview panel
 *   3. renderTilesetPalette() - Tile selection grid
 */

const Renderer = (function() {
    'use strict';
    
    // Canvas references (set by app.js)
    let levelCanvas = null;
    let levelCtx = null;
    let minimapCanvas = null;
    let minimapCtx = null;
    
    // Tile cache - stores pre-rendered 8x8 canvases for each unique tile
    let tileCache = {};
    let cacheTilesetId = null;
    let cacheValid = false;
    
    /**
     * Initialize canvas contexts
     * @param {string} levelCanvasId - ID of level canvas element
     * @param {string} minimapCanvasId - ID of minimap canvas element
     */
    function init(levelCanvasId, minimapCanvasId) {
        levelCanvas = document.getElementById(levelCanvasId);
        minimapCanvas = document.getElementById(minimapCanvasId);
        
        if (levelCanvas) {
            levelCtx = levelCanvas.getContext('2d');
            Logger.info('Renderer', 'Level canvas initialized');
        }
        
        if (minimapCanvas) {
            minimapCtx = minimapCanvas.getContext('2d');
            Logger.info('Renderer', 'Minimap canvas initialized');
        }
    }
    
    /**
     * Initialize tile cache - creates cached canvases for all 256 tiles in a tileset
     * @param {Array} tilesetTiles - Array of 256 tile objects with pixels and palette
     * @param {string} tilesetId - Unique identifier for the tileset (for cache invalidation)
     */
    function initTileCache(tilesetTiles, tilesetId) {
        if (!tilesetTiles || tilesetTiles.length === 0) {
            Logger.warn('Renderer', 'initTileCache: No tileset data provided');
            return;
        }
        
        // Invalidate cache if tileset changed
        if (cacheTilesetId !== tilesetId) {
            tileCache = {};
            cacheTilesetId = tilesetId;
            cacheValid = true;
        }
        
        // Create cached canvas for each tile
        for (let i = 0; i < 256; i++) {
            if (tileCache[i]) continue; // Already cached
            
            const tileData = tilesetTiles[i];
            if (!tileData || !tileData.pixels || !tileData.palette) continue;
            
            const canvas = document.createElement('canvas');
            canvas.width = 8;
            canvas.height = 8;
            const ctx = canvas.getContext('2d');
            
            const pixels = tileData.pixels;
            const palette = tileData.palette;
            
            for (let y = 0; y < 8; y++) {
                for (let x = 0; x < 8; x++) {
                    const paletteIndex = pixels[y * 8 + x];
                    const rgb = palette[paletteIndex];
                    if (rgb) {
                        ctx.fillStyle = `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
                        ctx.fillRect(x, y, 1, 1);
                    }
                }
            }
            
            tileCache[i] = canvas;
        }
        
        Logger.info('Renderer', `Tile cache initialized for tileset: ${tilesetId}`);
    }
    
    /**
     * Invalidate the tile cache (call when tileset changes)
     */
    function invalidateTileCache() {
        tileCache = {};
        cacheTilesetId = null;
        cacheValid = false;
        Logger.info('Renderer', 'Tile cache invalidated');
    }
    
    /**
     * Render the main level canvas
     * @param {Object} levelData - Current level data with background/foreground tiles
     * @param {Object} config - Render config (zoom, grid, layer, etc.)
     * @param {Array} tileColors - Array of color strings for tiles
     * @param {Array} tilesetTiles - Full tile pixel data (64 palette indices per tile)
     */
    function renderCanvas(levelData, config, tileColors, tilesetTiles) {
        Logger.info('Renderer', 'renderCanvas called');
        Logger.debug('Renderer', 'levelData: ' + JSON.stringify({bg: levelData.background?.length, fg: levelData.foreground?.length, enemies: levelData.enemies?.length}));
        Logger.debug('Renderer', 'config: zoom=' + config.zoom + ', layer=' + config.currentLayer + ', showEnemies=' + config.showEnemies);
        Logger.debug('Renderer', 'tileColors: ' + (tileColors?.length || 0) + ', tilesetTiles: ' + (tilesetTiles?.length || 0));
        
        if (!levelCtx || !levelCanvas) {
            Logger.warn('Renderer', 'Level canvas not initialized');
            return;
        }
        
        const { MAP_WIDTH, MAP_HEIGHT, TILE_SIZE } = window.APP_CONFIG;
        const { zoom, showGrid, snapToGrid, currentLayer, showEnemies } = config;
        
        // Set canvas size
        levelCanvas.width = MAP_WIDTH * TILE_SIZE * zoom;
        levelCanvas.height = MAP_HEIGHT * TILE_SIZE * zoom;
        
        Logger.debug('Renderer', 'Canvas size: ' + levelCanvas.width + 'x' + levelCanvas.height);
        
        // Clear canvas
        levelCtx.fillStyle = '#000';
        levelCtx.fillRect(0, 0, levelCanvas.width, levelCanvas.height);
        
        const tileSize = TILE_SIZE * zoom;
        const tiles = currentLayer === 'background' 
            ? (levelData.background || []) 
            : (levelData.foreground || []);
        
        // Draw tiles
        Logger.debug('Renderer', 'Drawing tiles...');
        
        const hasFullTileData = tilesetTiles && tilesetTiles.length > 0;
        
        tiles.forEach(tile => {
            if (tile.x < MAP_WIDTH && tile.y < MAP_HEIGHT) {
                const px = tile.x * tileSize;
                const py = tile.y * tileSize;
                
                // Check if tile is cached - use drawImage for performance
                const cachedTile = tileCache[tile.tile];
                if (cachedTile && zoom > 1) {
                    levelCtx.drawImage(cachedTile, 0, 0, 8, 8, px, py, tileSize, tileSize);
                    return;
                }
                
                if (hasFullTileData && tilesetTiles[tile.tile]) {
                    const tileData = tilesetTiles[tile.tile];
                    const pixels = tileData.pixels;
                    const palette = tileData.palette;
                    
                    if (pixels && palette) {
                        // Use cached canvas if available
                        if (cachedTile) {
                            levelCtx.drawImage(cachedTile, 0, 0, 8, 8, px, py, tileSize, tileSize);
                        } else {
                            const pixelSize = zoom;
                            for (let y = 0; y < 8; y++) {
                                for (let x = 0; x < 8; x++) {
                                    const paletteIndex = pixels[y * 8 + x];
                                    const rgb = palette[paletteIndex];
                                    if (rgb) {
                                        levelCtx.fillStyle = `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
                                        levelCtx.fillRect(px + x * pixelSize, py + y * pixelSize, pixelSize, pixelSize);
                                    }
                                }
                            }
                        }
                        return;
                    }
                }
                
                // Fallback to solid color
                const color = tileColors[tile.tile % tileColors.length] || '#000';
                levelCtx.fillStyle = color;
                const w = zoom > 2 ? tileSize - 1 : tileSize;
                const h = zoom > 2 ? tileSize - 1 : tileSize;
                levelCtx.fillRect(px, py, w, h);
            }
        });
        
        // Draw grid
        if (showGrid && zoom >= 2) {
            levelCtx.strokeStyle = 'rgba(0,255,136,0.15)';
            levelCtx.lineWidth = 1;
            
            const step = snapToGrid ? 1 : 8;
            for (let x = 0; x <= MAP_WIDTH; x += step) {
                levelCtx.beginPath();
                levelCtx.moveTo(x * tileSize, 0);
                levelCtx.lineTo(x * tileSize, levelCanvas.height);
                levelCtx.stroke();
            }
            for (let y = 0; y <= MAP_HEIGHT; y += step) {
                levelCtx.beginPath();
                levelCtx.moveTo(0, y * tileSize);
                levelCtx.lineTo(levelCanvas.width, y * tileSize);
                levelCtx.stroke();
            }
        }
        
        // Draw enemy markers
        if (showEnemies && levelData.enemies && levelData.enemies.length > 0) {
            levelData.enemies.forEach(enemy => {
                const x = enemy.x * tileSize;
                const y = enemy.y * tileSize;
                
                // Red triangle
                levelCtx.fillStyle = 'rgba(255, 0, 85, 0.8)';
                levelCtx.beginPath();
                levelCtx.moveTo(x + tileSize/2, y);
                levelCtx.lineTo(x + tileSize, y + tileSize);
                levelCtx.lineTo(x, y + tileSize);
                levelCtx.closePath();
                levelCtx.fill();
                
                // White border
                levelCtx.strokeStyle = '#fff';
                levelCtx.lineWidth = 1;
                levelCtx.stroke();
            });
        }
        
        Logger.debug('Renderer', `Canvas rendered: ${tiles.length} tiles, zoom=${zoom}x`);
    }
    
    /**
     * Render minimap overview
     * @param {Object} levelData - Current level data
     * @param {Array} tileColors - Array of color strings
     * @param {Array} tilesetTiles - Full tile pixel data (64 palette indices per tile)
     */
    function renderMinimap(levelData, tileColors, tilesetTiles) {
        if (!minimapCtx || !minimapCanvas) {
            Logger.warn('Renderer', 'Minimap canvas not initialized');
            return;
        }
        
        const { MAP_WIDTH, MAP_HEIGHT } = window.APP_CONFIG;
        
        minimapCanvas.width = MAP_WIDTH;
        minimapCanvas.height = MAP_HEIGHT;
        
        // Clear
        minimapCtx.fillStyle = '#000';
        minimapCtx.fillRect(0, 0, MAP_WIDTH, MAP_HEIGHT);
        
        // Draw background tiles
        const tiles = levelData.background || [];
        
        const hasFullTileData = tilesetTiles && tilesetTiles.length > 0;
        
        tiles.forEach(tile => {
            if (tile.x < MAP_WIDTH && tile.y < MAP_HEIGHT) {
                if (hasFullTileData && tilesetTiles[tile.tile]) {
                    const tileData = tilesetTiles[tile.tile];
                    const pixels = tileData.pixels;
                    const palette = tileData.palette;
                    
                    if (pixels && palette) {
                        // Sample center pixel (index 35 = roughly center of 8x8)
                        const paletteIndex = pixels[35];
                        const rgb = palette[paletteIndex];
                        if (rgb) {
                            minimapCtx.fillStyle = `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
                            minimapCtx.fillRect(tile.x, tile.y, 1, 1);
                            return;
                        }
                    }
                }
                
                // Fallback to solid color
                const color = tileColors[tile.tile % tileColors.length] || '#000';
                minimapCtx.fillStyle = color;
                minimapCtx.fillRect(tile.x, tile.y, 1, 1);
            }
        });
        
        // Border
        minimapCtx.strokeStyle = '#00ff88';
        minimapCtx.lineWidth = 1;
        minimapCtx.strokeRect(0, 0, MAP_WIDTH, MAP_HEIGHT);
        
        Logger.debug('Renderer', 'Minimap rendered');
    }
    
    /**
     * Render tile palette in the sidebar
     * @param {Array} tileColors - Array of color strings
     * @param {number} selectedTile - Currently selected tile ID
     * @param {Function} onSelect - Callback when tile is selected
     */
    function renderTilesetPalette(tileColors, selectedTile, onSelect) {
        const grid = document.getElementById('tileset');
        if (!grid) {
            Logger.warn('Renderer', 'Tileset grid not found');
            return;
        }
        
        grid.innerHTML = '';
        
        for (let i = 0; i < 256; i++) {
            const tile = document.createElement('div');
            tile.className = 'tile';
            tile.style.backgroundColor = tileColors[i] || '#000';
            tile.title = `Tile ${i} (0x${i.toString(16).toUpperCase().padStart(2,'0')})`;
            tile.dataset.tile = i;
            
            if (i === selectedTile) {
                tile.classList.add('selected');
            }
            
            tile.onclick = () => {
                if (onSelect) onSelect(i, tile);
            };
            
            grid.appendChild(tile);
        }
        
        Logger.debug('Renderer', 'Tileset palette rendered');
    }
    
    // Public API
    return {
        init: init,
        initTileCache: initTileCache,
        invalidateTileCache: invalidateTileCache,
        renderCanvas: renderCanvas,
        renderMinimap: renderMinimap,
        renderTilesetPalette: renderTilesetPalette
    };
})();
