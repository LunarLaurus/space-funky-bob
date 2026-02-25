/**
 * Space Funky B.O.B. Level Editor - Main Application
 * 
 * This is the main entry point that orchestrates the editor.
 * 
 * Architecture (file linking):
 *   index.html -> Loads these JS files in order:
 *     1. js/logger.js    - Global logging system
 *     2. js/api.js       - Server API calls (uses Logger)
 *     3. js/renderer.js  - Canvas rendering (uses Logger)
 *     4. js/app.js       - Main app logic (uses API, Renderer, Logger)
 * 
 * Data flow:
 *   User clicks level -> API.getLevel() -> Renderer.renderCanvas()
 *   User paints tile -> levelData updated -> Renderer.renderCanvas()
 *   User exports -> API.exportLevel() -> Server writes ROM
 * 
 * Configuration:
 *   - APP_CONFIG: Global constants (map size, tile size, etc.)
 *   - Logger: Global logging (Ctrl+L to toggle panel)
 */

(function() {
    'use strict';
    
    // =========================================================================
    // CONFIGURATION
    // =========================================================================
    
    // Global configuration constants
    window.APP_CONFIG = {
        MAP_WIDTH: 80,
        MAP_HEIGHT: 80,
        TILE_SIZE: 8,
        MAX_HISTORY: 20
    };
    
    // =========================================================================
    // APPLICATION STATE
    // =========================================================================
    
    // Calculate appropriate zoom for screen size
    function getInitialZoom() {
        const screenWidth = window.innerWidth;
        if (screenWidth > 1800) return 3;
        if (screenWidth > 1400) return 2;
        return 1;
    }
    
    const App = {
        // Current state
        editorData: null,
        currentMap: null,
        currentLevelData: null,
        
        // Editor state
        selectedTile: 1,
        zoom: getInitialZoom(),
        showGrid: false,
        snapToGrid: true,
        currentLayer: 'background',
        showEnemies: false,
        isDrawing: false,
        
        // Level data
        levelData: {
            background: [],
            foreground: [],
            enemies: [],
            metadata: {}
        },
        
        // Data viewer state
        dataExpanded: {},
        
        // History (undo/redo)
        undoStack: [],
        redoStack: [],
        
        // Tileset
        currentTileset: 'main_1',
        tileColors: [],
        tilesetData: null
    };
    
    // =========================================================================
    // INITIALIZATION
    // =========================================================================
    
    async function init() {
        Logger.info('App', 'Initializing Space Funky B.O.B. Level Editor');
        
        // Initialize renderer with canvas references
        Renderer.init('levelCanvas', 'minimap');
        
        // Load initial data
        await loadInitialData();
        
        // Setup event listeners
        setupEventListeners();
        
        // Setup keyboard shortcuts
        setupKeyboardShortcuts();
        
        // Update zoom display
        document.getElementById('zoomDisplay').textContent = App.zoom + 'x';
        
        // Setup modal buttons
        document.getElementById('btnTileViewer').onclick = openTileViewer;
        document.getElementById('btnAudio').onclick = openAudioModal;
        // Docs button opens wiki in new tab
        document.getElementById('btnDocs').onclick = () => {
            window.open('/wiki.html', '_blank');
        };
        
        // Test audio button
        document.getElementById('testAudioBtn').onclick = function() {
            alert('TEST AUDIO CLICKED!');
            console.log('TEST AUDIO CLICKED!');
        };
        
        Logger.info('App', 'Editor ready');
    }
    
    // Tile Viewer
    window.openTileViewer = async function() {
        const modal = document.getElementById('tileViewerModal');
        const select = document.getElementById('tileViewerTileset');
        
        // Populate tileset dropdown
        select.innerHTML = '<option value="">Select tileset...</option>';
        
        try {
            const data = await API.getAllTilesets();
            data.tilesets.forEach(ts => {
                const opt = document.createElement('option');
                opt.value = ts.offset;
                opt.textContent = ts.name + ` (variance: ${ts.variance.toFixed(1)})`;
                select.appendChild(opt);
            });
        } catch(e) {
            Logger.error('App', 'Failed to load tilesets: ' + e.message);
        }
        
        modal.style.display = 'block';
    };
    
    window.renderTileViewer = async function() {
        const select = document.getElementById('tileViewerTileset');
        const offset = select.value;
        
        if (!offset) return;
        
        const grid = document.getElementById('tileViewerGrid');
        grid.innerHTML = '<div style="color:var(--accent);grid-column:1/-1;text-align:center;padding:20px;">Loading...</div>';
        
        try {
            const response = await fetch('/tileset/custom?offset=' + offset);
            const data = await response.json();
            
            grid.innerHTML = '';
            data.tiles.forEach(tile => {
                const cvs = document.createElement('canvas');
                cvs.width = 8;
                cvs.height = 8;
                cvs.style.width = '40px';
                cvs.style.height = '40px';
                cvs.style.imageRendering = 'pixelated';
                cvs.title = 'Tile ' + tile.id;
                
                const ctx = cvs.getContext('2d');
                const palette = tile.palette;
                const pixels = tile.pixels;
                
                // pixels is array of 64 palette indices
                for (let i = 0; i < 64; i++) {
                    const x = i % 8;
                    const y = Math.floor(i / 8);
                    const colorIdx = pixels[i] || 0;
                    const rgb = palette[colorIdx] || [0, 0, 0];
                    ctx.fillStyle = `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
                    ctx.fillRect(x, y, 1, 1);
                }
                
                grid.appendChild(cvs);
            });
        } catch(e) {
            grid.innerHTML = '<div style="color:red;grid-column:1/-1;">Error: ' + e.message + '</div>';
        }
    };
    
    // Make globally accessible for debugging
    window.testAudio = async function() {
        console.log('[Audio] testAudio called');
        const ok = await initAudio();
        console.log('[Audio] testAudio result:', ok, 'Tone:', !!window.Tone, 'Synth:', !!audioSynth, 'Context:', !!audioContext);
        if (audioSynth && window.Tone) {
            const now = Tone.now();
            audioSynth.triggerAttackRelease("C4", "8n", now);
            console.log('[Audio] Played C4 via Tone');
        } else if (audioContext) {
            playFallbackSound();
            console.log('[Audio] Played via fallback');
        }
    };
    
    // Audio Modal
    let audioSynth = null;
    let audioInitialized = false;
    let audioContext = null;
    let toneLoaded = false;

    async function loadToneJS() {
        if (toneLoaded) return true;
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/tone@14.8.49/build/Tone.js';
            script.onload = () => {
                console.log('[Audio] Tone.js loaded');
                toneLoaded = true;
                resolve(true);
            };
            script.onerror = () => {
                console.error('[Audio] Failed to load Tone.js');
                resolve(false);
            };
            document.head.appendChild(script);
        });
    }

    // Play MIDI using JZZ
    async function playMIDI(midiUrl, name) {
        console.log('[Audio] playMIDI start:', midiUrl);
        alert('Attempting to play: ' + name);
        
        // Load JZZ
        if (!window.JZZ) {
            console.log('[Audio] Loading JZZ...');
            alert('Loading JZZ library...');
            await new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = 'https://jazz-soft.net/download/JZZ.js';
                script.onload = () => { alert('JZZ loaded'); resolve(); };
                script.onerror = () => { alert('JZZ failed to load'); reject(); };
                document.head.appendChild(script);
            });
        }
        
        if (!window.JZZ) {
            alert('JZZ not available. Download the file instead.');
            return;
        }
        
        try {
            console.log('[Audio] Fetching MIDI...');
            alert('Fetching: ' + midiUrl);
            const response = await fetch(midiUrl);
            const arrayBuffer = await response.arrayBuffer();
            const midiData = new Uint8Array(arrayBuffer);
            
            console.log('[Audio] Creating JZZ engine...');
            alert('Creating MIDI engine...');
            const port = await JZZ().openMidiOut();
            const engine = JZZ(midiData);
            engine.connect(port);
            engine.play();
            
            console.log('[Audio] Playing:', name);
            alert('Now playing: ' + name);
        } catch (e) {
            console.error('[Audio] Error:', e);
            alert('Error: ' + e.message);
        }
    }

    async function initAudio() {
        if (audioInitialized && (audioSynth || audioContext)) return true;
        console.log('[Audio] initAudio called');
        
        // Load Tone.js lazily
        await loadToneJS();
        
        try {
            // First resume any suspended AudioContext
            if (audioContext && audioContext.state === 'suspended') {
                await audioContext.resume();
                console.log('[Audio] Resumed suspended AudioContext');
            }
            
            if (!window.Tone) {
                console.log('[Audio] Tone.js not loaded, using Web Audio API fallback');
                Logger.warn('App', 'Tone.js not loaded, using Web Audio API fallback');
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                audioInitialized = true;
                console.log('[Audio] Web Audio API initialized');
                return true;
            }
            console.log('[Audio] Tone.js detected, initializing...');
            // Create our own AudioContext with user gesture
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            await audioContext.resume();
            // Use it with Tone.js
            Tone.setContext(audioContext);
            audioSynth = new Tone.PolySynth(Tone.Synth, {
                oscillator: { type: "triangle" },
                envelope: { attack: 0.02, decay: 0.1, sustain: 0.3, release: 0.8 }
            }).toDestination();
            audioInitialized = true;
            Logger.info('App', 'Audio synthesizer initialized');
            console.log('[Audio] Tone.js synth initialized');
            return true;
        } catch (e) {
            console.log('[Audio] Tone init failed: ' + e.message);
            Logger.warn('App', 'Audio initialization failed: ' + e.message);
            try {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                await audioContext.resume();
                audioInitialized = true;
                Logger.info('App', 'Using Web Audio API fallback');
                console.log('[Audio] Web Audio API fallback initialized');
                return true;
            } catch (e2) {
                Logger.error('App', 'Web Audio API failed: ' + e2.message);
                console.log('[Audio] Web Audio API failed: ' + e2.message);
                return false;
            }
        }
    }

    function playFallbackSound() {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioContext.state === 'suspended') {
            audioContext.resume();
        }
        const osc = audioContext.createOscillator();
        const gain = audioContext.createGain();
        osc.connect(gain);
        gain.connect(audioContext.destination);
        osc.type = 'triangle';
        const now = audioContext.currentTime;
        osc.frequency.setValueAtTime(523.25, now); // C5
        osc.frequency.setValueAtTime(659.25, now + 0.15); // E5
        osc.frequency.setValueAtTime(783.99, now + 0.3); // G5
        osc.frequency.setValueAtTime(1046.5, now + 0.45); // C6
        gain.gain.setValueAtTime(0.3, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);
        osc.start(now);
        osc.stop(now + 0.6);
    }

    window.playDemoSound = async function() {
        const ok = await initAudio();
        if (audioSynth && window.Tone) {
            const now = Tone.now();
            audioSynth.triggerAttackRelease(["C4", "E4", "G4"], "8n", now);
            audioSynth.triggerAttackRelease(["D4", "F4", "A4"], "8n", now + 0.2);
            audioSynth.triggerAttackRelease(["C4", "E4", "G4", "C5"], "4n", now + 0.4);
        } else if (ok && audioContext) {
            playFallbackSound();
        }
    };

    window.openAudioModal = async function() {
        document.getElementById('audioModal').style.display = 'block';
        
        const list = document.getElementById('audioList');
        list.innerHTML = '<div style="color:var(--accent);padding:10px;">Loading audio files...</div>';
        
        try {
            const response = await fetch('/midi');
            const data = await response.json();
            Audio.renderAudioList(data.files);
        } catch (e) {
            list.innerHTML = '<div style="color:red;padding:10px;">Error loading: ' + e.message + '</div>';
            Logger.error('App', 'Failed to load MIDI files: ' + e.message);
        }
    };
    
    // Global function to load all tilesets from ROM
    window.loadAllTilesets = async function() {
        const list = document.getElementById('tilesetList');
        list.innerHTML = '<div style="color:var(--accent);padding:4px;">Scanning ROM...</div>';
        
        try {
            const data = await API.getAllTilesets();
            
            if (data.tilesets && data.tilesets.length > 0) {
                list.innerHTML = '';
                
                data.tilesets.forEach((ts, idx) => {
                    const div = document.createElement('div');
                    div.style.cssText = 'padding:4px 6px;margin:2px 0;background:var(--bg-toolbar);cursor:pointer;border-left:2px solid transparent;';
                    div.textContent = ts.name + ` (variance: ${ts.variance.toFixed(1)})`;
                    div.onclick = function() {
                        // Apply this tileset to the editor
                        loadTilesetByOffset(ts.offset);
                        // Highlight selected
                        document.querySelectorAll('#tilesetList div').forEach(d => d.style.borderLeftColor = 'transparent');
                        div.style.borderLeftColor = 'var(--accent)';
                    };
                    div.onmouseover = function() {
                        div.style.background = '#2a2a4e';
                    };
                    div.onmouseout = function() {
                        div.style.background = 'var(--bg-toolbar)';
                    };
                    list.appendChild(div);
                });
                
                setStatus('Found ' + data.tilesets.length + ' tileset candidates');
            } else {
                list.innerHTML = '<div style="color:var(--text-dim);padding:4px;">No tilesets found</div>';
            }
        } catch (e) {
            Logger.error('App', 'Failed to load tilesets: ' + e.message);
            list.innerHTML = '<div style="color:red;padding:4px;">Error: ' + e.message + '</div>';
        }
    };
    
    async function loadTilesetByOffset(offset) {
        // Convert offset to tileset name or load directly
        const hex = '0x' + offset.toString(16);
        Logger.info('App', 'Loading tileset at: ' + hex);
        
        // Use the server's handle_tileset but with offset
        try {
            const response = await fetch('/tileset/custom?offset=' + offset);
            const data = await response.json();
            
            App.currentTileset = 'custom_' + offset;
            App.tilesetData = data;
            
            // Store full tile pixel data for rendering
            App.tilesetTiles = data.tiles;
            
            // Initialize tile cache for performance
            Renderer.initTileCache(data.tiles, 'custom_' + offset);
            
            // Also create color fallback array
            App.tileColors = data.tiles.map(t => {
                if (t.palette) {
                    // Use first non-black color from palette as representative
                    const rgb = t.palette[1] || t.palette[0] || [128,128,128];
                    return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
                }
                return '#888';
            });
            
            if (App.currentLevelData) {
                renderAll();
            }
            
            setStatus('Applied tileset: ' + hex);
        } catch (e) {
            Logger.error('App', 'Failed to load tileset: ' + e.message);
        }
    }
    
    async function loadInitialData() {
        setStatus('Loading level data...');
        
        try {
            // Load default tileset
            await loadTileset('main_1');
            
            // Load levels list
            const levels = await API.getLevels();
            renderMapList(levels);
            
            setStatus('Ready - Select a level to edit');
        } catch (e) {
            Logger.error('App', 'Failed to load initial data: ' + e.message);
            setStatus('Error loading data - using offline mode');
            renderOfflineMapList();
        }
    }
    
    // =========================================================================
    // LEVEL LOADING
    // =========================================================================
    
    async function selectLevel(level, element, event) {
        Logger.info('App', 'Loading level: ' + level.name);
        
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        // Update UI
        document.querySelectorAll('.map-list li').forEach(l => l.classList.remove('active'));
        element.classList.add('active');
        
        setStatus(`Loading ${level.name}...`);
        
        try {
            // Fetch level data from server
            const data = await API.getLevel(level.name);
            Logger.debug('App', `Got ${data.tiles?.length || 0} tiles`);
            
            // Get enemy groups from LEVELS.json
            let enemies = await loadEnemyData(level.name);
            
            // Update app state
            App.levelData = {
                background: Array.isArray(data.tiles) ? data.tiles : [],
                foreground: Array.isArray(data.foreground) ? data.foreground : [],
                enemies: enemies,
                metadata: {
                    name: data.name || level.name,
                    theme: level.theme,
                    author: data.author || 'Unknown',
                    music: data.music || '0'
                }
            };
            
            App.currentLevelData = data;
            App.currentMap = level;
            
            // Clear history
            App.undoStack = [];
            App.redoStack = [];
            
            // Update UI
            updateLevelInfo();
            updateHistoryDisplay();
            renderAll();
            
            // Enable buttons
            document.getElementById('btnImport').disabled = false;
            document.getElementById('btnExport').disabled = false;
            
            setStatus(`Loaded: ${level.name}`);
            Logger.info('App', 'Level loaded: ' + level.name);
            
        } catch (e) {
            Logger.error('App', 'Failed to load level: ' + e.message);
            setStatus('Error loading level: ' + e.message);
        }
    }
    
    async function loadEnemyData(levelName) {
        let enemies = [];
        
        try {
            const levelsData = await API.getDataFile('LEVELS.json');
            const worlds = levelsData.worlds || [];
            
            for (const world of worlds) {
                const levels = world.levels || [];
                const levelInfo = levels.find(l => l.id === levelName);
                
                if (levelInfo && levelInfo.enemy_groups) {
                    levelInfo.enemy_groups.forEach((group, idx) => {
                        enemies.push({
                            x: 10 + (idx * 5) % 60,
                            y: 10 + (idx * 7) % 50,
                            type: group
                        });
                    });
                    break;
                }
            }
        } catch (e) {
            Logger.debug('App', 'No enemy data found');
        }
        
        return enemies;
    }
    
    // =========================================================================
    // TILESET LOADING
    // =========================================================================
    
    async function loadTileset(name) {
        Logger.info('App', 'Loading tileset: ' + name);
        
        try {
            const data = await API.getTileset(name);
            
            App.currentTileset = name;
            App.tilesetData = data;
            
            // Store full tile pixel data
            App.tilesetTiles = data.tiles;
            
            // Initialize tile cache for performance
            Renderer.initTileCache(data.tiles, name);
            
            // Create color fallback array
            App.tileColors = data.tiles.map(t => {
                if (t.palette && t.pixels) {
                    // Use a representative color from palette
                    const rgb = t.palette[1] || t.palette[0] || [128,128,128];
                    return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
                }
                if (t.rgb) {
                    const [r, g, b] = t.rgb;
                    return `rgb(${r},${g},${b})`;
                }
                return '#888';
            });
            
            // Re-render with new colors
            if (App.currentLevelData) {
                renderAll();
            }
            
            Logger.info('App', `Tileset loaded: ${data.tiles.length} tiles`);
            
        } catch (e) {
            Logger.error('App', 'Failed to load tileset: ' + e.message);
            // Use fallback palette
            App.tileColors = generateFallbackPalette();
        }
    }
    
    function generateFallbackPalette() {
        const colors = [];
        for (let r = 0; r < 6; r++) {
            for (let g = 0; g < 6; g++) {
                for (let b = 0; b < 6; b++) {
                    colors.push(`rgb(${r*51},${g*51},${b*51})`);
                }
            }
        }
        colors[0] = '#000000';
        for (let i = 216; i < 256; i++) {
            const g = ((i - 216) * 255) >> 5;
            colors[i] = `rgb(${g},${g},${g})`;
        }
        return colors.slice(0, 256);
    }
    
    // =========================================================================
    // RENDERING
    // =========================================================================
    
    function renderAll() {
        Logger.info('App', 'renderAll called - tiles: ' + (App.levelData.background?.length || 0) + ', colors: ' + (App.tileColors?.length || 0));
        Renderer.renderCanvas(App.levelData, getRenderConfig(), App.tileColors, App.tilesetTiles);
        Renderer.renderMinimap(App.levelData, App.tileColors, App.tilesetTiles);
        Renderer.renderTilesetPalette(App.tileColors, App.selectedTile, onTileSelect);
        Logger.info('App', 'renderAll complete');
    }
    
    function getRenderConfig() {
        return {
            zoom: App.zoom,
            showGrid: App.showGrid,
            snapToGrid: App.snapToGrid,
            currentLayer: App.currentLayer,
            showEnemies: App.showEnemies
        };
    }
    
    function onTileSelect(index, element) {
        App.selectedTile = index;
        
        // Update UI
        document.querySelectorAll('.tile').forEach(t => t.classList.remove('selected'));
        if (element) element.classList.add('selected');
        
        updateStatusTile();
    }
    
    // =========================================================================
    // UI UPDATES
    // =========================================================================
    
    function updateLevelInfo() {
        const meta = App.levelData.metadata;
        
        document.getElementById('levelName').textContent = meta.name || '-';
        document.getElementById('levelTheme').textContent = meta.theme || '-';
        
        const bgCount = App.levelData.background.length;
        const fgCount = App.levelData.foreground.length;
        document.getElementById('levelTiles').textContent = `${bgCount} BG / ${fgCount} FG`;
        
        const size = (bgCount + fgCount) * 3;
        document.getElementById('levelSize').textContent = `${size} bytes`;
        
        // Update metadata form
        document.getElementById('metaName').value = meta.name || '';
        document.getElementById('metaTheme').value = meta.theme || 'Ancient';
        document.getElementById('metaAuthor').value = meta.author || '';
        document.getElementById('metaMusic').value = meta.music || '0';
    }
    
    function updateHistoryDisplay() {
        document.getElementById('btnUndo').disabled = App.undoStack.length === 0;
        document.getElementById('btnRedo').disabled = App.redoStack.length === 0;
        document.getElementById('statusHistory').textContent = 
            `${App.undoStack.length}/${window.APP_CONFIG.MAX_HISTORY}`;
    }
    
    function updateStatusTile() {
        document.getElementById('statusTile').textContent = 
            `Tile ${App.selectedTile} (0x${App.selectedTile.toString(16).toUpperCase()})`;
    }
    
    function setStatus(message) {
        document.getElementById('status').textContent = message;
    }
    
    // =========================================================================
    // LEVEL LIST RENDERING
    // =========================================================================
    
    function renderMapList(levels) {
        const list = document.getElementById('mapList');
        list.innerHTML = '';
        
        // Group by theme
        const categories = {};
        levels.forEach(level => {
            if (!categories[level.theme]) {
                categories[level.theme] = [];
            }
            categories[level.theme].push(level);
        });
        
        // Render categories
        for (const [theme, levelsInCat] of Object.entries(categories)) {
            const header = document.createElement('li');
            header.className = 'cat-header';
            header.textContent = theme;
            list.appendChild(header);
            
            levelsInCat.forEach(level => {
                const li = document.createElement('li');
                li.textContent = level.name;
                li.onclick = (e) => selectLevel(level, li, e);
                list.appendChild(li);
            });
        }
    }
    
    function renderOfflineMapList() {
        const list = document.getElementById('mapList');
        list.innerHTML = `
            <li class="cat-header">Ancient</li>
            <li data-theme="Ancient">ANC1</li>
            <li class="cat-header">Borg</li>
            <li data-theme="Borg">BORG1</li>
            <li class="cat-header">Bug</li>
            <li data-theme="Bug">BUG1</li>
            <li class="cat-header">Lava</li>
            <li data-theme="Lava">LAVA1</li>
        `;
    }
    
    // =========================================================================
    // EVENT LISTENERS
    // =========================================================================
    
    function setupEventListeners() {
        // Toolbar buttons
        document.getElementById('btnUndo').onclick = undo;
        document.getElementById('btnRedo').onclick = redo;
        document.getElementById('btnZoomIn').onclick = () => { App.zoom = Math.min(App.zoom + 1, 8); renderAll(); };
        document.getElementById('btnZoomOut').onclick = () => { App.zoom = Math.max(App.zoom - 1, 1); renderAll(); };
        document.getElementById('btnGrid').onclick = () => { App.showGrid = !App.showGrid; renderAll(); };
        document.getElementById('btnSnap').onclick = () => { App.snapToGrid = !App.snapToGrid; };
        document.getElementById('btnShowEnemies').onclick = () => { App.showEnemies = !App.showEnemies; renderAll(); };
        
        // Tileset selector
        document.getElementById('tilesetSelect').onchange = (e) => loadTileset(e.target.value);
        
        // Import/Export
        document.getElementById('btnExport').onclick = exportLevel;
        document.getElementById('btnExportROM').onclick = exportToROM;
        
        // Data Reference click handlers
        document.querySelectorAll('#dataList li').forEach(li => {
            li.onclick = async () => {
                const filename = li.dataset.file;
                const viewer = document.getElementById('dataViewer');
                const title = document.getElementById('dataTitle');
                const content = document.getElementById('dataContent');
                
                document.querySelectorAll('#dataList li').forEach(l => { l.style.background = ''; l.style.color = ''; });
                li.style.background = 'var(--accent)';
                li.style.color = '#000';
                
                viewer.style.display = 'block';
                title.textContent = filename;
                content.innerHTML = '<div style="color:var(--accent)">Loading...</div>';
                
                try {
                    const resp = await fetch('/data/' + filename);
                    const raw = await resp.json();
                    
                    let items = Array.isArray(raw) ? raw : (raw.tiles || raw.enemies || raw.worlds || raw.tilesets || []);
                    
                    App.dataExpanded[filename] = App.dataExpanded[filename] || {};
                    const expanded = App.dataExpanded[filename];
                    
                    function renderRows(type, fields) {
                        let html = '<table style="width:100%;font-size:9px;border-collapse:collapse;">';
                        html += '<tr style="background:var(--bg-toolbar);position:sticky;top:0;">';
                        fields.forEach(f => { html += `<th>${f.label}</th>`; });
                        html += '</tr>';
                        
                        items.forEach((item, idx) => {
                            const isExpanded = expanded[idx];
                            const rowStyle = isExpanded 
                                ? 'background:var(--bg-selection);' 
                                : 'cursor:pointer;';
                            const rowClick = `onclick="toggleRow(${idx})"`;
                            
                            html += `<tr class="data-row" data-idx="${idx}" style="${rowStyle}" ${rowClick}>`;
                            fields.forEach(f => { 
                                html += `<td>${item[f.key] !== undefined ? item[f.key] : '-'}</td>`; 
                            });
                            html += '</tr>';
                            
                            if (isExpanded) {
                                html += `<tr class="detail-row" data-parent="${idx}" style="background:var(--bg-dark);"><td colspan="${fields.length}">`;
                                html += '<div style="padding:8px;font-size:9px;">';
                                Object.entries(item).forEach(([k, v]) => {
                                    if (!fields.some(f => f.key === k)) {
                                        html += `<div><span style="color:var(--accent)">${k}:</span> ${JSON.stringify(v)}</div>`;
                                    }
                                });
                                html += '</div></td></tr>';
                            }
                        });
                        html += '</table>';
                        return html;
                    }
                    
                    let html = '';
                    
                    if (filename === 'ENEMIES.json') {
                        const fields = [
                            {key:'id',label:'ID'}, {key:'name',label:'Name'}, {key:'category',label:'Category'},
                            {key:'behavior',label:'Behavior'}, {key:'health',label:'Health'}, {key:'speed',label:'Speed'}, {key:'tiles_used',label:'Tiles'}
                        ];
                        html = renderRows('enemy', fields);
                    } else if (filename === 'TILES.json') {
                        const fields = [{key:'id',label:'ID'}, {key:'name',label:'Name'}, {key:'type',label:'Type'}];
                        items.forEach((t, idx) => {
                            const isExpanded = expanded[idx];
                            const rowStyle = isExpanded ? 'background:var(--bg-selection);' : 'cursor:pointer;';
                            html += `<div class="data-row" data-idx="${idx}" style="${rowStyle}padding:4px;border-bottom:1px solid var(--border);" onclick="toggleRow(${idx})">`;
                            html += `<span>${t.id}</span> | <span>${t.name||'-'}</span> | <span>${t.type||'-'}</span>`;
                            if (isExpanded) {
                                html += `<div style="padding:8px;margin-top:4px;background:var(--bg-dark);">`;
                                Object.entries(t).forEach(([k,v]) => {
                                    if (!['id','name','type'].includes(k)) {
                                        html += `<div><span style="color:var(--accent)">${k}:</span> ${JSON.stringify(v)}</div>`;
                                    }
                                });
                                html += '</div>';
                            }
                            html += '</div>';
                        });
                    } else if (filename === 'LEVELS.json') {
                        if (raw.worlds) {
                            raw.worlds.forEach((w, idx) => {
                                const isExpanded = expanded[idx];
                                const rowStyle = isExpanded ? 'background:var(--bg-selection);' : 'cursor:pointer;';
                                html += `<div class="data-row" data-idx="${idx}" style="${rowStyle}padding:4px;border-bottom:1px solid var(--border);" onclick="toggleRow(${idx})">`;
                                html += `<span style="color:var(--accent)">${w.name}</span>`;
                                if (isExpanded) {
                                    html += `<div style="padding:8px;margin-top:4px;background:var(--bg-dark);">`;
                                    Object.entries(w).forEach(([k,v]) => {
                                        html += `<div><span style="color:var(--accent)">${k}:</span> ${JSON.stringify(v)}</div>`;
                                    });
                                    html += '</div>';
                                }
                                html += '</div>';
                            });
                        }
                    } else if (filename === 'TILESETS.json') {
                        const fields = [{key:'id',label:'ID'}, {key:'name',label:'Name'}, {key:'rom_offset',label:'Offset'}, {key:'num_tiles',label:'Tiles'}, {key:'format',label:'Format'}];
                        html = renderRows('tileset', fields);
                    }
                    
                    content.innerHTML = html;
                    window.toggleRow = (idx) => { 
                        expanded[idx] = !expanded[idx]; 
                        const detailRow = content.querySelector(`.detail-row[data-parent="${idx}"]`);
                        const dataRow = content.querySelector(`.data-row[data-idx="${idx}"]`);
                        if (detailRow) {
                            detailRow.style.display = expanded[idx] ? 'table-row' : 'none';
                            if (dataRow) dataRow.style.background = expanded[idx] ? 'var(--bg-selection)' : '';
                        }
                    };
                } catch (e) {
                    content.innerHTML = '<div style="color:red">Error: ' + e.message + '</div>';
                }
            };
        });
        
        // Layer tabs
        document.querySelectorAll('.layer-tab').forEach(tab => {
            tab.onclick = () => {
                document.querySelectorAll('.layer-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                App.currentLayer = tab.dataset.layer;
                renderAll();
            };
        });
        
        // Canvas events (painting)
        const canvas = document.getElementById('levelCanvas');
        canvas.addEventListener('mousedown', onCanvasMouseDown);
        canvas.addEventListener('mousemove', onCanvasMouseMove);
        canvas.addEventListener('mouseup', () => App.isDrawing = false);
        canvas.addEventListener('mouseleave', () => App.isDrawing = false);
        
        // Metadata form
        ['metaName', 'metaTheme', 'metaAuthor', 'metaMusic'].forEach(id => {
            document.getElementById(id).addEventListener('change', (e) => {
                const key = id.replace('meta', '').toLowerCase();
                App.levelData.metadata[key] = e.target.value;
            });
        });
        
        // Grid button toggle
        document.getElementById('btnGrid').onclick = () => {
            App.showGrid = !App.showGrid;
            document.getElementById('btnGrid').classList.toggle('active', App.showGrid);
            renderAll();
        };
        
        // Enemy button toggle
        document.getElementById('btnShowEnemies').onclick = () => {
            App.showEnemies = !App.showEnemies;
            document.getElementById('btnShowEnemies').classList.toggle('active', App.showEnemies);
            renderAll();
        };
        
        // Snap button toggle
        document.getElementById('btnSnap').onclick = () => {
            App.snapToGrid = !App.snapToGrid;
            document.getElementById('btnSnap').classList.toggle('active', App.snapToGrid);
        };
    }
    
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+L: Toggle log panel
            if (e.ctrlKey && e.key === 'l') {
                e.preventDefault();
                Logger.togglePanel();
                return;
            }
            // Ctrl+S: Save/Export
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                exportLevel();
            }
            // Ctrl+Z: Undo
            if (e.ctrlKey && e.key === 'z') {
                e.preventDefault();
                undo();
            }
            // Ctrl+Y: Redo
            if (e.ctrlKey && e.key === 'y') {
                e.preventDefault();
                redo();
            }
            // +/-: Zoom
            if (e.key === '+' || e.key === '=') {
                App.zoom = Math.min(App.zoom + 1, 8);
                renderAll();
            }
            if (e.key === '-') {
                App.zoom = Math.max(App.zoom - 1, 1);
                renderAll();
            }
            // G: Grid
            if (e.key === 'g' && !e.ctrlKey) {
                App.showGrid = !App.showGrid;
                document.getElementById('btnGrid').classList.toggle('active', App.showGrid);
                renderAll();
            }
            // S: Snap
            if (e.key === 's' && !e.ctrlKey) {
                App.snapToGrid = !App.snapToGrid;
                document.getElementById('btnSnap').classList.toggle('active', App.snapToGrid);
            }
            // 0-9: Quick tile select
            if (e.key >= '0' && e.key <= '9') {
                App.selectedTile = parseInt(e.key);
                updateStatusTile();
            }
        });
    }
    
    // =========================================================================
    // CANVAS PAINTING
    // =========================================================================
    
    function onCanvasMouseDown(e) {
        if (!App.currentLevelData) return;
        
        const rect = e.target.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / (window.APP_CONFIG.TILE_SIZE * App.zoom));
        const y = Math.floor((e.clientY - rect.top) / (window.APP_CONFIG.TILE_SIZE * App.zoom));
        
        if (x < 0 || x >= window.APP_CONFIG.MAP_WIDTH || y < 0 || y >= window.APP_CONFIG.MAP_HEIGHT) return;
        
        App.isDrawing = true;
        saveState();
        
        const tileToPaint = e.button === 2 ? 0 : App.selectedTile;
        paintTile(x, y, tileToPaint);
    }
    
    function onCanvasMouseMove(e) {
        // Update tile coordinates display
        const rect = e.target.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / (window.APP_CONFIG.TILE_SIZE * App.zoom));
        const y = Math.floor((e.clientY - rect.top) / (window.APP_CONFIG.TILE_SIZE * App.zoom));
        
        document.getElementById('tileCoords').textContent = 
            (x >= 0 && x < window.APP_CONFIG.MAP_WIDTH && y >= 0 && y < window.APP_CONFIG.MAP_HEIGHT)
                ? `X: ${x}, Y: ${y}` 
                : 'Outside canvas';
        
        // Paint while dragging
        if (App.isDrawing && App.currentLevelData) {
            if (x >= 0 && x < window.APP_CONFIG.MAP_WIDTH && y >= 0 && y < window.APP_CONFIG.MAP_HEIGHT) {
                const tileToPaint = e.buttons === 2 ? 0 : App.selectedTile;
                paintTile(x, y, tileToPaint);
            }
        }
    }
    
    function paintTile(x, y, tileId) {
        const tiles = App.currentLayer === 'background' 
            ? App.levelData.background 
            : App.levelData.foreground;
        
        const existingIndex = tiles.findIndex(t => t.x === x && t.y === y);
        
        if (tileId === 0) {
            // Erase
            if (existingIndex !== -1) {
                tiles.splice(existingIndex, 1);
            }
        } else {
            // Paint
            if (existingIndex !== -1) {
                tiles[existingIndex].tile = tileId;
            } else {
                tiles.push({ x, y, tile: tileId });
            }
        }
        
        renderAll();
        updateLevelInfo();
    }
    
    // =========================================================================
    // HISTORY (UNDO/REDO)
    // =========================================================================
    
    function saveState() {
        const state = JSON.stringify({
            background: App.levelData.background,
            foreground: App.levelData.foreground
        });
        
        App.undoStack.push(state);
        if (App.undoStack.length > window.APP_CONFIG.MAX_HISTORY) {
            App.undoStack.shift();
        }
        App.redoStack = [];
        updateHistoryDisplay();
    }
    
    function undo() {
        if (App.undoStack.length === 0) return;
        
        const currentState = JSON.stringify({
            background: App.levelData.background,
            foreground: App.levelData.foreground
        });
        App.redoStack.push(currentState);
        
        const prevState = JSON.parse(App.undoStack.pop());
        App.levelData.background = prevState.background;
        App.levelData.foreground = prevState.foreground;
        
        updateHistoryDisplay();
        renderAll();
        updateLevelInfo();
        setStatus('Undo');
    }
    
    function redo() {
        if (App.redoStack.length === 0) return;
        
        const currentState = JSON.stringify({
            background: App.levelData.background,
            foreground: App.levelData.foreground
        });
        App.undoStack.push(currentState);
        
        const nextState = JSON.parse(App.redoStack.pop());
        App.levelData.background = nextState.background;
        App.levelData.foreground = nextState.foreground;
        
        updateHistoryDisplay();
        renderAll();
        updateLevelInfo();
        setStatus('Redo');
    }
    
    // =========================================================================
    // EXPORT
    // =========================================================================
    
    function exportLevel() {
        if (!App.currentLevelData) return;
        
        const exportData = {
            name: App.levelData.metadata.name,
            tiles: App.levelData.background,
            foreground: App.levelData.foreground,
            metadata: App.levelData.metadata
        };
        
        const json = JSON.stringify(exportData, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${App.levelData.metadata.name || 'level'}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        setStatus('Level exported');
    }
    
    async function exportToROM() {
        if (!App.currentLevelData) {
            setStatus('No level loaded');
            return;
        }
        
        const btn = document.getElementById('btnExportROM');
        btn.disabled = true;
        setStatus('Exporting to ROM...');
        
        try {
            const result = await API.exportLevel({
                name: App.levelData.metadata.name,
                tiles: App.levelData.background,
                offset: App.currentLevelData.offset
            });
            
            if (result.success) {
                setStatus(`Exported ${result.level} to ROM offset ${result.offset} (${result.tiles_written} tiles)`);
            } else {
                setStatus('Export failed: ' + (result.error || 'Unknown error'));
            }
        } catch (e) {
            setStatus('Export error: ' + e.message);
        }
        
        btn.disabled = false;
    }
    
    // =========================================================================
    // START APPLICATION
    // =========================================================================
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
