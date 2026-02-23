#!/usr/bin/env python3
"""
bob_graphics_classifier.py — Auto-detect graphics format (DEPRECATED)

⚠️  DEPRECATED: This module is superseded by bob_graphics.py (consolidated).

Use the consolidated module instead:
    from toolkit.bob_graphics import detect_graphics_format
    format = detect_graphics_format(data, offset)

This module is retained for backward compatibility only.
"""

import warnings
warnings.warn(
    "bob_graphics_classifier.py is deprecated. Use bob_graphics.py (consolidated module) instead.",
    DeprecationWarning,
    stacklevel=2
)

import argparse
import os
from pathlib import Path
from PIL import Image
import json
import math


def calculate_entropy(data):
    """Calculate Shannon entropy of data."""
    if len(data) == 0:
        return 0
    
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    
    entropy = 0
    for count in freq.values():
        p = count / len(data)
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy


def count_unique_colors(img):
    """Count unique colors in image."""
    colors = set()
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            colors.add(pixels[x, y])
    return len(colors)


def calculate_color_diversity(data, tile_size, tiles_per_row):
    """Calculate color diversity score for tile format."""
    max_tiles = len(data) // tile_size
    if max_tiles < 1:
        return 0
    
    unique_tile_patterns = set()
    for tile_idx in range(min(max_tiles, 64)):
        offset = tile_idx * tile_size
        if offset + tile_size <= len(data):
            tile_bytes = data[offset:offset + tile_size]
            unique_tile_patterns.add(tile_bytes)
    
    return len(unique_tile_patterns)


def render_snes_tile_2bpp(data, offset, width=8, height=8):
    """Render SNES 2bpp tile."""
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


def render_snes_tile_4bpp(data, offset, width=8, height=8):
    """Render SNES 4bpp tile."""
    if offset + (width * height // 2) > len(data):
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


def render_snes_tile_8bpp(data, offset, width=8, height=8):
    """Render 8bpp tile."""
    if offset + 64 > len(data):
        return None
    return list(data[offset:offset + 64])


def get_palette_2bpp_color():
    return [
        (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
        (0, 0, 128), (128, 0, 128), (0, 128, 128), (128, 128, 128),
        (64, 0, 0), (192, 0, 0), (64, 128, 0), (192, 128, 0),
        (0, 64, 0), (128, 64, 0), (0, 192, 0), (192, 192, 0),
    ]


def get_palette_4bpp_rgb():
    palette = []
    for r in range(4):
        for g in range(4):
            for b in range(4):
                palette.append((r * 63, g * 63, b * 63))
    return palette[:16]


def get_palette_8bpp():
    return [(i, i, i) for i in range(256)]


def tile_to_image(tile_data, width, height, palette):
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


def test_format(data, bpp, tiles_per_row, tile_width=8, tile_height=8):
    """Test a specific tile format and return score."""
    tile_size = tile_width * tile_height * bpp // 8
    max_tiles = len(data) // tile_size
    
    if max_tiles < 1:
        return None, 0
    
    if bpp == 2:
        render_func = render_snes_tile_2bpp
        palette = get_palette_2bpp_color()
    elif bpp == 4:
        render_func = render_snes_tile_4bpp
        palette = get_palette_4bpp_rgb()
    else:
        render_func = render_snes_tile_8bpp
        palette = get_palette_8bpp()
    
    rows = (max_tiles + tiles_per_row - 1) // tiles_per_row
    tile_img = Image.new('RGB', (tiles_per_row * tile_width, rows * tile_height))
    
    tiles_rendered = 0
    unique_tiles = set()
    
    for tile_idx in range(min(max_tiles, 256)):
        offset = tile_idx * tile_size
        tile = render_func(data, offset, tile_width, tile_height)
        if tile:
            tile_img_local = tile_to_image(tile, tile_width, tile_height, palette)
            x = (tile_idx % tiles_per_row) * tile_width
            y = (tile_idx // tiles_per_row) * tile_height
            tile_img.paste(tile_img_local, (x, y))
            tiles_rendered += 1
            unique_tiles.add(tuple(tile[:8]))
    
    if tiles_rendered == 0:
        return None, 0
    
    unique_colors = count_unique_colors(tile_img)
    color_diversity = len(unique_tiles)
    
    score = unique_colors * color_diversity
    
    return tile_img, {
        'bpp': bpp,
        'tiles_per_row': tiles_per_row,
        'tile_width': tile_width,
        'tile_height': tile_height,
        'tiles_rendered': tiles_rendered,
        'unique_colors': unique_colors,
        'tile_diversity': color_diversity,
        'score': score
    }


def classify_graphics(data, filename):
    """Auto-detect the best graphics format."""
    results = []
    
    formats = [
        (2, 8), (2, 16), (2, 32), (2, 64),
        (4, 8), (4, 16), (4, 32), (4, 64),
        (8, 8), (8, 16),
    ]
    
    for bpp, tpr in formats:
        img, info = test_format(data, bpp, tpr)
        if img:
            results.append((img, info))
    
    if not results:
        return None, None
    
    results.sort(key=lambda x: x[1]['score'], reverse=True)
    
    return results[0][0], results[0][1]


def process_file(input_path, output_dir):
    """Process and classify a graphics file."""
    filename = Path(input_path).stem
    
    with open(input_path, 'rb') as f:
        data = f.read()
    
    entropy = calculate_entropy(data)
    
    best_img, info = classify_graphics(data, filename)
    
    if best_img:
        out_name = f"{filename}_classified.png"
        best_img.save(output_dir / out_name)
        
        result = {
            'entropy': entropy,
            'size': len(data),
            'format': info,
            'output': out_name
        }
        
        return result
    
    return {'entropy': entropy, 'size': len(data), 'error': 'No valid format found'}


def main():
    parser = argparse.ArgumentParser(description="B.O.B. Graphics Classifier")
    parser.add_argument("--input", "-i", help="Input file")
    parser.add_argument("--output", "-o", default="data/gfx_classified", help="Output directory")
    parser.add_argument("--all", action="store_true", help="Process all files")
    
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
        result = process_file(f, output_dir)
        all_results[f.name] = result
    
    manifest_path = output_dir / "classification.json"
    with open(manifest_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nDone! Classified {len(files)} files")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
