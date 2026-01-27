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
    
    # SNES tiles are often 2bpp or 4bpp with low entropy
    # Check for patterns typical of graphics data
    zero_count = data.count(0)
    low_byte_count = sum(1 for b in data if b < 16)
    
    # Graphics often have many zeros and low values
    if zero_count > len(data) * 0.3:
        return True
    if low_byte_count > len(data) * 0.5:
        return True
    
    return False


def looks_like_compressed(data):
    """Heuristic to check if data looks compressed."""
    if len(data) < 16:
        return False
    
    entropy = calculate_entropy(data)
    # Compressed data typically has high entropy (6.5-8.0)
    return 6.0 < entropy < 8.0


def scan_rom_for_compressed_blocks(rom_data, header_offset, outdir):
    """
    Scan ROM for compressed blocks using heuristics.
    
    Returns:
        list: candidates with metadata
    """
    rom = rom_data[header_offset:]
    candidates = []
    
    # Test various decompressed sizes (common sizes for SNES graphics)
    test_sizes = [
        0x1000,  # 4KB - common for tile data
        0x2000,  # 8KB
        0x4000,  # 16KB
        0x8000,  # 32KB
        0x800,   # 2KB
        0x400,   # 1KB
    ]
    
    print(f"Scanning ROM of size {len(rom)} bytes...")
    
    # Scan with stride (every 16 bytes to balance speed vs coverage)
    stride = 16
    for offset in range(0, len(rom) - 16, stride):
        if offset % 0x10000 == 0:
            print(f"Progress: {offset / len(rom) * 100:.1f}%")
        
        # Quick filter: check if this looks like it could be compressed data
        sample = rom[offset:offset + 64]
        if not looks_like_compressed(sample):
            continue
        
        # Try decompressing with various sizes
        for dec_size in test_sizes:
            try:
                decompressed, consumed = bob_lz_decompress(rom[offset:], dec_size)
                
                # Check if decompression was successful and plausible
                if consumed > 0 and consumed < dec_size * 2:  # Reasonable compression ratio
                    dec_entropy = calculate_entropy(decompressed)
                    comp_entropy = calculate_entropy(rom[offset:offset + consumed])
                    
                    # Decompressed should have lower entropy than compressed
                    entropy_drop = comp_entropy - dec_entropy
                    
                    is_tile_data = looks_like_tile_data(decompressed)
                    
                    # Accept if entropy dropped or looks like tile data
                    if entropy_drop > 0.5 or is_tile_data:
                        candidate = {
                            "offset": hex(offset + header_offset),
                            "offset_int": offset + header_offset,
                            "compressed_size": consumed,
                            "decompressed_size": dec_size,
                            "success": True,
                            "entropy_compressed": round(comp_entropy, 2),
                            "entropy_decompressed": round(dec_entropy, 2),
                            "looks_like_tiles": is_tile_data,
                            "reason": "successful decompression with entropy drop" if entropy_drop > 0.5 else "matches tile data pattern"
                        }
                        
                        # Save decompressed data
                        outfile = outdir / f"decompressed_{offset + header_offset:06X}.bin"
                        outfile.write_bytes(decompressed)
                        candidate["output_file"] = str(outfile.name)
                        
                        candidates.append(candidate)
                        
                        # Don't test other sizes for this offset
                        break
            except ValueError:
                # Decompression failed, try next size
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
