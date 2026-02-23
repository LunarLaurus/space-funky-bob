/**
 * Canvas Events for Space Funky B.O.B. Level Editor
 * 
 * Handles mouse/touch painting on canvas.
 * Refactored from app.js (1186 lines → 200 lines)
 */

(function() {
    'use strict';
    
    let canvas = null;
    let isDrawing = false;
    let lastX = -1;
    let lastY = -1;
    
    /**
     * Initialize canvas event handlers
     * @param {string} canvasId - Canvas element ID
     */
    function initCanvasEvents(canvasId) {
        canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.warn('Canvas not found:', canvasId);
            return;
        }
        
        // Mouse events
        canvas.addEventListener('mousedown', onMouseDown);
        canvas.addEventListener('mousemove', onMouseMove);
        canvas.addEventListener('mouseup', onMouseUp);
        canvas.addEventListener('mouseleave', onMouseUp);
        
        // Touch events
        canvas.addEventListener('touchstart', onTouchStart, { passive: false });
        canvas.addEventListener('touchmove', onTouchMove, { passive: false });
        canvas.addEventListener('touchend', onTouchEnd);
        
        // Prevent context menu
        canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    }
    
    /**
     * Get tile coordinates from event
     * @param {MouseEvent|TouchEvent} e - Event
     * @returns {Object} { x, y } tile coordinates
     */
    function getTileCoords(e) {
        const rect = canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        
        const x = Math.floor((clientX - rect.left) / (window.APP_CONFIG?.TILE_SIZE || 8));
        const y = Math.floor((clientY - rect.top) / (window.APP_CONFIG?.TILE_SIZE || 8));
        
        return { x, y };
    }
    
    /**
     * Mouse down handler
     * @param {MouseEvent} e - Mouse event
     */
    function onMouseDown(e) {
        isDrawing = true;
        const { x, y } = getTileCoords(e);
        lastX = x;
        lastY = y;
        
        paintTile(x, y);
    }
    
    /**
     * Mouse move handler
     * @param {MouseEvent} e - Mouse event
     */
    function onMouseMove(e) {
        if (!isDrawing) return;
        
        const { x, y } = getTileCoords(e);
        
        // Draw line from last position
        if (lastX !== -1 && lastY !== -1) {
            drawLine(lastX, lastY, x, y);
        }
        
        lastX = x;
        lastY = y;
    }
    
    /**
     * Mouse up handler
     */
    function onMouseUp() {
        isDrawing = false;
        lastX = -1;
        lastY = -1;
    }
    
    /**
     * Touch start handler
     * @param {TouchEvent} e - Touch event
     */
    function onTouchStart(e) {
        e.preventDefault();
        onMouseDown(e);
    }
    
    /**
     * Touch move handler
     * @param {TouchEvent} e - Touch event
     */
    function onTouchMove(e) {
        e.preventDefault();
        onMouseMove(e);
    }
    
    /**
     * Touch end handler
     */
    function onTouchEnd() {
        onMouseUp();
    }
    
    /**
     * Paint single tile
     * @param {number} x - Tile X
     * @param {number} y - Tile Y
     */
    function paintTile(x, y) {
        if (!window.LevelData) return;
        
        const state = window.AppState?.getState() || {};
        const tileId = state.isErasing ? 0 : state.selectedTile || 0;
        
        window.LevelData.setTile(x, y, tileId);
        
        window.dispatchEvent(new CustomEvent('levelchange', {
            detail: { x, y, tileId }
        }));
    }
    
    /**
     * Draw line between two points (Bresenham's algorithm)
     * @param {number} x0 - Start X
     * @param {number} y0 - Start Y
     * @param {number} x1 - End X
     * @param {number} y1 - End Y
     */
    function drawLine(x0, y0, x1, y1) {
        const dx = Math.abs(x1 - x0);
        const dy = Math.abs(y1 - y0);
        const sx = x0 < x1 ? 1 : -1;
        const sy = y0 < y1 ? 1 : -1;
        let err = dx - dy;
        
        while (true) {
            paintTile(x0, y0);
            
            if (x0 === x1 && y0 === y1) break;
            
            const e2 = 2 * err;
            if (e2 > -dy) { err -= dy; x0 += sx; }
            if (e2 < dx) { err += dx; y0 += sy; }
        }
    }
    
    /**
     * Set canvas element
     * @param {HTMLCanvasElement} newCanvas - Canvas element
     */
    function setCanvas(newCanvas) {
        canvas = newCanvas;
    }
    
    // Export to window
    window.CanvasEvents = {
        initCanvasEvents,
        getTileCoords,
        paintTile,
        drawLine,
        setCanvas
    };
    
})();
