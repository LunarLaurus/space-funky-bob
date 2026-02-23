# Task ALPHA-005: Performance Profiling & Optimization

**Squad:** Alpha (Core Analysis Engine)  
**Priority:** P2 (Medium)  
**Complexity:** Medium  
**Estimated Effort:** 6-8 hours  
**Status:** ⏳ Pending

---

## Objective

Profile the core analysis pipeline to identify performance bottlenecks, then optimize hot paths to achieve 2x performance improvement on 1MB ROM scans.

---

## Context

Current performance baseline (from QWEN.md):
- LZ scan (stride=16) on 1MB ROM: ~30-60 seconds
- ROM mapping: ~5-10 seconds
- Full pipeline: <2 minutes

Target performance:
- LZ scan: <30 seconds
- ROM mapping: <5 seconds
- Full pipeline: <1 minute

This task will use profiling tools to identify bottlenecks and apply targeted optimizations.

---

## Acceptance Criteria

- [ ] Baseline benchmarks: Measure current performance on reference ROM
- [ ] Profiling report: Identify top 3 bottlenecks with cProfile
- [ ] Optimization 1: Entropy calculation (likely candidate for vectorization)
- [ ] Optimization 2: ROM I/O (reduce file reads)
- [ ] Optimization 3: Opcode density calculation (optimize 65816 disassembly)
- [ ] Benchmark suite: `benchmarks/benchmark_scan.py` for regression testing
- [ ] Performance gain: 2x improvement over baseline
- [ ] Documentation: `docs/PERFORMANCE.md` with optimization techniques

---

## Technical Notes

### Profiling Setup
```python
import cProfile
import pstats

def profile_scan():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run full scan
    from toolkit.bob_lz_scan import scan_rom
    candidates = scan_rom(rom_data)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

### Likely Optimizations

1. **Entropy Calculation:**
   - Use NumPy for vectorized histogram (if dependency allowed)
   - Cache frequency calculations for overlapping windows
   - Use integer arithmetic where possible

2. **ROM I/O:**
   - Memory-map ROM file instead of loading entirely
   - Batch reads for sequential access patterns

3. **Opcode Density:**
   - Pre-compute opcode validity table
   - Use bytearray for faster indexing
   - Early exit when density already below threshold

### Benchmark Suite
```python
# benchmarks/benchmark_scan.py
import time

def benchmark_scan(rom_path, iterations=5):
    rom_data = open(rom_path, 'rb').read()
    times = []
    for _ in range(iterations):
        start = time.time()
        scan_rom(rom_data)
        times.append(time.time() - start)
    return {
        'mean': sum(times) / len(times),
        'min': min(times),
        'max': max(times)
    }
```

---

## Files to Modify

- `toolkit/bob_lz_scan.py` — Optimize entropy calculation
- `toolkit/bob_map.py` — Optimize opcode density
- `benchmarks/benchmark_scan.py` — New benchmark suite
- `docs/PERFORMANCE.md` — New documentation

---

## Dependencies

- **Blocks:** None
- **Blocked by:** ALPHA-002, ALPHA-003 (optimize after features complete)

---

## Test Plan

1. Create `benchmarks/benchmark_scan.py`
2. Run baseline benchmarks, record results
3. Apply optimizations one at a time
4. Verify correctness after each optimization (no regressions)
5. Record final performance metrics
6. Add performance regression test to CI

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
