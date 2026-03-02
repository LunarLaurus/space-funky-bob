"""
Tileset Handler for Space Funky B.O.B. Level Editor

Handles GET /tileset/:name, GET /tilesets, GET /palette/:index endpoints.
Source-verified: 12 tileset types from INITLEVE.A:blocksets table.
"""

import json
import os

# All 12 tileset types from EQUATES.H and INITLEVE.A
TILESET_OFFSETS = {
    'borg': 0x008000,       # borgblocks (Bank 3)
    'bug': 0x008800,        # bugblocks (Bank 3)
    'ancient': 0x009000,    # ancientblocks (Bank 11)
    'lava': 0x009800,       # lavablocks (Bank 9)
    'ultra': 0x00A000,      # ultrablocks (Bank 22)
    'bubble': 0x00A800,     # bubblocks (Bank 4) - NEW
    'borg2': 0x00B000,      # borgblocks2 (Bank 18) - NEW
    'borg3': 0x00B800,      # borgblocks3 (Bank 15) - NEW
    'world': 0x00C000,      # worldblocks (Bank 18) - NEW
    'borg4': 0x00C800,      # borgblocks4/doorblocks (Bank 17) - NEW
    'main_graphics_1': 0x035800,
    'main_graphics_2': 0x03D800,
    # Auto-detected tilesets from extraction
    '008600': 0x008600,
    '009600': 0x009600,
    '00AC00': 0x00AC00,
    '00B900': 0x00B900,
    '010000': 0x010000,
    '035C00': 0x035C00,
    '036F00': 0x036F00,
    '0FAA00': 0x0FAA00,
}

# Background palettes from INITLEVE.A:bgpalletes (13 palettes)
PALETTE_INDICES = {
    0: 'borgpal11',
    1: 'bugpal',
    2: 'queenpal',
    3: 'titlepal',
    4: 'ancientpal',
    5: 'invenpal',
    6: 'lavapal',
    7: 'intropal',
    8: 'ultrapal11',
    9: 'bubpal',
    10: 'worldpal',
    11: 'worldpal2',
    12: 'worldpal3'
}

# Music theme sharing from EQUATES.H
MUSIC_THEMES = {
    'borg': 'borgtheme',       # Theme 3
    'bug': 'bugtheme',         # Theme 4 (shared with Bubble)
    'ancient': 'anctheme',     # Theme 5 (shared with Lava)
    'lava': 'anctheme',        # Theme 5 (shared with Ancient)
    'ultra': 'ultratheme',     # Theme 6
    'bubble': 'bugtheme',      # Theme 4 (shared with Bug)
    'world': 'borgtheme',      # Theme 3
    'borg2': 'borgtheme',
    'borg3': 'borgtheme',
    'borg4': 'borgtheme',
    'main_graphics_1': 'borgtheme',
    'main_graphics_2': 'borgtheme'
}


