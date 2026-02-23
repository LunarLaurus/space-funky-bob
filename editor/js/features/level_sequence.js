/**
 * Level Sequence Viewer for Space Funky B.O.B. Level Editor
 * 
 * Displays level progression sequences (themapsequence1/2/3).
 * NEW FEATURE - Source-verified from INITLEVE.A
 */

(function() {
    'use strict';
    
    // World sequences from INITLEVE.A:themapsequence1/2/3
    const WORLD_SEQUENCES = {
        0: [0, 1, 2, 9, 4, 22, 6, 5, 14, 20, 21, 18, 13, 11],  // 14 levels
        1: [23, 15, 7, 24, 16, 51, 19, 29, 32, 55, 25, 3, 27, 28, 33, 30, 26, 40, 34],  // 19 levels
        2: [35, 48, 36, 38, 43, 53, 47, 44, 37, 49, 56, 52, 12, 50, 10, 54, 59]  // 17 levels
    };
    
    /**
     * Initialize level sequence viewer
     * @param {string} containerId - Container element ID
     */
    function initLevelSequenceViewer(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn('Level sequence viewer container not found:', containerId);
            return;
        }
        
        container.innerHTML = `
            <div class="level-sequence-viewer">
                <h3>Level Progression Sequences</h3>
                <p class="source-note">Source: INITLEVE.A - themapsequence1/2/3 tables</p>
                <div class="sequences">
                    <div class="sequence" data-world="0">
                        <h4>World 0 (14 levels)</h4>
                        <div class="sequence-list"></div>
                    </div>
                    <div class="sequence" data-world="1">
                        <h4>World 1 (19 levels)</h4>
                        <div class="sequence-list"></div>
                    </div>
                    <div class="sequence" data-world="2">
                        <h4>World 2 (17 levels)</h4>
                        <div class="sequence-list"></div>
                    </div>
                </div>
            </div>
        `;
        
        // Populate sequences
        renderSequences();
    }
    
    /**
     * Render level sequences
     */
    function renderSequences() {
        Object.keys(WORLD_SEQUENCES).forEach(worldId => {
            const sequenceEl = document.querySelector(`.sequence[data-world="${worldId}"]`);
            if (!sequenceEl) return;
            
            const listEl = sequenceEl.querySelector('.sequence-list');
            const sequence = WORLD_SEQUENCES[worldId];
            
            listEl.innerHTML = sequence.map((mapNum, index) => `
                <span class="sequence-item" data-map="${mapNum}" data-index="${index}">
                    ${index + 1}: Map ${mapNum}
                </span>
            `).join('');
            
            // Add click handlers
            listEl.querySelectorAll('.sequence-item').forEach(item => {
                item.addEventListener('click', () => {
                    const mapNum = parseInt(item.dataset.map);
                    loadLevel(mapNum);
                });
            });
        });
    }
    
    /**
     * Load level by map number
     * @param {number} mapNumber - Map number
     */
    function loadLevel(mapNumber) {
        if (window.API) {
            window.API.getLevel(`map_${mapNumber.toString().padStart(3, '0')}`)
                .then(data => {
                    if (window.LevelData) {
                        window.LevelData.loadLevel(data);
                        window.dispatchEvent(new CustomEvent('levelchange'));
                    }
                })
                .catch(error => {
                    console.error('Failed to load level:', error);
                });
        }
    }
    
    /**
     * Get sequence for world
     * @param {number} worldId - World ID
     * @returns {Array} Level sequence
     */
    function getSequence(worldId) {
        return WORLD_SEQUENCES[worldId] || [];
    }
    
    /**
     * Get all sequences
     * @returns {Object} All world sequences
     */
    function getAllSequences() {
        return WORLD_SEQUENCES;
    }
    
    /**
     * Get total level count
     * @returns {number} Total levels across all worlds
     */
    function getTotalLevels() {
        return Object.values(WORLD_SEQUENCES).reduce((sum, seq) => sum + seq.length, 0);
    }
    
    // Export to window
    window.LevelSequenceViewer = {
        initLevelSequenceViewer,
        renderSequences,
        loadLevel,
        getSequence,
        getAllSequences,
        getTotalLevels
    };
    
})();
