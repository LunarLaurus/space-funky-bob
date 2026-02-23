#!/usr/bin/env python3
"""
bob_lz_scan.py — B.O.B. ROM Compressed Block Scanner

Scans a SNES ROM for B.O.B.-variant LZ77 compressed blocks and attempts
to decompress them. Outputs candidates.json with results and saves
successfully decompressed data to files.

Usage:
    python bob_lz_scan.py --rom SpaceFunkyBob.sfc --outdir out/
"""

import argparse
import json
import math
import os
import struct
from pathlib import Path

# Handle both module and standalone imports
try:
    from .bob_lz import bob_lz_decompress, bob_lz_decompress_exploratory
except ImportError:
    from bob_lz import bob_lz_decompress, bob_lz_decompress_exploratory


def detect_rom_header(rom_data):
    """
    Detect if ROM has a 512-byte copier header.
    
    B.O.B. is known to be LoROM at 0x7FC0 with title "B.O.B." and fixed byte 0x69.
    
    Returns:
        tuple: (has_header: bool, header_offset: int, title: str)
    """
    size = len(rom_data)
    
    # Try LoROM position with 512-byte header (common for .smc files)
    if size % 1024 == 512:  # Has 512-byte header
        header_pos = 0x7FC0 + 512
        if header_pos + 32 < size:
            title_data = rom_data[header_pos:header_pos + 21]
            title = title_data.rstrip(b'\x00 ').decode('ascii', errors='ignore')
            fixed_byte = rom_data[header_pos + 21] if header_pos + 21 < size else 0
            
            # B.O.B. specific: title should be "B.O.B." and fixed byte is 0x69
            if 'B.O.B' in title or fixed_byte == 0x69:
                return True, 512, title
            
            # Generic check for valid ASCII title
            if all(32 <= b < 127 or b == 0 for b in title_data):
                return True, 512, title
    
    # Check without header (headerless ROM)
    header_pos = 0x7FC0
    if header_pos + 32 < size:
        title_data = rom_data[header_pos:header_pos + 21]
        title = title_data.rstrip(b'\x00 ').decode('ascii', errors='ignore')
        fixed_byte = rom_data[header_pos + 21] if header_pos + 21 < size else 0
        
        if 'B.O.B' in title or fixed_byte == 0x69:
            return False, 0, title
        
        if all(32 <= b < 127 or b == 0 for b in title_data):
            return False, 0, title
    
    # Check HiROM position as fallback
    header_pos = 0xFFC0
    if header_pos + 32 < size:
        title_data = rom_data[header_pos:header_pos + 21]
        title = title_data.rstrip(b'\x00 ').decode('ascii', errors='ignore')
        if all(32 <= b < 127 or b == 0 for b in title_data):
            return False, 0, title
    
    return False, 0, "Unknown"


def detect_rom_mapping(rom_data, header_offset):
    """
    Detect LoROM vs HiROM mapping.
    
    B.O.B. is confirmed to be LoROM Fast (map mode byte should indicate this).
    ROM size: 8 Mbits = 1 MB = 0x100000 bytes
    
    Returns:
        str: "LoROM" or "HiROM"
    """
    rom = rom_data[header_offset:]
    
    # Check LoROM header position
    lo_pos = 0x7FC0
    hi_pos = 0xFFC0
    
    lo_score = 0
    hi_score = 0
    
    # Check if internal header exists and looks valid
    if lo_pos + 32 < len(rom):
        # Check makeup/version byte (byte 21)
        makeup = rom[lo_pos + 21]
        # B.O.B. uses 0x69 which is uncommon but valid
        # LoROM Fast = 0x20-0x2F range typically, but B.O.B. may differ
        if makeup in [0x00, 0x01, 0x02, 0x03, 0x13, 0x23, 0x33, 0x69]:
            lo_score += 2
        
        # Check ROM size byte (byte 23)
        # 8 Mbits = size byte 0x09 (2^9 * 1024 bytes = 512KB... wait, 8Mbit = 1MB = 0x0A)
        rom_size = rom[lo_pos + 23]
        if 7 <= rom_size <= 13:  # Valid range
            lo_score += 1
        
        # Check checksum complement
        if lo_pos + 31 < len(rom):
            checksum = struct.unpack('<H', rom[lo_pos + 28:lo_pos + 30])[0]
            complement = struct.unpack('<H', rom[lo_pos + 30:lo_pos + 32])[0]
            # B.O.B.: checksum=0x7379, complement=0x8C86
            # 0x7379 ^ 0x8C86 should = 0xFFFF
            if (checksum ^ complement) == 0xFFFF:
                lo_score += 3
    
    if hi_pos + 32 < len(rom):
        makeup = rom[hi_pos + 21]
        if makeup in [0x00, 0x01, 0x02, 0x03, 0x13, 0x23, 0x33]:
            hi_score += 2
        rom_size = rom[hi_pos + 23]
        if 7 <= rom_size <= 13:
            hi_score += 1
        if hi_pos + 31 < len(rom):
            checksum = struct.unpack('<H', rom[hi_pos + 28:hi_pos + 30])[0]
            complement = struct.unpack('<H', rom[hi_pos + 30:hi_pos + 32])[0]
            if (checksum ^ complement) == 0xFFFF:
                hi_score += 3
    
    return "HiROM" if hi_score > lo_score else "LoROM"


