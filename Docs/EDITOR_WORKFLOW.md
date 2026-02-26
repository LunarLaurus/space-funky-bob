# B.O.B. Level Editor - Complete Workflow

## Overview

This toolkit provides all tools needed to edit B.O.B. (Space Funky B.O.B.) SNES ROM levels.

## Quick Start

### 1. Extract Levels

```bash
cd toolkit
python bob_extract_levels.py --rom "../rom/B.O.B. (U) [!].smc" --outdir ../data/levels
```

This extracts all 138+ tilemaps to `data/levels/`

### 2. Preview Levels

```bash
python bob_visualize.py --tiledir ../data/levels --output ../data/levels/levels.html --limit 20
```

Open `data/levels/levels.html` in a browser to see level previews.

### 3. Edit Tilemaps

1. Navigate to the tilemap you want to edit in `data/levels/`
2. Edit the `.bin` file (0x800 bytes = 32x32 grid)
3. Each 2 bytes = one tile: `[low][high]`
   - Bits 0-9: Tile ID (0-1023)
   - Bits 10-11: CHR Bank (0-3)
   - Bits 12-13: Palette (0-3)
   - Bit 14: X-flip
   - Bit 15: Y-flip

### 4. Inject Modified Tilemap

```bash
python bob_inject.py \
    --rom "../rom/B.O.B. (U) [!].smc" \
    --tilemap ../data/levels/tilemap_04_02A000.bin \
    --offset 0x02A000 \
    --output "../rom/B.O.B.modified.smc"
```

### 5. Test Modified ROM

Run the modified ROM in an emulator (bsnes, Snes9x, etc.)

## Working with Compressed Graphics

### Extract Compressed Graphics

```bash
python bob_lz_scan.py --rom "../rom/B.O.B. (U) [!].smc" --outdir ../data/compressed
```

### Edit and Re-compress

```bash
# Edit the decompressed .bin file in data/compressed/
# Then re-compress and inject:

python bob_inject.py \
    --rom "../rom/B.O.B. (U) [!].smc" \
    --uncompressed ../data/compressed/decompressed_030000.bin \
    --offset 0x030000 \
    --output "../rom/B.O.B.modified.smc"
```

## Tool Reference

| Tool | Purpose | Usage |
|------|---------|-------|
| `bob_extract_levels.py` | Extract all tilemaps | `--rom ROM --outdir DIR` |
| `bob_visualize.py` | Generate HTML previews | `--tiledir DIR --output FILE` |
| `bob_inject.py` | Inject modified data | `--rom ROM --tilemap FILE --offset HEX` |
| `bob_lz_scan.py` | Find compressed blocks | `--rom ROM --outdir DIR` |
| `bob_lz_encode.py` | Compress data | (module use) |

## File Formats

### Tilemap (.bin)
- Size: 0x800 bytes (2048 bytes as extracted)
- Structure: 1024 16-bit entries in 32x32 grid
- Format: `YYYYXXPPCCCCCCCCCC` (Y=Yflip, X=Xflip, P=palette, C=CHR)

### Compressed Block
- LZ77 variant as documented at superfamicom.org
- Use `bob_lz_encode.py` to compress
- Use `bob_lz_decompress.py` to decompress

## ROM Map

| Address | Description |
|---------|-------------|
| 0x018000 | Compressed graphics |
| 0x028000-0x02C800 | Tilemaps (World 1 area) |
| 0x030000 | Compressed graphics |
| 0x038000-0x03C800 | Tilemaps (World 2 area) |
| 0x048000-0x04C800 | More tilemaps |
| 0x060000 | Compressed graphics |
| 0x090000 | Compressed graphics |
| 0x0A0000 | Compressed graphics |

## Tips

1. **Backup ROMs**: Always keep backups of your original ROM
2. **Use patches**: Use `--patch` in bob_inject.py to create diff patches
3. **Test often**: Test changes in emulator frequently
4. **Understand format**: Tilemaps need corresponding graphics (CHR tiles) to display correctly

## Troubleshooting

### Tilemap looks wrong in game?
- The game may have multiple layers (BG1, BG2, etc.)
- Check if you edited the correct tilemap offset
- Some tilemaps may share graphics data

### Compression doesn't work?
- Ensure uncompressed size matches expected (0x800 for standard)
- Use `--size` parameter to validate

### Game crashes after modification?
- Check offset is correct
- Ensure modified data fits within ROM bounds
- Verify checksum is valid (or use a header fixer)
