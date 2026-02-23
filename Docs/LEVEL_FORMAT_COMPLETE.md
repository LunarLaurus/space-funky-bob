# B.O.B. Level Format Specification — Complete Reference

**Document Version:** 1.0  
**Date:** 2026-02-23  
**Status:** Complete  
**Source:** Analysis of original development archives + ROM reverse engineering

---

## Executive Summary

Space Funky B.O.B. uses a tile-based level system with:
- **8-bit development format** (.MAP files in source archives)
- **16-bit ROM format** (SNES tilemap structure)
- **Runtime conversion** from 8-bit to 16-bit during level loading
- **LZ77 compression** for graphics data

This document provides the complete specification for level editing and tool development.

---

## 1. Level Types

From `INITLEVE.A` (source archive):

| ID | Level Type | Theme | Graphics Bank | Music Bank |
|----|------------|-------|---------------|------------|
| 0 | `borglevel` | Borg Fortress | Bank 7 | 0 |
| 1 | `buglevel` | Bug Planet | Bank 4 | 1 |
| 3 | `spacelevel` | Space | Bank 4 | 2 |
| 4 | `ancientlevel` | Ancient Ruins | Bank 19 | 2 |
| 6 | `lavalevel` | Lava World | Bank 4 | 2 |
| 8 | `ultralevel` | Ultra Force | Bank 24 | 3 |
| 9 | `bubblelevel` | Bubble Forest | Bank 24 | 3 |
| 10 | `worldlevel` | World Map | Bank 24 | 4 |
| 11 | `worldlevel2` | World Map 2 | Bank 24 | 4 |
| 12 | `worldlevel3` | World Map 3 | Bank 24 | 4 |
| 14 | `borglevel2` | Borg Fortress 2 | Bank 7 | 0 |

---

## 2. Tilemap Format

### 2.1 ROM Format (16-bit SNES)

**Location in ROM:** Addresses following pattern `0x028000 + n*0x800`

**Structure:**
```
Size: 0x800 bytes (2048 bytes)
Grid: 32x32 tiles (1024 entries)
Entry Size: 2 bytes (16-bit) per tile
Byte Order: Little-endian
```

**16-bit Entry Format:**
```
Bit 15 ─────────────────────────────┐ Y-Flip
Bit 14 ───────────────────────────┐ │ X-Flip
Bit 13-12 ─────────────────────┐ │ │ Palette (0-3)
Bit 11-10 ──────────────────┐ │ │ │ CHR Bank (0-3)
Bit 9-0 ────────────────┐ │ │ │ │ Tile ID (0-1023)
                        │ │ │ │ │
    0b YXpp cc tttt tttt
```

| Bits | Name | Range | Description |
|------|------|-------|-------------|
| 15 | Y-Flip | 0-1 | Vertical flip |
| 14 | X-Flip | 0-1 | Horizontal flip |
| 13-12 | Palette | 0-3 | Color palette selection |
| 11-10 | CHR Bank | 0-3 | Character ROM bank |
| 9-0 | Tile ID | 0-1023 | Tile index in graphics data |

**Python Parsing:**
```python
def parse_tilemap_entry(value):
    """Parse 16-bit tilemap entry."""
    return {
        'tile_id': value & 0x3FF,        # Bits 0-9
        'chr_bank': (value >> 10) & 0x3,  # Bits 10-11
        'palette': (value >> 12) & 0x3,   # Bits 12-13
        'x_flip': (value >> 14) & 1,      # Bit 14
        'y_flip': (value >> 15) & 1,      # Bit 15
    }

def build_tilemap_entry(tile_id, chr_bank=0, palette=0, x_flip=0, y_flip=0):
    """Build 16-bit tilemap entry."""
    return (tile_id & 0x3FF) | \
           ((chr_bank & 0x3) << 10) | \
           ((palette & 0x3) << 12) | \
           ((x_flip & 1) << 14) | \
           ((y_flip & 1) << 15)
```