def calculate_entropy(data):
    """Calculate Shannon entropy of byte data."""
    if not data:
        return 0.0
    
    freq = [0] * 256
    for byte in data:
        freq[byte] += 1
    
    entropy = 0.0
    data_len = len(data)
    for count in freq:
        if count > 0:
            p = count / data_len
            entropy -= p * math.log2(p)
    
    return entropy


def looks_like_tile_data(data):
    """Check if decompressed data resembles SNES tile data."""
    if len(data) < 32:
        return False
    
    # SNES tiles are often 2bpp or 4bpp with moderate entropy
    # Very low entropy (<0.5) usually indicates empty/filler data
    entropy = calculate_entropy(data)
    if entropy < 0.5:
        return False  # Too low entropy, likely empty data
    
    # Check for patterns typical of graphics data
    zero_count = data.count(0)
    low_byte_count = sum(1 for b in data if b < 16)
    
    # Graphics often have some zeros and low values, but not overwhelmingly so
    if zero_count > len(data) * 0.4:  # Reduced from 0.3
        return False  # Too many zeros, likely empty
    if low_byte_count > len(data) * 0.6:  # Reduced from 0.5
        return False  # Too many low bytes, likely empty
    
    # Look for more balanced graphics patterns
    # Real tile data has varied patterns, not just zeros
    unique_bytes = len(set(data))
    if unique_bytes < 8:  # Need some variety
        return False
    
    # Accept as potential tile data if it has moderate entropy and reasonable patterns
    return True


def looks_like_compressed(data):
    """Heuristic to check if data looks compressed."""
    if len(data) < 16:
        return False
    
    entropy = calculate_entropy(data)
    # Compressed data can have a wide range of entropy
    # B.O.B. data with mostly literals can have entropy as low as 2.5
    # Very low entropy (<2.0) is likely structured/repeated data
    # Very high entropy (>7.8) might be encrypted/compressed with different scheme
    return 2.0 < entropy < 8.0


