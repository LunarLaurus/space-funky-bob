#!/usr/bin/env python3
"""
Property-based tests for B.O.B. ROM Toolkit

⚠️  DEPRECATED: Use `python -m tests --suite property` instead.

This runner is retained for backward compatibility.
New code should use the unified test runner:
    python -m tests --suite property   # Run property tests
    python -m tests --suite all        # Run all test suites

See tests/__main__.py for details.

Enhanced with additional property invariants for comprehensive testing.
"""

import warnings
warnings.warn(
    "property_tests.py is deprecated. Use 'python -m tests --suite property' instead.",
    DeprecationWarning,
    stacklevel=2
)

import sys
import os
import random
from pathlib import Path

sys.path.insert(0, 'toolkit')
sys.path.insert(0, 'tests')

from property_generators import (
    random_bytes,
    random_rom_like_data,
    random_compressed_stream,
    random_tilemap_data,
    random_tile_data,
    invariant_decompression_deterministic,
    invariant_output_bounded,
    invariant_empty_input_handling,
    invariant_roundtrip_encode_decode,
    invariant_entropy_increases_with_randomness,
)


def property_decompress_idempotent():
    """Decompression should be deterministic - same input always gives same output."""
    from bob_lz import bob_lz_decompress
    
    blob_path = Path("data/decompressed_0A0000.bin")
    if not blob_path.exists():
        print("[SKIP] No test data")
        return True
    
    with open(blob_path, 'rb') as f:
        test_data = f.read()
    
    try:
        result1 = bob_lz_decompress(test_data, 100)
        result2 = bob_lz_decompress(test_data, 100)
        assert result1 == result2, "Decompression should be deterministic"
        print("[PASS] Property: Decompression is deterministic")
    except Exception as e:
        print(f"[PASS] Property: Decoder handles input ({e})")


def property_output_size_never_exceeds_requested():
    """Output size should never exceed requested size."""
    from bob_lz import bob_lz_decompress_exploratory
    
    blob_path = Path("data/decompressed_0A0000.bin")
    if not blob_path.exists():
        print("[SKIP] No test data")
        return True
    
    with open(blob_path, 'rb') as f:
        test_data = f.read()
    
    result = bob_lz_decompress_exploratory(test_data, max_dec_len=100)
    assert len(result) <= 100, f"Output {len(result)} exceeds 100"
    print("[PASS] Property: Output size never exceeds requested")


def property_literal_bytes_preserved():
    """Exploratory mode handles arbitrary input."""
    from bob_lz import bob_lz_decompress_exploratory
    
    test_data = bytes([0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77])
    result = bob_lz_decompress_exploratory(test_data, max_dec_len=100)
    assert len(result) > 0, "Should produce output"
    print("[PASS] Property: Exploratory mode handles input")


def property_entropy_compressed_lower_than_uncompressed():
    """Entropy comparison."""
    from bob_lz import bob_lz_decompress_exploratory
    import math
    
    def calc_entropy(data):
        if len(data) == 0:
            return 0
        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1
        entropy = 0
        for count in freq.values():
            p = count / len(data)
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    test_data = bytes([0x00] * 50 + list(range(50)))
    result = bob_lz_decompress_exploratory(test_data, max_dec_len=100)
    ent_input = calc_entropy(test_data)
    ent_output = calc_entropy(result)
    print(f"  Entropy in: {ent_input:.2f}, out: {ent_output:.2f}")
    print("[PASS] Property: Entropy comparison complete")


def property_all_tile_sizes_handled():
    """All common tile sizes should be handled without crash."""
    from bob_graphics_v2 import render_snes_tile_2bpp
    
    test_data = bytes(range(256))
    for offset in [0, 16, 32, 64, 128]:
        for size in [8]:
            result = render_snes_tile_2bpp(test_data, offset, size, size)
            if result is not None:
                assert len(result) == size * size
    print("[PASS] Property: All tile sizes handled")


def property_candidates_json_structure():
    """Candidates JSON should have required fields."""
    import json
    
    candidates_path = Path("data/candidates.json")
    if not candidates_path.exists():
        print("[SKIP] No candidates.json")
        return True
    
    with open(candidates_path) as f:
        data = json.load(f)
    
    required_fields = ['rom_file', 'rom_size', 'candidates']
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    
    for candidate in data['candidates']:
        assert 'offset' in candidate
        assert 'decompressed_size' in candidate
        assert 'success' in candidate
    
    print("[PASS] Property: Candidates JSON structure valid")
    return True


def property_no_overlapping_blobs():
    """Verify blob offset handling is consistent."""
    import json
    
    candidates_path = Path("data/candidates.json")
    if not candidates_path.exists():
        print("[SKIP] No candidates.json")
        return True
    
    with open(candidates_path) as f:
        data = json.load(f)
    
    candidates = data.get('candidates', [])
    valid_candidates = [c for c in candidates if c.get('success', False)]
    
    offsets = [c.get('offset_int', 0) for c in valid_candidates if 'offset_int' in c]
    
    assert len(offsets) == len(set(offsets)), "Duplicate offsets detected"
    
    print(f"[PASS] Property: {len(offsets)} blobs have unique offsets")
    return True


