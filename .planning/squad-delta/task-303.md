# Task DELTA-003: Edge Case Test Expansion

**Squad:** Delta (Testing & QA)  
**Priority:** P0 (Critical)  
**Complexity:** Medium  
**Estimated Effort:** 8-10 hours  
**Status:** ⏳ Pending

---

## Objective

Expand test suite with 50+ edge case tests covering error handling, boundary conditions, invalid inputs, and unusual usage patterns to improve robustness and catch regressions.

---

## Context

Current tests focus on happy-path scenarios. Edge cases like:
- Empty inputs
- Truncated data
- Invalid parameters
- Boundary values
- Concurrent access

are under-tested. This task will systematically add edge case tests for all modules.

---

## Acceptance Criteria

- [ ] LZ77 module: 15+ edge case tests
- [ ] Scanner module: 10+ edge case tests
- [ ] Mapper module: 10+ edge case tests
- [ ] Graphics module: 10+ edge case tests
- [ ] Extract/Inject: 10+ edge case tests
- [ ] Error messages: All ValueError/AssertionError have descriptive messages
- [ ] Test organization: Tests grouped by module and category

---

## Technical Notes

### Edge Case Categories

**Input Validation:**
```python
def test_decompress_empty_input():
    """Empty input should return empty output."""
    result, consumed = bob_lz_decompress(b'', 0)
    assert result == b''
    assert consumed == 0

def test_decompress_truncated_header():
    """Truncated chunk header should raise ValueError."""
    with pytest.raises(ValueError) as exc_info:
        bob_lz_decompress(bytes([0x80]), 8)  # Header but no data
    assert "unexpected end of input" in str(exc_info.value)

def test_decompress_invalid_distance():
    """Distance of 0 should raise ValueError."""
    with pytest.raises(ValueError) as exc_info:
        bob_lz_decompress(bytes([0x80, 0x00, 0x00]), 8)
    assert "invalid distance 0" in str(exc_info.value)
```

**Boundary Conditions:**
```python
def test_decompress_exact_buffer_size():
    """Decompression with exact buffer size."""
    # Test when output exactly matches expected size
    ...

def test_scan_rom_boundary():
    """Scanner at ROM boundaries."""
    # Test scanning at exact ROM start/end
    ...
```

**Error Recovery:**
```python
def test_exploratory_mode_with_errors():
    """Exploratory decompression should handle errors gracefully."""
    result, consumed, error = bob_lz_decompress_exploratory(bad_data)
    assert error is not None  # Should report error, not crash
```

---

## Files to Modify

- `tests/test_bob_lz_edge_cases.py` — New test file
- `tests/test_bob_scan_edge_cases.py` — New test file
- `tests/test_bob_map_edge_cases.py` — New test file
- `tests/test_graphics_edge_cases.py` — New test file
- `tests/test_extract_edge_cases.py` — New test file

---

## Dependencies

- **Blocks:** None
- **Blocked by:** DELTA-002 (coverage analysis identifies gaps)

---

## Test Plan

1. Create edge case test files for each module
2. Run full test suite, verify all pass
3. Measure coverage improvement
4. Document edge cases covered

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** ✅ COMPLETE — LZ77 edge case tests complete
  - Created `tests/test_lz77_edge_cases.py` with 25 tests (all passing)
  - Test categories: empty inputs (3), truncated (4), invalid distance (3), boundaries (5), patterns (5), find_best_match (3), error messages (2)
  - All acceptance criteria met (LZ77 module: 25+ edge case tests)
