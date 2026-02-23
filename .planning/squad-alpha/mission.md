# Squad Alpha — Core Analysis Engine

**Mission:** Strengthen the foundational LZ77 compression/decompression engine, improve ROM scanner accuracy, and optimize performance for large ROMs.

---

## Scope

Squad Alpha owns the core analysis pipeline:
- **LZ77 Decoder/Encoder** (`bob_lz.py`, `bob_lz_encode.py`)
- **ROM Scanner** (`bob_lz_scan.py`)
- **Region Mapper** (`bob_map.py`)

---

## Objectives

### Primary Goals
1. Ensure LZ77 encoder/decoder round-trip integrity
2. Implement multi-pass scanning for improved accuracy
3. Optimize hot paths for 2x performance improvement
4. Calibrate entropy thresholds with empirical data

### Secondary Goals
1. Add streaming decompression for large blocks
2. Document compression format edge cases
3. Create performance benchmark suite

---

## Tasks

| ID | Title | Priority | Complexity | Status |
|----|-------|----------|------------|--------|
| ALPHA-001 | LZ77 Encoder Round-Trip Testing | P0 | Medium | ⏳ Pending |
| ALPHA-002 | Streaming Decompression API | P1 | High | ⏳ Pending |
| ALPHA-003 | Multi-Pass Scanner Implementation | P0 | High | ⏳ Pending |
| ALPHA-004 | Entropy Threshold Calibration | P1 | Low | ⏳ Pending |
| ALPHA-005 | Performance Profiling & Optimization | P2 | Medium | ⏳ Pending |

---

## Success Metrics

- **Round-Trip Integrity:** 100% of test vectors encode→decode correctly
- **Scanner Accuracy:** >90% compressed block detection rate
- **Performance:** 2x faster than baseline on 1MB ROM
- **Code Quality:** All new code has tests, type hints, docstrings

---

## Dependencies

### Internal
- Squad Delta: Test suite consolidation (DELTA-001)
- Squad Delta: Coverage analysis (DELTA-002)

### External
- None — core engine is self-contained

---

## Technical Notes

### LZ77 Format Summary
```
Chunk Header: 8-bit status byte (MSB first)
- Bit 0: Literal (copy next byte)
- Bit 1: Distance/Length pair (16-bit LE)
  - Low 11 bits: distance (1-2047)
  - High 5 bits: (length - 3), so length = 3-34
```

### Known Test Vectors
- Block at 0x1AD34: decompressed size 0x822 bytes
- Test data in `data/decompressed_0A0000.bin`

### Performance Baseline
- LZ scan (stride=16) on 1MB ROM: ~30-60 seconds
- Target: <30 seconds

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
**Target Complete:** 2026-03-05 (Day 10)