### 2.2 Development Format (8-bit .MAP)

**Location:** `source/Disk C/*/` directories

**File Structure:**
```
Total Size: 131070 bytes (0x1FFFE)
Header: 0x200 bytes (zeros)
Data: 255 blocks × 0x200 bytes (512 bytes each)
Format: 8-bit tile IDs (0-255)
```

**Block Structure:**
```
Offset 0x00-0x01: 2-byte header (level index/type)
Offset 0x02-0x1FF: Tile data (510 bytes = 510 tiles)
```

**Known .MAP Files:**
| Directory | Files | Level Type |
|-----------|-------|------------|
| `ANCMAPS/` | ANC1.MAP - ANC8.MAP, ANCBOSS.MAP | Ancient Ruins |
| `BORGMAPS/` | BORG*.MAP | Borg Fortress |
| `BUGMAPS/` | BUG*.MAP | Bug Planet |
| `LAVAMAPS/` | LAVA*.MAP | Lava World |
| `SPACEMAP/` | SPACE*.MAP | Space |
| `ULTRAMPA/` | ULTRA*.MAP | Ultra Force |
| `WORLDMAP/` | WORLD*.MAP | World Map |

### 2.3 Format Conversion

**8-bit → 16-bit Conversion:**
```python
def convert_8bit_to_16bit(tile_id_8bit, level_type):
    """
    Convert 8-bit development tile ID to 16-bit SNES format.
    
    Args:
        tile_id_8bit: 8-bit tile ID from .MAP file
        level_type: Level type (0-14)
    
    Returns:
        16-bit tilemap entry
    """
    # CHR bank offset based on level type
    chr_bank_offsets = {
        0: 0,   # Borg
        1: 1,   # Bug
        3: 2,   # Space
        4: 3,   # Ancient
        6: 4,   # Lava
        8: 5,   # Ultra
        9: 5,   # Bubble
    }
    
    chr_bank = chr_bank_offsets.get(level_type, 0)
    palette = 0  # Default palette
    
    return build_tilemap_entry(
        tile_id=tile_id_8bit & 0xFF,
        chr_bank=chr_bank,
        palette=palette
    )
```

---

## 3. Map Dimensions

### 3.1 Runtime Memory Layout

From `SCROLL.A`:
```assembly
mapsize   = 8192*2      ; 16384 bytes (80x80 max)
scrollmap = $7e3000     ; WRAM base address
taskmap   = scrollmap + mapsize + bufferarea
```

**Maximum Dimensions:**
- **Width:** 80 tiles
- **Height:** 80 tiles
- **Total Size:** 16384 bytes (128KB in WRAM)

**Visible Screen:**
- **Width:** 32 tiles
- **Height:** 32 tiles
- **Tilemap Size:** 0x800 bytes (2KB)

### 3.2 Level Dimensions by Type

| Level Type | Width | Height | Tilemap Count |
|------------|-------|--------|---------------|
| Borg | 64 | 64 | 4 |
| Bug | 48 | 48 | 3 |
| Ancient | 56 | 56 | 4 |
| Lava | 40 | 40 | 2 |
| Ultra | 48 | 48 | 3 |
| World Map | 32 | 32 | 1 |

---

## 4. Tile Properties

### 4.1 Collision Types

From `WALLS.ASM`:

| ID | Name | Description |
|----|------|-------------|
| 0 | `blank` | No collision (pass-through) |
| 1 | `solid` | Solid wall (blocks movement) |
| 2 | `death` | Hazard (kills player) |
| 3 | `ladder` | Climbable (vertical movement) |
| 4 | `overhand` | Grab ledge (platform edge) |
| 5 | `elevator` | Elevator shaft (vertical transport) |
| 6 | `victory` | Level exit/victory |

### 4.2 Tile Property Tables

Each level type has a tile property table:

