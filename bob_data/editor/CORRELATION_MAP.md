# Space Funky B.O.B. - Project Correlation Mapping

## Project Overview
**Project**: Space Funky B.O.B. Level Editor
**Type**: Web-based ROM level editor for SNES game
**Author**: Null
**Location**: `/usr/workspace/space-funky-bob/`
**Server**: Python HTTP server on port 8000

---

## File Structure

```
space-funky-bob/
├── B.O.B._edit.smc              # Modified SNES ROM (1MB)
├── editor/
│   ├── server.py                # Python HTTP backend (769 lines)
│   ├── index.html               # Main editor UI (322 lines)
│   ├── wiki.html                # Documentation viewer
│   ├── WIKI.md                  # Technical wiki
│   ├── lib/
│   │   ├── rom_parser.py       # ROM parsing (246 lines)
│   │   ├── level_extract.py    # Level extraction (224 lines)
│   │   ├── lz77.py             # LZ77 compression (249 lines)
│   │   ├── tileset.py          # Tileset extraction (221 lines)
│   │   └── __init__.py
│   ├── js/
│   │   ├── app.js              # Main app logic (1186 lines)
│   │   ├── renderer.js         # Canvas rendering
│   │   ├── api.js              # Server communication
│   │   ├── audio.js            # MIDI/audio playback
│   │   ├── logger.js           # Logging system
│   │   └── JZZ.js              # MIDI library
│   └── css/
│       └── styles.css
├── tests/
│   └── test_editor.py
└── Space Funky B.O.B. Source Files/
    ├── Disk A/                  # Music (MIDI files)
    ├── Disk C/                  # Original MAP files
    └── ...
```

---

## Data Flow Architecture

### 1. ROM Loading Pipeline
```
B.O.B._edit.smc (1MB)
    ↓
rom_parser.py (ROMParser)
    ↓
level_extract.py (LevelExtractor)
    ↓
server.py (EditorHandler)
    ↓
JSON API → api.js (fetch)
    ↓
app.js (App state)
    ↓
renderer.js (Canvas)
```

### 2. Level Editing Pipeline
```
User clicks canvas
    ↓
app.js: onCanvasMouseDown/Move
    ↓
Paint tile to levelData
    ↓
renderAll() → Renderer.renderCanvas()
    ↓
Export: POST /export-level
    ↓
server.py: handle_export_level()
    ↓
Writes to B.O.B._edit.smc at ROM offset
```

---

## Key Data Structures

### ROM Offsets (Confirmed)
| Level     | ROM Offset  | SNES Address |
|-----------|-------------|--------------|
| WORLD_1   | 0xD4000     | $D4:0000     |
| WORLD_2   | 0xE4000     | $E4:0000     |
| WORLD_3   | 0xF4000     | $F4:0000     |

### Tileset Offsets
| Tileset   | ROM Offset  | Description        |
|-----------|-------------|-------------------|
| main_1    | 0x035800    | Primary graphics   |
| main_2    | 0x03D800    | Secondary graphics|
| borg      | 0x008000    | Borg Factory      |
| bug       | 0x008800    | Bug theme         |
| ancient   | 0x009000    | Ancient ruins     |
| lava      | 0x009800    | Lava theme        |
| ultra     | 0x00A000    | Ultra dimension   |

### Level Categories (from MAP files)
- ANCMAPS (Ancient)
- BORGMAPS (Borg/Factory)
- BUGMAPS (Bug)
- JUNGLEMA (Jungle)
- LAVAMAPS (Lava)
- SPACEMAP (Space)
- ULTRAMPA (Ultra)
- WORLDMAP (World)

---

## API Endpoints

| Method | Path                    | Description                    |
|--------|-------------------------|--------------------------------|
| GET    | /                      | Serve index.html               |
| GET    | /levels                | List all levels                |
| GET    | /level/:name           | Get level data                 |
| GET    | /tileset/:name         | Get tileset (SNES 4bpp decode)|
| GET    | /tileset/custom        | Tileset at custom offset       |
| GET    | /tilesets              | Scan ROM for tilesets          |
| GET    | /midi                  | List MIDI files                |
| GET    | /midi/:filename        | Serve MIDI file                |
| GET    | /data/:file            | Serve JSON data files          |
| POST   | /export-level          | Export level to ROM            |

---

## Technical Details

### SNES 4bpp Tile Format
- 8x8 pixels, 4 bits per pixel
- 32 bytes per tile (8 rows × 4 planes)
- Bit layout: plane0 | plane1 | plane2 | plane3
- MSB first decoding

### LZ77 Compression Format
- Status byte (8 bits) processed MSB first
- Bit 0 = literal byte
- Bit 1 = back-reference (distance/length pair)
- Distance: 11 bits (1-2047)
- Length: 5 bits + 3 (effective 3-34)

### Level Format
- 80×80 tile grid
- 16KB per level (0x4000 bytes)
- 8-bit tile IDs (0-255)
- Sparse format (only non-zero tiles stored)

---

## Server → Client Correlation

| Server (server.py)           | Client (app.js)           | Purpose                    |
|------------------------------|---------------------------|----------------------------|
| get_level_list()             | API.getLevels()           | Populate level sidebar     |
| get_level_data()            | API.getLevel()            | Load level into canvas     |
| handle_tileset()            | API.getTileset()          | Load graphics palette      |
| handle_export_level()       | API.exportLevel()         | Save changes to ROM        |
| handle_midi_list()          | Audio.renderAudioList()   | Show audio files           |
| handle_all_tilesets()       | loadAllTilesets()         | ROM scanner                |

---

## Configuration Constants

### app.js (APP_CONFIG)
- MAP_WIDTH: 80
- MAP_HEIGHT: 80
- TILE_SIZE: 8
- MAX_HISTORY: 20

### server.py
- PORT: 8000
- LEVEL_SIZE: 0x4000 (16384 bytes)
- MAP_WIDTH: 80
- MAP_HEIGHT: 80

---

## Known Issues / TODO
1. MIDI playback fails without hardware (falls back to Tone.js)
2. Tileset palettes are procedurally generated (not extracted from ROM)
3. Enemy markers are placeholder positions
4. No compression for level export (assumes uncompressed)

---

*Generated: 2026-02-14*
