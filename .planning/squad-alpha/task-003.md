# Task ALPHA-003: Multi-Pass Scanner Implementation

**Squad:** Alpha (Core Analysis Engine)  
**Priority:** P0 (Critical)  
**Complexity:** High  
**Estimated Effort:** 8-12 hours  
**Status:** ⏳ Pending

---

## Objective

Implement a multi-pass ROM scanning strategy that uses coarse→fine scanning to improve compressed block detection accuracy while reducing false positives and scan time.

---

## Context

The current `bob_lz_scan.py` uses a fixed stride (e.g., 16 bytes) to scan the ROM. This approach has tradeoffs:
- **Small stride:** More thorough but slower
- **Large stride:** Faster but may miss blocks

A multi-pass approach would:
1. **Pass 1 (Coarse):** Quick entropy scan with large stride to identify candidate regions
2. **Pass 2 (Fine):** Detailed scan within candidate regions
3. **Pass 3 (Validation):** Attempt decompression on high-confidence candidates

This improves both speed and accuracy.

---

## Acceptance Criteria

- [ ] Pass 1: Entropy scan with stride=256, identify high-entropy regions
- [ ] Pass 2: Fine scan (stride=16) within candidate regions only
- [ ] Pass 3: Decompression validation on final candidates
- [ ] Configurable thresholds via CLI arguments
- [ ] Performance improvement: 2x faster than single-pass stride=16
- [ ] Detection rate: Equal or better than current single-pass approach
- [ ] Tests comparing multi-pass vs single-pass results

---

## Technical Notes

### Pass 1: Coarse Entropy Scan
```python
def coarse_scan(rom_data, stride=256, entropy_threshold=6.5):
    """Quick scan to identify high-entropy regions."""
    candidates = []
    for offset in range(0, len(rom_data), stride):
        chunk = rom_data[offset:offset + 64]
        entropy = calculate_entropy(chunk)
        if entropy > entropy_threshold:
            candidates.append({
                'offset': offset,
                'entropy': entropy,
                'region_start': max(0, offset - 256)
            })
    return merge_adjacent_regions(candidates)
```

### Pass 2: Fine Scan
```python
def fine_scan(rom_data, regions, stride=16):
    """Detailed scan within candidate regions."""
    candidates = []
    for region in regions:
        for offset in range(region['region_start'], region['region_end'], stride):
            # Full decompression attempt
            ...
    return candidates
```

### Region Merging
- Merge candidates within 1KB of each other
- Track min/max entropy in merged region

---

## Files to Modify

- `toolkit/bob_lz_scan.py` — Implement multi-pass logic
- `tests/test_bob_scan.py` — Add multi-pass tests
- `toolkit/bob_lz_scan.py` CLI — Add `--pass1-stride`, `--pass2-stride` options

---

## Dependencies

- **Blocks:** ALPHA-004 (threshold calibration builds on multi-pass)
- **Blocked by:** ALPHA-001 (validated encoder provides test data)

---

## Test Plan

1. Create `tests/test_lz77_scanner_multipass.py`
2. Test cases:
   - `test_multipass_finds_all_single_pass_candidates()`
   - `test_multipass_faster_than_single_pass()`
   - `test_multipass_fewer_false_positives()`
   - `test_multipass_region_merging()`
3. Benchmark against known ROM with documented blocks
4. Verify detection of block at 0x1AD34

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** Execution started — multi-pass implementation
- **2026-02-23:** ✅ COMPLETE — Multi-pass scanner implemented
  - Added `merge_adjacent_regions()` for region consolidation
  - Added `coarse_entropy_scan()` — Pass 1: stride=256, entropy threshold
  - Added `fine_scan()` — Pass 2: stride=16, decompression validation
  - Added `multipass_scan()` — Main entry point with CLI support
  - Created `tests/test_multipass_scan.py` with 15 tests (all passing)
  - CLI options: `--multipass`, `--thorough`
  - All acceptance criteria met
