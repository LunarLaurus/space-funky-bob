"""
Palette Loader for Space Funky B.O.B.

Loads background and sprite palettes from ROM.
Source-verified: 13 background palettes from INITLEVE.A:bgpalletes table.
"""

from .rom_reader import ROMReader

# Background palette offsets from INITLEVE.A:bgpalletes
BG_PALETTE_OFFSETS = [
    0x000000,  # borgpal11
    0x000010,  # bugpal
    0x000020,  # queenpal
    0x000030,  # titlepal
    0x000040,  # ancientpal
    0x000050,  # invenpal
    0x000060,  # lavapal
    0x000070,  # intropal
    0x000080,  # ultrapal11
    0x000090,  # bubpal
    0x0000A0,  # worldpal
    0x0000B0,  # worldpal2
    0x0000C0,  # worldpal3
]

PALETTE_NAMES = [
    'borgpal11', 'bugpal', 'queenpal', 'titlepal', 'ancientpal',
    'invenpal', 'lavapal', 'intropal', 'ultrapal11', 'bubpal',
    'worldpal', 'worldpal2', 'worldpal3'
]

# SNES color format: RGB555 (15-bit color)
# Bit layout: 0BBBBBGG GGGRRRRR


class PaletteLoader:
    """Load palettes from B.O.B. ROM."""
    
    def __init__(self, rom_reader=None):
        """
        Initialize palette loader.
        
        Args:
            rom_reader: ROMReader instance or None
        """
        self.rom_reader = rom_reader
        self._palette_cache = {}
    
    def load_palette(self, palette_index):
        """
        Load background palette by index.
        
        Args:
            palette_index: Palette index (0-12)
        
        Returns:
            list: 16 RGB color tuples or None if not found
        """
        if palette_index < 0 or palette_index > 12:
            return None
        
        # Check cache
        if palette_index in self._palette_cache:
            return self._palette_cache[palette_index]
        
        if self.rom_reader is None:
            return None
        
        # Get palette offset
        offset = BG_PALETTE_OFFSETS[palette_index]
        
        # Read 16 colors (32 bytes, 2 bytes per color)
        data = self.rom_reader.read_bytes(offset, 32)
        if data is None:
            return None
        
        # Parse SNES RGB555 colors
        colors = []
        for i in range(16):
            color_low = data[i * 2]
            color_high = data[i * 2 + 1]
            color = color_low | (color_high << 8)
            
            # Extract RGB components (5 bits each)
            r = (color & 0x001F) << 3  # Scale to 8-bit
            g = ((color & 0x03E0) >> 5) << 3
            b = ((color & 0x7C00) >> 10) << 3
            
            colors.append((r, g, b))
        
        self._palette_cache[palette_index] = colors
        return colors
    
    def load_all_palettes(self):
        """
        Load all 13 background palettes.
        
        Returns:
            dict: Palette data with names and colors
        """
        palettes = {
            'metadata': {
                'total_palettes': 13,
                'source': 'INITLEVE.A:bgpalletes',
                'format': 'SNES RGB555 (15-bit)',
                'colors_per_palette': 16
            },
            'palettes': []
        }
        
        for i in range(13):
            colors = self.load_palette(i)
            palettes['palettes'].append({
                'index': i,
                'name': PALETTE_NAMES[i],
                'offset': f'0x{BG_PALETTE_OFFSETS[i]:06X}',
                'colors': colors if colors else []
            })
        
        return palettes
    
    def snes_color_to_rgb(self, snes_color):
        """
        Convert SNES RGB555 color to RGB tuple.
        
        Args:
            snes_color: 16-bit SNES color value
        
        Returns:
            tuple: (r, g, b) 8-bit values
        """
        r = (snes_color & 0x001F) << 3
        g = ((snes_color & 0x03E0) >> 5) << 3
        b = ((snes_color & 0x7C00) >> 10) << 3
        return (r, g, b)
    
    def rgb_to_snes_color(self, r, g, b):
        """
        Convert RGB tuple to SNES RGB555 color.
        
        Args:
            r, g, b: 8-bit color values
        
        Returns:
            int: 16-bit SNES color value
        """
        # Scale down to 5 bits
        r5 = r >> 3
        g5 = g >> 3
        b5 = b >> 3
        
        return r5 | (g5 << 5) | (b5 << 10)
    
    def get_palette_info(self):
        """
        Get palette information without loading colors.
        
        Returns:
            dict: Palette metadata
        """
        return {
            'metadata': {
                'total_palettes': 13,
                'source': 'INITLEVE.A:bgpalletes'
            },
            'palettes': [
                {
                    'index': i,
                    'name': PALETTE_NAMES[i],
                    'offset': f'0x{BG_PALETTE_OFFSETS[i]:06X}'
                }
                for i in range(13)
            ]
        }
