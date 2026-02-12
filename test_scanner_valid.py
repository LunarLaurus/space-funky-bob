#!/usr/bin/env python3
"""
Test the scanner with valid B.O.B. LZ77 format data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toolkit.bob_lz_scan import calculate_entropy, looks_like_compressed, scan_rom_for_compressed_blocks
from toolkit.bob_lz import bob_lz_decompress

def test_with_valid_lz77():
    """Create a ROM with valid B.O.B. LZ77 data"""
    # Create a fake B.O.B. ROM
    rom_data = bytearray(0x20000)  # 128KB ROM
    
    # Add LoROM header at 0x7FC0
    rom_data[0x7FC0:0x7FC0+21] = b"B.O.B.             "
    rom_data[0x7FD6] = 0x69  # Fixed byte
    rom_data[0x7FDA] = 0x09  # ROM size (8 Mbit)
    rom_data[0x7FEA:0x7FEC] = (0x7379).to_bytes(2, 'little')  # Checksum
    rom_data[0x7FEC:0x7FEE] = (0x8C86).to_bytes(2, 'little')  # Complement
    
    # Create valid B.O.B. LZ77 compressed data
    # Using the test case from bob_lz.py that we know works
    test_compressed = bytes([
        0x00,  # All literals
        0x48, 0x45, 0x4C, 0x4C, 0x4F, 0x20, 0x42, 0x4F,  # "HELLO BO"
        0x42, 0x20, 0x54, 0x45, 0x53, 0x54, 0x20, 0x44,  # "B TEST D"
        0x41, 0x54, 0x41, 0x00, 0x00, 0x00, 0x00, 0x00,  # "ATA" + padding
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # More padding
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # More padding
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # More padding
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # More padding
    ])
    
    # Place at multiple locations to test detection
    test_locations = [0x1000, 0x2000, 0x1AD34]
    
    for loc in test_locations:
        rom_data[loc:loc+len(test_compressed)] = test_compressed
    
    print("=== Testing Scanner with Valid LZ77 Data ===")
    
    # Test entropy detection on our test data
    for loc in test_locations:
        sample = rom_data[loc:loc+64]
        entropy = calculate_entropy(sample)
        looks_compressed = looks_like_compressed(sample)
        print(f"Location 0x{loc:X}: entropy={entropy:.2f}, looks_compressed={looks_compressed}")
    
    # Test decompression
    for loc in test_locations:
        try:
            decompressed, consumed = bob_lz_decompress(rom_data[loc:], 32)
            print(f"0x{loc:X}: Decompressed {len(decompressed)} bytes from {consumed} bytes")
        except Exception as e:
            print(f"0x{loc:X}: Decompression failed: {e}")
    
    # Run the scanner
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        outdir = Path(tmpdir)
        candidates = scan_rom_for_compressed_blocks(rom_data, 0, outdir)
        
        print(f"\nScanner found {len(candidates)} candidates")
        for candidate in candidates:
            print(f"  0x{candidate['offset_int']:06X}: success={candidate['success']}, reason={candidate['reason']}")

if __name__ == "__main__":
    test_with_valid_lz77()