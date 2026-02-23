"""Tests for benchmark suite (ALPHA-005)"""
import pytest
import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'benchmarks'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from benchmark_scan import (
    generate_test_data,
    benchmark_entropy_calculation,
    benchmark_header_detection,
    benchmark_full_scan,
    print_benchmark
)
from bob_lz_scan import calculate_entropy, detect_rom_header


class TestTestDataGeneration:
    """Test synthetic test data generation."""

    def test_generate_test_data_size(self):
        """Should generate correct size."""
        data = generate_test_data(1024)  # 1024 KB = 1 MB
        assert len(data) == 1024 * 1024

    def test_generate_test_data_deterministic(self):
        """Should be deterministic (same seed)."""
        data1 = generate_test_data(100)
        data2 = generate_test_data(100)
        assert data1 == data2

    def test_generate_test_data_varied(self):
        """Should have varied byte values."""
        data = generate_test_data(10)
        unique_bytes = len(set(data))
        assert unique_bytes > 100  # Should have good variety


class TestEntropyBenchmark:
    """Test entropy calculation benchmark."""

    def test_benchmark_entropy_runs(self):
        """Should complete without error."""
        data = generate_test_data(10)
        result = benchmark_entropy_calculation(data, iterations=10)
        
        assert result['function'] == 'calculate_entropy'
        assert result['iterations'] == 10
        assert result['mean'] > 0

    def test_benchmark_entropy_statistics(self):
        """Should calculate statistics."""
        data = generate_test_data(10)
        result = benchmark_entropy_calculation(data, iterations=20)
        
        assert 'mean' in result
        assert 'median' in result
        assert 'stdev' in result
        assert 'min' in result
        assert 'max' in result
        
        # Mean should be between min and max
        assert result['min'] <= result['mean'] <= result['max']


class TestHeaderDetectionBenchmark:
    """Test header detection benchmark."""

    def test_benchmark_header_runs(self):
        """Should complete without error."""
        data = generate_test_data(10)
        result = benchmark_header_detection(data, iterations=5)
        
        assert result['function'] == 'detect_rom_header'
        assert result['iterations'] == 5
        assert result['mean'] > 0


class TestFullScanBenchmark:
    """Test full scan benchmark."""

    def test_benchmark_full_scan_runs(self):
        """Should complete without error."""
        # Use small data for speed
        data = generate_test_data(100)  # 100 KB
        result = benchmark_full_scan(data, iterations=1)
        
        assert result['function'] == 'scan_rom_for_compressed_blocks'
        assert result['iterations'] == 1
        assert result['mean'] > 0


class TestBenchmarkOutput:
    """Test benchmark output formatting."""

    def test_print_benchmark_no_error(self):
        """Should print without error."""
        result = {
            'function': 'test_func',
            'iterations': 10,
            'mean': 1.5,
            'median': 1.4,
            'stdev': 0.2,
            'min': 1.2,
            'max': 2.0,
        }
        
        # Should not raise
        print_benchmark(result)


class TestBenchmarkIntegration:
    """Integration tests for benchmark suite."""

    def test_full_benchmark_workflow(self):
        """Should complete full benchmark workflow."""
        # Generate test data
        data = generate_test_data(50)  # 50 KB for speed
        
        # Run all benchmarks
        entropy_result = benchmark_entropy_calculation(data, iterations=5)
        header_result = benchmark_header_detection(data, iterations=2)
        scan_result = benchmark_full_scan(data, iterations=1)
        
        # Verify all completed
        assert entropy_result['mean'] > 0
        assert header_result['mean'] > 0
        assert scan_result['mean'] > 0


class TestBenchmarkModuleExists:
    """Test that benchmark module exists."""

    def test_benchmark_file_exists(self):
        """benchmark_scan.py should exist."""
        benchmark_path = os.path.join(
            os.path.dirname(__file__), '..', 'benchmarks', 'benchmark_scan.py'
        )
        assert os.path.exists(benchmark_path)

    def test_benchmark_syntax(self):
        """benchmark_scan.py should have valid Python syntax."""
        benchmark_path = os.path.join(
            os.path.dirname(__file__), '..', 'benchmarks', 'benchmark_scan.py'
        )
        
        with open(benchmark_path) as f:
            compile(f.read(), benchmark_path, 'exec')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
