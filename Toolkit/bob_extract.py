#!/usr/bin/env python3
"""
bob_extract.py - B.O.B. ROM Data Extraction Tool

Extracts code, data, and graphics regions from ROM based on classification.

Usage:
    python toolkit/bob_extract.py --rom rom/B.O.B..smc --type code --outdir data/extracted
    python toolkit/bob_extract.py --rom rom/B.O.B..smc --type data --outdir data/extracted
    python toolkit/bob_extract.py --rom rom/B.O.B..smc --type graphics --outdir data/extracted
    python toolkit/bob_extract.py --rom rom/B.O.B..smc --type all --outdir data/extracted

Output:
    code/    - Extracted code regions
    data/    - Extracted data regions  
    graphics/ - Extracted graphics regions
"""

import argparse
import json
import os
import struct
import math
from pathlib import Path
from collections import Counter


def calculate_entropy(data):
    """Calculate Shannon entropy."""
    if not data:
        return 0.0
    freq = Counter(data)
    entropy = 0.0
    data_len = len(data)
    for count in freq.values():
        if count > 0:
            p = count / data_len
            entropy -= p * math.log2(p)
    return entropy


def detect_rom_header(rom_data):
    """Detect ROM header and mapping."""
    size = len(rom_data)
    
    # Try LoROM position
    lo_pos = 0x7FC0
    if size > lo_pos + 32:
        title = rom_data[lo_pos:lo_pos+21].rstrip(b'\x00 ').decode('ascii', errors='ignore')
        fixed = rom_data[lo_pos + 21]
        if fixed == 0x69:  # B.O.B. fixed byte
            return 0, "LoROM", title
    
    # Try with 512-byte header
    if size % 1024 == 512:
        lo_pos = 0x7FC0 + 512
        if size > lo_pos + 32:
            title = rom_data[lo_pos:lo_pos+21].rstrip(b'\x00 ').decode('ascii', errors='ignore')
            fixed = rom_data[lo_pos + 21]
            if fixed == 0x69:
                return 512, "LoROM", title
    
    return 0, "LoROM", "Unknown"