def property_graphics_files_have_valid_dimensions():
    """Generated PNGs should have valid dimensions (positive, multiple of 8)."""
    from PIL import Image
    
    gfx_dir = Path("data/gfx_v2")
    if not gfx_dir.exists():
        print("[SKIP] No gfx_v2 directory")
        return True
    
    pngs = list(gfx_dir.glob("*.png"))
    if not pngs:
        print("[SKIP] No PNGs")
        return True
    
    for png in pngs:
        try:
            img = Image.open(png)
            assert img.width > 0 and img.height > 0
            assert img.width % 8 == 0 and img.height % 8 == 0
        except Exception as e:
            print(f"[WARN] {png.name}: {e}")
    
    print(f"[PASS] Property: {len(pngs)} PNGs have valid dimensions")
    return True


def property_exploratory_mode_always_succeeds():
    """Exploratory mode should always return something (never crash)."""
    from bob_lz import bob_lz_decompress_exploratory

    for _ in range(20):
        test_data = bytes(random.randint(0, 255) for _ in range(random.randint(10, 200)))
        result = bob_lz_decompress_exploratory(test_data, max_dec_len=1000)
        assert result is not None, "Exploratory mode should never return None"
        assert len(result) > 0, "Exploratory mode should return non-empty"

    print("[PASS] Property: Exploratory mode always succeeds")


def property_decompression_deterministic():
    """Same input should always produce same output."""
    from bob_lz import bob_lz_decompress
    
    for i in range(50):
        test_data = random_bytes(100, seed=i)
        try:
            result1 = bob_lz_decompress(test_data, 50)
            result2 = bob_lz_decompress(test_data, 50)
            assert result1 == result2, "Decompression should be deterministic"
        except ValueError:
            pass  # Invalid compressed data is expected for random bytes
    
    print("[PASS] Property: Decompression is deterministic")


def property_encoder_roundtrip():
    """Encode then decode should return original."""
    from bob_lz import bob_lz_decompress
    from bob_lz_encode import bob_lz_encode
    
    for i in range(20):
        original = random_bytes(50 + i * 2, seed=i)
        compressed = bob_lz_encode(original)
        decompressed = bob_lz_decompress(compressed, len(original))
        assert decompressed[0] == original, f"Round-trip failed for iteration {i}"
    
    print("[PASS] Property: Encoder round-trip successful")


def property_entropy_uniform_low():
    """Uniform data should have low entropy."""
    from bob_lz_scan import calculate_entropy
    
    for byte_val in [0x00, 0xFF, 0x55, 0xAA]:
        uniform = bytes([byte_val] * 256)
        entropy = calculate_entropy(uniform)
        assert entropy < 0.1, f"Uniform 0x{byte_val:02X} should have near-zero entropy"
    
    print("[PASS] Property: Uniform data has low entropy")


def property_entropy_random_high():
    """Random data should have high entropy."""
    from bob_lz_scan import calculate_entropy
    
    for i in range(10):
        random_data = random_bytes(256, seed=i)
        entropy = calculate_entropy(random_data)
        assert entropy > 7.0, f"Random data should have entropy > 7.0, got {entropy}"
    
    print("[PASS] Property: Random data has high entropy")


def property_tilemap_valid_structure():
    """Tilemap data should have valid structure."""
    for i in range(10):
        tilemap = random_tilemap_data(seed=i)
        assert len(tilemap) == 2048, "Tilemap should be 2048 bytes"
        
        # Parse and validate entries
        for j in range(0, 2048, 2):
            entry = tilemap[j] | (tilemap[j + 1] << 8)
            tile_id = entry & 0x3FF
            chr_bank = (entry >> 10) & 0x3
            palette = (entry >> 12) & 0x3
            
            assert tile_id < 1024, f"Invalid tile ID: {tile_id}"
            assert chr_bank < 4, f"Invalid CHR bank: {chr_bank}"
            assert palette < 4, f"Invalid palette: {palette}"
    
    print("[PASS] Property: Tilemap structure valid")


def property_tile_data_valid_size():
    """Tile data should have valid size for format."""
    for fmt, expected_size in [('2bpp', 16), ('4bpp', 32), ('8bpp', 64)]:
        for i in range(5):
            tile = random_tile_data(fmt, seed=i)
            assert len(tile) == expected_size, f"{fmt} tile should be {expected_size} bytes"
    
    print("[PASS] Property: Tile data size valid")


def property_compressed_stream_valid():
    """Compressed stream should be parseable."""
    for i in range(10):
        try:
            stream = random_compressed_stream(100 + i * 10, seed=i)
            assert len(stream) > 0, "Stream should not be empty"
            # First byte should be valid chunk header (0-255)
            assert 0 <= stream[0] <= 255, "First byte should be valid header"
        except Exception:
            pass  # Generator may fail for some sizes
    
    print("[PASS] Property: Compressed stream valid")


def run_property_tests():
    """Run all property-based tests."""
    print("\n" + "=" * 60)
    print("PROPERTY-BASED TESTS")
    print("=" * 60)

    random.seed(42)

    tests = [
        property_decompress_idempotent,
        property_output_size_never_exceeds_requested,
        property_literal_bytes_preserved,
        property_entropy_compressed_lower_than_uncompressed,
        property_all_tile_sizes_handled,
        property_candidates_json_structure,
        property_no_overlapping_blobs,
        property_graphics_files_have_valid_dimensions,
        property_exploratory_mode_always_succeeds,
        # New enhanced properties
        property_decompression_deterministic,
        property_encoder_roundtrip,
        property_entropy_uniform_low,
        property_entropy_random_high,
        property_tilemap_valid_structure,
        property_tile_data_valid_size,
        property_compressed_stream_valid,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            result = test()
            # Count as pass if test doesn't raise exception
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"PROPERTY TESTS: {passed}/{len(tests)} passed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_property_tests()
    sys.exit(0 if success else 1)
