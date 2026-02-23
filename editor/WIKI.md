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

### Level Counts (Source Verified)
| World | Levels | Source Reference |
|-------|--------|------------------|
| World 0 | 14 levels | `INITLEVE.A:maxmaps` (dc.b 14,19,17) |
| World 1 | 19 levels | `INITLEVE.A:themapsequence2` |
| World 2 | 17 levels | `INITLEVE.A:themapsequence3` |
| **Total** | **60 unique maps defined** | 50 used in final game |

### Level Locations (ROM)
| World | PC Offset | SNES Address | Theme |
|-------|-----------|--------------|-------|
| World 0 | 0xD4000 | 0x9AC000 | Borg Factory |
| World 1 | 0xE4000 | 0x9CC000 | Bug Planet |
| World 2 | 0xF4000 | 0x9EC000 | Ancient Temple |

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

### Music Theme Sharing (Source Verified)
| Theme ID | Name | Used By | Source Reference |
|----------|------|---------|------------------|
| 3 | borgtheme | World 0 (Borg levels) | `EQUATES.H` |
| 4 | bugtheme | Bug levels + **Bubble levels** | `EQUATES.H` (bubbletheme equ 4) |
| 5 | anctheme | Ancient levels + **Lava levels** | `EQUATES.H` (lavatheme equ 5) |
| 6 | ultratheme | Ultra levels | `EQUATES.H` |

**Key Finding:** Bug/Bubble share theme 4, Ancient/Lava share theme 5 — explaining why certain level types share music.

---

## Game Worlds

### World Structure (Source Verified)

**CRITICAL:** The game has **3 main worlds** with **8 level categories** mixed WITHIN each world. Lava, Ultra, and Bubble are level types that exist WITHIN the 3 worlds, NOT as separate worlds.

| World | Levels | Level Categories Used | Music Themes |
|-------|--------|----------------------|--------------|
| **World 0** | 14 levels | borglevel (0), buglevel (1) | borgtheme, bugtheme |
| **World 1** | 19 levels | ancientlevel (4), borglevel2 (2), **lavalevel (6)** | anctheme (shared with Lava) |
| **World 2** | 17 levels | ultralevel (8), **bubblelevel (9)**, borglevel3 (3) | ultratheme, bubbletheme (shared with Bug) |

### Level Category Breakdown

| Category ID | Name | Description | Bank |
|-------------|------|-------------|------|
| 0 | borglevel | Borg/Industrial | Bank 3 |
| 1 | buglevel | Bug/Organic | Bank 12 |
| 2 | borglevel2 | Borg Variant 2 | Bank 16 |
| 3 | borglevel3 | Borg Variant 3 | Bank 22 |
| 4 | ancientlevel | Ancient/Ruins | Bank 18 |
| 6 | lavalevel | Lava/Volcanic | Bank 14 |
| 8 | ultralevel | Ultra Force/Neon | Bank 11 |
| 9 | bubblelevel | Bubble Forest | Bank 19 |

### World Progression Sequences

**World 0 (14 levels):** Storage→Bug1→Outpost→SnakyBug→Prison→LastBug→Scooters→Bug2→SnakeBoss→Decision→BugChambers→HouseOBeef→QueenMap→SpacePort

**World 1 (19 levels):** Ancient1→StepLadder→Lava→Hourglass→BigLadder→Lava99→ElevatorDrop→AncientHmmmm→Lava66→Scooter2→Vertical→Popeye→BorgDecision→AncientRollo→LavaBoss→BorgTower→AncientPlanet→ScreenLifter→SpacePort2

**World 2 (17 levels):** Ultra1→Borg32→Bubble1→Ultra3→Bubble2→MutoidMan→Scooter3→Bubble3→Ultra2→Borg34→Ultra4→PussBoss→Scooter4→Borg34→Madman→UltraBoss→SpacePort3

---

## Boss Battles

### 10 Boss Battles (Source Verified)

| # | Boss Name | Level Index | Category | Source Reference |
|---|-----------|-------------|----------|------------------|
| 1 | Popeye Boss | 3 | Ancient | `INITLEVE.A:106` |
| 2 | Queen Bug | 13 | Bug | `INITLEVE.A:115` |
| 3 | Snake Boss | 14 | Borg | `INITLEVE.A:116` |
| 4 | Spider Boss | 17 | Borg | `INITLEVE.A:119` |
| 5 | Ancient Boss (Flower) | 31 | Ancient | `INITLEVE.A:133` |
| 6 | Lava Boss | 33 | Lava | `INITLEVE.A:135` |
| 7 | Screen Lifter | 40 | Borg | `INITLEVE.A:141` |
| 8 | Puss Boss | 52 | Ultra | `INITLEVE.A:145` |
| 9 | Mutoid Man | 53 | Ultra | `INITLEVE.A:146` |
| 10 | Ultra Boss | 54 | Ultra | `INITLEVE.A:147` |

### Boss Battle Mechanics

**Boss Variables:**
- `bossstrength` — Boss HP (max 48)
- `bossx`, `bossy` — Boss position (16-bit)
- `bossdir`, `bossdirv` — Boss direction (horizontal/vertical)
- `bosscount1-3` — Boss behavior counters
- `bossangry` — Angry boss counter
- `bossready` — Boss ready to attack flag

**Screen Locking:** During boss battles, the screen is locked and centered on the boss using `centrescroll`, `centrescrx`, and `centreydir` variables.