# 65816 opcode table for code detection
OPCODES_65816 = {
    0x00: 2, 0x01: 2, 0x02: 2, 0x03: 2, 0x04: 2, 0x05: 2, 0x06: 2, 0x07: 2,
    0x08: 1, 0x09: 2, 0x0A: 1, 0x0B: 1, 0x0C: 2, 0x0D: 3, 0x0E: 3, 0x0F: 3,
    0x10: 2, 0x11: 2, 0x12: 2, 0x13: 2, 0x14: 2, 0x15: 2, 0x16: 2, 0x17: 2,
    0x18: 1, 0x19: 3, 0x1A: 1, 0x1B: 1, 0x1C: 2, 0x1D: 3, 0x1E: 3, 0x1F: 3,
    0x20: 3, 0x21: 2, 0x22: 3, 0x23: 2, 0x24: 2, 0x25: 2, 0x26: 2, 0x27: 2,
    0x28: 1, 0x29: 2, 0x2A: 1, 0x2B: 1, 0x2C: 2, 0x2D: 3, 0x2E: 3, 0x2F: 3,
    0x30: 2, 0x31: 2, 0x32: 2, 0x33: 2, 0x34: 2, 0x35: 2, 0x36: 2, 0x37: 2,
    0x38: 1, 0x39: 3, 0x3A: 1, 0x3B: 1, 0x3C: 2, 0x3D: 3, 0x3E: 3, 0x3F: 3,
    0x40: 1, 0x41: 2, 0x42: 1, 0x43: 2, 0x44: 1, 0x45: 2, 0x46: 2, 0x47: 2,
    0x48: 1, 0x49: 2, 0x4A: 1, 0x4B: 1, 0x4C: 3, 0x4D: 3, 0x4E: 3, 0x4F: 3,
    0x50: 2, 0x51: 2, 0x52: 2, 0x53: 2, 0x54: 2, 0x55: 2, 0x56: 2, 0x57: 2,
    0x58: 1, 0x59: 3, 0x5A: 1, 0x5B: 1, 0x5C: 2, 0x5D: 3, 0x5E: 3, 0x5F: 3,
    0x60: 1, 0x61: 2, 0x62: 1, 0x63: 2, 0x64: 1, 0x65: 2, 0x66: 2, 0x67: 2,
    0x68: 1, 0x69: 2, 0x6A: 1, 0x6B: 1, 0x6C: 3, 0x6D: 3, 0x6E: 3, 0x6F: 3,
    0x70: 2, 0x71: 2, 0x72: 2, 0x73: 2, 0x74: 2, 0x75: 2, 0x76: 2, 0x77: 2,
    0x78: 1, 0x79: 3, 0x7A: 1, 0x7B: 1, 0x7C: 2, 0x7D: 3, 0x7E: 3, 0x7F: 3,
    0x80: 2, 0x81: 3, 0x82: 2, 0x83: 2, 0x84: 2, 0x85: 2, 0x86: 2, 0x87: 2,
    0x88: 1, 0x89: 2, 0x8A: 1, 0x8B: 1, 0x8C: 3, 0x8D: 3, 0x8E: 3, 0x8F: 3,
    0x90: 1, 0x91: 2, 0x92: 2, 0x93: 2, 0x94: 2, 0x95: 2, 0x96: 2, 0x97: 2,
    0x98: 1, 0x99: 3, 0x9A: 1, 0x9B: 1, 0x9C: 2, 0x9D: 3, 0x9E: 3, 0x9F: 3,
    0xA0: 2, 0xA1: 2, 0xA2: 2, 0xA3: 2, 0xA4: 2, 0xA5: 2, 0xA6: 2, 0xA7: 2,
    0xA8: 1, 0xA9: 2, 0xAA: 1, 0xAB: 1, 0xAC: 2, 0xAD: 3, 0xAE: 3, 0xAF: 3,
    0xB0: 2, 0xB1: 2, 0xB2: 2, 0xB3: 2, 0xB4: 2, 0xB5: 2, 0xB6: 2, 0xB7: 2,
    0xB8: 1, 0xB9: 3, 0xBA: 1, 0xBB: 1, 0xBC: 2, 0xBD: 3, 0xBE: 3, 0xBF: 3,
    0xC0: 2, 0xC1: 2, 0xC2: 2, 0xC3: 2, 0xC4: 2, 0xC5: 2, 0xC6: 2, 0xC7: 2,
    0xC8: 1, 0xC9: 2, 0xCA: 1, 0xCB: 1, 0xCC: 2, 0xCD: 3, 0xCE: 3, 0xCF: 3,
    0xD0: 2, 0xD1: 2, 0xD2: 2, 0xD3: 2, 0xD4: 2, 0xD5: 2, 0xD6: 2, 0xD7: 2,
    0xD8: 1, 0xD9: 3, 0xDA: 1, 0xDB: 1, 0xDC: 2, 0xDD: 3, 0xDE: 3, 0xDF: 3,
    0xE0: 1, 0xE1: 2, 0xE2: 2, 0xE3: 2, 0xE4: 2, 0xE5: 2, 0xE6: 2, 0xE7: 2,
    0xE8: 1, 0xE9: 2, 0xEA: 1, 0xEB: 1, 0xEC: 2, 0xED: 3, 0xEE: 3, 0xEF: 3,
    0xF0: 2, 0xF1: 2, 0xF2: 2, 0xF3: 2, 0xF4: 2, 0xF5: 2, 0xF6: 2, 0xF7: 2,
    0xF8: 1, 0xF9: 3, 0xFA: 1, 0xFB: 1, 0xFC: 2, 0xFD: 3, 0xFE: 3, 0xFF: 3,
}


def analyze_code_region(rom_data, start, end, mapping):
    """Analyze if a region contains code."""
    region = rom_data[start:end]
    if len(region) < 16:
        return 0, 0
    
    # Check opcode density
    valid_ops = 0
    total_ops = 0
    i = 0
    max_check = min(256, len(region))
    
    while i < max_check - 1:
        opcode = region[i]
        if opcode in OPCODES_65816:
            length = OPCODES_65816[opcode]
            if i + length <= len(region):
                valid_ops += 1
                total_ops += 1
                i += length
            else:
                break
        else:
            total_ops += 1
            i += 1
    
    if total_ops == 0:
        return 0, calculate_entropy(region)
    
    opcode_density = valid_ops / total_ops
    entropy = calculate_entropy(region)
    
    return opcode_density, entropy


def classify_regions(rom_data, mapping):
    """Classify all regions in ROM."""
    regions = []
    rom = rom_data
    
    # Fixed window size for scanning
    window = 0x200  # 512 bytes
    
    i = 0
    while i < len(rom) - window:
        region_data = rom[i:i+window]
        entropy = calculate_entropy(region_data)
        opcode_density, _ = analyze_code_region(rom, i, i+window, mapping)
        
        # Classify
        if opcode_density > 0.70:
            region_type = "code"
        elif entropy < 3.0:
            region_type = "graphics"
        elif entropy > 7.0:
            region_type = "compressed"
        else:
            region_type = "data"
        
        regions.append({
            "start": i,
            "end": i + window,
            "type": region_type,
            "entropy": round(entropy, 2),
            "opcode_density": round(opcode_density, 2)
        })
        
        i += window
    
    # Merge consecutive regions of same type
    merged = []
    for r in regions:
        if merged and merged[-1]["type"] == r["type"]:
            merged[-1]["end"] = r["end"]
            merged[-1]["size"] = merged[-1]["end"] - merged[-1]["start"]
        else:
            r["size"] = r["end"] - r["start"]
            merged.append(r)
    
    return merged


