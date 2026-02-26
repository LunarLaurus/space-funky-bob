# v0.5.0 WebUI Refinement Plan

**Branch:** `feature/v0.5.0-webui-refinement`  
**Created:** 2026-02-26  
**Parent:** `feature/v0.4.0-webui-overhaul`  
**Sprint Duration:** 2 weeks (estimated)  
**Architect:** Lauren

---

## Mission

Refine and polish the WebUI with focused improvements to individual features. v0.4.0 established the modular architecture; v0.5.0 delivers **polish, completeness, and user experience enhancements**.

---

## Focus Areas

### 1. 🎨 Editor Tab (Core Experience)

**Current State:**
- ✅ Level list loading
- ✅ Tile editing (pencil, eraser, fill, select, picker)
- ✅ Minimap rendering
- ✅ Toolbar with tool selection
- ✅ History (undo/redo)
- ✅ Save/export functionality

**Refinement Targets:**
- [ ] **Level Metadata Editing** — Complete form with all fields (name, theme, author, music, time limit)
- [ ] **Tile Variations Panel** — Show all tile variations for selected tile ID
- [ ] **Enemy Placement** — Visual enemy spawning with drag-and-drop
- [ ] **Zoom Controls** — Mouse wheel zoom, zoom presets (1x, 2x, 4x, fit)
- [ ] **Grid Toggle** — Show/hide grid overlay
- [ ] **Keyboard Shortcuts** — Comprehensive shortcut system (Ctrl+Z, Ctrl+S, etc.)
- [ ] **Status Bar** — Real-time cursor position, tile ID, selection info

**Priority:** P0 (Core experience)

---

### 2. 👹 Boss Battles Feature

**Current State:**
- ✅ `boss_viewer.js` module exists
- ✅ Backend handler (`boss_handler.py`) ready
- ✅ Source data from `INITLEVE.A:fightboss`

**Refinement Targets:**
- [ ] **Boss List Display** — Grid view of all 10 bosses with sprites
- [ ] **Boss Stats Panel** — HP, attack patterns, location, music
- [ ] **Source References** — Link to assembly source (BOSS.ASP files)
- [ ] **Battle Preview** — Simulated boss battle view (static for now)
- [ ] **Export Boss Data** — JSON export for modding

**Priority:** P1 (Reference tool)

---

### 3. 🗺️ Level Sequences Feature

**Current State:**
- ✅ `level_sequence.js` module exists
- ✅ World sequence data (3 worlds, 60 levels)
- ✅ Source data from `INITLEVE.A:themapsequence1/2/3`

**Refinement Targets:**
- [ ] **Visual Flow Chart** — Directed graph showing level progression
- [ ] **World Tabs** — Switch between World 0, 1, 2
- [ ] **Level Cards** — Each level shows thumbnail, name, type, music
- [ ] **Branching Paths** — Show optional levels vs required
- [ ] **Statistics** — Total levels, average length, boss count
- [ ] **Export Sequence** — JSON/PNG export of flow chart

**Priority:** P1 (Reference tool)

---

### 4. 🔐 Password Tool Feature

**Current State:**
- ✅ `password.js` module exists
- ✅ Password generation algorithm
- ✅ Source data from `INITLEVE.A:passwords`

**Refinement Targets:**
- [ ] **Password Generator UI** — Select world/level → Generate password
- [ ] **Password Decoder** — Enter password → Show world/level
- [ ] **Password Table** — Complete reference table (all 60 levels)
- [ ] **Copy to Clipboard** — One-click copy
- [ ] **Share Link** — Generate shareable URL with password pre-filled

**Priority:** P2 (Nice-to-have)

---

### 5. 🎨 Tileset Browser Feature

**Current State:**
- ✅ `tileset_panel.js` module exists
- ✅ Backend handler (`tileset_handler.py`) ready
- ✅ Source data from `INITLEVE.A:blocksets`

**Refinement Targets:**
- [ ] **Tileset Gallery** — Grid view of all 12 tilesets
- [ ] **Tile Inspector** — Click tile to see properties (ID, palette, animation)
- [ ] **Palette Viewer** — SNES palette display (16 colors per palette)
- [ ] **Animation Preview** — Animated tiles (if applicable)
- [ ] **Export Tileset** — PNG sprite sheet + JSON metadata
- [ ] **ROM Scanner** — Scan ROM for additional tilesets

**Priority:** P1 (Reference tool)

---

## Technical Debt

### CSS Refinements
- [ ] **Responsive Design** — Mobile/tablet support
- [ ] **Dark Theme** — Enhanced contrast for long sessions
- [ ] **Loading States** — Spinners/skeletons for async operations
- [ ] **Error Handling** — User-friendly error messages

