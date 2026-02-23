# Task ALPHA-001: LZ77 Encoder Round-Trip Testing

**Squad:** Alpha (Core Analysis Engine)  
**Priority:** P0 (Critical)  
**Complexity:** Medium  
**Estimated Effort:** 4-6 hours  
**Status:** ⏳ Pending

---

## Objective

Validate that the LZ77 encoder (`bob_lz_encode.py`) produces output that the decoder (`bob_lz.py`) can correctly decompress, ensuring perfect round-trip integrity for all test vectors.

---

## Context

The B.O.B. toolkit includes both a decoder (`bob_lz.py`) and an encoder (`bob_lz_encode.py`). While the decoder has unit tests, the encoder lacks comprehensive validation. This task ensures that:
1. Encoded data decodes back to the original input
2. Edge cases (empty data, single bytes, large files) are handled
3. Compression ratio is reasonable for typical inputs

This is critical for the level editor workflow, where modified data must be re-compressed and injected back into the ROM.

---

## Acceptance Criteria

- [ ] Round-trip test: encode(original) → decode(result) == original for all test vectors
- [ ] Edge case tests: empty data, single byte, 1KB, 64KB inputs
- [ ] Known block test: decompress known ROM block, re-compress, verify match
- [ ] Compression ratio test: typical inputs achieve >30% compression
- [ ] All tests integrated into `run_full_test_suite.py`

---

## Technical Notes

### Test Vector Sources
1. **Synthetic data:** Random bytes, repeating patterns, sequential bytes
2. **Extracted ROM data:** Use `data/decompressed_*.bin` files
3. **Known block:** Block at 0x1AD34 (0x822 bytes decompressed)

### Encoder Parameters
- `lazy=True`: Use lazy matching for better compression
- Window size: 2047 bytes (max distance)
- Max match length: 34 bytes

### Test Implementation
```python
from toolkit.bob_lz_encode import bob_lz_encode
from toolkit.bob_lz import bob_lz_decompress

def test_round_trip(original_data):
    compressed = bob_lz_encode(original_data)
    decompressed, consumed = bob_lz_decompress(compressed, len(original_data))
    assert decompressed == original_data
```

---

## Files to Modify

- `toolkit/bob_lz_encode.py` — May need bug fixes
- `tests/test_bob_lz.py` — Add round-trip tests
- `run_full_test_suite.py` — Integrate new tests

---

## Dependencies

- **Blocks:** ALPHA-002 (streaming API needs validated encoder)
- **Blocked by:** None

---

## Test Plan

1. Create test file `tests/test_lz77_roundtrip.py`
2. Implement test cases:
   - `test_round_trip_empty()`
   - `test_round_trip_single_byte()`
   - `test_round_trip_small_data()`
   - `test_round_trip_large_data()`
   - `test_round_trip_rom_block()`
3. Run full test suite, verify 0 failures
4. Measure compression ratios

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
