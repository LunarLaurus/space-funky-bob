#!/usr/bin/env python3
"""
bob_graphics_v2.py — B.O.B. ROM Graphics Renderer v2 (DEPRECATED)

⚠️  DEPRECATED: This module is superseded by bob_graphics.py (consolidated).

Use the consolidated module instead:
    from toolkit.bob_graphics import SNESGraphicsRenderer
    renderer = SNESGraphicsRenderer(format='2bpp')
    img = renderer.render_tiles(data, cols=32)

This module is retained for backward compatibility only.
"""

import warnings
warnings.warn(
    "bob_graphics_v2.py is deprecated. Use bob_graphics.py (consolidated module) instead.",
    DeprecationWarning,
    stacklevel=2
)

import argparse
import os
from pathlib import Path
from PIL import Image
import json


def render_snes_tile_2bpp(data, offset, width=8, height=8):
    """Render SNES 2bpp tile (standard format)."""
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


def get_palette_2bpp_color():
    """2bpp color palette."""
    return [
        (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
        (0, 0, 128), (128, 0, 128), (0, 128, 128), (128, 128, 128),
        (64, 0, 0), (192, 0, 0), (64, 128, 0), (192, 128, 0),
        (0, 64, 0), (128, 64, 0), (0, 192, 0), (192, 192, 0),
    ]


def get_palette_2bpp_grayscale():
    """2bpp grayscale palette."""
    return [
        (0, 0, 0), (17, 17, 17), (34, 34, 34), (51, 51, 51),
        (68, 68, 68), (85, 85, 85), (102, 102, 102), (119, 119, 119),
        (136, 136, 136), (153, 153, 153), (170, 170, 170), (187, 187, 187),
        (204, 204, 204), (221, 221, 221), (238, 238, 238), (255, 255, 255),
    ]


def tile_to_image(tile_data, width, height, palette):
    """Convert tile data to image."""
    if not tile_data or not palette:
        return None
    
    img: Image.Image = Image.new('RGB', (width, height))
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


def render_2bpp_32(data, tiles_per_row=32):
    """Render 2bpp tiles with 32 tiles per row (confirmed format)."""
    tile_size = 16  # 8x8 * 2bpp = 16 bytes
    max_tiles = len(data) // tile_size
    
    if max_tiles < 1:
        return None
    
    rows = (max_tiles + tiles_per_row - 1) // tiles_per_row
    tile_img = Image.new('RGB', (tiles_per_row * 8, rows * 8))
    
    tiles_rendered = 0
    for tile_idx in range(max_tiles):
        offset = tile_idx * tile_size
        tile = render_snes_tile_2bpp(data, offset)
        if tile:
            tile_img_local = tile_to_image(tile, 8, 8, get_palette_2bpp_color())
            if tile_img_local is not None:
                x = (tile_idx % tiles_per_row) * 8
                y = (tile_idx // tiles_per_row) * 8
                tile_img.paste(tile_img_local, (x, y))
                tiles_rendered += 1
    
    return tile_img, tiles_rendered


def render_2bpp_16(data):
    """Render 2bpp tiles with 16 tiles per row."""
    return render_2bpp_32(data, 16)


def render_2bpp_8(data):
    """Render 2bpp tiles with 8 tiles per row."""
    return render_2bpp_32(data, 8)


def analyze_graphics(data, filename):
    """Analyze and render graphics file with multiple formats."""
    results = {}
    size = len(data)
    
    if size < 16:
        return results
    
    try:
        result = render_2bpp_32(data, 32)
        if result:
            img, count = result
            results['2bpp_32x'] = {'img': img, 'tiles': count}
    except Exception:
        pass
    
    try:
        result = render_2bpp_32(data, 16)
        if result:
            img, count = result
            results['2bpp_16x'] = {'img': img, 'tiles': count}
    except Exception:
        pass
    
    try:
        result = render_2bpp_32(data, 8)
        if result:
            img, count = result
            results['2bpp_8x'] = {'img': img, 'tiles': count}
    except Exception:
        pass
    
    return results


def process_file(input_path, output_dir):
    """Process a single graphics file."""
    filename = Path(input_path).stem
    
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
    except Exception:
        return {}
    
    results = analyze_graphics(data, filename)
    
    saved = {}
    for fmt, result in results.items():
        try:
            img = result.get('img')
            if img is not None:
                out_name = f"{filename}_{fmt}.png"
                img.save(output_dir / out_name)
                saved[fmt] = out_name
        except Exception:
            pass
    
    return saved


def main():
    parser = argparse.ArgumentParser(description="B.O.B. ROM Graphics Renderer v2")
    parser.add_argument("--input", "-i", help="Input file")
    parser.add_argument("--output", "-o", default="data/gfx_v2", help="Output directory")
    parser.add_argument("--all", action="store_true", help="Process all decompressed files")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.input:
        files = [Path(args.input)]
    elif args.all:
        files = sorted(Path("data").glob("decompressed_*.bin"))
    else:
        print("Error: Specify --input or --all")
        return
    
    print(f"Processing {len(files)} files...")
    
    all_results = {}
    for f in files:
        print(f"  {f.name}")
        saved = process_file(f, output_dir)
        all_results[f.name] = saved
    
    # Save manifest
    manifest_path = output_dir / "render_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nDone! Rendered {len(files)} files")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
