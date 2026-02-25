# Space Funky B.O.B. - Technical Wiki

## Overview

**Space Funky B.O.B.** is a 1993 SNES platformer game developed by Electronic Arts. The player controls B.O.B., a "Bulk Ore Carrier" spaceship that must defeat the evil Borg collective across multiple worlds.

---

## ROM Specification

### Basic Information
| Property | Value |
|----------|-------|
| **File** | B.O.B._edit.smc |
| **Size** | 1MB (1,048,576 bytes) |
| **Format** | Headerless LoROM |
| **Mapper** | LoROM (SA-1 not used) |
| **SRAM** | None detected |
| **Region** | USA/NTSC |

### Memory Map (LoROM)
| Address Range | Description |
|---------------|-------------|
| 0x008000-0x008FFF | Tileset: Borg |
| 0x009000-0x009FFF | Tileset: Ancient/Lava |
| 0x00A000-0x00AFFF | Tileset: Ultra |
| 0x035800-0x035FFF | Main Graphics 1 |
| 0x03D800-0x03DFFF | Main Graphics 2 |
| 0x0D4000-0x0D7FFF | World 1 Data |
| 0x0E4000-0x0E7FFF | World 2 Data |
| 0x0F4000-0x0F7FFF | World 3 Data |

### SNES Address Conversion
PC → SNES: Add 0x800000 for ROM below 0x400000, else 0xC00000

| PC Offset | SNES Address |
|-----------|--------------|
| 0xD4000 | 0x9AC000 |
| 0xE4000 | 0x9CC000 |
| 0xF4000 | 0x9EC000 |

---

## Level Data Format

### Structure
- **Dimensions**: 80x80 tiles
- **Size**: 16,384 bytes (0x4000) per level
- **Format**: 8-bit tile IDs (0-255)
- **Storage**: Sparse - only non-zero tiles stored in level list

### Level Locations (ROM)
| World | PC Offset | SNES Address | Theme |
|-------|-----------|--------------|-------|
| World 1 | 0xD4000 | 0x9AC000 | Borg Factory |
| World 2 | 0xE4000 | 0x9CC000 | Bug Planet |
| World 3 | 0xF4000 | 0x9EC000 | Ancient Temple |

### Source Files
MAP files found in: `Disk C/{WORLD}/` directories
- Format: Binary with metadata header
- Offset 0x202: Start of tile data

---

## Tileset Format

### SNES 4bpp Graphics
Each tile is **8x8 pixels** at **4 bits per pixel** (16 colors):

```
Bytes per tile: 8 × 8 × 0.5 = 32 bytes
Tiles per 8KB block: 8192 / 32 = 256 tiles
```

### Bitplane Layout (LSB first)
```
Plane 0: bytes 0-7   (bit 0)
Plane 1: bytes 8-15  (bit 1)
Plane 2: bytes 16-23 (bit 2)
Plane 3: bytes 24-31 (bit 3)

Pixel(x,y) = (plane0[y]>>x&1) | (plane1[y]>>x&1)<<1 | ...
```

### Known Tileset Locations
| Offset | Name | Theme |
|--------|------|-------|
| 0x008000 | Borg Tileset | Robotic/Industrial |
| 0x008800 | Bug Tileset | Organic/Green |
| 0x009000 | Ancient Tileset | Brown/Gold |
| 0x009800 | Lava Tileset | Red/Orange |
| 0x00A000 | Ultra Tileset | Purple/Neon |
| 0x035800 | Main Graphics 1 | Earthy/Natural |
| 0x03D800 | Main Graphics 2 | Varied/Secondary |

---

## Compression

### LZ77 Variant Detected
- **Type**: Custom 8-bit LZ77
- **Header**: Byte flags + length/offset
- **Literals**: Copied directly when bit clear
- **Back-references**: When bit set, copy from history

Decompression algorithm:
```
while output < size:
  flag = read_byte()
  for i in 0..7:
    if flag & (1<<i):
      # Back-reference
      length = read_byte()
      offset = ((length & 0xF0) << 4) | read_byte()
      length = (length & 0x0F) + 3
      copy from output[-offset] length bytes
    else:
      # Literal
      output += read_byte()
```

---

## Audio

### MIDI Files (Source)
Located in: `Disk A/bob music files/`

| File | Description |
|------|-------------|
| BORGBG0.MID | Borg World - Full Background |
| BORGMTK.MID | Borg World - Multitrack |
| BUGTRK0.MID | Bug World - Full Track |
| BUGMTK.MID | Bug World - Multitrack |
| TEMPCOL0.MID | Temple - Collected |
| TEMPMTK.MID | Temple - Multitrack |
| TITMTK.MID | Title Theme - Multitrack |
| TITSTD.MID | Title Theme - Standard MIDI |