def extract_regions(rom_data, regions, region_type, outdir):
    """Extract specific region type to files."""
    extracted = []
    type_dir = outdir / region_type
    type_dir.mkdir(parents=True, exist_ok=True)
    
    for i, region in enumerate(regions):
        if region["type"] != region_type:
            continue
        
        start = region["start"]
        end = region["end"]
        data = rom_data[start:end]
        
        filename = f"{region_type}_{start:06X}_{end:06X}.bin"
        filepath = type_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(data)
        
        extracted.append({
            "filename": filename,
            "start": start,
            "end": end,
            "size": len(data),
            "entropy": region["entropy"],
            "filepath": str(filepath)
        })
    
    return extracted


def extract_graphics_blocks(rom_data, candidates_json, outdir):
    """Extract compressed blocks that are likely graphics."""
    gfx_dir = outdir / "graphics"
    gfx_dir.mkdir(parents=True, exist_ok=True)
    
    # Load candidates if available
    if candidates_json and os.path.exists(candidates_json):
        with open(candidates_json) as f:
            data = json.load(f)
        candidates = data.get("candidates", [])
    else:
        candidates = []
    
    # Also scan for tile-like patterns
    extracted = []
    
    # Extract known compressed blocks
    for i, c in enumerate(candidates):
        if not c.get("success", False):
            continue
        
        # Check if it looks like graphics
        if c.get("looks_like_tiles", False):
            offset = c["offset_int"]
            size = c["decompressed_size"]
            
            # Find the decompressed file
            decompressed_file = f"decompressed_{offset:06X}.bin"
            source = os.path.join(os.path.dirname(candidates_json), decompressed_file)
            
            if os.path.exists(source):
                dest = gfx_dir / f"gfx_{offset:06X}_{size:04X}.bin"
                with open(source, "rb") as src:
                    with open(dest, "wb") as dst:
                        dst.write(src.read())
                
                extracted.append({
                    "filename": dest.name,
                    "offset": offset,
                    "size": size,
                    "type": "compressed_graphics"
                })
    
    return extracted


def main():
    parser = argparse.ArgumentParser(description="B.O.B. ROM Extraction Tool")
    parser.add_argument("--rom", required=True, help="Path to ROM file")
    parser.add_argument("--type", choices=["code", "data", "graphics", "all"], default="all", help="Type to extract")
    parser.add_argument("--outdir", default="data/extracted", help="Output directory")
    parser.add_argument("--candidates", help="Path to candidates.json (for graphics)")
    
    args = parser.parse_args()
    
    # Load ROM
    with open(args.rom, "rb") as f:
        rom_data = f.read()
    
    header_offset, mapping, title = detect_rom_header(rom_data)
    rom = rom_data[header_offset:]
    
    print(f"ROM: {title}")
    print(f"Size: {len(rom_data):,} bytes")
    print(f"Mapping: {mapping}")
    print(f"Header offset: {header_offset}")
    print()
    
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    
    # Classify regions
    print("Classifying regions...")
    regions = classify_regions(rom, mapping)
    
    # Count types
    type_counts = {}
    for r in regions:
        t = r["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"Found: {type_counts}")
    print()
    
    # Extract requested types
    if args.type in ("code", "all"):
        print("Extracting code regions...")
        code_extracted = extract_regions(rom, regions, "code", outdir)
        print(f"  Extracted {len(code_extracted)} code regions")
    
    if args.type in ("data", "all"):
        print("Extracting data regions...")
        data_extracted = extract_regions(rom, regions, "data", outdir)
        print(f"  Extracted {len(data_extracted)} data regions")
    
    if args.type in ("graphics", "all"):
        print("Extracting graphics regions...")
        gfx_extracted = extract_regions(rom, regions, "graphics", outdir)
        print(f"  Extracted {len(gfx_extracted)} graphics regions")
        
        # Also extract compressed graphics blocks
        if args.candidates:
            compressed_gfx = extract_graphics_blocks(rom, args.candidates, outdir)
            print(f"  Extracted {len(compressed_gfx)} compressed graphics blocks")
    
    # Save classification map
    classification = {
        "rom_file": args.rom,
        "rom_size": len(rom_data),
        "mapping": mapping,
        "header_offset": header_offset,
        "regions": regions,
        "type_counts": type_counts
    }
    
    with open(outdir / "classification.json", "w") as f:
        json.dump(classification, f, indent=2)
    
    print()
    print(f"Extraction complete! Output in: {outdir}")
    print(f"Classification saved to: {outdir / 'classification.json'}")


if __name__ == "__main__":
    main()