def scan_rom_for_compressed_blocks(rom_data, header_offset, outdir, fast=True):
    """
    Scan ROM for compressed blocks using fast heuristics.
    
    Args:
        rom_data: full ROM data
        header_offset: ROM header offset (0 or 512)
        outdir: output directory for candidates
        fast: if True, use larger stride and skip encoder verification
    
    Returns:
        list: candidates with metadata
    """
    rom = rom_data[header_offset:]
    candidates = []
    
    # Core test sizes (most common for SNES graphics)
    test_sizes = [
        0x800,   # 2KB - common for small blocks
        0x1000,  # 4KB - very common
        0x2000,  # 8KB
        0x4000,  # 16KB
        0x822,   # Known block size from documentation
    ]
    
    # Import encoder for verification (optional)
    try:
        from bob_lz_encode import bob_lz_encode
        has_encoder = True
    except ImportError:
        has_encoder = False
    
    # Stride: 64 bytes for fast mode (covers most blocks), 16 for thorough
    stride = 64 if fast else 16
    
    print(f"Scanning ROM of size {len(rom)} bytes (stride={stride})...")
    
    for offset in range(0, len(rom) - 16, stride):
        if offset % 0x20000 == 0:
            progress = offset / len(rom) * 100
            print(f"Progress: {progress:.1f}% (found {len(candidates)})")
        
        # Pre-filter: check if this region has compressed-like entropy
        sample = rom[offset:offset + 64]
        if not looks_like_compressed(sample):
            continue
        
        # Try decompressing with various sizes
        for dec_size in test_sizes:
            if offset + 10 >= len(rom):
                continue
            
            try:
                decompressed, consumed = bob_lz_decompress(rom[offset:], dec_size)
                
                # Must consume some input and achieve compression
                if consumed < 3 or consumed >= dec_size * 0.85:
                    continue
                
                # Calculate entropies
                comp_entropy = calculate_entropy(rom[offset:offset + consumed])
                dec_entropy = calculate_entropy(decompressed)
                
                # Quick acceptance: compressed data should have higher entropy than result
                if comp_entropy < 2.0:
                    continue
                
                # Encoder verification if available and result looks promising
                verified = False
                if has_encoder and dec_entropy > 1.0:
                    try:
                        re_encoded = bob_lz_encode(decompressed)
                        re_decoded, _ = bob_lz_decompress(re_encoded, dec_size)
                        verified = (re_decoded == decompressed)
                    except Exception:
                        pass
                
                # Acceptance: verified OR entropy drop with reasonable output
                if verified or (dec_entropy < comp_entropy and dec_entropy > 1.0):
                    # Check for duplicates
                    if any(c["offset_int"] == offset + header_offset for c in candidates):
                        continue
                    
                    candidate = {
                        "offset": hex(offset + header_offset),
                        "offset_int": offset + header_offset,
                        "compressed_size": consumed,
                        "decompressed_size": dec_size,
                        "success": True,
                        "entropy_compressed": round(comp_entropy, 2),
                        "entropy_decompressed": round(dec_entropy, 2),
                        "looks_like_tiles": looks_like_tile_data(decompressed),
                        "encoder_verified": verified,
                    }
                    
                    # Save decompressed data
                    outfile = outdir / f"decompressed_{offset + header_offset:06X}.bin"
                    outfile.write_bytes(decompressed[:dec_size])
                    candidate["output_file"] = str(outfile.name)
                    
                    candidates.append(candidate)
                    break  # Found valid, don't try other sizes
                    
            except (ValueError, IndexError):
                continue
    
    print(f"\nFound {len(candidates)} candidate compressed blocks")
    return candidates


def main():
    parser = argparse.ArgumentParser(description="Scan SNES ROM for B.O.B. compressed blocks")
    parser.add_argument("--rom", required=True, help="Path to ROM file")
    parser.add_argument("--outdir", default="out", help="Output directory")
    args = parser.parse_args()
    
    # Read ROM
    rom_path = Path(args.rom)
    if not rom_path.exists():
        print(f"Error: ROM file not found: {rom_path}")
        return 1
    
    rom_data = rom_path.read_bytes()
    print(f"Loaded ROM: {len(rom_data)} bytes ({len(rom_data) / 1024 / 1024:.2f} MB)")
    
    # Detect header
    has_header, header_offset, title = detect_rom_header(rom_data)
    print(f"ROM title: '{title}'")
    print(f"Copier header: {'yes' if has_header else 'no'} (offset: {header_offset})")
    
    # Detect mapping
    mapping = detect_rom_mapping(rom_data, header_offset)
    print(f"ROM mapping: {mapping}")
    
    # Create output directory
    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)
    
    # Scan for compressed blocks
    candidates = scan_rom_for_compressed_blocks(rom_data, header_offset, outdir)
    
    # Save candidates.json
    output = {
        "rom_file": str(rom_path),
        "rom_size": len(rom_data),
        "rom_title": title,
        "has_header": has_header,
        "header_offset": header_offset,
        "rom_mapping": mapping,
        "num_candidates": len(candidates),
        "candidates": candidates
    }
    
    json_path = outdir / "candidates.json"
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to {json_path}")
    print(f"Decompressed files saved to {outdir}/")
    
    return 0


if __name__ == "__main__":
    exit(main())
