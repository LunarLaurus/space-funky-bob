# Task GAMMA-002: Tilemap Extraction Validation

**Squad:** Gamma (Level Editor Tools)  
**Priority:** P1 (High)  
**Complexity:** Low  
**Estimated Effort:** 3-4 hours  
**Status:** ⏳ Pending

---

## Objective

Create comprehensive test suite for tilemap extraction tools, ensuring all known tilemap locations are correctly extracted and validated against expected format.

---

## Context

The `bob_extract_levels.py` tool extracts tilemaps from known ROM locations. While the tool exists, it lacks:
- Comprehensive test coverage
- Validation of extracted data format
- Regression tests for future changes
- Documentation of expected outputs

This task will create a test suite that validates extraction correctness.

---

## Acceptance Criteria

- [ ] Test all known tilemap locations (10+ locations)
- [ ] Validate tilemap structure (1024 entries, 16-bit each)
- [ ] Verify tile ID ranges (0-1023 valid)
- [ ] Check palette/christ_bank values (0-3 valid)
- [ ] Test edge cases (partial tilemaps, corrupted data)
- [ ] Integration with `run_full_test_suite.py`
- [ ] Documentation of test methodology

---

## Technical Notes

### Known Tilemap Locations

```python
TILEMAP_LOCATIONS = [
    {'offset': 0x028000, 'size': 0x800, 'name': 'level_01'},
    {'offset': 0x028800, 'size': 0x800, 'name': 'level_02'},
    {'offset': 0x029000, 'size': 0x800, 'name': 'level_03'},
    {'offset': 0x029800, 'size': 0x800, 'name': 'level_04'},
    {'offset': 0x038000, 'size': 0x800, 'name': 'level_05'},
    # ... more locations
]
```

### Validation Checks

```python
def validate_tilemap_entry(entry):
    """Validate a single 16-bit tilemap entry."""
    tile_id = entry & 0x3FF
    chr_bank = (entry >> 10) & 0x3
    palette = (entry >> 12) & 0x3
    x_flip = (entry >> 14) & 1
    y_flip = (entry >> 15) & 1
    
    assert tile_id < 1024, f"Invalid tile ID: {tile_id}"
    assert chr_bank < 4, f"Invalid CHR bank: {chr_bank}"
    assert palette < 4, f"Invalid palette: {palette}"
    assert x_flip in [0, 1], f"Invalid X flip: {x_flip}"
    assert y_flip in [0, 1], f"Invalid Y flip: {y_flip}"
```

---

## Files to Modify

- `tests/test_tilemap_extraction.py` — New test file
- `toolkit/bob_extract_levels.py` — Add validation hooks
- `run_full_test_suite.py` — Integrate new tests

---

## Dependencies

- **Blocks:** GAMMA-004 (CLI needs validated extraction)
- **Blocked by:** GAMMA-001 (format documentation informs validation)

---

## Test Plan

1. Create `tests/test_tilemap_extraction.py`
2. Test cases:
   - `test_extract_all_known_locations()`
   - `test_validate_tilemap_structure()`
   - `test_validate_tile_entries()`
   - `test_partial_tilemap_handling()`
   - `test_round_trip_injection()`
3. Run full test suite, verify 0 failures

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
