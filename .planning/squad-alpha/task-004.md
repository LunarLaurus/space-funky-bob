# Task ALPHA-004: Entropy Threshold Calibration

**Squad:** Alpha (Core Analysis Engine)  
**Priority:** P1 (High)  
**Complexity:** Low  
**Estimated Effort:** 3-4 hours  
**Status:** ⏳ Pending

---

## Objective

Calibrate entropy thresholds and heuristics used in compressed block detection using empirical data from known ROM blocks, reducing false positives and false negatives.

---

## Context

The current scanner uses hardcoded entropy thresholds:
- `entropy > 6.5`: Likely compressed
- `entropy > 7.2`: Definitely compressed
- `entropy < 4.0`: Likely graphics

These thresholds were chosen heuristically and may not be optimal for all ROMs. This task will:
1. Collect entropy data from known compressed blocks
2. Analyze entropy distributions for different region types
3. Calibrate thresholds for optimal detection
4. Document threshold selection rationale

---

## Acceptance Criteria

- [ ] Entropy dataset: Collect entropy values from 50+ known blocks
- [ ] Distribution analysis: Plot entropy histograms for code/data/compressed/graphics
- [ ] Threshold optimization: Find thresholds that maximize F1 score
- [ ] Documentation: Write `docs/ENTROPY_THRESHOLDS.md` with methodology
- [ ] Config file: Add `configs/thresholds.yaml` with calibrated values
- [ ] Tests: Verify new thresholds detect all known blocks

---

## Technical Notes

### Data Collection
```python
# Scan known compressed blocks
for candidate in candidates:
    if candidate['success']:
        compressed_data = rom[candidate['offset']:candidate['offset']+64]
        entropy = calculate_entropy(compressed_data)
        data.append({
            'type': 'compressed',
            'entropy': entropy,
            'offset': candidate['offset']
        })
```

### Threshold Optimization
```python
from sklearn.metrics import f1_score

def find_optimal_threshold(entropies, labels):
    """Find threshold that maximizes F1 score."""
    best_f1 = 0
    best_threshold = 0
    for threshold in np.arange(5.0, 8.0, 0.1):
        predictions = [1 if e > threshold else 0 for e in entropies]
        f1 = f1_score(labels, predictions)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    return best_threshold
```

### Recommended Thresholds (to be validated)
- **Compressed:** entropy > 6.8
- **Graphics:** entropy < 4.5 AND low byte variance
- **Code:** entropy < 6.5 AND high opcode density
- **Data:** 4.5 < entropy < 6.8

---

## Files to Modify

- `toolkit/bob_lz_scan.py` — Update threshold constants
- `configs/thresholds.yaml` — New config file
- `docs/ENTROPY_THRESHOLDS.md` — New documentation
- `tests/test_bob_scan.py` — Add threshold validation tests

---

## Dependencies

- **Blocks:** None
- **Blocked by:** ALPHA-003 (multi-pass scanner provides better data)

---

## Test Plan

1. Create `tests/test_entropy_thresholds.py`
2. Test cases:
   - `test_thresholds_detect_known_blocks()`
   - `test_thresholds_minimize_false_positives()`
   - `test_thresholds_configurable()`
3. Validate against full B.O.B. ROM
4. Document false positive/negative rates

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** ✅ COMPLETE — Entropy threshold calibration complete
  - Created `configs/thresholds.yaml` — Calibrated threshold configuration
  - Created `docs/ENTROPY_THRESHOLDS.md` — Threshold methodology documentation
  - Created `tests/test_entropy_thresholds.py` — 15 tests (all passing)
  - Documented: entropy ranges by type, threshold derivation, validation results
  - All acceptance criteria met
