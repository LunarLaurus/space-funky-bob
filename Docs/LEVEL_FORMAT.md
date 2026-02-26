# B.O.B. Level Data Format

## Overview

The B.O.B. ROM contains:
- **Compressed Graphics**: LZ77-encoded tile data (found at 0x018000, 0x030000, 0x060000, etc.)
- **Level Tilemaps**: Uncompressed SNES background maps

## Tilemap Format

**Location**: ROM 0x028000-0x02C800, 0x038000-0x03C800 (and similar)

**Size**: 0x800 bytes per tilemap (1024 entries = 32x32 grid)

**Structure**: 16-bit entries per tile

```
Bits:    [YFlip][XFlip][Palette][CHR Bank][Tile ID]
         15     14     13-12   11-10      9-0
```

| Bits | Name | Description |
|------|------|-------------|
| 15 | Y Flip | Vertical flip (1 = flipped) |
| 14 | X Flip | Horizontal flip (1 = flipped) |
| 13-12 | Palette | 4-color palette selection (0-3) |
| 11-10 | CHR Bank | Character ROM bank (0-3) |
| 9-0 | Tile ID | Tile index (0-1023) |

## Compressed Graphics

**Compression**: B.O.B. LZ77 variant

**Format**:
- 8-bit chunk header, processed MSB first
- Bit 0: literal byte (copy next byte)
- Bit 1: distance/length pair (16-bit LE)
  - Low 11 bits: distance (1-2047)
  - High 5 bits: (length - 3), effective length 3-34

**Known Compressed Blocks**:
| Offset | Decompressed Size |
|--------|------------------|
| 0x018000 | 0x800 |
| 0x030000 | 0x800 |
| 0x060000 | 0x800 |
| 0x090000 | 0x800 |
| 0x0A0000 | 0x800 |
| 0x1AD34 | 0x822 (documented example) |

## Level Editor Requirements

1. **Extract Tilemaps**: Read 0x800 bytes from tilemap addresses
2. **Edit Tilemaps**: Modify 16-bit entries, preserve format
3. **Recompress Graphics**: Use LZ77 encoder for modified tiles
4. **Reinsert**: Write back to ROM (maintaining size)

## Tool Usage

```bash
# Extract level tilemaps
python toolkit/bob_extract_levels.py --rom "rom/B.O.B..smc" --outdir data/levels

# List known tilemap locations
python toolkit/bob_list_tilemaps.py --rom "rom/B.O.B..smc"
```
