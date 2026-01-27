#!/usr/bin/env python3
"""
validate_known_block.py - Validate decoder against known B.O.B. compressed block

Tests the decoder against the documented compressed block at offset 0x1AD34
with known decompressed size 0x822 bytes.

Usage:
    python validate_known_block.py bob.smc
"""

import sys
from pathlib import Path
from bob_lz import bob_lz_decompress


def validate_known_block(rom_path):
    """Validate against known B.O.B. compressed block."""
    
    # Read ROM
    rom_data = Path(rom_path).read_bytes()
    print(f"Loaded ROM: {len(rom_data)} bytes ({len(rom_data) / 1024 / 1024:.2f} MB)")
    
    # Detect header (512 bytes for .smc files)
    header_offset = 512 if len(rom_data) % 1024 == 512 else 0
    print(f"Header offset: {header_offset}")
    
    # Check ROM title to confirm it's B.O.B.
    rom = rom_data[header_offset:]
    if len(rom) > 0x7FC0 + 21:
        title_bytes = rom[0x7FC0:0x7FC0 + 21]
        title = title_bytes.rstrip(b'\x00 ').decode('ascii', errors='ignore')
        print(f"ROM title: '{title}'")
        
        if 'B.O.B' not in title:
            print("⚠ Warning: ROM title doesn't contain 'B.O.B'. This may not be the correct ROM.")
    
    # Known compressed block from documentation
    # Source: "Let's say you have the ROM loaded, and have a 0x822 byte file at offset 0x1AD34"
    compressed_offset = 0x1AD34
    expected_dec_size = 0x822
    
    print(f"\nTesting known compressed block:")
    print(f"  Offset: 0x{compressed_offset:X}")
    print(f"  Expected decompressed size: 0x{expected_dec_size:X} ({expected_dec_size} bytes)")
    
    # Read compressed data (read extra to ensure we have enough)
    actual_offset = compressed_offset + header_offset
    compressed_data = rom_data[actual_offset:actual_offset + 0x2000]
    
    try:
        # Decompress
        decompressed, consumed = bob_lz_decompress(compressed_data, expected_dec_size)
        
        # Validate
        if len(decompressed) == expected_dec_size:
            print(f"\n✓ SUCCESS!")
            print(f"  Consumed: {consumed} bytes (0x{consumed:X})")
            print(f"  Decompressed: {len(decompressed)} bytes (0x{len(decompressed):X})")
            print(f"  Compression ratio: {consumed / len(decompressed) * 100:.1f}%")
            
            # Show first 32 bytes
            print(f"\n  First 32 bytes of decompressed data:")
            hex_str = " ".join(f"{b:02X}" for b in decompressed[:32])
            print(f"  {hex_str}")
            
            # Calculate entropy as additional validation
            from collections import Counter
            freq = Counter(decompressed)
            entropy = 0.0
            for count in freq.values():
                p = count / len(decompressed)
                entropy -= p * (p and (p * 0.693147 + (1-p) * 0.693147))  # log2 approx
            print(f"  Entropy: {entropy:.2f} bits/byte")
            
            return True
        else:
            print(f"\n✗ FAILED: Size mismatch")
            print(f"  Expected: {expected_dec_size} bytes")
            print(f"  Got: {len(decompressed)} bytes")
            return False
            
    except ValueError as e:
        print(f"\n✗ FAILED: Decompression error")
        print(f"  Error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_known_block.py <path_to_bob.smc>")
        print("\nExample:")
        print("  python validate_known_block.py bob.smc")
        print("  python validate_known_block.py SpaceFunkyBob.sfc")
        return 1
    
    rom_path = sys.argv[1]
    
    if not Path(rom_path).exists():
        print(f"Error: ROM file not found: {rom_path}")
        return 1
    
    success = validate_known_block(rom_path)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
