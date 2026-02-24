"""
Extract Tilesets with Palettes from B.O.B. ROM

Extracts all 12 tileset types with palette assignments.
Source: INITLEVE.A:blocksets, bgpalletes
Output: data/tilesets_enhanced/
"""

import json
from pathlib import Path

# All 12 tileset types from EQUATES.H and INITLEVE.A
TILESET_DATA = {
    'borg': {'offset': '0x008000', 'bank': 3, 'palette': 0},
    'bug': {'offset': '0x008800', 'bank': 3, 'palette': 1},
    'ancient': {'offset': '0x009000', 'bank': 11, 'palette': 4},
    'lava': {'offset': '0x009800', 'bank': 9, 'palette': 6},
    'ultra': {'offset': '0x00A000', 'bank': 22, 'palette': 8},
    'bubble': {'offset': '0x00A800', 'bank': 4, 'palette': 9},
    'borg2': {'offset': '0x00B000', 'bank': 18, 'palette': 0},
    'borg3': {'offset': '0x00B800', 'bank': 15, 'palette': 0},
    'world': {'offset': '0x00C000', 'bank': 18, 'palette': 10},
    'borg4': {'offset': '0x00C800', 'bank': 17, 'palette': 0},
    'main_graphics_1': {'offset': '0x035800', 'bank': None, 'palette': None},
    'main_graphics_2': {'offset': '0x03D800', 'bank': None, 'palette': None},
}

# 13 background palettes from INITLEVE.A:bgpalletes
PALETTE_NAMES = [
    'borgpal11', 'bugpal', 'queenpal', 'titlepal', 'ancientpal',
    'invenpal', 'lavapal', 'intropal', 'ultrapal11', 'bubpal',
    'worldpal', 'worldpal2', 'worldpal3'
]


def extract_tilesets(output_dir):
    """Extract tileset metadata with palette assignments."""
    print("Extracting tileset data...")
    
    output_dir = Path(output_dir) / 'tilesets_enhanced'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create tileset index
    tileset_index = {
        'metadata': {
            'total_tilesets': 12,
            'source': 'INITLEVE.A:blocksets',
            'format': 'SNES 4bpp (8x8 pixels, 16 colors)',
            'bytes_per_tile': 32,
            'tiles_per_8kb': 256
        },
        'palettes': {
            'total': 13,
            'source': 'INITLEVE.A:bgpalletes',
            'names': PALETTE_NAMES
        },
        'tilesets': []
    }
    
    for name, data in TILESET_DATA.items():
        tileset_info = {
            'id': name,
            'rom_offset': data['offset'],
            'bank': data['bank'],
            'palette_index': data['palette'],
            'palette_name': PALETTE_NAMES[data['palette']] if data['palette'] else None,
            'music_theme': get_music_theme(name)
        }
        tileset_index['tilesets'].append(tileset_info)
    
    # Save index
    output_file = output_dir / 'index.json'
    with open(output_file, 'w') as f:
        json.dump(tileset_index, f, indent=2)
    
    print(f"Extracted 12 tilesets to {output_file}")
    return tileset_index


def get_music_theme(tileset_name):
    """Get music theme for tileset (from EQUATES.H)."""
    themes = {
        'borg': 'borgtheme', 'borg2': 'borgtheme', 'borg3': 'borgtheme',
        'borg4': 'borgtheme', 'bug': 'bugtheme', 'bubble': 'bugtheme',
        'ancient': 'anctheme', 'lava': 'anctheme', 'ultra': 'ultratheme',
        'world': 'borgtheme', 'main_graphics_1': 'borgtheme',
        'main_graphics_2': 'borgtheme'
    }
    return themes.get(tileset_name, 'unknown')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract tilesets from B.O.B.')
    parser.add_argument('--output', default='../data', help='Output directory')
    
    args = parser.parse_args()
    extract_tilesets(args.output)
