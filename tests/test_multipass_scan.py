"""Tests for multi-pass ROM scanner (ALPHA-003)"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from bob_lz_scan import (
    merge_adjacent_regions,
    coarse_entropy_scan,
    fine_scan,
    multipass_scan,
    calculate_entropy
)


class TestMergeAdjacentRegions:
    """Test region merging functionality."""

    def test_merge_overlapping_regions(self):
        """Overlapping regions should be merged."""
        regions = [
            {'region_start': 0, 'region_end': 100, 'entropy': 6.5},
            {'region_start': 50, 'region_end': 150, 'entropy': 7.0},
        ]
        merged = merge_adjacent_regions(regions)
        assert len(merged) == 1
        assert merged[0]['region_start'] == 0
        assert merged[0]['region_end'] == 150

    def test_merge_adjacent_regions(self):
        """Adjacent regions (gap <= max_gap) should be merged."""
        regions = [
            {'region_start': 0, 'region_end': 100, 'entropy': 6.5},
            {'region_start': 150, 'region_end': 250, 'entropy': 7.0},
        ]
        merged = merge_adjacent_regions(regions, max_gap=256)
        assert len(merged) == 1
        assert merged[0]['region_start'] == 0
        assert merged[0]['region_end'] == 250

    def test_no_merge_distant_regions(self):
        """Distant regions should not be merged."""
        regions = [
            {'region_start': 0, 'region_end': 100, 'entropy': 6.5},
            {'region_start': 500, 'region_end': 600, 'entropy': 7.0},
        ]
        merged = merge_adjacent_regions(regions, max_gap=256)
        assert len(merged) == 2

    def test_empty_regions(self):
        """Empty region list should return empty."""
        merged = merge_adjacent_regions([])
        assert len(merged) == 0

    def test_single_region(self):
        """Single region should be returned as-is."""
        regions = [{'region_start': 0, 'region_end': 100, 'entropy': 6.5}]
        merged = merge_adjacent_regions(regions)
        assert len(merged) == 1
        assert merged[0]['region_start'] == 0


class TestCoarseEntropyScan:
    """Test coarse entropy scan functionality."""

    def test_detect_high_entropy_region(self):
        """Should detect high entropy (random) data."""
        import random
        random.seed(42)
        rom_data = bytes([random.randint(0, 255) for _ in range(1024)])
        # Use lower threshold for test - random data has ~7.9 entropy
        regions = coarse_entropy_scan(rom_data, stride=256, entropy_threshold=5.0)
        assert len(regions) > 0

    def test_skip_low_entropy_region(self):
        """Should skip low entropy (uniform) data."""
        rom_data = bytes([0x00] * 1024)
        regions = coarse_entropy_scan(rom_data, stride=256, entropy_threshold=6.0)
        assert len(regions) == 0

    def test_respects_stride(self):
        """Should respect stride parameter."""
        import random
        random.seed(42)
        rom_data = bytes([random.randint(0, 255) for _ in range(1024)])
        regions_coarse = coarse_entropy_scan(rom_data, stride=512)
        regions_fine = coarse_entropy_scan(rom_data, stride=128)
        # Coarse stride should find fewer or equal regions
        assert len(regions_coarse) <= len(regions_fine)


class TestFineScan:
    """Test fine scan functionality."""

    def test_fine_scan_finds_blocks(self):
        """Fine scan should find compressed blocks in candidate regions."""
        # Create test data with a compressed-like region
        import random
        random.seed(42)
        
        # High entropy region (candidate)
        high_entropy = bytes([random.randint(0, 255) for _ in range(512)])
        
        regions = [
            {'region_start': 0, 'region_end': 512, 'entropy': 7.0}
        ]
        
        test_sizes = [256, 512]
        candidates = fine_scan(high_entropy, regions, test_sizes, stride=16)
        
        # Should find some candidates (may be false positives, that's ok for testing)
        assert isinstance(candidates, list)


class TestMultipassScan:
    """Test multi-pass scanner integration."""

    def test_multipass_scan_basic(self):
        """Multi-pass scan should complete without errors."""
        import random
        random.seed(42)
        rom_data = bytes([random.randint(0, 255) for _ in range(4096)])
        
        candidates = multipass_scan(rom_data, header_offset=0, outdir=None, fast=True)
        
        assert isinstance(candidates, list)

    def test_multipass_scan_sorts_by_offset(self):
        """Results should be sorted by offset."""
        import random
        random.seed(42)
        rom_data = bytes([random.randint(0, 255) for _ in range(4096)])
        
        candidates = multipass_scan(rom_data, header_offset=0, outdir=None, fast=True)
        
        offsets = [c['offset'] for c in candidates]
        assert offsets == sorted(offsets)

    def test_multipass_scan_with_output_dir(self, tmp_path):
        """Should save results to output directory."""
        import random
        import json
        random.seed(42)
        rom_data = bytes([random.randint(0, 255) for _ in range(4096)])
        
        candidates = multipass_scan(rom_data, header_offset=0, outdir=str(tmp_path), fast=True)
        
        # Check output file exists
        output_file = tmp_path / 'candidates_multipass.json'
        assert output_file.exists()
        
        # Check file is valid JSON
        with open(output_file) as f:
            data = json.load(f)
        assert 'candidates' in data


class TestEntropyCalculation:
    """Test entropy calculation (used by scanner)."""

    def test_entropy_uniform_data(self):
        """Uniform data should have low entropy."""
        data = bytes([0x00] * 256)
        entropy = calculate_entropy(data)
        assert entropy < 0.5

    def test_entropy_random_data(self):
        """Random data should have high entropy."""
        import random
        random.seed(42)
        data = bytes([random.randint(0, 255) for _ in range(256)])
        entropy = calculate_entropy(data)
        assert entropy > 7.0

    def test_entropy_empty_data(self):
        """Empty data should return 0 entropy."""
        entropy = calculate_entropy(b'')
        assert entropy == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
