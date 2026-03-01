# v0.5.0 WebUI Refinement Plan — SYNTHESIZED

**Branch:** `feature/v0.5.0-webui-refinement`
**Created:** 2026-02-26
**Updated:** 2026-02-26 (Post sub-agent analysis)
**Parent:** `feature/v0.4.0-webui-overhaul`
**Sprint Duration:** 2 weeks (74 hours estimated)
**Architect:** Lauren

---

## Mission

**Rebalanced focus** based on 150-commit analysis and 5 sub-agent investigations:

- **Audio**: 38 commits (25%) — 🔥 Heavily Loved
- **Planning**: 36 commits (24%) — 🔥 Heavily Loved  
- **WebUI**: 20 commits (13%) — ⚡ Active
- **Testing**: 14 commits (9%) — ⚠️ Neglected (105 commits stale)
- **Toolkit**: 9 commits (6%) — ⚠️ Neglected (40 commits stale)
- **Infrastructure**: 4 commits (3%) — 🚨 Critical (148 commits stale)

v0.5.0 delivers **critical foundation fixes** (P0) followed by **feature completion** (P1) to rebalance development effort and address technical debt.

---

## Commit Analysis Summary

| Area | Commits | % | Last Touched | Status |
|------|---------|---|--------------|--------|
| Audio | 38 | 25% | 0 commits ago | ✅ Current |
| Planning | 36 | 24% | 0 commits ago | ✅ Current |
| WebUI | 20 | 13% | 2 commits ago | ✅ Current |
| Testing | 14 | 9% | 105 commits ago | 🚨 Stale |
| Documentation | 13 | 9% | 1 commit ago | ✅ Current |
| Toolkit | 9 | 6% | 40 commits ago | ⚠️ Stale |
| Infrastructure | 4 | 3% | 148 commits ago | 🚨 Critical |

**Key Finding:** Audio + Planning = 50% of commits; Infrastructure + Testing + Toolkit = only 18%

---

## P0 — Critical Fixes (16 hours, Week 1 Days 1-5)

### WebUI (4 hours)
- [ ] **WEBUI-001**: Fix level list population (`app.js` — `#mapList` never populated from API)
- [ ] **WEBUI-002**: Fix tileset data loading (tile renderer uses placeholders, not ROM data)
- [ ] **WEBUI-003**: Fix tileset browser feature (container ID mismatch: `#tileset` vs `#tileset-browser`)
- [ ] **WEBUI-004**: Fix layer data structure (single `tiles` array vs `background`/`foreground` arrays)

### Testing (6 hours)
- [ ] **TEST-001**: Integrate pytest into CI (currently only runs legacy `run_tests.py`)
- [ ] **TEST-002**: Add coverage threshold enforcement (recommend 70% minimum)
- [ ] **TEST-003**: Remove deprecated test runners from CI (`run_tests.py`, `property_tests.py`)

### Toolkit (2 hours)
- [ ] **TOOL-001**: Fix syntax error in `bob_analyze.py` (line 93 indentation)
- [ ] **TOOL-002**: Remove 4 deprecated graphics modules (`bob_graphics_v2.py`, `bob_graphics_legacy.py`, `bob_graphics_classifier.py`, `bob_graphics_consolidated.py`)

### Infrastructure (4 hours)
- [ ] **INFRA-001**: Update `.gitignore` for new files (docs/api/_build/, editor modules)
- [ ] **INFRA-002**: Update CI/CD workflows (`.github/workflows/ci.yml` — add pytest, coverage)
- [ ] **INFRA-003**: Update `requirements.txt` with current dependencies

---

## P1 — High Priority (36 hours, Week 2 Days 6-10)

### WebUI (8 hours)
- [ ] **WEBUI-101**: Add enemy markers rendering (enemy data structure + rendering)
- [ ] **WEBUI-102**: Fix level sequence loading (level name format mismatch)
- [ ] **WEBUI-103**: Fix password encoding (implement full algorithm with boss flags)
- [ ] **WEBUI-104**: Add enemy data endpoint (`GET /enemies`)
- [ ] **WEBUI-105**: Implement tile variations ROM scanning

