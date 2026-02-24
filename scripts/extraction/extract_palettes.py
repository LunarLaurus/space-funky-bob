"""
Extract Palettes from B.O.B. ROM

Extracts 13 background palettes from INITLEVE.A:bgpalletes.
Output: data/palettes.json
"""

import json
from pathlib import Path

# 13 background palettes from INITLEVE.A:bgpalletes
PALETTE_DATA = {
    0: {'name': 'borgpal11', 'offset': '0x000000'},
    1: {'name': 'bugpal', 'offset': '0x000010'},
    2: {'name': 'queenpal', 'offset': '0x000020'},
    3: {'name': 'titlepal', 'offset': '0x000030'},
    4: {'name': 'ancientpal', 'offset': '0x000040'},
    5: {'name': 'invenpal', 'offset': '0x000050'},
    6: {'name': 'lavapal', 'offset': '0x000060'},
    7: {'name': 'intropal', 'offset': '0x000070'},
    8: {'name': 'ultrapal11', 'offset': '0x000080'},
    9: {'name': 'bubpal', 'offset': '0x000090'},
    10: {'name': 'worldpal', 'offset': '0x0000A0'},
    11: {'name': 'worldpal2', 'offset': '0x0000B0'},
    12: {'name': 'worldpal3', 'offset': '0x0000C0'},
}


def extract_palettes(rom_path, output_dir):
    """Extract palettes from ROM."""
    print(f"Extracting palettes from {rom_path}...")
    
    with open(rom_path, 'rb') as f:
        rom_data = f.read()
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    palettes = {
        'metadata': {
            'total_palettes': 13,
            'source': 'INITLEVE.A:bgpalletes',
            'format': 'SNES RGB555 (15-bit)',
            'colors_per_palette': 16
        },
        'palettes': []
    }
    
    for idx, data in PALETTE_DATA.items():
        # Read palette data from ROM (32 bytes = 16 colors * 2 bytes)
        offset = int(data['offset'], 16)
        palette_bytes = rom_data[offset:offset + 32]
        
        # Parse SNES RGB555 colors
        colors = []
        for i in range(16):
            if i * 2 + 1 < len(palette_bytes):
                color_low = palette_bytes[i * 2]
                color_high = palette_bytes[i * 2 + 1]
                color = color_low | (color_high << 8)
                
                r = (color & 0x001F) << 3
                g = ((color & 0x03E0) >> 5) << 3
                b = ((color & 0x7C00) >> 10) << 3
                
                colors.append({'r': r, 'g': g, 'b': b, 'hex': f'#{r:02X}{g:02X}{b:02X}'})
        
        palettes['palettes'].append({
            'index': idx,
            'name': data['name'],
            'offset': data['offset'],
            'colors': colors
        })
    
    # Save palettes
    output_file = output_dir / 'palettes.json'
    with open(output_file, 'w') as f:
        json.dump(palettes, f, indent=2)
    
    print(f"Extracted 13 palettes to {output_file}")
    return palettes


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract palettes from B.O.B. ROM')
    parser.add_argument('--rom', required=True, help='ROM file path')
    parser.add_argument('--output', default='../data', help='Output directory')
    
    args = parser.parse_args()
    extract_palettes(args.rom, args.output)
