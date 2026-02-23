#!/usr/bin/env python3
"""
bob_graphics.py — B.O.B. ROM Graphics Renderer (Consolidated)

Unified graphics module for SNES tile rendering and graphics analysis.
Consolidates bob_graphics.py, bob_graphics_v2.py, bob_graphics_classifier.py.

Usage:
    # Render a single file
    python toolkit/bob_graphics.py --input data/decompressed_0A0000.bin --output data/gfx_png
    
    # Render all decompressed files
    python toolkit/bob_graphics.py --all

Output:
    PNG images of rendered tiles/sprites in multiple formats
"""

import argparse
import os
import warnings
from pathlib import Path
from PIL import Image, ImageDraw
import json
from typing import List, Optional, Tuple, Dict, Any


# =============================================================================
# SNES Tile Rendering Functions
# =============================================================================

def render_snes_tile_2bpp(data: bytes, offset: int, width: int = 8, height: int = 8) -> Optional[List[int]]:
    """
    Render SNES 2bpp tile (4 colors, 16 bytes per tile).
    
    Args:
        data: Source data containing tile
        offset: Offset in data where tile begins
        width: Tile width (default 8)
        height: Tile height (default 8)
    
    Returns:
        List of pixel values (0-3) or None if insufficient data
    """
    if offset + (width * height // 4) > len(data):
        return None
    
    tile = []
    for y in range(height):
        row_offset = offset + y * 2
        if row_offset + 1 >= len(data):
            break
        b1, b2 = data[row_offset], data[row_offset + 1]
        for x in range(width):
            bit0 = (b1 >> (7 - x)) & 1
            bit1 = (b2 >> (7 - x)) & 1
            pixel = (bit1 << 1) | bit0
            tile.append(pixel)
    return tile


def render_snes_tile_4bpp(data: bytes, offset: int, width: int = 8, height: int = 8) -> Optional[List[int]]:
    """
    Render SNES 4bpp tile (16 colors, 32 bytes per tile).
    
    Args:
        data: Source data containing tile
        offset: Offset in data where tile begins
        width: Tile width (default 8)
        height: Tile height (default 8)
    
    Returns:
        List of pixel values (0-15) or None if insufficient data
    """
    if offset + 32 > len(data):
        return None
    
    tile = []
    for y in range(height):
        row_offset = offset + y * 4
        if row_offset + 3 >= len(data):
            break
        b1, b2, b3, b4 = data[row_offset:row_offset + 4]
        for x in range(width):
            bit0 = (b1 >> (7 - x)) & 1
            bit1 = (b2 >> (7 - x)) & 1
            bit2 = (b3 >> (7 - x)) & 1
            bit3 = (b4 >> (7 - x)) & 1
            pixel = (bit3 << 3) | (bit2 << 2) | (bit1 << 1) | bit0
            tile.append(pixel)
    return tile


def render_snes_tile_8bpp(data: bytes, offset: int, width: int = 8, height: int = 8) -> Optional[List[int]]:
    """
    Render SNES 8bpp tile (256 colors, 64 bytes per tile).
    
    Args:
        data: Source data containing tile
        offset: Offset in data where tile begins
        width: Tile width (default 8)
        height: Tile height (default 8)
    
    Returns:
        List of pixel values (0-255) or None if insufficient data
    """
    if offset + 64 > len(data):
        return None
    
    tile = []
    for y in range(height):
        row_offset = offset + y * 8
        if row_offset + 7 >= len(data):
            break
        for x in range(width):
            pixel = data[row_offset + x]
            tile.append(pixel)
    return tile


# =============================================================================
# Palette Functions
# =============================================================================

def get_palette_2bpp_color() -> List[Tuple[int, int, int]]:
    """Get 2bpp color palette (16 colors)."""
    return [
        (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
        (0, 0, 128), (128, 0, 128), (0, 128, 128), (128, 128, 128),
        (64, 0, 0), (192, 0, 0), (64, 128, 0), (192, 128, 0),
        (0, 64, 0), (128, 64, 0), (0, 192, 0), (192, 192, 0),
    ]


def get_palette_2bpp_grayscale() -> List[Tuple[int, int, int]]:
    """Get 2bpp grayscale palette."""
    return [
        (0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)
    ]


def get_palette_4bpp() -> List[Tuple[int, int, int]]:
    """Get 4bpp palette (16 colors from RGB555-like encoding)."""
    palette = []
    for r in range(4):
        for g in range(4):
            for b in range(4):
                palette.append((r * 63, g * 63, b * 63))
    return palette[:16]


def get_palette_8bpp_grayscale() -> List[Tuple[int, int, int]]:
    """Get 8bpp grayscale palette (256 colors)."""
    return [(i, i, i) for i in range(256)]


def snes_color_to_rgb(snes_value: int) -> Tuple[int, int, int]:
    """
    Convert SNES RGB555 color value to RGB888 tuple.
    
    Args:
        snes_value: 16-bit SNES color value (BBBBBGGGGGRRRRR)
    
    Returns:
        (R, G, B) tuple with 0-255 values
    """
    r = (snes_value & 0x1F) * 255 // 31
    g = ((snes_value >> 5) & 0x1F) * 255 // 31
    b = ((snes_value >> 10) & 0x1F) * 255 // 31
    return (r, g, b)


def extract_palette(rom_data: bytes, offset: int, num_colors: int = 16) -> List[Tuple[int, int, int]]:
    """
    Extract SNES palette from ROM data.
    
    Args:
        rom_data: ROM data
        offset: Offset where palette begins
        num_colors: Number of colors to extract
    
    Returns:
        List of (R, G, B) tuples
    """
    palette = []
    for i in range(num_colors):
        if offset + i * 2 + 1 >= len(rom_data):
            break
        value = rom_data[offset + i * 2] | (rom_data[offset + i * 2 + 1] << 8)
        palette.append(snes_color_to_rgb(value))
    return palette


# =============================================================================
# Image Generation Functions
# =============================================================================

def tile_to_image(tile_data: List[int], width: int, height: int, 
                  palette: Optional[List[Tuple[int, int, int]]] = None) -> Optional[Image.Image]:
    """
    Convert tile pixel data to PIL Image.
    
    Args:
        tile_data: List of pixel indices
        width: Image width
        height: Image height
        palette: Optional palette (list of RGB tuples)
    
    Returns:
        PIL Image or None
    """
    if not tile_data or len(tile_data) != width * height:
        return None
    
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            idx = y * width + x
            if idx < len(tile_data):
                color_idx = min(tile_data[idx], len(palette) - 1) if palette else tile_data[idx]
                if palette:
                    pixels[x, y] = palette[color_idx] if color_idx < len(palette) else (0, 0, 0)
                else:
                    # Grayscale fallback
                    gray = (color_idx / max(len(tile_data) - 1, 1)) * 255
                    pixels[x, y] = (int(gray), int(gray), int(gray))
    
    return img


def render_tiles_to_sheet(tiles: List[List[int]], cols: int = 32, 
                          palette: Optional[List[Tuple[int, int, int]]] = None,
                          tile_size: int = 8, spacing: int = 1) -> Image.Image:
    """
    Render multiple tiles to a sprite sheet.
    
    Args:
        tiles: List of tile pixel arrays
        cols: Number of columns
        palette: Optional palette
        tile_size: Size of each tile
        spacing: Spacing between tiles
    
    Returns:
        PIL Image sprite sheet
    """
    rows = (len(tiles) + cols - 1) // cols
    sheet_width = cols * tile_size + (cols + 1) * spacing
    sheet_height = rows * tile_size + (rows + 1) * spacing
    
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    for idx, tile_pixels in enumerate(tiles):
        col = idx % cols
        row = idx // cols
        x = spacing + col * (tile_size + spacing)
        y = spacing + row * (tile_size + spacing)
        
        tile_img = tile_to_image(tile_pixels, tile_size, tile_size, palette)
        if tile_img:
            sheet.paste(tile_img, (x, y))
    
    return sheet


# =============================================================================
# Format Detection Functions
# =============================================================================

def detect_graphics_format(data: bytes, offset: int = 0, window_size: int = 256) -> str:
    """
    Auto-detect graphics format from data.
    
    Args:
        data: Source data
        offset: Offset to analyze
        window_size: Size of analysis window
    
    Returns:
        Format string: '2bpp', '4bpp', '8bpp', or 'unknown'
    """
    if offset + window_size > len(data):
        window_size = len(data) - offset
    
    chunk = data[offset:offset + window_size]
    
    # Calculate entropy
    freq = [0] * 256
    for byte in chunk:
        freq[byte] += 1
    
    import math
    entropy = 0.0
    data_len = len(chunk)
    for count in freq:
        if count > 0:
            p = count / data_len
            entropy -= p * math.log2(p)
    
    # Heuristics
    if entropy < 3.0:
        return '2bpp'  # Low entropy = few colors
    elif entropy < 5.0:
        return '4bpp'  # Medium entropy
    elif entropy < 7.0:
        return '8bpp'  # Higher entropy
    else:
        return 'unknown'  # Too random


# =============================================================================
# High-Level API
# =============================================================================

class SNESGraphicsRenderer:
    """
    Main renderer class for SNES graphics.
    
    Provides unified API for rendering tiles and sprite sheets.
    """
    
    def __init__(self, format: str = '2bpp', tile_size: int = 8):
        """
        Initialize renderer.
        
        Args:
            format: Graphics format ('2bpp', '4bpp', '8bpp')
            tile_size: Tile size in pixels (default 8)
        """
        self.format = format
        self.tile_size = tile_size
        self.palette = None
        
        # Set default palette based on format
        if format == '2bpp':
            self.palette = get_palette_2bpp_color()
        elif format == '4bpp':
            self.palette = get_palette_4bpp()
        elif format == '8bpp':
            self.palette = get_palette_8bpp_grayscale()
    
    def render_tile(self, data: bytes, offset: int = 0) -> Optional[List[int]]:
        """
        Render single tile to pixel array.
        
        Args:
            data: Source data
            offset: Tile offset
        
        Returns:
            Pixel array or None
        """
        if self.format == '2bpp':
            return render_snes_tile_2bpp(data, offset, self.tile_size, self.tile_size)
        elif self.format == '4bpp':
            return render_snes_tile_4bpp(data, offset, self.tile_size, self.tile_size)
        elif self.format == '8bpp':
            return render_snes_tile_8bpp(data, offset, self.tile_size, self.tile_size)
        return None
    
    def render_tiles(self, data: bytes, offset: int = 0, count: Optional[int] = None,
                     cols: int = 32) -> Image.Image:
        """
        Render multiple tiles to sprite sheet.
        
        Args:
            data: Source data
            offset: Starting offset
            count: Number of tiles (default: all that fit)
            cols: Number of columns in sheet
        
        Returns:
            PIL Image sprite sheet
        """
        tiles = []
        bytes_per_tile = self.tile_size * self.tile_size * (int(self.format[0]) // 4 + 1)
        
        if count is None:
            count = (len(data) - offset) // bytes_per_tile
        
        for i in range(count):
            tile_offset = offset + i * bytes_per_tile
            tile = self.render_tile(data, tile_offset)
            if tile:
                tiles.append(tile)
        
        return render_tiles_to_sheet(tiles, cols, self.palette, self.tile_size)
    
    def render_to_file(self, data: bytes, output_path: str, offset: int = 0,
                       count: Optional[int] = None, cols: int = 32) -> str:
        """
        Render tiles and save to file.
        
        Args:
            data: Source data
            output_path: Output file path
            offset: Starting offset
            count: Number of tiles
            cols: Columns in sheet
        
        Returns:
            Output file path
        """
        img = self.render_tiles(data, offset, count, cols)
        img.save(output_path)
        return output_path


def extract_and_render(rom_data: bytes, offset: int, count: int = 32, 
                       format: str = 'auto', output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    High-level API: extract and render in one call.
    
    Args:
        rom_data: ROM data
        offset: Graphics offset
        count: Number of tiles
        format: Format ('2bpp', '4bpp', '8bpp', 'auto')
        output_path: Optional output file
    
    Returns:
        Dict with image and metadata
    """
    if format == 'auto':
        format = detect_graphics_format(rom_data, offset)
    
    renderer = SNESGraphicsRenderer(format=format)
    img = renderer.render_tiles(rom_data, offset, count)
    
    result = {
        'image': img,
        'format': format,
        'offset': offset,
        'tile_count': count
    }
    
    if output_path:
        img.save(output_path)
        result['output_path'] = output_path
    
    return result


# =============================================================================
# Legacy Compatibility Functions (Deprecated)
# =============================================================================

def render_raw_bitmap(data, width, height, palette_type='grayscale'):
    """
    Render data as raw bitmap.
    
    Deprecated: Use SNESGraphicsRenderer or tile_to_image instead.
    """
    warnings.warn(
        "render_raw_bitmap is deprecated. Use SNESGraphicsRenderer instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... (keep original implementation for backward compatibility)
    data = bytes(data)
    needed = width * height
    if len(data) < needed:
        data = data + bytes(needed - len(data))
    elif len(data) > needed:
        data = data[:needed]

    img = Image.new('RGB', (width, height))
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            idx = y * width + x
            byte = data[idx] if idx < len(data) else 0

            if palette_type == 'grayscale':
                pixels[x, y] = (byte, byte, byte)
            elif palette_type == 'snes3':
                r = ((byte >> 0) & 1) * 127 + ((byte >> 3) & 1) * 128
                g = ((byte >> 1) & 1) * 127 + ((byte >> 4) & 1) * 128
                b = ((byte >> 2) & 1) * 127 + ((byte >> 5) & 1) * 128
                pixels[x, y] = (r, g, b)
            else:
                pixels[x, y] = (byte, byte ^ 0xFF, byte >> 1)

    return img


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="B.O.B. ROM Graphics Renderer (Consolidated)")
    parser.add_argument("--input", "-i", required=True, help="Input file or directory")
    parser.add_argument("--output", "-o", default="data/gfx_png", help="Output directory")
    parser.add_argument("--all", action="store_true", help="Render all files")
    parser.add_argument("--format", "-f", default="2bpp", help="Graphics format (2bpp, 4bpp, 8bpp, auto)")
    parser.add_argument("--cols", type=int, default=32, help="Tiles per row")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find files to process
    if input_path.is_file():
        files = [input_path]
    elif args.all:
        files = list(Path("data").glob("decompressed_*.bin"))
    else:
        files = list(input_path.glob("*.bin"))
    
    print(f"Processing {len(files)} files with format={args.format}...")
    
    for f in files:
        print(f"Rendering: {f.name}")
        with open(f, 'rb') as data_file:
            data = data_file.read()
        
        renderer = SNESGraphicsRenderer(format=args.format)
        out_name = f"{f.stem}_render.png"
        out_path = output_dir / out_name
        renderer.render_to_file(data, str(out_path), cols=args.cols)
        print(f"  -> {out_name}")
    
    print(f"\nDone! Output: {output_dir}")


if __name__ == "__main__":
    main()
