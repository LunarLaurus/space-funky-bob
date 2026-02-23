#!/usr/bin/env python3
"""
bob_inject.py - Inject modified data back into B.O.B. ROM

Usage:
    python bob_inject.py --rom "rom/B.O.B..smc" --tilemap data/levels/tilemap_04_02A000.bin --offset 0x02A000 --output "rom/B.O.B.modified.smc"
    
    # Inject compressed graphics
    python bob_inject.py --rom "rom/B.O.B..smc" --compressed data/gfx.bin --offset 0x030000 --size 0x800 --output "rom/B.O.B.modified.smc"
"""

import argparse
import struct
import sys
from pathlib import Path

try:
    from bob_lz_encode import bob_lz_encode
    from bob_lz import bob_lz_decompress
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from bob_lz_encode import bob_lz_encode
    from bob_lz import bob_lz_decompress


def inject_tilemap(rom_data, tilemap_path, offset, output_path=None):
    """Inject a tilemap into the ROM at the specified offset."""
    tilemap_data = Path(tilemap_path).read_bytes()
    
    if len(tilemap_data) != 0x800:
        print(f"Warning: Tilemap is {len(tilemap_data)} bytes, expected 0x800")
    
    rom = bytearray(rom_data)
    
    # Ensure we have enough space
    if offset + len(tilemap_data) > len(rom):
        print(f"Error: Offset 0x{offset:06X} + size {len(tilemap_data)} exceeds ROM size")
        return None
    
    # Inject the data
    rom[offset:offset + len(tilemap_data)] = tilemap_data
    
    print(f"Injected tilemap from {tilemap_path}")
    print(f"  Offset: 0x{offset:06X}")
    print(f"  Size: {len(tilemap_data)} bytes")
    
    if output_path:
        Path(output_path).write_bytes(rom)
        print(f"Saved to: {output_path}")
    
    return bytes(rom)


def inject_compressed(rom_data, compressed_path, offset, expected_size=None, output_path=None):
    """Inject pre-compressed data into ROM."""
    compressed = Path(compressed_path).read_bytes()
    
    rom = bytearray(rom_data)
    
    # Validate compression if size provided
    if expected_size:
        test_decompressed, consumed = bob_lz_decompress(compressed, expected_size)
        if consumed != len(compressed):
            print(f"Warning: Compressed data doesn't match expected size {expected_size}")
            print(f"  Consumed: {consumed}, File size: {len(compressed)}")
    
    if offset + len(compressed) > len(rom):
        print(f"Error: Offset 0x{offset:06X} + size {len(compressed)} exceeds ROM size")
        return None
    
    rom[offset:offset + len(compressed)] = compressed
    
    print(f"Injected compressed data from {compressed_path}")
    print(f"  Offset: 0x{offset:06X}")
    print(f"  Compressed size: {len(compressed)} bytes")
    
    if output_path:
        Path(output_path).write_bytes(rom)
        print(f"Saved to: {output_path}")
    
    return bytes(rom)


def compress_and_inject(rom_data, uncompressed_path, offset, output_path=None):
    """Compress data and inject into ROM."""
    uncompressed = Path(uncompressed_path).read_bytes()
    
    # Compress the data
    compressed = bob_lz_encode(uncompressed)
    
    # Verify compression
    test_decompressed, consumed = bob_lz_decompress(compressed, len(uncompressed))
    if test_decompressed != uncompressed:
        print("Error: Compression verification failed!")
        return None
    
    rom = bytearray(rom_data)
    
    if offset + len(compressed) > len(rom):
        print(f"Error: Offset 0x{offset:06X} + size {len(compressed)} exceeds ROM size")
        return None
    
    rom[offset:offset + len(compressed)] = compressed
    
    ratio = len(compressed) / len(uncompressed) * 100
    print(f"Compressed and injected from {uncompressed_path}")
    print(f"  Original: {len(uncompressed)} bytes")
    print(f"  Compressed: {len(compressed)} bytes ({ratio:.1f}%)")
    print(f"  Offset: 0x{offset:06X}")
    
    if output_path:
        Path(output_path).write_bytes(rom)
        print(f"Saved to: {output_path}")
    
    return bytes(rom)


def create_patch(original_rom, modified_rom, patch_path):
    """Create a patch file between original and modified ROM."""
    original = Path(original_rom).read_bytes()
    modified = Path(modified_rom).read_bytes()
    
    if len(original) != len(modified):
        print("Error: ROM sizes don't match")
        return
    
    patches = []
    i = 0
    while i < len(original):
        if original[i] != modified[i]:
            # Find run length
            j = i
            while j < len(original) and original[j] != modified[j]:
                j += 1
            
            patches.append({
                'offset': i,
                'original': original[i:j].hex(),
                'modified': modified[i:j].hex(),
                'size': j - i
            })
            i = j
        else:
            i += 1
    
    import json
    patch_data = {
        'original_size': len(original),
        'modified_size': len(modified),
        'num_patches': len(patches),
        'patches': patches
    }
    
    with open(patch_path, 'w') as f:
        json.dump(patch_data, f, indent=2)
    
    print(f"Created patch with {len(patches)} changes")
    print(f"Saved to: {patch_path}")


def main():
    parser = argparse.ArgumentParser(description="Inject modified data into B.O.B. ROM")
    parser.add_argument("--rom", required=True, help="Original ROM file")
    parser.add_argument("--output", help="Output ROM file (optional)")
    parser.add_argument("--tilemap", help="Tilemap file to inject")
    parser.add_argument("--offset", type=lambda x: int(x, 0), help="Offset in ROM (hex)")
    parser.add_argument("--compressed", help="Pre-compressed file to inject")
    parser.add_argument("--uncompressed", help="Uncompressed file to compress and inject")
    parser.add_argument("--size", type=lambda x: int(x, 0), help="Expected decompressed size (for validation)")
    parser.add_argument("--patch", nargs=2, help="Create patch: --patch original_rom modified_rom")
    
    args = parser.parse_args()
    
    # Handle patch creation
    if args.patch:
        create_patch(args.patch[0], args.patch[1], args.output or "patch.json")
        return
    
    # Load original ROM
    rom_data = Path(args.rom).read_bytes()
    print(f"Loaded ROM: {len(rom_data):,} bytes")
    
    # Determine output path
    output_path = args.output
    if not output_path:
        # Create modified filename
        p = Path(args.rom)
        output_path = str(p.parent / f"{p.stem}_modified{p.suffix}")
    
    # Perform injection
    if args.tilemap:
        if not args.offset:
            print("Error: --offset required for tilemap injection")
            return 1
        inject_tilemap(rom_data, args.tilemap, args.offset, output_path)
    
    elif args.compressed:
        if not args.offset:
            print("Error: --offset required for compressed injection")
            return 1
        inject_compressed(rom_data, args.compressed, args.offset, args.size, output_path)
    
    elif args.uncompressed:
        if not args.offset:
            print("Error: --offset required for uncompressed injection")
            return 1
        compress_and_inject(rom_data, args.uncompressed, args.offset, output_path)
    
    else:
        print("Error: Specify --tilemap, --compressed, or --uncompressed")
        return 1
    
    print("\nInjection complete!")
    return 0


if __name__ == "__main__":
    exit(main())
