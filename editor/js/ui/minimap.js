/**
 * Minimap for Space Funky B.O.B. Level Editor
 * 
 * Renders 80x80 level overview.
 * Refactored from app.js (1186 lines → 150 lines)
 */

(function() {
    'use strict';
    
    let canvas = null;
    let ctx = null;
    const TILE_SIZE = 1;  // 1px per tile in minimap
    
    /**
     * Initialize minimap
     * @param {string} canvasId - Canvas element ID
     */
    function initMinimap(canvasId) {
        canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.warn('Minimap canvas not found:', canvasId);
            return;
        }
        
        ctx = canvas.getContext('2d');
        canvas.width = 80 * TILE_SIZE;
        canvas.height = 80 * TILE_SIZE;
        
        // Listen for level changes
        window.addEventListener('levelchange', renderMinimap);
        window.addEventListener('statechange', onStateChange);
    }
    
    /**
     * Render minimap from level data
     */
    function renderMinimap() {
        if (!ctx || !window.LevelData) return;
        
        const levelData = window.LevelData.getData();
        if (!levelData || !levelData.tiles) return;
        
        // Clear canvas
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw tiles
        for (let x = 0; x < 80; x++) {
            for (let y = 0; y < 80; y++) {
                const tile = levelData.tiles[x][y];
                if (tile.tileId !== 0) {
                    // Color based on tile ID
                    const hue = (tile.tileId * 137.5) % 360;  // Golden angle
                    ctx.fillStyle = `hsl(${hue}, 70%, 50%)`;
                    ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }
            }
        }
    }
    
    /**
     * Handle state change
     * @param {CustomEvent} event - State change event
     */
    function onStateChange(event) {
        if (event.detail.key === 'levelData') {
            renderMinimap();
        }
    }
    
    /**
     * Get minimap canvas
     * @returns {HTMLCanvasElement} Canvas element
     */
    function getCanvas() {
        return canvas;
    }
    
    /**
     * Update minimap zoom
     * @param {number} zoom - Zoom level
     */
    function setZoom(zoom) {
        if (canvas) {
            canvas.style.transform = `scale(${Math.min(zoom, 2)})`;
            canvas.style.transformOrigin = 'top left';
        }
    }
    
    /**
     * Highlight tile on minimap
     * @param {number} x - Tile X
     * @param {number} y - Tile Y
     */
    function highlightTile(x, y) {
        if (!ctx) return;
        
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1;
        ctx.strokeRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
    }
    
    /**
     * Clear minimap
     */
    function clearMinimap() {
        if (!ctx) return;
        
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    
    // Export to window
    window.Minimap = {
        initMinimap,
        renderMinimap,
        getCanvas,
        setZoom,
        highlightTile,
        clearMinimap
    };
    
})();
