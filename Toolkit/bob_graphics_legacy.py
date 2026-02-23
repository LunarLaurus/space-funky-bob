#!/usr/bin/env python3
"""
bob_graphics_legacy.py — B.O.B. ROM Graphics Renderer (LEGACY/DEPRECATED)

⚠️  DEPRECATED: This module is legacy code. Use bob_graphics.py (consolidated) instead.

This module is retained for backward compatibility. All new code should use:
    from toolkit.bob_graphics import SNESGraphicsRenderer, render_snes_tile_2bpp

The consolidated module provides:
- Unified API with SNESGraphicsRenderer class
- 2bpp/4bpp/8bpp rendering support
- Palette extraction and application
- Format auto-detection
- Better documentation and testing

Migration guide:
    OLD: from toolkit.bob_graphics import render_snes_tile_2bpp
    NEW: from toolkit.bob_graphics import SNESGraphicsRenderer
         renderer = SNESGraphicsRenderer(format='2bpp')
         tile = renderer.render_tile(data, offset)

Original module preserved for reference and backward compatibility.
"""

import warnings
warnings.warn(
    "bob_graphics_legacy.py is deprecated. Use bob_graphics.py (consolidated module) instead.",
    DeprecationWarning,
    stacklevel=2
)

import argparse
import os
from pathlib import Path
from PIL import Image, ImageDraw
import json


def render_raw_bitmap(data, width, height, palette_type='grayscale'):
    """Render data as raw bitmap."""
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
            if idx >= len(data):
                byte = 0
            else:
                byte = data[idx]
            
            if palette_type == 'grayscale':
                pixels[x, y] = (byte, byte, byte)
            elif palette_type == 'snes3':
                r = ((byte >> 0) & 1) * 127 + ((byte >> 3) & 1) * 128
                g = ((byte >> 1) & 1) * 127 + ((byte >> 4) & 1) * 128
                b = ((byte >> 2) & 1) * 127 + ((byte >> 5) & 1) * 128
                pixels[x, y] = (r, g, b)
            elif palette_type == 'rainbow':
                r = (byte >> 3) * 36
                g = ((byte >> 1) & 3) * 85
                b = (byte & 7) * 36
                pixels[x, y] = (r, g, b)
            else:
                pixels[x, y] = (byte, byte ^ 0xFF, byte >> 1)
    
    return img


def render_snes_tile_2bpp(data, offset, width=8, height=8):
    """Render SNES 2bpp tile."""
    if offset + 16 > len(data):
        return None
    
    tile = []
    for y in range(height):
        row_data = data[offset + y*2 : offset + y*2 + 2]
        if len(row_data) < 2:
            break
        b1, b2 = row_data
        for x in range(width):
            bit0 = (b1 >> (7 - x)) & 1
            bit1 = (b2 >> (7 - x)) & 1
            pixel = (bit1 << 1) | bit0
            tile.append(pixel)
    
    return tile


def render_snes_tile_4bpp(data, offset, width=8, height=8):
    """Render SNES 4bpp tile."""
    if offset + 32 > len(data):
        return None
    
    tile = []
    for y in range(height):
        row_data = data[offset + y*4 : offset + y*4 + 4]
        if len(row_data) < 4:
            break
        b1, b2, b3, b4 = row_data
        for x in range(width):
            bit0 = (b1 >> (7 - x)) & 1
            bit1 = (b2 >> (7 - x)) & 1
            bit2 = (b3 >> (7 - x)) & 1
            bit3 = (b4 >> (7 - x)) & 1
            pixel = (bit3 << 3) | (bit2 << 2) | (bit1 << 1) | bit0
            tile.append(pixel)
    
    return tile


def tile_to_image(tile_data, width, height, palette):
    """Convert tile data to image."""
    if not tile_data or not palette:
        return None
    
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            idx = y * width + x
            if idx < len(tile_data):
                color_idx = min(tile_data[idx], len(palette) - 1)
                pixels[x, y] = palette[color_idx]
            else:
                pixels[x, y] = (0, 0, 0)
    
    return img


