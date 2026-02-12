#!/usr/bin/env python3
"""
Debug the exact test case from the unit tests
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toolkit.bob_lz import bob_lz_decompress

def debug_unit_test_data():
    """Use the exact test data that works in unit tests"""
    
    # Test 1 from the unit tests - this should work
    print("=== Test 1: Literal bytes ===")
    compressed = bytes([0x00, 0x48, 0x45, 0x4C, 0x4C, 0x4F, 0x20, 0x57, 0x4F])
    decompressed, consumed = bob_lz_decompress(compressed, 8)
    print(f"Input: {compressed.hex()}")
    print(f"Output: {decompressed}")
    print(f"Consumed: {consumed}")
    print(f"Success: {decompressed == b'HELLO WO'}")
    
    # Calculate entropy
    from toolkit.bob_lz_scan import calculate_entropy, looks_like_compressed
    entropy = calculate_entropy(compressed)
    looks_compressed = looks_like_compressed(compressed)
    print(f"Entropy: {entropy:.2f}")
    print(f"Looks compressed: {looks_compressed}")
    
    print("\n=== Test 2: Higher entropy literals ===")
    # Create some data with higher entropy using varied ASCII
    import random
    random.seed(456)
    literal_bytes = bytes(random.randint(32, 126) for _ in range(15))
    compressed = bytes([0xFF]) + literal_bytes  # 0xFF = all 8 bits are literals
    # Note: 0xFF means all 8 bits are 1, but we want all literals, so use 0x00
    compressed = bytes([0x00]) + literal_bytes[:8]  # Use 8 literals only
    
    try:
        decompressed, consumed = bob_lz_decompress(compressed, 8)
        print(f"Input size: {len(compressed)}")
        print(f"Output: {decompressed}")
        print(f"Consumed: {consumed}")
    except Exception as e:
        print(f"Decompression failed: {e}")
    
    entropy = calculate_entropy(compressed)
    looks_compressed = looks_like_compressed(compressed)
    print(f"Entropy: {entropy:.2f}")
    print(f"Looks compressed: {looks_compressed}")
    
    print("\n=== Test 3: Simple high entropy literals ===")
    import random
    random.seed(123)
    
    # Create simple high entropy literal-only data
    # Just one 0x00 header followed by 8 high-entropy literal bytes
    high_entropy_bytes = bytes(random.randint(65, 122) for _ in range(8))  # Upper and lower case letters
    compressed = bytes([0x00]) + high_entropy_bytes
    
    try:
        decompressed, consumed = bob_lz_decompress(compressed, 8)
        print(f"Decompressed {len(decompressed)} bytes from {consumed} bytes consumed")
        print(f"Output: {decompressed}")
        print(f"Success: {len(decompressed) == 8}")
    except Exception as e:
        print(f"Decompression failed: {e}")
    
    entropy = calculate_entropy(compressed)
    looks_compressed = looks_like_compressed(compressed)
    print(f"Entropy: {entropy:.2f}")
    print(f"Looks compressed: {looks_compressed}")
    
    # Test with a larger sample that should pass scanner
    print("\n=== Test 4: Create data that will pass scanner ===")
    # Create 64 bytes of high entropy valid LZ77 data
    all_literals = []
    for i in range(8):
        header = 0x00  # 8 literals
        literals = [random.randint(65, 122) for _ in range(8)]
        all_literals.extend([header] + literals)
    
    compressed = bytes(all_literals)
    
    try:
        decompressed, consumed = bob_lz_decompress(compressed, 64)
        print(f"Large test - Decompressed {len(decompressed)} bytes from {consumed} bytes consumed")
        success = len(decompressed) == 64
        print(f"Success: {success}")
    except Exception as e:
        print(f"Large test - Decompression failed: {e}")
        success = False
    
    entropy = calculate_entropy(compressed)
    looks_compressed = looks_like_compressed(compressed)
    print(f"Entropy: {entropy:.2f}")
    print(f"Looks compressed: {looks_compressed}")
    print(f"Would pass scanner: {looks_compressed and success}")

if __name__ == "__main__":
    debug_unit_test_data()