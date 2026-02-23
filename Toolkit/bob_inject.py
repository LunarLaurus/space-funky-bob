#!/usr/bin/env python3
"""
bob_inject.py - Inject modified data back into B.O.B. ROM

Usage:
    python bob_inject.py --rom "rom/B.O.B..smc" --tilemap data/levels/tilemap_04_02A000.bin --offset 0x02A000 --output "rom/B.O.B.modified.smc"

    # Inject compressed graphics
    python bob_inject.py --rom "rom/B.O.B..smc" --compressed data/gfx.bin --offset 0x030000 --size 0x800 --output "rom/B.O.B.modified.smc"

Safety Features:
    - Automatic backup creation
    - Size and boundary validation
    - SNES checksum verification
    - Dry-run mode
"""

import argparse
import struct
import sys
import shutil
from datetime import datetime
from pathlib import Path

try:
    from bob_lz_encode import bob_lz_encode
    from bob_lz import bob_lz_decompress
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from bob_lz_encode import bob_lz_encode
    from bob_lz import bob_lz_decompress


# =============================================================================
# Safety Functions
# =============================================================================

def create_backup(rom_path):
    """
    Create timestamped backup of ROM file.
    
    Args:
        rom_path: Path to ROM file
        
    Returns:
        Path to backup file
    """
    rom_path = Path(rom_path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = rom_path.parent / f"{rom_path.stem}.backup.{timestamp}{rom_path.suffix}"
    shutil.copy2(rom_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path


def validate_injection(rom_data, offset, new_data, max_size=None):
    """
    Validate injection is safe.
    
    Args:
        rom_data: ROM data
        offset: Injection offset
        new_data: Data to inject
        max_size: Maximum allowed size (optional)
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Check bounds
    if offset < 0:
        errors.append(f"Offset 0x{offset:X} is negative")
    
    if offset >= len(rom_data):
        errors.append(f"Offset 0x{offset:X} exceeds ROM size (0x{len(rom_data):X})")
    
    if offset + len(new_data) > len(rom_data):
        errors.append(f"Data exceeds ROM size: offset 0x{offset:X} + size {len(new_data)} > ROM size 0x{len(rom_data):X}")
    
    # Check max size if specified
    if max_size and len(new_data) > max_size:
        errors.append(f"Data size {len(new_data)} exceeds maximum {max_size}")
    
    return errors


def verify_checksum(rom_data):
    """
    Verify SNES ROM checksum at 0x7FDC-0x7FDF.
    
    Args:
        rom_data: ROM data
        
    Returns:
        tuple: (is_valid, stored_checksum, calculated_checksum)
    """
    # Detect header offset
    header_offset = 0
    if len(rom_data) % 1024 == 512:
        header_offset = 512
    
    checksum_pos = 0x7FDC + header_offset
    
    if checksum_pos + 4 > len(rom_data):
        return False, 0, 0
    
    stored_checksum = struct.unpack('<H', rom_data[checksum_pos:checksum_pos+2])[0]
    stored_complement = struct.unpack('<H', rom_data[checksum_pos+2:checksum_pos+4])[0]
    
    # Calculate checksum (sum of bytes from 0 to 0x7FDC)
    calculated = sum(rom_data[0:checksum_pos]) & 0xFFFF
    calculated_complement = 0xFFFF - calculated
    
    is_valid = (stored_checksum == calculated and stored_complement == calculated_complement)
    
    return is_valid, stored_checksum, calculated


def verify_injection_area(rom_data, offset, size, protected_regions=None):
    """
    Verify injection area doesn't overlap with protected regions.
    
    Args:
        rom_data: ROM data
        offset: Injection offset
        size: Injection size
        protected_regions: List of (start, end) tuples
        
    Returns:
        List of warning messages
    """
    warnings = []
    
    # Default protected regions for B.O.B.
    if protected_regions is None:
        protected_regions = [
            (0x7FC0, 0x7FFF),  # Header
        ]
    
    # Check for overlaps
    for start, end in protected_regions:
        if offset < end and (offset + size) > start:
            warnings.append(f"WARNING: Injection overlaps with protected region 0x{start:X}-0x{end:X}")
    
    return warnings


def dry_run_inject(rom_data, offset, new_data):
    """
    Simulate injection without modifying data.
    
    Args:
        rom_data: ROM data
        offset: Injection offset
        new_data: Data to inject
        
    Returns:
        dict: Dry run results
    """
    # Validate
    errors = validate_injection(rom_data, offset, new_data)
    warnings = verify_injection_area(rom_data, offset, len(new_data))
    
    # Calculate what would change
    changed_bytes = sum(1 for i in range(len(new_data)) 
                       if offset + i < len(rom_data) and rom_data[offset + i] != new_data[i])
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'offset': offset,
        'size': len(new_data),
        'changed_bytes': changed_bytes,
        'would_modify': changed_bytes > 0
    }


def inject_tilemap(rom_data, tilemap_path, offset, output_path=None, create_backup_file=False):
    """
    Inject a tilemap into the ROM at the specified offset.
    
    Args:
        rom_data: ROM data
        tilemap_path: Path to tilemap file
        offset: Injection offset
        output_path: Output ROM path
        create_backup_file: Create backup before injection (only if output_path is file)
        
    Returns:
        Modified ROM data or None on error
    """
    tilemap_data = Path(tilemap_path).read_bytes()

    if len(tilemap_data) != 0x800:
        print(f"Warning: Tilemap is {len(tilemap_data)} bytes, expected 0x800")

    # Validate injection
    errors = validate_injection(rom_data, offset, tilemap_data)
    if errors:
        for error in errors:
            print(f"Error: {error}")
        return None
    
    # Create backup if requested
    if create_backup_file and output_path:
        create_backup(output_path)

    rom = bytearray(rom_data)
    rom[offset:offset + len(tilemap_data)] = tilemap_data

    print(f"Injected tilemap from {tilemap_path}")
    print(f"  Offset: 0x{offset:06X}")
    print(f"  Size: {len(tilemap_data)} bytes")

    if output_path:
        Path(output_path).write_bytes(rom)
        print(f"Saved to: {output_path}")

    return bytes(rom)


def inject_compressed(rom_data, compressed_path, offset, expected_size=None, output_path=None, create_backup_file=False):
    """
    Inject pre-compressed data into ROM.
    
    Args:
        rom_data: ROM data
        compressed_path: Path to compressed file
        offset: Injection offset
        expected_size: Expected decompressed size
        output_path: Output ROM path
        create_backup_file: Create backup before injection
        
    Returns:
        Modified ROM data or None on error
    """
    compressed = Path(compressed_path).read_bytes()
    
    # Validate injection
    errors = validate_injection(rom_data, offset, compressed, expected_size)
    if errors:
        for error in errors:
            print(f"Error: {error}")
        return None

    # Validate compression if size provided
    if expected_size:
        test_decompressed, consumed = bob_lz_decompress(compressed, expected_size)
        if consumed != len(compressed):
            print(f"Warning: Compressed data doesn't match expected size {expected_size}")
            print(f"  Consumed: {consumed}, File size: {len(compressed)}")

    # Create backup if requested
    if create_backup_file and output_path:
        create_backup(output_path)

    rom = bytearray(rom_data)
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
    parser.add_argument("--dry-run", action="store_true", help="Simulate injection without modifying")
    parser.add_argument("--backup", action="store_true", help="Create backup before injection")
    parser.add_argument("--verify-checksum", action="store_true", help="Verify ROM checksum after injection")

    args = parser.parse_args()

    # Handle patch creation
    if args.patch:
        create_patch(args.patch[0], args.patch[1], args.output or "patch.json")
        return

    # Load original ROM
    rom_data = Path(args.rom).read_bytes()
    print(f"Loaded ROM: {len(rom_data):,} bytes")

    # Handle dry-run mode
    if args.dry_run:
        if args.tilemap:
            tilemap_data = Path(args.tilemap).read_bytes()
            result = dry_run_inject(rom_data, args.offset, tilemap_data)
        elif args.compressed:
            compressed_data = Path(args.compressed).read_bytes()
            result = dry_run_inject(rom_data, args.offset, compressed_data)
        elif args.uncompressed:
            uncompressed_data = Path(args.uncompressed).read_bytes()
            compressed_data = bob_lz_encode(uncompressed_data)
            result = dry_run_inject(rom_data, args.offset, compressed_data)
        else:
            print("Error: Specify --tilemap, --compressed, or --uncompressed for dry-run")
            return 1
        
        print("\n=== DRY RUN RESULTS ===")
        print(f"Valid: {result['valid']}")
        print(f"Offset: 0x{result['offset']:06X}")
        print(f"Size: {result['size']} bytes")
        print(f"Would modify: {result['changed_bytes']} bytes")
        
        if result['errors']:
            print("\nErrors:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['warnings']:
            print("\nWarnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        return 0 if result['valid'] else 1

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
        inject_tilemap(rom_data, args.tilemap, args.offset, output_path, create_backup_file=args.backup)

    elif args.compressed:
        if not args.offset:
            print("Error: --offset required for compressed injection")
            return 1
        inject_compressed(rom_data, args.compressed, args.offset, args.size, output_path, create_backup_file=args.backup)

    elif args.uncompressed:
        if not args.offset:
            print("Error: --offset required for uncompressed injection")
            return 1
        compress_and_inject(rom_data, args.uncompressed, args.offset, output_path)

    else:
        print("Error: Specify --tilemap, --compressed, or --uncompressed")
        return 1

    # Verify checksum if requested
    if args.verify_checksum and output_path:
        output_rom = Path(output_path).read_bytes()
        is_valid, stored, calculated = verify_checksum(output_rom)
        if is_valid:
            print(f"\nChecksum verification: PASS (0x{stored:04X})")
        else:
            print(f"\nChecksum verification: FAIL")
            print(f"  Stored: 0x{stored:04X}, Calculated: 0x{calculated:04X}")

    print("\nInjection complete!")
    return 0


if __name__ == "__main__":
    exit(main())
