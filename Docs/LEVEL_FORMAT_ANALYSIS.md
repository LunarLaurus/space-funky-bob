# Space Funky B.O.B. Level Format Analysis

## Overview

This document describes the level data format in Space Funky B.O.B. based on analysis of the original development source code and ROM.

## Level Types

From `INITLEVE.A`:
```
borglevel     = 0    # Borg fortress
buglevel      = 1    # Bug planet
spacelevel    = 3    # Space
ancientlevel  = 4    # Ancient ruins
lavalevel     = 6    # Lava world
ultralevel    = 8    # Ultra Force
bubblelevel   = 9    # Bubble forest
worldlevel    = 10   # World map
worldlevel2   = 11   
worldlevel3   = 12   
borglevel2    = 14   
```

## Map Data Storage

### ROM Bank Mapping

Different level types load from different ROM banks:
- Borg levels: bank 7
- Ancient levels: bank 19  
- Bubble/Ultra levels: bank 24
- (Other banks for different themes)

In LoROM mapping, each bank is 0x4000 bytes (32KB), mirrored throughout the 1MB ROM.

### Tilemap Format

**ROM Tilemap** (at addresses like 0x028000, 0x038000, etc.):
- Size: 0x800 bytes (2048 entries for 32x32 grid)
- Format: 16-bit SNES tilemap format
  - Bits 14-15: Palette (0-3)
  - Bits 10-13: CHR bank (0-15)
  - Bits 0-9: Tile ID (0-1023)
  - Bit 15: Y-flip
  - Bit 14: X-flip

### Map Size

From `SCROLL.A`:
```
mapsize   = 8192*2  = 16384 bytes  (80x80 max)
scrollmap = $7e3000
taskmap   = scrollmap + mapsize + bufferarea
```

## Development .MAP Files

Located in `source/Disk C/ANCMAPS/` and related directories.

### File Structure

- Total size: 131070 bytes (0x1FFFE)
- Header: 0x200 bytes of zeros
- Data: 255 blocks of 0x200 bytes each
- Format: 8-bit tile IDs (different from 16-bit ROM format)

### Block Format

Each 0x200 byte block appears to contain:
- 2-byte header: Unknown purpose (possibly level index or type)
- Tile data: 8-bit tile IDs
- Some blocks contain ASCII strings (like level names or metadata)

### Level Block Organization

Looking at ANC1.MAP:
```
Offset 0x200: 00 00 42 12 [tile data...]  (first level section)
Offset 0x230: 58 00 [zeros...]
Offset 0x300: 00 00 67 15 [tile data...]  (second level section)
Offset 0x330: 2a 43 44 45 (ASCII "CDE" - possibly level name)
...
```

## Level Loading Process

From the source code, levels are loaded as follows:

1. **Level Selection**: `mapnumber` and `maptype` determine which level
2. **Bank Loading**: Based on `maptype`, appropriate ROM bank is accessed
3. **Decompression**: Data is decompressed using the custom LZ77 variant
4. **Tilemap Conversion**: 8-bit .MAP tile IDs are converted to 16-bit SNES format
5. **RAM Placement**: Decompressed to `scrollmap` at $7e3000

## Block/Collision Data

From `WALLS.ASM`:
- Tile IDs have associated properties (solid, blank, death, ladder, etc.)
- Different level types have different tile property tables:
  - `borgkars` - Borg level tile properties
  - `bugkars` - Bug level tile properties  
  - `lavakars` - Lava level tile properties

### Tile Property IDs

```
#blank    = 0    (no collision)
#solid    = 1    (solid wall)
#death    = 2    (kill player)
#ladder   = 3    (climbable)
#overhand = 4    (can grab ledges)
#elevator = 5    (elevator shaft)
#victory  = 6    (level exit)
```

## Map Dimensions

Based on `SCROLL.A` and game mechanics:
- Maximum: 80x80 tiles (16384 bytes)
- Typical: Variable per level
- Screen: 32x32 tiles displayed at once (0x800 bytes for tilemap)

## Animation and Graphics

From `INITLEVE.A`:
```
animset:    # Based on maptype
  dc.b 0    # borg
  dc.b 4    # bug
  dc.b 1    # lava
  dc.b 2    # ultra
  ...

soundbank:  # Based on maptype
  dc.b 0    # borg
  dc.b 1    # bug
  dc.b 2    # ancient
  ...
```

## Enemy Generation

From `GENERATE.A`:
- Enemies are generated based on map tile values
- `generate_left_enemies` / `generate_right_enemies` scan map data
- Tile values determine enemy types and positions

## Tilemap Extraction

Our toolkit extracts tilemaps from ROM addresses in the pattern:
- 0x028000, 0x028800, 0x029000, ... (0x800 interval)
- 0x038000, 0x038800, ...
- Each is 0x800 bytes (32x32 SNES tilemap)

## Conversion Notes

To convert .MAP tile IDs to ROM 16-bit format:
1. Take the 8-bit tile ID from .MAP
2. Add appropriate CHR bank offset (based on level type)
3. Set palette based on tile type (from WALLS.ASM tables)
4. Format: `YFlip|XFlip|Palette|CHRbank|TileID`

## References

- `source/Disk D & E/BOBSNE3/INITLEVE.A` - Level initialization
- `source/Disk D & E/BOBSNE3/SCROLL.A` - Scroll/map routines
- `source/Disk D & E/BOBSNE2/WALLS.ASM` - Tile collision properties
- `source/Disk D & E/BOBSNE3/GENERATE.A` - Enemy generation from maps
- `source/Disk D & E/BOBSNE3/COLLIDE.A` - Collision detection

---

Last Updated: February 14, 2026
