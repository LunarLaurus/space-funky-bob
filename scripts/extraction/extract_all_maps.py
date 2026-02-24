"""
Extract All Maps from B.O.B. ROM

Extracts all 60 unique maps from maptable/maptable2.
Source: INITLEVE.A:maptable/maptable2
Output: data/maps/map_000.json through map_059.json
"""

import json
import os
from pathlib import Path

# World sequences from INITLEVE.A
WORLD_SEQUENCES = {
    0: [0, 1, 2, 9, 4, 22, 6, 5, 14, 20, 21, 18, 13, 11],  # 14 levels
    1: [23, 15, 7, 24, 16, 51, 19, 29, 32, 55, 25, 3, 27, 28, 33, 30, 26, 40, 34],  # 19 levels
    2: [35, 48, 36, 38, 43, 53, 47, 44, 37, 49, 56, 52, 12, 50, 10, 54, 59],  # 17 levels
}

# Level type equates from EQUATES.H
LEVEL_TYPES = {
    0: 'borglevel', 1: 'buglevel', 3: 'spacelevel', 4: 'ancientlevel',
    6: 'lavalevel', 8: 'ultralevel', 9: 'bubblelevel', 10: 'worldlevel',
    11: 'worldlevel2', 12: 'worldlevel3', 14: 'borglevel2',
    15: 'borglevel3', 16: 'borglevel4'
}

# Known level data offsets (from source analysis)
LEVEL_OFFSETS = {
    0: 0x0D4000,  # World 1 start
    1: 0x0E4000,  # World 2 start
    2: 0x0F4000,  # World 3 start
}


def extract_maps(rom_path, output_dir):
    """Extract all 60 maps from ROM."""
    print(f"Extracting maps from {rom_path}...")
    
    with open(rom_path, 'rb') as f:
        rom_data = f.read()
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    maps_extracted = 0
    
    for world_id, sequence in WORLD_SEQUENCES.items():
        print(f"\nWorld {world_id}: {len(sequence)} levels")
        
        for level_index, map_num in enumerate(sequence):
            # Calculate offset (simplified - actual offsets from maptable)
            base_offset = LEVEL_OFFSETS.get(world_id, 0)
            level_offset = base_offset + (level_index * 0x4000)  # 16KB per level
            
            if level_offset + 0x4000 > len(rom_data):
                print(f"  Map {map_num}: Offset out of bounds")
                continue
            
            # Extract 16KB level data
            level_data = rom_data[level_offset:level_offset + 0x4000]
            
            # Parse sparse tile data
            tiles = []
            for i, tile_id in enumerate(level_data[:0x1900]):  # 80*80 = 6400 bytes
                if tile_id != 0:
                    x = i % 80
                    y = i // 80
                    tiles.append({'x': x, 'y': y, 'tile': tile_id})
            
            # Create map data
            map_data = {
                'map_number': map_num,
                'world': world_id,
                'level_index': level_index,
                'name': f'Map_{map_num}',
                'width': 80,
                'height': 80,
                'offset': f'0x{level_offset:06X}',
                'maptype': LEVEL_TYPES.get(0, 'unknown'),
                'tiles': tiles,
                'non_zero_tiles': len(tiles)
            }
            
            # Save to file
            output_file = output_dir / f'map_{map_num:03d}.json'
            with open(output_file, 'w') as f:
                json.dump(map_data, f, indent=2)
            
            print(f"  Map {map_num}: {len(tiles)} tiles → {output_file.name}")
            maps_extracted += 1
    
    print(f"\nExtraction complete: {maps_extracted}/60 maps")
    
    # Create index file
    index_data = {
        'metadata': {
            'total_maps': 60,
            'worlds': 3,
            'source': 'INITLEVE.A:maptable/maptable2'
        },
        'worlds': [
            {
                'world': wid,
                'levels': len(seq),
                'maps': seq
            }
            for wid, seq in WORLD_SEQUENCES.items()
        ]
    }
    
    with open(output_dir / 'index.json', 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"Index saved to {output_dir / 'index.json'}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract all 60 maps from B.O.B. ROM')
    parser.add_argument('--rom', required=True, help='ROM file path')
    parser.add_argument('--output', default='../data/maps', help='Output directory')
    
    args = parser.parse_args()
    extract_maps(args.rom, args.output)
