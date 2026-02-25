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
                <div class="viewer-header">
                    <h2>Level Progression</h2>
                    <span class="source-tag">Source: INITLEVE.A - themapsequence1/2/3</span>
                </div>
                <div class="world-stats">
                    <div class="stat">
                        <span class="stat-value">50</span>
                        <span class="stat-label">Total Levels</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">3</span>
                        <span class="stat-label">Worlds</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">14/19/17</span>
                        <span class="stat-label">Levels per World</span>
                    </div>
                </div>
                <div class="sequences-grid">
                    <div class="sequence-card world-0" data-world="0">
                        <div class="sequence-header">
                            <h3>World 0</h3>
                            <span class="level-count">14 levels</span>
                        </div>
                        <div class="sequence-subtitle">Borg Factory / Bug Planet</div>
                        <div class="sequence-list"></div>
                    </div>
                    <div class="sequence-card world-1" data-world="1">
                        <div class="sequence-header">
                            <h3>World 1</h3>
                            <span class="level-count">19 levels</span>
                        </div>
                        <div class="sequence-subtitle">Ancient Ruins / Lava</div>
                        <div class="sequence-list"></div>
                    </div>
                    <div class="sequence-card world-2" data-world="2">
                        <div class="sequence-header">
                            <h3>World 2</h3>
                            <span class="level-count">17 levels</span>
                        </div>
                        <div class="sequence-subtitle">Ultra Force / Bubble Forest</div>
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
            const sequenceEl = document.querySelector(`.sequence-card[data-world="${worldId}"]`);
            if (!sequenceEl) return;

            const listEl = sequenceEl.querySelector('.sequence-list');
            const sequence = WORLD_SEQUENCES[worldId];

            listEl.innerHTML = sequence.map((mapNum, index) => `
                <button class="sequence-btn" data-map="${mapNum}" data-index="${index}" title="Map ${mapNum}">
                    <span class="seq-num">${index + 1}</span>
                    <span class="seq-map">${mapNum}</span>
                </button>
            `).join('');

            // Add click handlers
            listEl.querySelectorAll('.sequence-btn').forEach(item => {
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