| Level Type | Table Name | Source File |
|------------|------------|-------------|
| Borg | `borgkars` | WALLS.ASM |
| Bug | `bugkars` | WALLS.ASM |
| Lava | `lavakars` | WALLS.ASM |
| Ancient | `anckars` | WALLS.ASM |
| Ultra | `ultrakars` | WALLS.ASM |

**Table Structure:**
```assembly
; Example from WALLS.ASM
borgkars:
    dc.b 0    ; Tile 0: blank
    dc.b 1    ; Tile 1: solid
    dc.b 2    ; Tile 2: death
    ...
    dc.b 3    ; Tile N: ladder
```

---

## 5. Graphics Data

### 5.1 Compressed Graphics Blocks

**Compression:** B.O.B. LZ77 variant (see `toolkit/bob_lz.py`)

**Known Compressed Blocks:**

| ROM Offset | Decompressed Size | Graphics Type | Level Usage |
|------------|-------------------|---------------|-------------|
| 0x018000 | 0x800 | Tiles | Borg levels |
| 0x030000 | 0x800 | Tiles | Bug levels |
| 0x060000 | 0x800 | Tiles | Ancient levels |
| 0x090000 | 0x800 | Tiles | Lava levels |
| 0x0A0000 | 0x800 | Tiles | Ultra levels |
| 0x1AD34 | 0x822 | Unknown | Documented test block |

### 5.2 Graphics Format

**Tile Size:** 8x8 pixels
**Color Depth:** 2bpp (4 colors per tile)
**Bytes per Tile:** 16 bytes

**2bpp Tile Layout:**
```
Row 0: [bitplane0 byte 0] [bitplane1 byte 0]
Row 1: [bitplane0 byte 1] [bitplane1 byte 1]
...
Row 7: [bitplane0 byte 7] [bitplane1 byte 7]

Pixel value = (bitplane1 << 1) | bitplane0
```

---

## 6. Level Loading Process

### 6.1 Loading Sequence

1. **Level Selection**
   - `mapnumber` selects specific level
   - `maptype` selects level theme (borg, bug, ancient, etc.)

2. **Bank Loading**
   - Based on `maptype`, appropriate ROM bank is accessed
   - Bank mapping: see Section 1

3. **Decompression**
   - Graphics data decompressed using LZ77 variant
   - See `toolkit/bob_lz.py` for decompression

4. **Tilemap Conversion**
   - 8-bit .MAP tile IDs converted to 16-bit SNES format
   - CHR bank offset applied based on level type
   - Palette assigned from tile property tables

5. **RAM Placement**
   - Decompressed tilemap placed at `$7e3000` (scrollmap)
   - Enemy generation scans tilemap for spawn points

### 6.2 Enemy Generation

From `GENERATE.A`:
- `generate_left_enemies` / `generate_right_enemies` scan map data
- Tile values determine enemy types and positions
- Enemy types based on level theme

---

## 7. Animation and Audio

### 7.1 Animation Sets

From `INITLEVE.A`:
```assembly
animset:
    dc.b 0    ; borg
    dc.b 4    ; bug
    dc.b 1    ; lava
    dc.b 2    ; ultra
    dc.b 3    ; ancient
```

| Animation Set | Level Types |
|---------------|-------------|
| 0 | Borg |
| 1 | Lava |
| 2 | Ultra |
| 3 | Ancient |
| 4 | Bug |

### 7.2 Sound Bank

From `INITLEVE.A`:
```assembly
soundbank:
    dc.b 0    ; borg
    dc.b 1    ; bug
    dc.b 2    ; ancient
    dc.b 3    ; lava
    dc.b 4    ; ultra
```

---

## 8. Tool Integration

### 8.1 Extraction

```bash
# Extract all tilemaps from ROM
python toolkit/bob_extract_levels.py --rom "rom/B.O.B..smc" --outdir data/levels

# Output:
#   data/levels/tilemap_00_028000.bin
#   data/levels/tilemap_00_028000.json
#   data/levels/index.json
```

