/**
 * API Module - Server Communication
 * 
 * Handles all HTTP requests to the Python backend server.
 * Uses the global Logger for request/response logging.
 * 
 * Files linking:
 *   - app.js imports and uses API methods
 *   - Depends on: logger.js (global Logger)
 * 
 * Endpoints:
 *   GET /levels        - List all available levels
 *   GET /level/:name   - Get specific level data
 *   GET /data/:file    - Get data JSON files
 *   GET /tileset/:name - Get tileset color data
 *   POST /export-level - Export level back to ROM
 */

const API = (function() {
    'use strict';
    
    const BASE = '';
    const TIMEOUT = 30000;
    
    async function request(method, path, data = null) {
        const options = {
            method: method,
            headers: {}
        };
        
        if (data && method === 'POST') {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(data);
        }
        
        Logger.debug('API', `${method} ${path}`);
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);
            options.signal = controller.signal;
            
            const response = await fetch(BASE + path, options);
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const json = await response.json();
                Logger.debug('API', `${method} ${path} -> OK (JSON)`);
                return json;
            } else {
                const text = await response.text();
                Logger.debug('API', `${method} ${path} -> OK (text)`);
                return text;
            }
        } catch (error) {
            Logger.error('API', `${method} ${path} -> Error: ${error.message}`);
            throw error;
        }
    }
    
    // Public API
    return {
        /**
         * Get list of all available levels
         * @returns {Promise<Array>} Array of level objects
         */
        getLevels: function() {
            return request('GET', '/levels');
        },
        
        /**
         * Get data for a specific level
         * @param {string} name - Level name
         * @returns {Promise<Object>} Level data with tiles array
         */
        getLevel: function(name) {
            return request('GET', '/level/' + encodeURIComponent(name));
        },
        
        /**
         * Get data file (ENEMIES.json, TILES.json, etc.)
         * @param {string} filename - Name of data file
         * @returns {Promise<Object>} Parsed JSON data
         */
        getDataFile: function(filename) {
            return request('GET', '/data/' + filename);
        },
        
        /**
         * Get tileset color palette from ROM
         * @param {string} name - Tileset name (main_1, borg, bug, etc.)
         * @returns {Promise<Object>} Tileset data with RGB colors
         */
        getTileset: function(name) {
            return request('GET', '/tileset/' + encodeURIComponent(name));
        },
        
        /**
         * Get all possible tilesets from ROM
         * @returns {Promise<Array>} Array of tileset objects
         */
        getAllTilesets: function() {
            return request('GET', '/tilesets');
        },

        /**
         * Get all boss battles from ROM
         * @returns {Promise<Object>} Boss data with metadata
         */
        getBosses: function() {
            return request('GET', '/bosses');
        },

        /**
         * Export level data back to ROM
         * @param {Object} levelData - Level data to export
         * @returns {Promise<Object>} Export result
         */
        exportLevel: function(levelData) {
            return request('POST', '/export-level', levelData);
        },
        
        /**
         * Test connection to server
         * @returns {Promise<boolean>} True if server is reachable
         */
        ping: async function() {
            try {
                await request('GET', '/');
                return true;
            } catch {
                return false;
            }
        }
    };
})();

// Export to window for global access
window.API = API;
