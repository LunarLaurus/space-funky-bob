# Task BETA-005: Sprite Sheet Generation

**Squad:** Beta (Graphics & Visualization)  
**Priority:** P2 (Medium)  
**Complexity:** Medium  
**Estimated Effort:** 6-8 hours  
**Status:** ⏳ Pending

---

## Objective

Implement sprite sheet generation that assembles extracted tiles into organized PNG sprite sheets, enabling quick visual review of graphics assets and easy integration with level editors.

---

## Context

Extracted graphics tiles are most useful when assembled into sprite sheets:
- **Tile sheets:** All tiles from a compressed block arranged in a grid
- **Sprite sheets:** Multiple frames of an animated sprite
- **Background sheets:** Complete background tile sets

Sprite sheets enable:
- Quick visual identification of graphics assets
- Easy import into level editors
- Animation frame sequencing
- Asset cataloging for ROM hackers

---

## Acceptance Criteria

- [ ] Grid layout: Configurable rows/cols for tile arrangement
- [ ] Auto-sizing: Automatically determine optimal grid dimensions
- [ ] Spacing: Configurable spacing between tiles
- [ ] Labels: Optional tile indices/labels
- [ ] Multiple formats: Support 2bpp, 4bpp, 8bpp in same sheet
- [ ] Palette support: Apply extracted palettes
- [ ] Output: PNG format with transparency support
- [ ] Metadata: Generate JSON manifest with tile positions
- [ ] Tests: Verify tile positions and output quality

---

## Technical Notes

### Sprite Sheet Layout
```python
def generate_sprite_sheet(tiles, cols=16, tile_size=8, spacing=1, palette=None):
    """
    Generate sprite sheet from tiles.
    
    Args:
        tiles: List of tile pixel arrays
        cols: Number of columns
        tile_size: Size of each tile (8 for 8x8)
        spacing: Pixels between tiles
        palette: Optional palette to apply
    
    Returns:
        PIL Image of sprite sheet
    """
    rows = math.ceil(len(tiles) / cols)
    sheet_width = cols * tile_size + (cols + 1) * spacing
    sheet_height = rows * tile_size + (rows + 1) * spacing
    
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    for idx, tile_pixels in enumerate(tiles):
        col = idx % cols
        row = idx // cols
        x = spacing + col * (tile_size + spacing)
        y = spacing + row * (tile_size + spacing)
        
        # Convert tile pixels to image
        tile_img = pixels_to_image(tile_pixels, tile_size, palette)
        sheet.paste(tile_img, (x, y))
    
    return sheet
```

### Manifest Format
```json
{
  "sprite_sheet": "gfx_sheet_0A0000.png",
  "tile_size": 8,
  "format": "2bpp",
  "cols": 16,
  "rows": 2,
  "total_tiles": 32,
  "tiles": [
    {"index": 0, "x": 1, "y": 1, "offset": "0x00"},
    {"index": 1, "x": 9, "y": 1, "offset": "0x10"},
    ...
  ]
}
```

---

## Files to Modify

- `toolkit/bob_graphics.py` — Add sprite sheet generation
- `toolkit/bob_render.py` — Integrate sprite sheets
- `toolkit/bob_extract.py` — Add sprite sheet output option

---

## Dependencies

- **Blocks:** None
- **Blocked by:** BETA-001 (consolidated module), BETA-002 (complete renderer)

---

## Test Plan

1. Create `tests/test_sprite_sheets.py`
2. Test cases:
   - `test_sprite_sheet_grid_layout()`
   - `test_sprite_sheet_auto_size()`
   - `test_sprite_sheet_with_spacing()`
   - `test_sprite_sheet_with_palette()`
   - `test_sprite_sheet_manifest()`
3. Visual verification with known graphics blocks

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
