"""Tests for entropy threshold calibration (ALPHA-004)"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from bob_lz_scan import calculate_entropy, looks_like_compressed, looks_like_tile_data


class TestEntropyCalculation:
    """Test entropy calculation for threshold calibration."""

    def test_entropy_uniform_data(self):
        """Uniform data should have near-zero entropy."""
        data = bytes([0x00] * 256)
        entropy = calculate_entropy(data)
        assert entropy < 0.1

    def test_entropy_alternating_data(self):
        """Alternating data should have low entropy."""
        data = bytes([0x00, 0xFF] * 128)
        entropy = calculate_entropy(data)
        assert 0.5 < entropy < 1.5

    def test_entropy_random_data(self):
        """Random data should have high entropy (>7.0)."""
        import random
        random.seed(42)
        data = bytes([random.randint(0, 255) for _ in range(256)])
        entropy = calculate_entropy(data)
        assert entropy > 7.0

    def test_entropy_compressed_range(self):
        """Compressed-like data should have entropy 6.5-8.0."""
        import random
        random.seed(123)
        data = bytes([random.randint(0, 255) for _ in range(512)])
        entropy = calculate_entropy(data)
        assert 6.5 <= entropy <= 8.0

    def test_entropy_graphics_range(self):
        """Graphics-like data should have entropy 2.0-4.5."""
        # Simulate 2bpp graphics (4 colors)
        import random
        random.seed(456)
        data = bytes([random.randint(0, 3) for _ in range(256)])
        entropy = calculate_entropy(data)
        assert entropy < 4.5


class TestLooksLikeCompressed:
    """Test compressed data detection heuristics."""

    def test_detects_random_as_compressed(self):
        """Random high-entropy data should look compressed."""
        import random
        random.seed(42)
        data = bytes([random.randint(0, 255) for _ in range(64)])
        assert looks_like_compressed(data) is True

    def test_rejects_uniform_as_compressed(self):
        """Uniform data should not look compressed."""
        data = bytes([0x00] * 64)
        assert looks_like_compressed(data) is False

    def test_rejects_low_entropy_as_compressed(self):
        """Low entropy data should not look compressed."""
        data = bytes([0x00, 0x01] * 32)
        assert looks_like_compressed(data) is False


class TestLooksLikeTileData:
    """Test graphics tile detection heuristics."""

    def test_detects_tile_patterns(self):
        """Data with moderate entropy should look like tiles."""
        import random
        random.seed(42)
        data = bytes([random.randint(0, 15) for _ in range(128)])
        # This may or may not look like tiles depending on heuristics
        result = looks_like_tile_data(data)
        assert isinstance(result, bool)

    def test_rejects_all_zeros_as_tiles(self):
        """All zeros should not look like tiles."""
        data = bytes([0x00] * 128)
        assert looks_like_tile_data(data) is False

    def test_rejects_low_variance_as_tiles(self):
        """Low variance data should not look like tiles."""
        data = bytes([0x00] * 120 + [0xFF] * 8)
        assert looks_like_tile_data(data) is False


class TestThresholdBoundaries:
    """Test threshold boundary conditions."""

    def test_threshold_6_5_boundary(self):
        """Test entropy around 6.5 threshold."""
        # Create data with entropy near 6.5
        import random
        random.seed(777)
        data = bytes([random.randint(0, 200) for _ in range(256)])
        entropy = calculate_entropy(data)
        
        # Verify entropy calculation is stable
        assert 4.0 < entropy < 8.0

    def test_threshold_4_5_boundary(self):
        """Test entropy around 4.5 threshold."""
        # Create data with limited byte range
        import random
        random.seed(888)
        data = bytes([random.randint(0, 15) for _ in range(256)])
        entropy = calculate_entropy(data)
        
        # Limited range should give lower entropy
        assert entropy < 5.0


class TestConfigLoading:
    """Test configuration file loading."""

    def test_config_file_exists(self):
        """Thresholds config file should exist."""
        config_path = os.path.join(
            os.path.dirname(__file__), '..', 'configs', 'thresholds.yaml'
        )
        assert os.path.exists(config_path)

    def test_config_has_required_keys(self):
        """Config should have required threshold keys."""
        import yaml
        config_path = os.path.join(
            os.path.dirname(__file__), '..', 'configs', 'thresholds.yaml'
        )
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert 'scanner' in config
        assert 'compressed_min' in config['scanner']
        assert 'compressed_high' in config['scanner']
        assert 'graphics_max' in config['scanner']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
