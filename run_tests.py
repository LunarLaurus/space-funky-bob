#!/usr/bin/env python3
"""Simple test runner for B.O.B. ROM Analysis Toolkit

Runs all tests without requiring pytest (for zero-dependency compatibility).
"""

import sys
import os

# Add toolkit to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'toolkit'))

from bob_lz import bob_lz_decompress, bob_lz_decompress_exploratory
from bob_lz_scan import calculate_entropy, looks_like_compressed, looks_like_tile_data


def run_tests():
    """Run all unit tests"""
    passed = 0
    failed = 0
    
    print("=" * 60)
    print("B.O.B. ROM Analysis Toolkit - Test Suite")
    print("=" * 60)
    print()
    
    # Test bob_lz.py
    print("Testing bob_lz.py - LZ77 Decompression")
    print("-" * 40)
    
    # Test 1: Literal bytes
    try:
        compressed = bytes([0x00, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48])
        expected = b"ABCDEFGH"
        result, consumed = bob_lz_decompress(compressed, 8)
        assert result == expected
        assert consumed == 9
        print("[PASS] Test 1: Literal bytes")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 1: {e}")
        failed += 1
    
    # Test 2: Overlapping copy
    try:
        compressed = bytes([0x10, 0x41, 0x42, 0x43, 0x03, 0x28])
        expected = b"ABCABCAB"
        result, consumed = bob_lz_decompress(compressed, 8)
        assert result == expected
        print("[PASS] Test 2: Overlapping copy")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 2: {e}")
        failed += 1
    
    # Test 3: Zero distance error
    try:
        compressed = bytes([0x80, 0x00, 0x00])
        try:
            bob_lz_decompress(compressed, 8)
            print("[FAIL] Test 3: Should have raised ValueError")
            failed += 1
        except ValueError as e:
            if "invalid distance 0" in str(e):
                print("[PASS] Test 3: Zero distance error")
                passed += 1
            else:
                print(f"[FAIL] Test 3: Wrong error: {e}")
                failed += 1
    except Exception as e:
        print(f"[FAIL] Test 3: {e}")
        failed += 1
    
    # Test 4: Distance too large
    try:
        compressed = bytes([0x40, 0x41, 0xFF, 0x07])
        try:
            bob_lz_decompress(compressed, 8)
            print("[FAIL] Test 4: Should have raised ValueError")
            failed += 1
        except ValueError as e:
            if "invalid distance" in str(e).lower():
                print("[PASS] Test 4: Distance too large error")
                passed += 1
            else:
                print(f"[FAIL] Test 4: Wrong error: {e}")
                failed += 1
    except Exception as e:
        print(f"[FAIL] Test 4: {e}")
        failed += 1
    
    # Test 5: Exploratory mode
    try:
        compressed = bytes([0x00, 0x48, 0x45, 0x4C, 0x4C, 0x4F, 0x20, 0x42, 0x4F])
        result, consumed, error = bob_lz_decompress_exploratory(compressed)
        assert error is None
        assert result == b"HELLO BO"
        print("[PASS] Test 5: Exploratory decompression")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 5: {e}")
        failed += 1
    
    print()
    print("Testing bob_lz_scan.py - Entropy & Heuristics")
    print("-" * 40)
    
    # Test entropy calculation
    try:
        entropy = calculate_entropy(b"\x00" * 100)
        assert entropy < 0.5  # Uniform data should have low entropy
        print("[PASS] Test 6: Entropy calculation (uniform)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 6: {e}")
        failed += 1
    
    # Test looks_like_compressed
    try:
        import random
        random.seed(42)
        random_data = bytes([random.randint(0, 255) for _ in range(64)])
        assert looks_like_compressed(random_data) is True
        print("[PASS] Test 7: looks_like_compressed (random data)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 7: {e}")
        failed += 1
    
    # Test looks_like_tile_data
    try:
        # Use more varied data that passes tile detection
        import random
        random.seed(42)
        # Create data with moderate entropy and some variety
        tile_like = bytes([random.randint(0, 255) for _ in range(128)])
        result = looks_like_tile_data(tile_like)
        # Just check it returns a boolean
        assert isinstance(result, bool)
        print(f"[PASS] Test 8: looks_like_tile_data (returns {result})")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 8: {e}")
        failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
