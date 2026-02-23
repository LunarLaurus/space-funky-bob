# Task ALPHA-002: Streaming Decompression API

**Squad:** Alpha (Core Analysis Engine)  
**Priority:** P1 (High)  
**Complexity:** High  
**Estimated Effort:** 8-10 hours  
**Status:** ⏳ Pending

---

## Objective

Implement a streaming decompression API that can handle large compressed blocks without requiring the entire decompressed size upfront, enabling processing of blocks larger than available RAM.

---

## Context

The current `bob_lz_decompress()` function requires the exact decompressed size as a parameter. This works for known blocks but is limiting for:
1. Large compressed blocks with unknown decompressed size
2. Memory-constrained environments
3. Real-time processing pipelines

A streaming API would yield decompressed chunks as they become available, similar to Python's `gzip.GzipFile`.

---

## Acceptance Criteria

- [ ] Streaming API: `bob_lz_decompress_stream(src, chunk_size=4096)` generator
- [ ] Auto-detection of decompressed size (no `dec_len` parameter required)
- [ ] Memory efficiency: never hold more than `chunk_size` bytes in output buffer
- [ ] Backward compatibility: existing API unchanged
- [ ] Tests for streaming vs batch output equivalence
- [ ] Documentation with usage examples

---

## Technical Notes

### API Design
```python
def bob_lz_decompress_stream(src_bytes, chunk_size=4096):
    """
    Streaming LZ77 decompression generator.
    
    Yields:
        bytes: Decompressed chunks of up to chunk_size bytes
    
    Returns:
        int: Total bytes decompressed
    """
```

### Implementation Approach
1. Process input chunks incrementally
2. Yield output when `chunk_size` bytes accumulated
3. Maintain sliding window for backreferences
4. Handle chunk boundaries correctly for overlapping copies

### Memory Considerations
- Must retain full sliding window (2047 bytes max)
- Output buffer limited to `chunk_size`
- Input buffer can be streamed

---

## Files to Modify

- `toolkit/bob_lz.py` — Add streaming function
- `tests/test_bob_lz.py` — Add streaming tests
- `docs/USER_GUIDE.md` — Add streaming usage examples

---

## Dependencies

- **Blocks:** ALPHA-005 (performance profiling should include streaming)
- **Blocked by:** ALPHA-001 (encoder validation ensures streaming has valid test data)

---

## Test Plan

1. Create `tests/test_lz77_stream.py`
2. Test cases:
   - `test_stream_small_data()`
   - `test_stream_large_data()`
   - `test_stream_chunk_boundaries()`
   - `test_stream_equivalence_to_batch()`
   - `test_stream_memory_efficiency()`
3. Verify output matches batch decompression
4. Profile memory usage with large inputs

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