### JavaScript Refinements
- [ ] **Error Boundaries** — Catch and log errors gracefully
- [ ] **Performance** — Lazy loading for large datasets
- [ ] **Caching** — Cache API responses to reduce server load
- [ ] **TypeScript Migration** — Optional: Add type safety

### Backend Refinements
- [ ] **API Documentation** — OpenAPI/Swagger spec
- [ ] **Rate Limiting** — Prevent abuse
- [ ] **Logging** — Structured logging for debugging
- [ ] **Testing** — Integration tests for handlers

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Feature Completeness** | 100% | All 5 features functional |
| **Load Time** | <2s | Time to interactive |
| **Error Rate** | <1% | Errors per 100 actions |
| **User Actions** | 10+ | Clicks to complete common tasks |
| **Code Quality** | 0 lint errors | ESLint/Flake8 reports |

---

## Sprint Schedule

### Week 1: Core Features
| Day | Focus | Deliverables |
|-----|-------|--------------|
| 1-2 | Editor Tab | Metadata form, tile variations, zoom |
| 3-4 | Tileset Browser | Gallery, inspector, palette viewer |
| 5 | Boss Battles | Boss list, stats, export |

### Week 2: Polish & Testing
| Day | Focus | Deliverables |
|-----|-------|--------------|
| 6-7 | Level Sequences | Flow chart, world tabs, export |
| 8 | Password Tool | Generator, decoder, table |
| 9 | CSS/UX Polish | Responsive design, loading states |
| 10 | Testing & Bug Fixes | Integration tests, bug fixes |

---

## Task Breakdown

### Editor Tab (P0)
- [ ] `EDITOR-001`: Complete level metadata form
- [ ] `EDITOR-002`: Tile variations panel
- [ ] `EDITOR-003`: Zoom controls (mouse wheel + buttons)
- [ ] `EDITOR-004`: Grid toggle overlay
- [ ] `EDITOR-005`: Keyboard shortcuts system
- [ ] `EDITOR-006`: Enhanced status bar

### Tileset Browser (P1)
- [ ] `TILESET-001`: Tileset gallery grid
- [ ] `TILESET-002`: Tile inspector panel
- [ ] `TILESET-003`: Palette viewer
- [ ] `TILESET-004`: Export functionality
- [ ] `TILESET-005`: ROM scanner integration

### Boss Battles (P1)
- [ ] `BOSS-001`: Boss list grid
- [ ] `BOSS-002`: Boss stats panel
- [ ] `BOSS-003`: Source references
- [ ] `BOSS-004`: Export boss data

### Level Sequences (P1)
- [ ] `SEQUENCE-001`: Visual flow chart
- [ ] `SEQUENCE-002`: World tabs
- [ ] `SEQUENCE-003`: Level cards
- [ ] `SEQUENCE-004`: Statistics panel
- [ ] `SEQUENCE-005`: Export flow chart

### Password Tool (P2)
- [ ] `PASSWORD-001`: Generator UI
- [ ] `PASSWORD-002`: Decoder UI
- [ ] `PASSWORD-003`: Password table
- [ ] `PASSWORD-004`: Copy/share features

### CSS/UX (P1)
- [ ] `CSS-001`: Responsive breakpoints
- [ ] `CSS-002`: Enhanced dark theme
- [ ] `CSS-003`: Loading spinners
- [ ] `CSS-004`: Error message toasts

---

## Files to Modify

| Directory | Files | Purpose |
|-----------|-------|---------|
| `editor/js/ui/` | `toolbar.js`, `tileset_panel.js` | Editor enhancements |
| `editor/js/features/` | `level_sequence.js`, `password.js` | Feature modules |
| `editor/css/` | `features.css`, `components.css` | Styling updates |
| `editor/handlers/` | All handlers | Backend improvements |
| `editor/index.html` | Main HTML | Add missing UI elements |

---

## Dependencies

- ✅ Modular architecture (v0.4.0 complete)
- ✅ Backend handlers implemented
- ✅ Source data verified (QWEN-SOURCE-FINDINGS.md)
- ⏳ ROM file required for tileset scanning (user-provided)

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| ROM file not available | Tileset scanner blocked | Use cached data, mark as optional |
| Browser compatibility | Some features break | Test on Chrome/Firefox/Edge |
| Performance issues | Slow load times | Lazy loading, caching |
| Scope creep | Sprint overruns | Stick to P0/P1, defer P2 |

---

## Definition of Done

Each feature is complete when:
- [ ] UI is functional and styled
- [ ] Backend API returns correct data
- [ ] Error handling in place
- [ ] Source references documented
- [ ] Export functionality works
- [ ] Tested on Chrome/Firefox

---

**Last Updated:** 2026-02-26  
**Next Review:** End of Week 1 (Editor + Tileset + Boss complete)
