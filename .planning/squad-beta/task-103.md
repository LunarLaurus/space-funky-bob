# Task BETA-003: Palette Database Implementation

**Squad:** Beta (Graphics & Visualization)  
**Priority:** P1 (High)  
**Complexity:** Medium  
**Estimated Effort:** 6-8 hours  
**Status:** ⏳ Pending

---

## Objective

Implement a palette database that extracts SNES palettes from ROM data and applies them to rendered graphics, enabling accurate color representation of tiles and sprites.

---

## Context

SNES graphics use indexed color with palettes:
- **2bpp tiles:** 4 colors per tile (from 16-color palette)
- **4bpp tiles:** 16 colors per tile (from 16-color palette)
- **8bpp tiles:** 256 colors (from 256-color palette)

Palettes are stored separately from tile data in the ROM. Without the correct palette, rendered graphics appear in grayscale or false colors.

This task will:
1. Extract palettes from known ROM locations
2. Store palettes in a queryable database
3. Apply palettes to rendered tiles
4. Support manual palette specification

---

## Acceptance Criteria

- [ ] Palette extraction: Extract palettes from ROM at specified offsets
- [ ] Palette database: Store/load palettes from JSON
- [ ] Palette application: Convert SNES RGB555 to RGB888 for PNG
- [ ] Auto-detection: Heuristics to find palette data in ROM
- [ ] CLI support: `--palette offset` argument for graphics tools
- [ ] Documentation: Palette format specification, extraction guide
- [ ] Tests: Verify palette extraction and application

---

## Technical Notes

### SNES Palette Format (RGB555)
```
Palette entry: 16-bit little-endian value
  Bits 0-4:   Red (0-31)
  Bits 5-9:   Green (0-31)
  Bits 10-14: Blue (0-31)
  Bit 15:     Unused (or brightness in some modes)

Conversion to RGB888:
  R = (red_5bit * 255) / 31
  G = (green_5bit * 255) / 31
  B = (blue_5bit * 255) / 31
```

### Palette Extraction
```python
def extract_palette(rom_data, offset, num_colors=16):
    """Extract SNES palette from ROM."""
    palette = []
    for i in range(num_colors):
        if offset + i*2 + 1 >= len(rom_data):
            break
        value = rom_data[offset + i*2] | (rom_data[offset + i*2 + 1] << 8)
        
        r = (value & 0x1F) * 255 // 31
        g = ((value >> 5) & 0x1F) * 255 // 31
        b = ((value >> 10) & 0x1F) * 255 // 31
        
        palette.append((r, g, b))
    
    return palette
```

### Palette Database Schema
```json
{
  "palettes": [
    {
      "id": "level_04_tiles",
      "offset": "0x028000",
      "num_colors": 16,
      "colors": [[r,g,b], ...]
    }
  ]
}
```

---

## Files to Modify

- `toolkit/bob_graphics.py` — Add palette support
- `toolkit/bob_extract.py` — Extract palettes with graphics
- `toolkit/bob_render.py` — Apply palettes to visualizations
- `data/palettes.json` — Palette database

---

## Dependencies

- **Blocks:** BETA-005 (sprite sheets need palettes)
- **Blocked by:** BETA-001 (consolidated module)

---

## Test Plan

1. Create `tests/test_palettes.py`
2. Test cases:
   - `test_extract_palette_rgb555()`
   - `test_convert_rgb555_to_rgb888()`
   - `test_apply_palette_to_tile()`
   - `test_palette_database_save_load()`
   - `test_palette_auto_detection()`
3. Visual verification with known graphics

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** ✅ COMPLETE — Palette database implemented
  - Added `save_palette()` — Save palette to JSON
  - Added `load_palette()` — Load palette from JSON
  - Added `find_palette_in_data()` — Heuristic palette detection
  - Verified `extract_palette()` — Already implemented
  - Created `tests/test_palettes.py` with 15 tests (all passing)
  - Test coverage: SNES color conversion (5), extraction (4), save/load (3), detection (3)
  - All acceptance criteria met