def get_tile_palette(mode):
    """Get palette for tile rendering."""
    if mode == '2bpp':
        return [
            (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
            (0, 0, 128), (128, 0, 128), (0, 128, 128), (128, 128, 128),
            (64, 0, 0), (192, 0, 0), (64, 128, 0), (192, 128, 0),
            (0, 64, 0), (128, 64, 0), (0, 192, 0), (192, 192, 0),
        ]
    else:  # 4bpp
        palette = []
        for r in range(4):
            for g in range(4):
                for b in range(4):
                    palette.append((r * 63, g * 63, b * 63))
        return palette[:16]


def render_graphics_file(input_path, output_dir):
    """Render a single graphics file in multiple formats."""
    filename = Path(input_path).stem
    
    with open(input_path, 'rb') as f:
        data = f.read()
    
    results = {}
    
    # 1. Try different raw bitmap dimensions
    for width in [64, 32, 16, 8]:
        height = len(data) // width
        if height * width == len(data):
            # Render as raw grayscale
            out_name = f"{filename}_raw_{width}x{height}.png"
            img = render_raw_bitmap(data, width, height, 'grayscale')
            img.save(output_dir / out_name)
            results[f'raw_{width}x{height}'] = out_name
            
            # Render as rainbow
            out_name = f"{filename}_rainbow_{width}x{height}.png"
            img = render_raw_bitmap(data, width, height, 'rainbow')
            img.save(output_dir / out_name)
            results[f'rainbow_{width}x{height}'] = out_name
    
    # 2. Try tile formats
    tiles_per_row = 16
    
    # 2bpp tiles
    tile_img_2bpp = Image.new('RGB', (tiles_per_row * 8, 128))
    tiles_2bpp = 0
    for tile_idx in range(min(256, len(data) // 16)):
        offset = tile_idx * 16
        tile = render_snes_tile_2bpp(data, offset)
        if tile:
            tile_img = tile_to_image(tile, 8, 8, get_tile_palette('2bpp'))
            x = (tile_idx % tiles_per_row) * 8
            y = (tile_idx // tiles_per_row) * 8
            tile_img_2bpp.paste(tile_img, (x, y))
            tiles_2bpp += 1
    
    if tiles_2bpp > 0:
        out_name = f"{filename}_tiles_2bpp.png"
        tile_img_2bpp.save(output_dir / out_name)
        results['tiles_2bpp'] = out_name
    
    # 4bpp tiles
    tile_img_4bpp = Image.new('RGB', (tiles_per_row * 8, 256))
    tiles_4bpp = 0
    for tile_idx in range(min(256, len(data) // 32)):
        offset = tile_idx * 32
        tile = render_snes_tile_4bpp(data, offset)
        if tile:
            tile_img = tile_to_image(tile, 8, 8, get_tile_palette('4bpp'))
            x = (tile_idx % tiles_per_row) * 8
            y = (tile_idx // tiles_per_row) * 8
            tile_img_4bpp.paste(tile_img, (x, y))
            tiles_4bpp += 1
    
    if tiles_4bpp > 0:
        out_name = f"{filename}_tiles_4bpp.png"
        tile_img_4bpp.save(output_dir / out_name)
        results['tiles_4bpp'] = out_name
    
    # 3. Create contact sheet with all renderings
    contact_sheet = Image.new('RGB', (512, 600))
    draw = ImageDraw.Draw(contact_sheet)
    
    # Add header
    draw.text((10, 10), f"File: {filename}", fill=(255, 255, 255))
    draw.text((10, 30), f"Size: {len(data)} bytes", fill=(200, 200, 200))
    
    # Try to load and paste key renderings
    y_offset = 60
    
    # Try 64x32 raw
    key = 'raw_64x32'
    if key in results:
        try:
            img = Image.open(output_dir / results[key])
            img = img.resize((128, 64))
            contact_sheet.paste(img, (10, y_offset))
            draw.text((150, y_offset + 20), "Raw 64x32", fill=(200, 200, 200))
            y_offset += 80
        except:
            pass
    
    # Try rainbow
    key = 'rainbow_64x32'
    if key in results:
        try:
            img = Image.open(output_dir / results[key])
            img = img.resize((128, 64))
            contact_sheet.paste(img, (10, y_offset))
            draw.text((150, y_offset + 20), "Rainbow 64x32", fill=(200, 200, 200))
            y_offset += 80
        except:
            pass
    
    # Try tiles
    key = 'tiles_2bpp'
    if key in results:
        try:
            img = Image.open(output_dir / results[key])
            img = img.resize((256, 128))
            contact_sheet.paste(img, (10, y_offset))
            draw.text((280, y_offset + 50), "2bpp Tiles", fill=(200, 200, 200))
            y_offset += 150
        except:
            pass
    
    out_name = f"{filename}_overview.png"
    contact_sheet.save(output_dir / out_name)
    results['overview'] = out_name
    
    return results


def main():
    parser = argparse.ArgumentParser(description="B.O.B. ROM Graphics Renderer")
    parser.add_argument("--input", "-i", required=True, help="Input file or directory")
    parser.add_argument("--output", "-o", default="data/gfx_png", help="Output directory")
    parser.add_argument("--all", action="store_true", help="Render all files")
    
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
    
    print(f"Processing {len(files)} files...")
    
    all_results = {}
    for f in files:
        print(f"Rendering: {f.name}")
        results = render_graphics_file(f, output_dir)
        all_results[f.name] = results
    
    # Save manifest
    manifest = {
        'total_files': len(files),
        'results': all_results
    }
    
    manifest_path = output_dir / "render_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nDone! Rendered {len(files)} files")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