### Testing (12 hours)
- [ ] **TEST-101**: Add tests for `bob_analyze.py` (0% coverage currently)
- [ ] **TEST-102**: Add tests for `bob_extract.py` (0% coverage)
- [ ] **TEST-103**: Add tests for `bob_map.py` (HTML visualization)
- [ ] **TEST-104**: Add tests for `toolkit/analysis/` (7 modules, 0% coverage)
- [ ] **TEST-105**: Mock external data dependencies (ROM files, data files)

### Documentation (6 hours)
- [ ] **DOC-101**: Update version references (DELIVERABLES.md, EPICS.md, SPRINTS.md, PRD.md)
- [ ] **DOC-102**: Fix API module paths (`docs/api/modules.rst` — incorrect paths)
- [ ] **DOC-103**: Create troubleshooting guide (`docs/TROUBLESHOOTING.md`)
- [ ] **DOC-104**: Consolidate level format docs (merge 3 files into 1)

### Toolkit (8 hours)
- [ ] **TOOL-101**: Consolidate duplicate utility functions (`calculate_entropy`, `detect_rom_header`)
- [ ] **TOOL-102**: Standardize import patterns across toolkit
- [ ] **TOOL-103**: Add type hints to all modules

---

## P2 — Medium Priority (22 hours, Post-v0.5.0 or Time Permitting)

### WebUI (6 hours)
- [ ] **WEBUI-201**: Palette viewer UI
- [ ] **WEBUI-202**: Copy-to-clipboard for passwords
- [ ] **WEBUI-203**: Dark mode toggle
- [ ] **WEBUI-204**: Inline styles → CSS migration

### Documentation (8 hours)
- [ ] **DOC-201**: FAQ document
- [ ] **DOC-202**: Migration guide
- [ ] **DOC-203**: Architecture Decision Records (ADRs)
- [ ] **DOC-204**: Contributor quick-start
- [ ] **DOC-205**: Release notes (v0.2.0, v0.3.0, v0.4.0)

### Toolkit (6 hours)
- [ ] **TOOL-201**: Performance benchmarks in CI
- [ ] **TOOL-202**: Additional test coverage (remaining gaps)

### Infrastructure (2 hours)
- [ ] **INFRA-201**: Pre-commit hooks
- [ ] **INFRA-202**: Dependency automation

---

## Focus Areas (Original v0.5.0 Goals — Deferred)

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

## Success Metrics (Updated)

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **WebUI Features Functional** | 60% | 100% | Manual testing |
| **Modules with Test Coverage** | 47% | 80%+ | `pytest --cov` report |
| **CI Runs Full Test Suite** | ❌ | ✅ | GitHub Actions logs |
| **Coverage Threshold Enforced** | ❌ | ✅ (70%) | `.coveragerc` |
| **Deprecated Modules** | 4 | 0 | `toolkit/` directory count |
| **Documentation Health Score** | 80/100 | 90/100 | Documentation audit |
| **Infrastructure Staleness** | 148 commits | 0 commits | `git log` analysis |
| **Load Time** | N/A | <2s | Browser DevTools |
| **Code Quality** | N/A | 0 lint errors | ESLint/Flake8 |

---

## Sprint Schedule (Rebalanced)

### Week 1: Foundation Fixes (P0)
| Day | Focus | Deliverables |
|-----|-------|--------------|
| **Day 1** | WebUI P0 fixes | Level list working, tileset data loads, layer structure fixed |
| **Day 2** | WebUI P0 fixes (cont.) | Enemy markers, tile variations scanning |
| **Day 3** | Testing CI integration | Pytest in CI, coverage threshold enforcement |
| **Day 4** | Toolkit cleanup | Remove 4 deprecated graphics modules, fix `bob_analyze.py` syntax |
| **Day 5** | Infrastructure update | Update `.gitignore`, CI/CD workflows, `requirements.txt` |

### Week 2: Feature Completion (P1)
| Day | Focus | Deliverables |
|-----|-------|--------------|
| **Day 6** | WebUI P1 features | Enemy data endpoint, password encoding fix, level sequence loading |
| **Day 7** | Testing gaps | Add tests for `bob_analyze.py`, `bob_extract.py`, `bob_map.py` |
| **Day 8** | Documentation update | Fix version refs, create troubleshooting guide, consolidate level format docs |
| **Day 9** | Toolkit tests | Add tests for 8 untested modules |
| **Day 10** | Polish & bug fixes | Final testing, documentation review |

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
