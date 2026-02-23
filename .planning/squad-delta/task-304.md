# Task DELTA-004: Property-Based Test Enhancement

**Squad:** Delta (Testing & QA)  
**Priority:** P2 (Medium)  
**Complexity:** Medium  
**Estimated Effort:** 4-6 hours  
**Status:** ⏳ Pending

---

## Objective

Enhance property-based testing with additional invariants, randomized test data generation, and automated edge case discovery to complement example-based tests.

---

## Context

The existing `property_tests.py` has basic property tests but lacks:
- Comprehensive invariant coverage
- Sophisticated random data generation
- Automated shrinking for failure minimization
- Integration with hypothesis library (optional)

Property-based testing finds bugs that example-based tests miss by testing invariants over many random inputs.

---

## Acceptance Criteria

- [ ] Invariant expansion: 10+ property invariants
- [ ] Random generators: Custom generators for ROM data, compressed streams
- [ ] Shrinking: Failed tests minimize counterexample
- [ ] Integration: Property tests in unified runner
- [ ] Documentation: Property testing guide
- [ ] Bug discovery: Find at least 1 previously unknown bug

---

## Technical Notes

### Property Invariants

**LZ77 Properties:**
```python
def property_decompression_is_deterministic():
    """Same input always produces same output."""
    for _ in range(100):
        data = random_compressed_data()
        result1 = decompress(data)
        result2 = decompress(data)
        assert result1 == result2

def property_output_size_bounded():
    """Output never exceeds requested size."""
    for max_size in [100, 1000, 10000]:
        data = random_bytes()
        result = decompress_exploratory(data, max_size)
        assert len(result) <= max_size

def property_literal_bytes_preserved():
    """Literal bytes appear in output unchanged."""
    # If we know certain bytes are literals, they should match
    ...
```

**Scanner Properties:**
```python
def property_high_entropy_detected_as_compressed():
    """Random high-entropy data should be flagged as compressed."""
    random_data = bytes([random.randint(0, 255) for _ in range(256)])
    assert looks_like_compressed(random_data) is True

def property_low_entropy_not_detected_as_compressed():
    """Uniform data should not be flagged as compressed."""
    uniform_data = bytes([0x00] * 256)
    assert looks_like_compressed(uniform_data) is False
```

### Random Data Generators

```python
def random_compressed_data(min_size=16, max_size=4096):
    """Generate random but valid compressed data."""
    # Create synthetic compressed stream
    ...

def random_rom_data(size=1024*1024):
    """Generate random ROM-like data with header."""
    # Include valid header, mixed content
    ...
```

---

## Files to Modify

- `property_tests.py` — Expand with new properties
- `tests/property_generators.py` — New random generators
- `tests/__main__.py` — Integrate property tests

---

## Dependencies

- **Blocks:** None
- **Blocked by:** DELTA-001 (unified runner integration)

---

## Test Plan

1. Add 10+ new property invariants
2. Run property tests with 1000+ iterations each
3. Document any bugs discovered
4. Add regression tests for discovered bugs

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
