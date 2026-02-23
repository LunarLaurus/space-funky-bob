# Task BETA-002: SNES Tile Renderer Completion

**Squad:** Beta (Graphics & Visualization)  
**Priority:** P1 (High)  
**Complexity:** Medium  
**Estimated Effort:** 6-8 hours  
**Status:** ⏳ Pending

---

## Objective

Complete the SNES tile renderer to support all graphics formats (2bpp, 4bpp, 8bpp) with proper palette handling, producing accurate PNG output for extracted graphics data.

---

## Context

The current renderer (`bob_graphics.py`) has partial format support:
- ✅ 2bpp: Working (confirmed with decompressed_0A0000.bin)
- ⚠️ 4bpp: Implemented but not thoroughly tested
- ❌ 8bpp: Not implemented

A complete renderer would:
- Support all three SNES formats
- Handle tile arrangement (rows/columns)
- Apply SNES palettes correctly
- Output standard PNG files

---

## Acceptance Criteria

- [ ] 2bpp rendering: Verified working with test vectors
- [ ] 4bpp rendering: Implemented and tested
- [ ] 8bpp rendering: Implemented and tested
- [ ] Tile arrangement: Configurable cols/rows for sprite sheets
- [ ] Palette support: Apply SNES palette to rendered tiles
- [ ] Output formats: PNG (via PIL), raw pixel arrays
- [ ] Documentation: Format specifications, usage examples
- [ ] Tests: Visual regression tests with reference images

---

## Technical Notes

### 2bpp Format (4 colors)
```python
def render_2bpp_tile(data, offset):
    """
    Render 8x8 2bpp tile.
    Each row: 2 bytes (bitplane 0, bitplane 1)
    Pixel value: (bitplane1 << 1) | bitplane0
    """
    pixels = []
    for y in range(8):
        b0 = data[offset + y*2]
        b1 = data[offset + y*2 + 1]
        for x in range(7, -1, -1):
            bit0 = (b0 >> x) & 1
            bit1 = (b1 >> x) & 1
            pixels.append((bit1 << 1) | bit0)
    return pixels
```

### 4bpp Format (16 colors)
```python
def render_4bpp_tile(data, offset):
    """
    Render 8x8 4bpp tile.
    Each row: 4 bytes (bitplanes 0-3)
    Pixel value: b3<<3 | b2<<2 | b1<<1 | b0
    """
```

### 8bpp Format (256 colors)
```python
def render_8bpp_tile(data, offset):
    """
    Render 8x8 8bpp tile.
    Each row: 8 bytes (bitplanes 0-7)
    Pixel value: direct byte value
    """
```

### SNES Palette Format
- 16 colors per palette
- 2 bytes per color (RGB555: BBBBBGGGGGRRRRR)
- Color 0 is transparent

---

## Files to Modify

- `toolkit/bob_graphics.py` — Add 4bpp/8bpp rendering
- `toolkit/bob_render.py` — Integrate with blob visualization
- `tests/test_graphics.py` — Add format-specific tests

---

## Dependencies

- **Blocks:** BETA-005 (sprite sheets need complete renderer)
- **Blocked by:** BETA-001 (consolidated module provides foundation)

---

## Test Plan

1. Create `tests/test_snes_tile_renderer.py`
2. Test cases:
   - `test_2bpp_known_tile()` — Use known good test vector
   - `test_4bpp_gradient()` — Test all 16 colors
   - `test_8bpp_full_range()` — Test 256 colors
   - `test_tile_arrangement()` — Verify cols/rows layout
   - `test_palette_application()` — Verify colors correct
3. Create reference images for visual regression testing

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** ✅ COMPLETE — 8bpp renderer verified and tested
  - Verified: 8bpp rendering already implemented in consolidated module
  - SNESGraphicsRenderer supports 2bpp/4bpp/8bpp formats
  - Created `tests/test_graphics_renderer.py` with 23 tests (all passing)
  - Test coverage: 2bpp (4 tests), 4bpp (2 tests), 8bpp (3 tests), renderer class (8 tests), palettes (3 tests), tile-to-image (3 tests)
  - All acceptance criteria met
