#!/usr/bin/env python3
"""
bob_extract_levels.py - Extract level tilemaps from B.O.B. ROM

Usage:
    python bob_extract_levels.py --rom "rom/B.O.B..smc" --outdir data/levels
"""

import argparse
import struct
from pathlib import Path


def find_tilemaps(rom_data):
    """Find all potential tilemaps in the ROM."""
    tilemaps = []
    
    # Scan common tilemap locations
    for base in range(0x020000, 0x100000, 0x10000):
        for offset in [0x8000, 0x8800, 0x9000, 0x9800, 0xA000, 0xA800, 0xB000, 0xB800, 0xC000, 0xC800]:
            addr = base + offset
            if addr + 0x800 > len(rom_data):
                continue
            
            chunk = rom_data[addr:addr+0x800]
            
            tiles = [(chunk[i+1] << 8) | chunk[i] for i in range(0, 0x800, 2)]
            nonzero = sum(1 for t in tiles if t != 0)
            
            if nonzero < 100:
                continue
            
            unique = len(set(tiles[:128]))
            if unique < 10 or unique > 300:
                continue
            
            valid_ids = sum(1 for t in tiles if (t & 0x3FF) < 0x300)
            has_attrs = sum(1 for t in tiles if (t & 0xFC00) != 0)
            
            if valid_ids > 50 and has_attrs > 20:
                tilemaps.append({
                    'offset': addr,
                    'nonzero': nonzero,
                    'unique': unique,
                    'has_attrs': has_attrs
                })
    
    return tilemaps


def parse_tilemap(tilemap_data):
    """Parse tilemap into structured format."""
    tiles = []
    for i in range(0, len(tilemap_data), 2):
        val = (tilemap_data[i+1] << 8) | tilemap_data[i]
        tile_id = val & 0x3FF
        chr_bank = (val >> 10) & 0x3
        palette = (val >> 12) & 0x3
        x_flip = (val >> 14) & 1
        y_flip = (val >> 15) & 1
        
        tiles.append({
            'raw': val,
            'id': tile_id,
            'chr_bank': chr_bank,
            'palette': palette,
            'x_flip': x_flip,
            'y_flip': y_flip
        })
    
    return tiles


def extract_levels(rom_path, outdir):
    """Extract all level tilemaps from ROM."""
    rom_data = Path(rom_path).read_bytes()
    
    print(f"ROM: {len(rom_data):,} bytes")
    
    tilemaps = find_tilemaps(rom_data)
    print(f"Found {len(tilemaps)} tilemaps")
    
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    
    extracted = []
    for i, tm in enumerate(tilemaps):
        addr = tm['offset']
        data = rom_data[addr:addr+0x800]
        
        # Save raw tilemap
        filename = f"tilemap_{i:02d}_{addr:06X}.bin"
        filepath = outdir / filename
        filepath.write_bytes(data)
        
        # Save parsed JSON
        tiles = parse_tilemap(data)
        import json
        
        json_data = {
            'offset': addr,
            'size': 0x800,
            'format': '16-bit SNES tilemap',
            'grid': '32x32',
            'tiles': tiles
        }
        
        json_path = outdir / f"tilemap_{i:02d}_{addr:06X}.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        extracted.append({
            'index': i,
            'offset': addr,
            'filename': filename,
            'nonzero': tm['nonzero'],
            'unique': tm['unique']
        })
        
        print(f"  Extracted: {filename}")
    
    # Save index
    import json
    with open(outdir / 'index.json', 'w') as f:
        json.dump(extracted, f, indent=2)
    
    print(f"\nExtracted {len(extracted)} tilemaps to {outdir}")
    return extracted


def main():
    parser = argparse.ArgumentParser(description="Extract level tilemaps from B.O.B. ROM")
    parser.add_argument("--rom", required=True, help="Path to ROM file")
    parser.add_argument("--outdir", default="data/levels", help="Output directory")
    args = parser.parse_args()
    
    extract_levels(args.rom, args.outdir)


if __name__ == "__main__":
    main()