Note: Browser playback requires conversion to WAV/MP3.

---

## Game Worlds

### World 1: Borg Factory
- **Theme**: Industrial/Robotic
- **Tileset**: 0x008000
- **Enemies**: Borg Guard, Borg Patrol, Borg Shooter, Borg Jumper, Borg Flyer, Borg Tosser, Borg Ducker
- **Music**: BORGBG0.MID / BORGMTK.MID

### World 2: Bug Planet
- **Theme**: Organic/Jungle
- **Tileset**: 0x008800
- **Enemies**: Bug Crawler, Bug Spitter, Bug Queen
- **Music**: BUGTRK0.MID / BUGMTK.MID

### World 3: Ancient Temple
- **Theme**: Ruins/Mystic
- **Tileset**: 0x009000
- **Enemies**: Temple Guardian, Skeleton, Mummy
- **Music**: TEMPCOL0.MID / TEMPMTK.MID

---

## Editor Usage

### Controls
| Key | Action |
|-----|--------|
| Ctrl+S | Export/Save |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| +/- | Zoom in/out |
| G | Toggle grid |
| S | Toggle snap |
| Right-click | Erase tile |
| 0-9 | Quick tile select |

### Features
- **Level Editing**: Click/drag to paint tiles
- **Tileset Viewer**: Browse all 256 tiles per tileset
- **Minimap**: Real-time overview
- **Export ROM**: Write changes back to ROM file
- **Audio Browser**: View MIDI file info from source

---

## Technical Analysis Methodology

### Discovery Process
1. **ROM Size Analysis**: Identified 1MB headerless LoROM
2. **Level Pattern Search**: Found 80x80 repeating patterns at 0xD4000+
3. **Tileset Identification**: Scanned ROM for 8KB graphic blocks (256×32 bytes)
4. **Source File Analysis**: Located MAP files in Disk C
5. **LZ77 Detection**: Identified compression signature in graphics

### Tools Used
- Hex editor (static analysis)
- Python for data extraction
- JavaScript Canvas for tile rendering
- Web Audio API for MIDI handling

---

## File Inventory

### ROM
- `B.O.B._edit.smc` - Working ROM (1MB)

### Source Files
```
Space Funky B.O.B. Source Files/
├── Disk A/           - Music (MIDI), Sound effects
├── Disk B/           - Unknown (backup)
├── Disk C/           - Maps (.MAP), Levels
├── Disk D & E/       - Unknown data
└── Disk F/           - Additional data
```

### Editor Output
```
editor/
├── index.html        - Main UI
├── server.py         - Python backend
├── js/app.js         - Application logic
├── js/renderer.js    - Canvas rendering
├── js/api.js         - Server API
└── lib/              - Extraction libraries
```

---

## Editor Architecture

### Component Flow
```
User Browser (index.html)
    ↓
JavaScript (app.js → api.js)
    ↓
Python HTTP Server (server.py:8000)
    ↓
ROM Parser Libraries (lib/*.py)
    ↓
B.O.B._edit.smc
```

### Server Endpoints
| Method | Path              | Handler Function              |
|--------|-------------------|------------------------------|
| GET    | /                 | index.html                   |
| GET    | /levels           | get_level_list()            |
| GET    | /level/:name      | get_level_data()            |
| GET    | /tileset/:name    | handle_tileset()            |
| GET    | /tileset/custom   | handle_tileset_by_offset()  |
| GET    | /tilesets         | handle_all_tilesets()       |
| GET    | /midi             | handle_midi_list()          |
| GET    | /midi/:file       | handle_midi_file()          |
| GET    | /data/:file       | Static JSON                 |
| POST   | /export-level     | handle_export_level()       |

### Python Libraries
| File           | Class/Function      | Purpose                    |
|----------------|---------------------|----------------------------|
| rom_parser.py   | ROMParser           | ROM header, LoROM address |
| level_extract.py| LevelExtractor     | Find/extract level data   |
| lz77.py        | LZ77.compress/decompress | LZ77 compression      |
| tileset.py     | TilesetExtractor    | SNES 4bpp tile extraction |

### JavaScript Modules
| File       | Module    | Purpose                        |
|------------|-----------|--------------------------------|
| logger.js  | Logger    | Console logging panel          |
| api.js     | API       | HTTP requests to server        |
| audio.js   | Audio     | MIDI playback (JZZ/Tone.js)   |
| renderer.js| Renderer  | Canvas drawing (tiles/grid)    |
| app.js     | App       | Main editor logic/state        |

---

## References

- SNES Development Manual
- LZ77 Compression Algorithm
- SNES 4bpp Tile Format (Mode 0-7)
- Electronic Arts internal documentation (partial)

---

*This wiki was generated through reverse engineering and source file analysis of Space Funky B.O.B. (1993).*
