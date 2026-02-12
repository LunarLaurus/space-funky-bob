#!/usr/bin/env python3
"""
Test scanner with ROM containing valid high-entropy compressed data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toolkit.bob_lz_scan import scan_rom_for_compressed_blocks
from pathlib import Path
import tempfile
import random

def create_test_rom_with_valid_data():
    """Create a test ROM with valid compressed data"""
    
    # Create fake B.O.B. ROM
    rom_data = bytearray(0x20000)  # 128KB ROM
    
    # Add LoROM header
    rom_data[0x7FC0:0x7FC0+21] = b"B.O.B.             "
    rom_data[0x7FD6] = 0x69  # Fixed byte
    rom_data[0x7FDA] = 0x09  # ROM size (8 Mbit)
    rom_data[0x7FEA:0x7FEC] = (0x7379).to_bytes(2, 'little')  # Checksum
    rom_data[0x7FEC:0x7FEE] = (0x8C86).to_bytes(2, 'little')  # Complement
    
    # Create high entropy compressed data that will pass scanner
    # Must be at least 0x400 (1KB) when decompressed to match scanner test_sizes
    random.seed(42)
    
    # Create 0x800 bytes (2KB) of decompressed data
    target_size = 0x800  # 2KB
    all_data = []
    
    # Generate enough chunks to decompress to target_size
    # Each chunk header + 8 literals = 9 bytes input -> 8 bytes output
    # For 0x800 bytes output, need 0x800/8 = 256 chunks = 256*9 = 2304 bytes input
    num_chunks = (target_size + 7) // 8  # Round up
    
    for i in range(num_chunks):
        header = 0x00  # All literals for this chunk
        # Use printable ASCII for variety
        literals = bytes([random.randint(33, 126) for _ in range(8)])
        all_data.append(header)
        all_data.extend(literals)
    
    test_compressed = bytes(all_data[:target_size + 256])  # Some extra bytes
    print(f"Test compressed data size: {len(test_compressed)} bytes")
    
    # Place at known location
    rom_data[0x10000:0x10000+len(test_compressed)] = test_compressed
    
    print("=== Testing Complete Scanner ===")
    print(f"ROM size: {len(rom_data)} bytes")
    print(f"Test data location: 0x10000")
    print(f"Test data size: {len(test_compressed)} bytes")
    
    # Test decompression at that location
    from toolkit.bob_lz import bob_lz_decompress
    try:
        decompressed, consumed = bob_lz_decompress(test_compressed, 64)
        print(f"Manual decompression: {len(decompressed)} bytes from {consumed} consumed")
        success = len(decompressed) == 64
        print(f"Manual test success: {success}")
    except Exception as e:
        print(f"Manual test failed: {e}")
        success = False
    
    if success:
        # Debug the values for our test location
        from toolkit.bob_lz_scan import calculate_entropy, looks_like_compressed, looks_like_tile_data
        
        sample = rom_data[0x10000:0x10000+72]  # 72 bytes = 8 headers + 64 literals
        sample_entropy = calculate_entropy(sample)
        looks_compressed = looks_like_compressed(sample)
        
        print(f"Debug - Sample entropy: {sample_entropy:.2f}")
        print(f"Debug - Looks compressed: {looks_compressed}")
        
        # Debug decompressed data properties - try all test sizes
        print("\nDebug - Testing different decompression sizes:")
        for test_size in [0x1000, 0x2000, 0x4000, 0x8000, 0x800, 0x400, 64]:
            try:
                decompressed, consumed = bob_lz_decompress(test_compressed, test_size)
                if consumed > 0:
                    dec_entropy = calculate_entropy(decompressed)
                    looks_like_tiles = looks_like_tile_data(decompressed)
                    entropy_drop = sample_entropy - dec_entropy
                    
                    cond1 = entropy_drop > 0.1
                    cond2 = looks_like_tiles and dec_entropy > 1.0
                    cond3 = consumed > 50 and dec_entropy > 1.5
                    
                    print(f"  Size {test_size:5d}: consumed={consumed:4d}, dec_ent={dec_entropy:.2f}, tiles={looks_like_tiles}")
                    print(f"         drop={entropy_drop:.2f}, cond1={cond1}, cond2={cond2}, cond3={cond3}")
                    
            except Exception as e:
                pass
        
        # Run full scanner
        with tempfile.TemporaryDirectory() as tmpdir:
            outdir = Path(tmpdir)
            candidates = scan_rom_for_compressed_blocks(rom_data, 0, outdir)
            
            print(f"\nScanner found {len(candidates)} candidates")
            for candidate in candidates:
                print(f"  0x{candidate['offset_int']:06X}: success={candidate['success']}, compressed={candidate['compressed_size']}, decompressed={candidate['decompressed_size']}")
                print(f"    Reason: {candidate['reason']}")
                print(f"    Entropy: {candidate['entropy_compressed']} -> {candidate['entropy_decompressed']}")
                print(f"    Looks like tiles: {candidate['looks_like_tiles']}")
            
            # Check if our test location was found
            test_loc_found = any(c['offset_int'] == 0x10000 for c in candidates)
            print(f"\nTest location 0x10000 found: {test_loc_found}")
            
            if test_loc_found:
                print("SUCCESS: Scanner correctly identified valid compressed data!")
            else:
                print("ISSUE: Scanner missed our test compressed block")
                
    else:
        print("Cannot test scanner - manual decompression failed")

if __name__ == "__main__":
    create_test_rom_with_valid_data()