# Squad Beta — Graphics & Visualization

**Mission:** Unify the fragmented graphics pipeline, complete the SNES tile renderer, and enhance HTML visualization for intuitive ROM exploration.

---

## Scope

Squad Beta owns graphics detection, rendering, and visualization:
- **Graphics Detection** (`bob_graphics.py`, `bob_graphics_v2.py`, `bob_graphics_classifier.py`)
- **Tile Rendering** (`bob_render.py`)
- **ROM Visualization** (`bob_visualize.py`)

---

## Objectives

### Primary Goals
1. Consolidate 4 graphics modules into unified pipeline
2. Complete SNES tile renderer with full format support (2bpp/4bpp/8bpp)
3. Implement palette extraction and application
4. Enhance HTML ROM map with interactive features

### Secondary Goals
1. Generate sprite sheets from extracted tiles
2. Add graphics format auto-detection
3. Create graphics preview CLI tool

---

## Tasks

| ID | Title | Priority | Complexity | Status |
|----|-------|----------|------------|--------|
| BETA-001 | Graphics Module Consolidation | P0 | High | ⏳ Pending |
| BETA-002 | SNES Tile Renderer Completion | P1 | Medium | ⏳ Pending |
| BETA-003 | Palette Database Implementation | P1 | Medium | ⏳ Pending |
| BETA-004 | HTML ROM Map Enhancement | P2 | Low | ⏳ Pending |
| BETA-005 | Sprite Sheet Generation | P2 | Medium | ⏳ Pending |

---

## Success Metrics

- **Module Consolidation:** Single `bob_graphics.py` with clear API
- **Renderer Completeness:** Support 2bpp, 4bpp, 8bpp formats
- **Detection Accuracy:** >90% correct format auto-detection
- **Visualization Quality:** Interactive HTML with tooltips, filtering

---

## Dependencies

### Internal
- Squad Alpha: Multi-pass scanner (ALPHA-003) for better graphics region detection
- Squad Delta: Test suite consolidation (DELTA-001)

### External
- PIL/Pillow for PNG rendering (already in use)

---

## Technical Notes

### SNES Graphics Formats

**2bpp (4 colors):**
- 16 bytes per 8x8 tile
- 2 bitplanes, 8 bytes each
- Each pixel: 2 bits (0-3)

**4bpp (16 colors):**
- 32 bytes per 8x8 tile
- 4 bitplanes, 8 bytes each
- Each pixel: 4 bits (0-15)

**8bpp (256 colors):**
- 64 bytes per 8x8 tile
- 8 bitplanes, 8 bytes each
- Each pixel: 8 bits (0-255)

### Current Module Fragmentation

| Module | Purpose | Status |
|--------|---------|--------|
| `bob_graphics.py` | Basic rendering | Working, limited formats |
| `bob_graphics_v2.py` | Enhanced rendering | Working, 2bpp confirmed |
| `bob_graphics_classifier.py` | Format detection | Experimental |
| `bob_graphics_test_suite.py` | Test rendering | Test harness only |

---

## Status Log

### Day 1 (2026-02-23)
- Squad created
- Task descriptors written
- Awaiting kickoff

---

**Lead:** TBD  
**Members:** TBD  
**Started:** 2026-02-23  
**Target Complete:** 2026-03-07 (Day 12)
