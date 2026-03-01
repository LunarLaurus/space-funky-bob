/**
 * Global Logging System
 * 
 * Provides centralized logging with:
 * - Log levels (debug, info, warn, error)
 * - Optional on-screen log panel (toggle with Ctrl+L)
 * - Timestamps
 * - Module filtering
 * 
 * Usage:
 *   Logger.info('module', 'message')
 *   Logger.error('module', 'message')
 *   Logger.debug('module', 'message')
 * 
 * Files linking:
 *   - app.js imports and uses Logger
 *   - api.js imports and uses Logger  
 *   - renderer.js imports and uses Logger
 */

const Logger = (function() {
    'use strict';
    
    const LEVELS = {
        debug: 0,
        info: 1,
        warn: 2,
        error: 3
    };
    
    let currentLevel = 'debug';  // Changed to debug to show all logs
    let showPanel = false;
    let logHistory = [];
    const MAX_HISTORY = 100;
    
    function formatTime() {
        const now = new Date();
        return now.toTimeString().split(' ')[0] + '.' + 
               String(now.getMilliseconds()).padStart(3, '0');
    }
    
    function createEntry(level, module, message) {
        return {
            time: formatTime(),
            level: level,
            module: module,
            message: message,
            timestamp: Date.now()
        };
    }
    
    function shouldLog(level) {
        return LEVELS[level] >= LEVELS[currentLevel];
    }
    
    function addToHistory(entry) {
        logHistory.push(entry);
        if (logHistory.length > MAX_HISTORY) {
            logHistory.shift();
        }
    }
    
    function renderToPanel(entry) {
        let panel = document.getElementById('logPanel');
        if (!panel) {
            panel = document.createElement('div');
            panel.id = 'logPanel';
            document.body.appendChild(panel);
        }
        
        const div = document.createElement('div');
        div.className = 'log-entry ' + entry.level;
        div.textContent = `[${entry.time}] [${entry.level.toUpperCase()}] [${entry.module}] ${entry.message}`;
        
        panel.appendChild(div);
        panel.scrollTop = panel.scrollHeight;
    }
    
    function log(level, module, message) {
        if (!shouldLog(level)) return;
        
        const entry = createEntry(level, module, message);
        addToHistory(entry);
        
        // Console output
        const prefix = `[${entry.time}] [${module}]`;
        switch (level) {
            case 'debug':
                console.debug(prefix, message);
                break;
            case 'info':
                console.info(prefix, message);
                break;
            case 'warn':
                console.warn(prefix, message);
                break;
            case 'error':
                console.error(prefix, message);
                break;
        }
        
        // Panel output
        if (showPanel) {
            renderToPanel(entry);
        }
    }
    
    // Public API
    return {
        debug: function(module, message) { log('debug', module, message); },
        info: function(module, message) { log('info', module, message); },
        warn: function(module, message) { log('warn', module, message); },
        error: function(module, message) { log('error', module, message); },
        
        setLevel: function(level) {
            if (LEVELS.hasOwnProperty(level)) {
                currentLevel = level;
                log('info', 'Logger', 'Log level set to: ' + level);
            }
        },
        
        togglePanel: function() {
            showPanel = !showPanel;
            const panel = document.getElementById('logPanel');
            if (panel) {
                panel.classList.toggle('visible', showPanel);
            }
            if (showPanel) {
                // Re-render history
                const panel = document.getElementById('logPanel');
                if (panel) {
                    panel.innerHTML = '';
                    logHistory.forEach(renderToPanel);
                }
            }
            return showPanel;
        },
        
        clear: function() {
            logHistory = [];
            const panel = document.getElementById('logPanel');
            if (panel) panel.innerHTML = '';
        },
        
        getHistory: function() {
            return [...logHistory];
        }
    };
})();

// Auto-init: Toggle log panel with Ctrl+L
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        Logger.togglePanel();
    }
});

Logger.info('Logger', 'Global logging initialized. Press Ctrl+L to toggle log panel.');