**Boss Sound Effects:** 11 boss-specific SFX including `SFXSNAKEBOSS1-3`, `SFXQUEENSCREAM`, etc.

---

## Death Types

### 6 Death Types (Source Verified)

| Type | Value | Sound Effect | Trigger |
|------|-------|--------------|---------|
| Crumbled | 0 | `SFXCRUMBLEDEATH` ($95) | Walking/crouching death |
| Drained | 1 | None | Energy drained |
| Sidecrush | 2 | None | Squished from side |
| Topcrush | 3 | `SFXEXPLODE2` ($9F) | Squished/blown up |
| Melted | 4 | `SFXMELTDEATH` ($94) | Background drain |
| Burned | 5 | Unused | Fried by flames |

---

## Task System

### 36-Slot Task System (Source Verified)

**Source:** `NINSYS.A`, `DATA.A`

**Task Capacity:**
```assembly
TSKmax  equ  36    ; Maximum concurrent tasks
```

### Task Type Allocation

| Type ID | Name | Slots | Start Slot | Description |
|---------|------|-------|------------|-------------|
| 0 | type_bob | 2 | 0 | Bob player tasks |
| 1 | type_enemy | 15 | 2 | Borgs, Boxes, enemies |
| 2 | type_remote | 3 | 18 | Remote weapons |
| 3 | type_weapon | 3 | 21 | Projectiles/weapons |
| 4 | type_walk | 4 | 24 | Platforms/moving objects |
| 5 | type_item | 3 | 29 | Collectible items |
| 6 | type_inven | 3 | 32 | Inventory tasks |

### 64-Byte Task Data Structure

| Offset | Field | Size | Description |
|--------|-------|------|-------------|
| 0 | TSKflags | 1 | Active ($80), Waiting ($40) |
| 1-2 | TSKadrLo/Hi | 2 | Resume address (program counter) |
| 3 | TSKwaitLo | 1 | Wait counter |
| 4 | TSKbank | 1 | ROM bank for task code |
| 5-6 | PICxlo/hi | 2 | X position |
| 7-8 | PICylo/hi | 2 | Y position |
| 9-10 | PICadrLo/Hi | 2 | Picture/sprite address |
| 11 | PICattr | 1 | Attributes (hflip/vflip) |
| 12 | PICbank | 1 | Sprite bank |
| 13 | PICflag | 1 | General flags |
| 14 | PICanim | 1 | Animation frame counter |
| 15 | PICstatus | 1 | Status/state variable |
| 16 | PICdir | 1 | Direction (horizontal) |
| 17 | PIClogic | 1 | Logic/type reference |
| 18 | PICcount | 1 | General counter |
| 19 | PICthingy | 1 | Secondary counter |
| 20 | PICyhi | 1 | Y position high |
| 21 | PICsize | 1 | Sprite size |
| 22 | PICyoffset | 1 | Y offset |
| 23 | PICdirv | 1 | Direction (vertical) |
| 24-25 | PICtemp1/2 | 2 | Temporary variables |
| 26 | PICtether | 1 | Task zone holder |
| 27 | PICcolor | 1 | Color palette |
| 28 | PICscroll | 1 | Scroll sync flag |
| 29-30 | PICmaplo/hi | 2 | Task map location |
| 31 | PICcount2 | 1 | Variable usage |
| 32 | PICvomit | 1 | Animation/vomit counter |
| 33 | PICtype | 1 | Task type reference |
| 34 | PICtrigger | 1 | Map piece trigger |
| 35 | PICed | 1 | Edge variable |
| 36 | PIChealth | 1 | Health/strength |
| 37 | PICmoveh | 1 | Horizontal movement |
| 38 | PICmovev | 1 | Vertical movement |
| 39 | PICprior | 1 | Priority (0=behind, 1=front) |
| 40 | PICcolorhit | 1 | Enemy blink color |
| 41 | PICcollide | 1 | Collision flag |
| 42 | PICshake | 1 | Shake counter (anger effect) |
| 43 | PICfloat | 1 | Float counter |
| 44 | PIClocked | 1 | Lock flag (for missiles) |
| 45 | PICbehind1 | 1 | Background priority |
| 46 | PIChit | 1 | Hit flag |

### Task Scheduling Functions

| Function | Purpose |
|----------|---------|
| TSKschedule | Search for inactive task, initialize, return task ID |
| TSKsuspend | Save current PC to TSKadrLo/Hi |
| TSKwait | Set wait counter, jump to suspend |
| TSKcancel | Zero flags, clear task |

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

**MAP File Count: 82 total MAP files**

| Directory | Count | Description |
|-----------|-------|-------------|
| BORGMAPS | 29 | Borg level maps |
| BUGMAPS | 9 | Bug level maps |
| JUNGLEMA | 5 | Jungle level maps |
| LAVAMAPS | 6 | Lava level maps |
| ULTRAMPA | 11 | Ultra level maps |
| ANCMAPS | 16 | Ancient level maps |
| WORLDMAP | 4 | World map screens |
| SPACEMAP | 2 | Space level maps |
| **TOTAL** | **82** | All MAP files |

```
Space Funky B.O.B. Source Files/
├── Disk A/           - Music (MIDI), Sound effects
├── Disk B/           - Unknown (backup)
├── Disk C/           - Maps (.MAP), Levels (82 MAP files)
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