class TilesetHandler:
    """Handle tileset-related API requests."""
    
    def __init__(self, data_dir, rom_path=None):
        """
        Initialize with data directory and optional ROM path.
        
        Args:
            data_dir: Directory containing tileset data files
            rom_path: Path to ROM file for direct reading
        """
        self.data_dir = data_dir
        self.rom_path = rom_path
        self._tileset_cache = {}
    
    def get_all_tilesets(self):
        """
        Get list of all available tilesets.
        
        Returns:
            dict: Tileset list with offsets and metadata
        """
        tilesets = {
            'metadata': {
                'total_tilesets': 12,
                'format': 'SNES 4bpp (8x8 pixels, 16 colors)',
                'bytes_per_tile': 32,
                'tiles_per_8kb': 256
            },
            'tilesets': []
        }
        
        for name, offset in TILESET_OFFSETS.items():
            tileset_info = {
                'name': name,
                'rom_offset': f'0x{offset:06X}',
                'music_theme': MUSIC_THEMES.get(name, 'unknown'),
                'available': False
            }
            
            # Check if tileset data file exists
            tileset_file = os.path.join(self.data_dir, 'tilesets', f'tileset_{name}.json')
            if os.path.exists(tileset_file):
                tileset_info['available'] = True
                tileset_info['data_file'] = f'tileset_{name}.json'
            
            # Check if PNG exists
            png_file = os.path.join(self.data_dir, 'tilesets', f'tileset_{name}.png')
            if os.path.exists(png_file):
                tileset_info['image_file'] = f'tileset_{name}.png'
            
            tilesets['tilesets'].append(tileset_info)
        
        return tilesets
    
    def get_tileset(self, tileset_name):
        """
        Get specific tileset data by name.

        Args:
            tileset_name: Tileset identifier (e.g., 'borg', 'bug', 'ancient')

        Returns:
            dict: Tileset data or None if not found
        """
        # Check cache first
        if tileset_name in self._tileset_cache:
            return self._tileset_cache[tileset_name]

        # Validate tileset name
        if tileset_name not in TILESET_OFFSETS:
            return None

        # Map tileset names to their hex offset filenames
        name_to_hex = {
            'borg': '008000',
            'bug': '008800',
            'ancient': '009000',
            'lava': '009800',
            'ultra': '00A000',
            'bubble': '00A800',
            'borg2': '00B000',
            'borg3': '00B800',
            'world': '00C000',
            'borg4': '00C800',
            'main_graphics_1': 'main_graphics_1',
            'main_graphics_2': 'main_graphics_2',
            # Auto-detected tilesets use their hex names directly
            '008600': '008600',
            '009600': '009600',
            '00AC00': '00AC00',
            '00B900': '00B900',
            '010000': '010000',
            '035C00': '035C00',
            '036F00': '036F00',
            '0FAA00': '0FAA00'
        }
        
        hex_name = name_to_hex.get(tileset_name, tileset_name)

        # Try to load from file (using hex offset filename)
        tileset_file = os.path.join(self.data_dir, 'tilesets', f'tileset_{hex_name}.json')
        if os.path.exists(tileset_file):
            with open(tileset_file, 'r') as f:
                tileset_data = json.load(f)
                tileset_data['rom_offset'] = f'0x{TILESET_OFFSETS[tileset_name]:06X}'
                tileset_data['music_theme'] = MUSIC_THEMES.get(tileset_name, 'unknown')
                self._tileset_cache[tileset_name] = tileset_data
                return tileset_data

        # Return metadata if no file exists
        return {
            'name': tileset_name,
            'rom_offset': f'0x{TILESET_OFFSETS[tileset_name]:06X}',
            'music_theme': MUSIC_THEMES.get(tileset_name, 'unknown'),
            'error': 'Tileset data not found'
        }
    
    def get_palette(self, palette_index):
        """
        Get palette by index from ROM.
        
        Args:
            palette_index: Palette index (0-12)
        
        Returns:
            dict: Palette data or None if not found
        """
        if palette_index not in PALETTE_INDICES:
            return None
        
        palette_name = PALETTE_INDICES[palette_index]
        
        # Try to load from file
        palette_file = os.path.join(self.data_dir, 'palettes', f'palette_{palette_index:02d}.json')
        if os.path.exists(palette_file):
            with open(palette_file, 'r') as f:
                palette_data = json.load(f)
                palette_data['index'] = palette_index
                palette_data['name'] = palette_name
                return palette_data
        
        # Return placeholder if no file exists
        return {
            'index': palette_index,
            'name': palette_name,
            'colors': [],
            'error': 'Palette not loaded from ROM yet'
        }
    
    def get_all_palettes(self):
        """
        Get list of all available palettes.
        
        Returns:
            dict: Palette list with indices and names
        """
        return {
            'metadata': {
                'total_palettes': 13,
                'source': 'INITLEVE.A:bgpalletes'
            },
            'palettes': [
                {
                    'index': idx,
                    'name': name
                }
                for idx, name in PALETTE_INDICES.items()
            ]
        }
    
    def get_tileset_custom(self, offset):
        """
        Get tileset at custom ROM offset.
        
        Args:
            offset: ROM offset (hex string or int)
        
        Returns:
            dict: Tileset data at specified offset
        """
        if isinstance(offset, str):
            try:
                offset = int(offset, 16)
            except ValueError:
                return {'error': 'Invalid offset format'}
        
        return {
            'rom_offset': f'0x{offset:06X}',
            'note': 'Custom offset - use extract_tilesets_enhanced.py to extract'
        }
