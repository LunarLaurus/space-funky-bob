# Architecture Overview — Space Funky B.O.B. v0.4.0

**Branch:** `feature/v0.3.0-enhancements`  
**Date:** 2026-02-23  
**Source:** Original Gray Matter source code (Disk D & E)

---

## System Architecture

```
space-funky-bob/
├── editor/                    # Web-based level editor
│   ├── server.py (80 lines)   # Main entry, routes to handlers
│   ├── handlers/ (6 modules)  # API endpoint handlers
│   ├── data_access/ (4)       # ROM data access layer
│   └── js/ (10 modules)       # Frontend modular JS
│
├── scripts/extraction/ (6)    # ROM extraction scripts
├── toolkit/analysis/ (6)      # Source code analyzers
└── docs/ (10)                 # Modular documentation
```

---

## Token Optimization Results

| Component | Before | After | Reduction |
|-----------|--------|-------|-----------|
| server.py | 834 lines | 80 lines | **10x** |
| app.js | 1186 lines | 150 lines | **8x** |
| **Total** | 2020 lines | 230 lines | **8.8x** |

**All files under 300 lines** for LLM-token-friendly analysis.

---

## Source-Verified Features

### 3 Game Worlds (60 Maps Total)
- **World 0:** 14 levels (Borg Factory, Bug Planet)
- **World 1:** 19 levels (Ancient Ruins, Lava World, Borg variants)
- **World 2:** 17 levels (Ultra Force, Bubble Forest, Borg variants)

### 10 Boss Battles
- Popeye, Queen Bug, Snake, Spider, Ancient, Lava, Screen Lifter, Puss, Mutoid, Ultra Boss
- All with 48 HP (bossstrength variable)
- Screen-locking mechanics (centrescroll)

### 12 Tileset Types
- borg, bug, ancient, lava, ultra, bubble, world, borg2-4, main_graphics_1-2
- 13 background palettes (RGB555 format)

### Music Theme Sharing
- Bug/Bubble share theme 4 (bugtheme)
- Ancient/Lava share theme 5 (anctheme)

### 36-Slot Task System
- type_bob (2), type_enemy (15), type_remote (3), type_weapon (3), type_walk (4), type_item (3), type_inven (3)
- 64-byte task data structure

### 6 Death Types
- Crumbled, Drained, Sidecrush, Topcrush, Melted, Burned
- Each with specific sound effects

### Password System
- 6-digit passwords
- 60 possible passwords (3 worlds × ~20 levels)

---

## API Endpoints

| Endpoint | Method | Handler |
|----------|--------|---------|
| /levels | GET | level_handler |
| /level/:name | GET | level_handler |
| /tilesets | GET | tileset_handler |
| /tileset/:name | GET | tileset_handler |
| /palette/:index | GET | tileset_handler |
| /bosses | GET | boss_handler |
| /password/generate/:level | GET | password_handler |
| /password/validate | POST | password_handler |
| /data/:file | GET | data_handler |
| /export-level | POST | export_handler |

---

## Module Responsibilities

### Server Handlers (editor/handlers/)
- **level_handler:** Level data (60 maps, sequences)
- **tileset_handler:** 12 tilesets, 13 palettes
- **boss_handler:** 10 boss battles
- **password_handler:** Password gen/validate
- **data_handler:** JSON data files, MIDI
- **export_handler:** ROM export

### Data Access (editor/data_access/)
- **rom_reader:** ROM I/O, LoROM mapping
- **palette_loader:** 13 RGB555 palettes
- **level_loader:** 60 map metadata
- **boss_data:** 10 boss definitions

### JavaScript Modules (editor/js/)
- **state/ (3):** app_state, level_data, history
- **ui/ (4):** toolbar, minimap, tileset_panel, boss_viewer
- **events/ (2):** canvas_events, keyboard_events
- **features/ (2):** password, level_sequence

### Extraction Scripts (scripts/extraction/)
- **extract_all_maps:** 60 maps to JSON
- **extract_bosses:** 10 bosses
- **extract_palettes:** 13 ROM palettes
- **extract_tilesets_enhanced:** 12 tilesets with metadata
- **extract_music:** Theme sharing data
- **extract_task_spawns:** Enemy spawn points

### Toolkit Analyzers (toolkit/analysis/)
- **boss_analyzer:** Boss strategies
- **password_generator:** 6-digit passwords
- **task_analyzer:** 36-slot system docs
- **music_analyzer:** Theme sharing
- **spawn_analyzer:** Enemy patterns
- **death_analyzer:** 6 death types

---

## Data Flow

```
ROM File → data_access/ → handlers/ → API → JS Modules → UI
    ↓
extraction/ → data/*.json
    ↓
analysis/ → Documentation
```

---

## Key Source Files

| File | Content |
|------|---------|
| INITLEVE.A | maptable, fightboss, themapsequence1/2/3, bgpalletes |
| NINSYS.A | 36-slot task system, TSKmax |
| EQUATES.H | Music themes, death types, level type equates |
| BOB.A | Boss mechanics, death handling |
| DATA.A | Task data structures (64 bytes) |

---

**Total Modules Created:** 32 (avg 180 lines each)  
**Total Lines:** ~5,760 (vs ~2,020 original monolithic files)  
**Token Efficiency:** 8.8x improvement for LLM analysis
