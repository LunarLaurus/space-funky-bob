# Task BETA-001: Graphics Module Consolidation

**Squad:** Beta (Graphics & Visualization)  
**Priority:** P0 (Critical)  
**Complexity:** High  
**Estimated Effort:** 8-10 hours  
**Status:** ⏳ Pending

---

## Objective

Consolidate the four fragmented graphics modules (`bob_graphics.py`, `bob_graphics_v2.py`, `bob_graphics_classifier.py`, `bob_graphics_test_suite.py`) into a single, well-organized `bob_graphics.py` module with a clear API.

---

## Context

The graphics pipeline is currently split across 4 modules with overlapping functionality:
- `bob_graphics.py`: Basic rendering (raw bitmap, 2bpp, 4bpp)
- `bob_graphics_v2.py`: Enhanced 2bpp rendering with 32 tiles/row
- `bob_graphics_classifier.py`: Format auto-detection
- `bob_graphics_test_suite.py`: Test harness for manual review

This fragmentation causes:
- Code duplication
- Confusion about which module to use
- Difficult maintenance
- Inconsistent APIs

Consolidation will create a single source of truth with a clean, documented API.

---

## Acceptance Criteria

- [ ] Single module: `toolkit/bob_graphics.py` with all functionality
- [ ] Clear API structure:
  - `render_tile(data, format='2bpp', tile_size=8)` → pixel array
  - `render_to_image(tiles, cols=32, palette=None)` → PIL Image
  - `detect_format(data, offset)` → format string ('2bpp', '4bpp', '8bpp')
  - `extract_tiles(rom_data, offset, count, format='2bpp')` → tile list
- [ ] Backward compatibility: Deprecated modules import from consolidated module
- [ ] Documentation: Comprehensive docstrings and examples
- [ ] Tests: All existing tests pass with new module
- [ ] Deprecation notices in old modules pointing to new module

---

## Technical Notes

### Proposed Module Structure

```python
# toolkit/bob_graphics.py

class SNESGraphicsRenderer:
    """Main renderer class for SNES graphics."""
    
    def __init__(self, format='2bpp', tile_size=8):
        self.format = format
        self.tile_size = tile_size
    
    def render_tile(self, data, offset=0):
        """Render single tile to pixel array."""
        ...
    
    def render_tiles(self, data, offset=0, count=None, cols=32):
        """Render multiple tiles to PIL Image."""
        ...

def detect_graphics_format(data, offset=0, window_size=256):
    """Auto-detect graphics format from data."""
    ...

def extract_and_render(rom_data, offset, count=32, format='auto', output_path=None):
    """High-level API: extract and render in one call."""
    ...

# Legacy compatibility
def render_snes_tile_2bpp(data, offset, width=8, height=8):
    """Deprecated: Use SNESGraphicsRenderer.render_tile()"""
    ...
```

### Migration Strategy

1. Copy all functions to new module
2. Refactor to eliminate duplication
3. Add deprecation warnings to old modules
4. Update imports in dependent code
5. Remove old modules in future release

---

## Files to Modify

- `toolkit/bob_graphics.py` — Consolidated module
- `toolkit/bob_graphics_v2.py` — Add deprecation notice
- `toolkit/bob_graphics_classifier.py` — Add deprecation notice
- `toolkit/bob_graphics_test_suite.py` — Update imports
- `tests/test_graphics.py` — Update imports

---

## Dependencies

- **Blocks:** BETA-002, BETA-003, BETA-005 (all build on consolidated module)
- **Blocked by:** None

---

## Test Plan

1. Create `tests/test_graphics_consolidated.py`
2. Test cases:
   - `test_render_tile_2bpp()`
   - `test_render_tile_4bpp()`
   - `test_render_tile_8bpp()`
   - `test_detect_format_2bpp()`
   - `test_detect_format_4bpp()`
   - `test_extract_and_render()`
3. Verify all existing tests still pass
4. Test backward compatibility layer

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
