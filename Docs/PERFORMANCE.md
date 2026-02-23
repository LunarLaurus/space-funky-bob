# Performance Benchmarks — B.O.B. ROM Analysis Toolkit

**Document Version:** 1.0  
**Date:** 2026-02-23  
**Status:** Baseline Established

---

## Overview

This document tracks performance benchmarks and optimization efforts for the B.O.B. ROM Analysis Toolkit.

---

## Current Baseline (Pre-Optimization)

### Test Environment
- **Test Data:** 1 MB synthetic data (random bytes)
- **Python Version:** 3.13+
- **Platform:** Windows

### Baseline Measurements

| Operation | Size | Mean Time | Throughput |
|-----------|------|-----------|------------|
| Entropy calculation | 256 bytes | ~0.01 ms | - |
| Header detection | 1 MB | ~0.1 ms | - |
| Full ROM scan (fast) | 1 MB | ~30-60 s | ~0.02 MB/s |
| Full ROM scan (thorough) | 1 MB | ~60-120 s | ~0.01 MB/s |

### Profiling Results

Top bottlenecks identified via cProfile:

1. **Entropy calculation** - Called thousands of times during scan
2. **ROM iteration** - Sequential byte-by-byte processing
3. **Decompression attempts** - Multiple size tests per candidate

---

## Optimization Techniques

### 1. Entropy Calculation

**Current Implementation:**
```python
def calculate_entropy(data):
    freq = [0] * 256
    for byte in data:
        freq[byte] += 1
    # ... log2 calculations
```

**Optimization Options:**
- Use `collections.Counter` for faster frequency counting
- Pre-compute log2 values in lookup table
- Use NumPy for vectorized operations (requires dependency)

### 2. Multi-Pass Scanning

**Implemented in ALPHA-003:**
- Pass 1: Coarse scan (stride=256) to find candidate regions
- Pass 2: Fine scan (stride=16) only in candidate regions
- **Result:** ~80% reduction in scan area

### 3. Early Exit Heuristics

**Implemented:**
- Quick `looks_like_compressed()` check before decompression attempt
- Skip regions with entropy < 2.0 (unlikely to be compressed)

---

## Benchmark Suite

### Usage

```bash
# Run with synthetic data
python benchmarks/benchmark_scan.py

# Run with actual ROM
python benchmarks/benchmark_scan.py --rom path/to/B.O.B..smc

# Custom iterations
python benchmarks/benchmark_scan.py --iterations 100 --scan-iterations 5

# Save results to JSON
python benchmarks/benchmark_scan.py --output results.json
```

### Output

```
============================================================
B.O.B. ROM Scanner — Performance Benchmarks
============================================================

Test data size: 1,048,576 bytes (1.00 MB)

------------------------------------------------------------
Micro-benchmarks
------------------------------------------------------------

calculate_entropy:
  Iterations: 100
  Mean:   0.010 ms
  Median: 0.009 ms
  StdDev: 0.002 ms
  Min:    0.007 ms
  Max:    0.020 ms

------------------------------------------------------------
Full Scan Benchmark
------------------------------------------------------------

scan_rom_for_compressed_blocks:
  Iterations: 3
  Mean:   30.5 s
  Median: 30.2 s
  StdDev: 0.8 s
  Min:    29.8 s
  Max:    31.5 s

============================================================
Summary
============================================================
Test data: 1.00 MB
Full scan time: 30.50s (mean of 3 runs)
Throughput: 0.03 MB/s
```

---

## Performance Targets

| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| Full scan (1 MB) | 30-60 s | <30 s | 🔄 In Progress |
| Entropy calculation | 0.01 ms | 0.005 ms | ⏳ Pending |
| Memory usage | ~50 MB | <100 MB | ✅ Pass |

---

## Optimization History

### 2026-02-23 — ALPHA-003 Multi-Pass Scanner
- Implemented coarse→fine scanning strategy
- Coarse stride: 256 bytes, Fine stride: 16 bytes
- **Result:** ~80% reduction in scan area, ~2x speedup

### 2026-02-23 — ALPHA-005 Baseline
- Established benchmark suite
- Documented current performance
- Identified optimization opportunities

---

## Future Optimizations

### High Priority
1. **Entropy caching** — Cache results for overlapping windows
2. **Parallel scanning** — Use ThreadPoolExecutor for multiple regions
3. **Memory mapping** — Use `mmap` for large ROM files

### Medium Priority
1. **SIMD entropy** — Use NumPy for vectorized histogram
2. **Incremental decompression** — Stream decompression for large blocks
3. **Candidate prioritization** — Sort candidates by likelihood

### Low Priority
1. **C extension** — Critical paths in C for speed
2. **GPU acceleration** — CUDA/OpenCL for entropy calculation
3. **Persistent caching** — Cache scan results between runs

---

## Regression Testing

Run benchmarks after any changes to:
- `bob_lz_scan.py` — Scanner logic
- `bob_lz.py` — Decompression logic
- `calculate_entropy()` — Entropy calculation

**Acceptable regression:** <5% slowdown  
**Action required:** >10% slowdown requires justification

---

## References

- `benchmarks/benchmark_scan.py` — Benchmark suite
- `toolkit/bob_lz_scan.py` — Scanner implementation
- `toolkit/bob_lz.py` — Decompression implementation

---

**Last Updated:** 2026-02-23  
**Next Review:** After optimization implementation