### 8.2 Injection

```bash
# Inject modified tilemap
python toolkit/bob_inject.py --rom "rom/B.O.B..smc" \
    --tilemap data/levels/tilemap_04_02A000.bin \
    --offset 0x02A000 \
    --output "rom/B.O.B.modified.smc"
```

### 8.3 Editing Workflow

1. Extract tilemap: `bob_extract_levels.py`
2. Convert to editable format (JSON or custom editor)
3. Modify tiles
4. Convert back to 16-bit SNES format
5. Inject with `bob_inject.py`
6. Test in emulator

---

## 9. Source Archive Reference

### 9.1 Directory Structure

```
source/
├── Disk A/                    # Music files, equates
│   └── bob music files ƒ/
├── Disk B (CPBACKUP001)/      # Backup disk
├── Disk C/                    # Level .MAP files
│   ├── ANCMAPS/               # Ancient ruins maps
│   ├── BORGMAPS/              # Borg fortress maps
│   ├── BUGMAPS/               # Bug planet maps
│   ├── LAVAMAPS/              # Lava world maps
│   ├── SPACEMAP/              # Space maps
│   ├── ULTRAMPA/              # Ultra Force maps
│   └── WORLDMAP/              # World maps
├── Disk D & E/                # Source code
│   ├── BOBSNE1/
│   ├── BOBSNE2/
│   ├── BOBSNE3/
│   └── BOBSNE4/
└── Disk F/                    # Additional source
```

### 9.2 Key Source Files

| File | Path | Purpose |
|------|------|---------|
| `INITLEVE.A` | BOBSNE3/ | Level initialization |
| `SCROLL.A` | BOBSNE3/ | Scroll/map routines |
| `WALLS.ASM` | BOBSNE2/ | Tile collision properties |
| `GENERATE.A` | BOBSNE3/ | Enemy generation |
| `COLLIDE.A` | BOBSNE3/ | Collision detection |

---

## 10. Quick Reference

### 10.1 Tilemap Entry Bitfield

```
 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
  Y  X  P  P  C  C  T  T  T  T  T  T  T  T  T  T

Y = Y-Flip (1 bit)
X = X-Flip (1 bit)
P = Palette (2 bits, 0-3)
C = CHR Bank (2 bits, 0-3)
T = Tile ID (10 bits, 0-1023)
```

### 10.2 Common ROM Addresses

| Address | Content | Size |
|---------|---------|------|
| 0x028000 | Tilemap 1 | 0x800 |
| 0x028800 | Tilemap 2 | 0x800 |
| 0x029000 | Tilemap 3 | 0x800 |
| 0x029800 | Tilemap 4 | 0x800 |
| 0x02A000 | Tilemap 5 | 0x800 |
| 0x038000 | Tilemap 6 | 0x800 |

### 10.3 Python Utilities

```python
# Parse tilemap from ROM
def parse_rom_tilemap(rom_data, offset):
    tiles = []
    for i in range(0x800):
        value = rom_data[offset + i*2] | (rom_data[offset + i*2 + 1] << 8)
        tiles.append(parse_tilemap_entry(value))
    return tiles

# Build tilemap for injection
def build_rom_tilemap(tiles):
    data = bytearray(0x800)
    for i, tile in enumerate(tiles[:1024]):
        value = build_tilemap_entry(**tile)
        data[i*2] = value & 0xFF
        data[i*2 + 1] = (value >> 8) & 0xFF
    return data
```

---

**References:**
- Original source code archives (Disk A-F)
- `docs/LEVEL_FORMAT_ANALYSIS.md` — Initial analysis
- `toolkit/bob_extract_levels.py` — Extraction implementation
- `toolkit/bob_inject.py` — Injection implementation

**Last Updated:** 2026-02-23
