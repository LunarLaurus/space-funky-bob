/**
 * Boss Viewer for Space Funky B.O.B. Level Editor
 * 
 * Displays 10 boss battles with stats.
 * NEW FEATURE - Source-verified from INITLEVE.A:fightboss
 */

(function() {
    'use strict';
    
    // 10 boss battles from source
    const BOSSES = [
        { id: 1, name: 'Popeye Boss', level: 3, category: 'ancient', hp: 48 },
        { id: 2, name: 'Queen Bug', level: 13, category: 'bug', hp: 48 },
        { id: 3, name: 'Snake Boss', level: 14, category: 'borg', hp: 48 },
        { id: 4, name: 'Spider Boss', level: 17, category: 'borg', hp: 48 },
        { id: 5, name: 'Ancient Boss', level: 31, category: 'ancient', hp: 48 },
        { id: 6, name: 'Lava Boss', level: 33, category: 'lava', hp: 48 },
        { id: 7, name: 'Screen Lifter', level: 40, category: 'borg', hp: 48 },
        { id: 8, name: 'Puss Boss', level: 52, category: 'ultra', hp: 48 },
        { id: 9, name: 'Mutoid Man', level: 53, category: 'ultra', hp: 48 },
        { id: 10, name: 'Ultra Boss', level: 54, category: 'ultra', hp: 48 }
    ];
    
    /**
     * Initialize boss viewer
     * @param {string} containerId - Container element ID
     */
    async function initBossViewer(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn('Boss viewer container not found:', containerId);
            return;
        }
        
        // Load boss data from API or use static data
        let bossData;
        if (window.API) {
            bossData = await window.API.getBosses();
        } else {
            bossData = { bosses: BOSSES };
        }
        
        renderBossCards(bossData.bosses || BOSSES);
    }
    
    /**
     * Render boss cards
     * @param {Array} bosses - Boss list
     */
    function renderBossCards(bosses) {
        const container = document.getElementById('boss-viewer');
        if (!container) return;
        
        container.innerHTML = '';
        
        bosses.forEach(boss => {
            const card = document.createElement('div');
            card.className = 'boss-card';
            card.dataset.bossId = boss.id;
            
            card.innerHTML = `
                <h3>${boss.name}</h3>
                <div class="boss-stats">
                    <div>Level: ${boss.level}</div>
                    <div>Category: ${boss.category}</div>
                    <div>HP: ${boss.hp}</div>
                </div>
                <div class="boss-sounds">
                    ${boss.sounds ? boss.sounds.map(s => `<span class="sound-tag">${s}</span>`).join('') : ''}
                </div>
            `;
            
            container.appendChild(card);
        });
    }
    
    /**
     * Get boss by ID
     * @param {number} bossId - Boss ID
     * @returns {Object|null} Boss data
     */
    function getBossById(bossId) {
        return BOSSES.find(b => b.id === bossId) || null;
    }
    
    /**
     * Get all bosses
     * @returns {Array} Boss list
     */
    function getAllBosses() {
        return BOSSES;
    }
    
    /**
     * Get bosses by category
     * @param {string} category - Category filter
     * @returns {Array} Filtered boss list
     */
    function getBossesByCategory(category) {
        return BOSSES.filter(b => b.category === category);
    }
    
    // Export to window
    window.BossViewer = {
        initBossViewer,
        renderBossCards,
        getBossById,
        getAllBosses,
        getBossesByCategory
    };
    
})();
