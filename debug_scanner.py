#!/usr/bin/env python3
"""
Debug script to analyze the known compressed block at 0x1AD34
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toolkit.bob_lz_scan import calculate_entropy, looks_like_compressed
from toolkit.bob_lz import bob_lz_decompress

def debug_known_block():
    """Debug the known compressed block"""
    # Create a fake B.O.B. ROM for testing (just header + known block)
    rom_data = bytearray(0x20000)  # 128KB ROM
    
    # Add LoROM header at 0x7FC0
    # B.O.B. header values
    rom_data[0x7FC0:0x7FC0+21] = b"B.O.B.             "  # Title
    rom_data[0x7FD5] = 0x30  # Game code (ASCII '0')
    rom_data[0x7FD6] = 0x69  # Fixed byte
    rom_data[0x7FD7] = 0x00  # Expansion RAM size
    rom_data[0x7FD8] = 0x00  # Special version
    rom_data[0x7FD9] = 0x00  # Cartridge type (ROM only)
    rom_data[0x7FDA] = 0x09  # ROM size (8 Mbit = 1MB)
    rom_data[0x7FDB] = 0x00  # RAM size
    rom_data[0x7FDC] = 0x00  # Destination code
    rom_data[0x7FDD] = 0x01  # License
    rom_data[0x7FDE] = 0x00  # Version
    # Checksum and complement at 0x7FEA-0x7FED
    rom_data[0x7FEA:0x7FEC] = (0x7379).to_bytes(2, 'little')  # Checksum
    rom_data[0x7FEC:0x7FEE] = (0x8C86).to_bytes(2, 'little')  # Complement
    
    # Insert some test compressed data at known location
    # Create a more realistic compressed block with some entropy
    import random
    random.seed(42)  # For reproducibility
    
    # Create a mixed pattern with some structure but high entropy
    test_compressed = bytearray([0xFF])  # Start with mixed literals/backrefs
    for i in range(127):  # 128 bytes total
        if i % 3 == 0:
            # Add some literal bytes with varying values
            test_compressed.extend([random.randint(0x20, 0x7F)])
        else:
            # Add some structured high-entropy bytes
            test_compressed.extend([random.randint(0x80, 0xFF)])
    
    # Place at 0x1AD34
    rom_data[0x1AD34:0x1AD34+len(test_compressed)] = test_compressed
    
    print("=== Debugging Known Block Analysis ===")
    print(f"Test ROM size: {len(rom_data)} bytes")
    print(f"Known block location: 0x1AD34")
    
    # Test the scanner's filter function
    sample = rom_data[0x1AD34:0x1AD34+64]
    entropy = calculate_entropy(sample)
    looks_compressed = looks_like_compressed(sample)
    
    print(f"\nSample entropy (first 64 bytes): {entropy:.2f}")
    print(f"Looks compressed (6.0-8.0 range): {looks_compressed}")
    
    # Try different sample sizes
    for size in [32, 64, 128, 256]:
        if 0x1AD34 + size <= len(rom_data):
            sample = rom_data[0x1AD34:0x1AD34+size]
            entropy = calculate_entropy(sample)
            looks_compressed = looks_like_compressed(sample)
            print(f"Sample size {size:3d}: entropy={entropy:.2f}, looks_compressed={looks_compressed}")
    
    # Test decompression
    try:
        decompressed, consumed = bob_lz_decompress(rom_data[0x1AD34:], 0x822)
        print(f"\nDecompression successful!")
        print(f"Consumed: {consumed} bytes")
        print(f"Decompressed: {len(decompressed)} bytes")
        print(f"Expected: 0x822 = 2082 bytes")
        
        if len(decompressed) > 0:
            dec_entropy = calculate_entropy(decompressed)
            comp_entropy = calculate_entropy(rom_data[0x1AD34:0x1AD34+consumed])
            print(f"Compressed entropy: {comp_entropy:.2f}")
            print(f"Decompressed entropy: {dec_entropy:.2f}")
            print(f"Entropy drop: {comp_entropy - dec_entropy:.2f}")
        
    except Exception as e:
        print(f"Decompression failed: {e}")

if __name__ == "__main__":
    debug_known_block()