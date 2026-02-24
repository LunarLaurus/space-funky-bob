# Editor Server Architecture

**Refactored:** 834 lines → 80 lines (10x reduction)  
**Pattern:** Handler-based routing with data access layer

---

## Module Structure

```
editor/
├── server.py (80 lines)       # Entry point, routing only
├── handlers/ (6 modules)      # API endpoint handlers
│   ├── __init__.py
│   ├── level_handler.py       # GET /levels, /level/:name
│   ├── tileset_handler.py     # GET /tileset/*, /tilesets, /palette/:index
│   ├── data_handler.py        # GET /data/:file, /midi/*
│   ├── export_handler.py      # POST /export-level
│   ├── boss_handler.py        # GET /bosses
│   └── password_handler.py    # GET/POST /password/*
│
└── data_access/ (4 modules)   # ROM data access
    ├── __init__.py
    ├── rom_reader.py          # ROM I/O, LoROM mapping
    ├── palette_loader.py      # 13 RGB555 palettes
    ├── level_loader.py        # 60 maps metadata
    └── boss_data.py           # 10 boss definitions
```

---

## Request Flow

```
HTTP Request → server.py → Handler → Data Access → Response
                  ↓
            (80 lines, routing only)
                  ↓
    ┌─────────────┴──────────────┐
    │                            │
handlers/                  data_access/
(6 modules)                (4 modules)
    │                            │
    └────────────┬───────────────┘
                 ↓
           ROM / JSON files
```

---

## Handler Responsibilities

### level_handler.py (150 lines)
- `get_level_list()` — Return 60 maps with world organization
- `get_level_data(name)` — Load specific level
- `get_level_sequences()` — Return themapsequence1/2/3

### tileset_handler.py (180 lines)
- `get_all_tilesets()` — Return 12 tilesets with offsets
- `get_tileset(name)` — Load specific tileset
- `get_palette(index)` — Load RGB555 palette (0-12)

### boss_handler.py (120 lines)
- `get_all_bosses()` — Return 10 boss battles
- `get_boss_by_id(id)` — Get specific boss
- `get_boss_sounds()` — Return boss sound catalog

### password_handler.py (100 lines)
- `generate_password(world, level)` — Generate 6-digit password
- `validate_password(digits)` — Validate password

---

## Data Access Layer

### rom_reader.py (200 lines)
- `read_bytes(offset, length)` — Read ROM data
- `read_word(offset)` — Read 16-bit little-endian
- `snes_to_rom_offset(snes_address)` — LoROM conversion
- `get_rom_info()` — ROM metadata

### palette_loader.py (180 lines)
- `load_palette(index)` — Load 16-color RGB555 palette
- `load_all_palettes()` — Load all 13 palettes
- `snes_color_to_rgb(color)` — Convert RGB555 to RGB

### level_loader.py (200 lines)
- `get_map_info(map_number)` — Get map metadata
- `get_world_sequence(world_id)` — Get level sequence
- `get_all_levels()` — Return 60 maps

### boss_data.py (150 lines)
- `get_all_bosses()` — Return 10 bosses
- `get_boss_by_id(id)` — Get boss by ID
- `get_boss_mechanics()` — Return boss variables

---

## API Endpoints

| Endpoint | Method | Handler | Lines |
|----------|--------|---------|-------|
| /levels | GET | level_handler | 150 |
| /level/:name | GET | level_handler | 150 |
| /tilesets | GET | tileset_handler | 180 |
| /tileset/:name | GET | tileset_handler | 180 |
| /palette/:index | GET | tileset_handler | 180 |
| /bosses | GET | boss_handler | 120 |
| /password/generate/:level | GET | password_handler | 100 |
| /password/validate | POST | password_handler | 100 |
| /data/:file | GET | data_handler | 100 |
| /export-level | POST | export_handler | 150 |

---

## Source-Verified Constants

All handlers use constants from source code:

| Constant | Source | Value |
|----------|--------|-------|
| WORLD_SEQUENCES | INITLEVE.A | 14+19+17 levels |
| LEVEL_TYPES | EQUATES.H | 13 types (0-16) |
| BOSS_DATA | INITLEVE.A:fightboss | 10 bosses |
| PALETTE_INDICES | INITLEVE.A:bgpalletes | 13 palettes |
| MUSIC_THEMES | EQUATES.H | 4 themes (sharing) |

---

## Testing

```bash
cd editor
python server.py
# Server running at http://localhost:8000

# Test endpoints
curl http://localhost:8000/levels
curl http://localhost:8000/bosses
curl http://localhost:8000/password/generate/0/0
```

---

**Benefits of Refactoring:**
- Each module under 200 lines (LLM-token-friendly)
- Clear separation of concerns
- Easy to add new endpoints
- Testable independently
