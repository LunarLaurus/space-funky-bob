#!/usr/bin/env python3
"""
benchmark_scan.py — Performance benchmarks for B.O.B. ROM Scanner

Usage:
    python benchmarks/benchmark_scan.py
    python benchmarks/benchmark_scan.py --rom path/to/rom.sfc
    python benchmarks/benchmark_scan.py --iterations 10
"""

import argparse
import time
import statistics
import sys
from pathlib import Path

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'toolkit'))

from bob_lz_scan import scan_rom_for_compressed_blocks, detect_rom_header, calculate_entropy


def generate_test_data(size_kb=1024):
    """Generate synthetic test data."""
    import random
    random.seed(42)
    return bytes([random.randint(0, 255) for _ in range(size_kb * 1024)])


def benchmark_entropy_calculation(data, iterations=100):
    """Benchmark entropy calculation."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        calculate_entropy(data[:256])
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        'function': 'calculate_entropy',
        'iterations': iterations,
        'mean': statistics.mean(times) * 1000,  # ms
        'median': statistics.median(times) * 1000,
        'stdev': statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        'min': min(times) * 1000,
        'max': max(times) * 1000,
    }


def benchmark_header_detection(data, iterations=10):
    """Benchmark ROM header detection."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        detect_rom_header(data)
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        'function': 'detect_rom_header',
        'iterations': iterations,
        'mean': statistics.mean(times) * 1000,
        'median': statistics.median(times) * 1000,
        'stdev': statistics.stdev(times) * 1000 if len(times) > 1 else 0,
        'min': min(times) * 1000,
        'max': max(times) * 1000,
    }


def benchmark_full_scan(data, iterations=3):
    """Benchmark full ROM scan."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        # Run scan with fast mode
        scan_rom_for_compressed_blocks(data, 0, None, fast=True)
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        'function': 'scan_rom_for_compressed_blocks',
        'iterations': iterations,
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'min': min(times),
        'max': max(times),
    }


def print_benchmark(result):
    """Print benchmark result."""
    unit = 's' if result['mean'] > 1 else 'ms'
    factor = 1 if unit == 's' else 1
    
    print(f"\n{result['function']}:")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Mean:   {result['mean']:.3f} {unit}")
    print(f"  Median: {result['median']:.3f} {unit}")
    print(f"  StdDev: {result['stdev']:.3f} {unit}")
    print(f"  Min:    {result['min']:.3f} {unit}")
    print(f"  Max:    {result['max']:.3f} {unit}")


def main():
    parser = argparse.ArgumentParser(description='B.O.B. ROM Scanner Benchmarks')
    parser.add_argument('--rom', help='Path to ROM file (optional, uses synthetic data if not provided)')
    parser.add_argument('--iterations', type=int, default=10, help='Iterations for micro-benchmarks')
    parser.add_argument('--scan-iterations', type=int, default=3, help='Iterations for full scan')
    parser.add_argument('--output', help='Output JSON file (optional)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("B.O.B. ROM Scanner — Performance Benchmarks")
    print("=" * 60)
    
    # Load or generate test data
    if args.rom:
        print(f"\nLoading ROM: {args.rom}")
        rom_data = Path(args.rom).read_bytes()
        print(f"ROM size: {len(rom_data):,} bytes ({len(rom_data) / 1024 / 1024:.2f} MB)")
    else:
        print("\nGenerating synthetic test data (1 MB)...")
        rom_data = generate_test_data(1024)
        print(f"Test data size: {len(rom_data):,} bytes (1 MB)")
    
    # Run benchmarks
    results = []
    
    print("\n" + "-" * 60)
    print("Micro-benchmarks")
    print("-" * 60)
    
    # Entropy calculation
    result = benchmark_entropy_calculation(rom_data, args.iterations)
    results.append(result)
    print_benchmark(result)
    
    # Header detection
    result = benchmark_header_detection(rom_data, args.iterations)
    results.append(result)
    print_benchmark(result)
    
    print("\n" + "-" * 60)
    print("Full Scan Benchmark")
    print("-" * 60)
    
    # Full scan
    result = benchmark_full_scan(rom_data, args.scan_iterations)
    results.append(result)
    print_benchmark(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Test data: {len(rom_data) / 1024 / 1024:.2f} MB")
    print(f"Full scan time: {result['mean']:.2f}s (mean of {result['iterations']} runs)")
    
    # Calculate throughput
    throughput = len(rom_data) / result['mean'] / 1024 / 1024  # MB/s
    print(f"Throughput: {throughput:.2f} MB/s")
    
    # Save results if requested
    if args.output:
        import json
        output_data = {
            'test_data_size': len(rom_data),
            'results': results
        }
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
