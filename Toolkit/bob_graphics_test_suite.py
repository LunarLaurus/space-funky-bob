#!/usr/bin/env python3
"""
bob_graphics_test_suite.py - Comprehensive Graphics Format Test Suite

Tests ALL possible variations of SNES/graphics formats for manual review.
Generates multiple variations per blob for type detection.

Usage:
    python toolkit/bob_graphics_test_suite.py --input data/decompressed_0A0000.bin --output data/gfx_review
    python toolkit/bob_graphics_test_suite.py --all
"""

import argparse
import os
from pathlib import Path
from PIL import Image, ImageDraw
import json


def render_raw_bitmap(data, width, height, palette_type='grayscale'):
    """Render data as raw bitmap."""
    if len(data) < width * height:
        data = data + bytes(width * height - len(data))
    elif len(data) > width * height:
        data = data[:width * height]
    
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            idx = y * width + x
            byte = data[idx]
            
            if palette_type == 'grayscale':
                pixels[x, y] = (byte, byte, byte)
            elif palette_type == 'grayscale_inv':
                pixels[x, y] = (byte ^ 0xFF, byte ^ 0xFF, byte ^ 0xFF)
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
            elif palette_type == 'snes5bit':
                r = (byte >> 3) * 9
                g = ((byte >> 3) & 0x7) * 9
                b = (byte & 7) * 9
                pixels[x, y] = (r, g, b)
            else:
                pixels[x, y] = (byte, byte ^ 0xFF, byte >> 1)
    
    return img


def render_snes_tile_1bpp(data, offset, width=8, height=8):
    """Render 1bpp tile (monochrome)."""
    if offset + width * height // 8 > len(data):
        return None
    
    tile = []
    for y in range(height):
        byte_idx = offset + y
        if byte_idx >= len(data):
            break
        byte = data[byte_idx]
        for x in range(width):
            bit = (byte >> (7 - x)) & 1
            tile.append(bit)
    return tile


def render_snes_tile_2bpp(data, offset, width=8, height=8):
    """Render SNES 2bpp tile (standard)."""
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


def render_snes_tile_2bpp_planar(data, offset, width=8, height=8):
    """Render 2bpp tile with planar (interleaved) bit order."""
    if offset + (width * height // 4) > len(data):
        return None
    
    tile = []
    for y in range(height):
        for x in range(width):
            bit0 = (data[offset + x] >> (7 - y)) & 1
            bit1 = (data[offset + 8 + x] >> (7 - y)) & 1
            pixel = (bit1 << 1) | bit0
            tile.append(pixel)
    return tile


def render_snes_tile_4bpp(data, offset, width=8, height=8):
    """Render SNES 4bpp tile (standard)."""
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


def render_snes_tile_4bpp_mode7(data, offset, width=8, height=8):
    """Render 4bpp Mode 7 style (linear)."""
    if offset + 64 > len(data):
        return None
    
    tile = []
    for i in range(64):
        byte = data[offset + i]
        tile.append(byte & 0x0F)
    return tile


def render_snes_tile_8bpp(data, offset, width=8, height=8):
    """Render 8bpp tile (256 colors)."""
    if offset + 64 > len(data):
        return None
    return list(data[offset:offset + 64])


def tile_to_image(tile_data, width, height, palette):
    """Convert tile data to image."""
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


def get_palette_1bpp():
    """1bpp palette (2 colors)."""
    return [(0, 0, 0), (255, 255, 255)]


def get_palette_2bpp():
    """2bpp palette (4 colors)."""
    return [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]


def get_palette_2bpp_color():
    """2bpp color palette."""
    return [
        (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
        (0, 0, 128), (128, 0, 128), (0, 128, 128), (128, 128, 128),
        (64, 0, 0), (192, 0, 0), (64, 128, 0), (192, 128, 0),
        (0, 64, 0), (128, 64, 0), (0, 192, 0), (192, 192, 0),
    ]


def get_palette_4bpp():
    """4bpp palette (16 colors) - NES style."""
    return [
        (0, 0, 0), (0, 0, 128), (128, 0, 0), (128, 0, 128),
        (0, 128, 0), (0, 128, 128), (128, 128, 0), (128, 128, 128),
        (0, 0, 64), (0, 0, 255), (255, 0, 0), (255, 0, 255),
        (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255),
    ]


def get_palette_4bpp_rgb():
    """4bpp RGB palette."""
    palette = []
    for r in range(4):
        for g in range(4):
            for b in range(4):
                palette.append((r * 63, g * 63, b * 63))
    return palette[:16]


def get_palette_8bpp():
    """8bpp grayscale palette."""
    return [(i, i, i) for i in range(256)]


def get_palette_8bpp_rainbow():
    """8bpp rainbow palette."""
    palette = []
    for i in range(256):
        r = (i >> 4) * 17
        g = ((i >> 2) & 3) * 51
        b = (i & 3) * 51
        palette.append((r, g, b))
    return palette


def test_raw_bitmap_variations(data, filename, output_dir):
    """Test all raw bitmap dimension variations."""
    results = {}
    size = len(data)
    
    divisors = []
    for w in range(1, 129):
        if size % w == 0:
            h = size // w
            if 1 <= h <= 256 and 1 <= w <= 256:
                divisors.append((w, h))
    
    divisors = sorted(divisors, key=lambda x: x[0])[:32]
    
    for width, height in divisors:
        for palette_type in ['grayscale', 'grayscale_inv', 'rainbow', 'snes5bit']:
            try:
                img = render_raw_bitmap(data, width, height, palette_type)
                out_name = f"{filename}_raw_{width}x{height}_{palette_type}.png"
                img.save(output_dir / out_name)
                results[f'raw_{width}x{height}_{palette_type}'] = out_name
            except:
                pass
    
    return results


def test_tile_variations(data, filename, output_dir):
    """Test all tile format variations."""
    results = {}
    size = len(data)
    
    tile_configs = [
        ('1bpp', 1, 8, 8, get_palette_1bpp, render_snes_tile_1bpp),
        ('2bpp', 2, 8, 8, get_palette_2bpp, render_snes_tile_2bpp),
        ('2bpp_color', 2, 8, 8, get_palette_2bpp_color, render_snes_tile_2bpp),
        ('2bpp_planar', 2, 8, 8, get_palette_2bpp, render_snes_tile_2bpp_planar),
        ('4bpp', 4, 8, 8, get_palette_4bpp, render_snes_tile_4bpp),
        ('4bpp_rgb', 4, 8, 8, get_palette_4bpp_rgb, render_snes_tile_4bpp),
        ('4bpp_mode7', 4, 8, 8, get_palette_4bpp, render_snes_tile_4bpp_mode7),
        ('8bpp', 8, 8, 8, get_palette_8bpp, render_snes_tile_8bpp),
        ('8bpp_rainbow', 8, 8, 8, get_palette_8bpp_rainbow, render_snes_tile_8bpp),
    ]
    
    for tiles_per_row in [8, 16, 32]:
        for tile_name, bpp, tw, th, palette_func, render_func in tile_configs:
            tile_size = tw * th * bpp // 8
            max_tiles = size // tile_size
            
            if max_tiles < 1 or max_tiles > 512:
                continue
            
            try:
                tile_img = Image.new('RGB', (tiles_per_row * tw, ((max_tiles + tiles_per_row - 1) // tiles_per_row) * th))
                tiles_rendered = 0
                
                for tile_idx in range(min(max_tiles, 256)):
                    offset = tile_idx * tile_size
                    tile = render_func(data, offset, tw, th)
                    if tile:
                        tile_img_local = tile_to_image(tile, tw, th, palette_func())
                        x = (tile_idx % tiles_per_row) * tw
                        y = (tile_idx // tiles_per_row) * th
                        tile_img.paste(tile_img_local, (x, y))
                        tiles_rendered += 1
                
                if tiles_rendered > 0:
                    out_name = f"{filename}_tiles_{tile_name}_{tiles_per_row}x.png"
                    tile_img.save(output_dir / out_name)
                    results[f'tiles_{tile_name}_{tiles_per_row}'] = out_name
            except Exception as e:
                pass
    
    return results


def test_16x16_tile_variations(data, filename, output_dir):
    """Test 16x16 tile variations (sprite tiles)."""
    results = {}
    size = len(data)
    
    tile_configs = [
        ('2bpp', 2, get_palette_2bpp_color),
        ('4bpp', 4, get_palette_4bpp_rgb),
        ('8bpp', 8, get_palette_8bpp),
    ]
    
    for tile_name, bpp, palette_func in tile_configs:
        tile_size = 16 * 16 * bpp // 8
        max_tiles = size // tile_size
        
        if max_tiles < 1 or max_tiles > 64:
            continue
        
        try:
            tiles_per_row = 8
            tile_img = Image.new('RGB', (tiles_per_row * 16, ((max_tiles + tiles_per_row - 1) // tiles_per_row) * 16))
            tiles_rendered = 0
            
            for tile_idx in range(min(max_tiles, 64)):
                offset = tile_idx * tile_size
                tile = render_snes_tile_4bpp(data, offset, 16, 16)
                if tile:
                    tile_img_local = tile_to_image(tile, 16, 16, palette_func())
                    x = (tile_idx % tiles_per_row) * 16
                    y = (tile_idx // tiles_per_row) * 16
                    tile_img.paste(tile_img_local, (x, y))
                    tiles_rendered += 1
            
            if tiles_rendered > 0:
                out_name = f"{filename}_tiles_16x16_{tile_name}.png"
                tile_img.save(output_dir / out_name)
                results[f'tiles_16x16_{tile_name}'] = out_name
        except:
            pass
    
    return results


def test_linear_formats(data, filename, output_dir):
    """Test linear format variations."""
    results = {}
    size = len(data)
    
    linear_configs = [
        (64, 64, '8bpp'),
        (128, 64, '8bpp'),
        (256, 32, '8bpp'),
        (128, 128, '8bpp'),
        (32, 64, '8bpp'),
        (256, 64, '8bpp'),
    ]
    
    for width, height, fmt in linear_configs:
        if width * height == size:
            for palette in ['grayscale', 'rainbow']:
                try:
                    img = render_raw_bitmap(data, width, height, palette)
                    out_name = f"{filename}_linear_{width}x{height}_{palette}.png"
                    img.save(output_dir / out_name)
                    results[f'linear_{width}x{height}_{palette}'] = out_name
                except:
                    pass
    
    return results


def test_snes_mode_formats(data, filename, output_dir):
    """Test SNES video mode specific formats."""
    results = {}
    size = len(data)
    
    if size >= 8192:
        for mode in ['mode1', 'mode2', 'mode3', 'mode4', 'mode5']:
            try:
                width, height = 128, 64
                if size >= 16384:
                    width, height = 256, 64
                if size >= 32768:
                    width, height = 256, 128
                
                img = Image.new('RGB', (width, height))
                pixels = img.load()
                
                for i in range(min(size, width * height)):
                    byte = data[i]
                    x = i % width
                    y = i // width
                    
                    if mode == 'mode1':
                        r = (byte >> 3) * 36
                        g = ((byte >> 1) & 3) * 85
                        b = (byte & 7) * 36
                    elif mode == 'mode2':
                        r = byte
                        g = byte ^ 0xFF
                        b = byte >> 1
                    elif mode == 'mode3':
                        r = (byte >> 4) * 17
                        g = ((byte >> 2) & 3) * 51
                        b = (byte & 3) * 51
                    elif mode == 'mode4':
                        r = (byte >> 3) * 36
                        g = ((byte >> 3) & 7) * 36
                        b = (byte & 7) * 36
                    else:  # mode5
                        r = byte >> 2
                        g = (byte >> 2) & 3
                        b = byte & 3
                    
                    pixels[x, y] = (r, g, b)
                
                out_name = f"{filename}_snes_{mode}.png"
                img.save(output_dir / out_name)
                results[f'snes_{mode}'] = out_name
            except:
                pass
    
    return results


def test_scanline_formats(data, filename, output_dir):
    """Test scanline/interlace formats."""
    results = {}
    size = len(data)
    
    for interlace in [True, False]:
        for h in [128, 192, 224, 240, 256]:
            w = size // h
            if w * h == size and w in [256, 320, 512, 640]:
                for palette in ['grayscale', 'rainbow']:
                    try:
                        if interlace:
                            img = Image.new('RGB', (w, h * 2))
                            pixels = img.load()
                            for y in range(h):
                                for x in range(w):
                                    byte = data[y * w + x]
                                    if palette == 'grayscale':
                                        pixels[x, y * 2] = (byte, byte, byte)
                                        pixels[x, y * 2 + 1] = (byte // 2, byte // 2, byte // 2)
                                    else:
                                        r = (byte >> 3) * 36
                                        g = ((byte >> 1) & 3) * 85
                                        b = (byte & 7) * 36
                                        pixels[x, y * 2] = (r, g, b)
                                        pixels[x, y * 2 + 1] = (r // 2, g // 2, b // 2)
                        else:
                            img = render_raw_bitmap(data, w, h, palette)
                        
                        suffix = 'interlace' if interlace else 'progressive'
                        out_name = f"{filename}_{suffix}_{w}x{h}_{palette}.png"
                        img.save(output_dir / out_name)
                        results[f'{suffix}_{w}x{h}_{palette}'] = out_name
                    except:
                        pass
    
    return results


def test_all_formats(input_path, output_dir):
    """Test all format variations for a single file."""
    filename = Path(input_path).stem
    
    with open(input_path, 'rb') as f:
        data = f.read()
    
    print(f"Testing {filename} ({len(data)} bytes)")
    
    all_results = {}
    
    print("  - Raw bitmap variations...")
    all_results.update(test_raw_bitmap_variations(data, filename, output_dir))
    
    print("  - Tile variations (8x8)...")
    all_results.update(test_tile_variations(data, filename, output_dir))
    
    print("  - Tile variations (16x16)...")
    all_results.update(test_16x16_tile_variations(data, filename, output_dir))
    
    print("  - Linear formats...")
    all_results.update(test_linear_formats(data, filename, output_dir))
    
    print("  - SNES mode formats...")
    all_results.update(test_snes_mode_formats(data, filename, output_dir))
    
    print("  - Scanline formats...")
    all_results.update(test_scanline_formats(data, filename, output_dir))
    
    return all_results, len(data)


def create_review_index(results_by_file, output_dir):
    """Create HTML index for manual review."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>B.O.B. Graphics Review - Manual Type Detection</title>
    <style>
        body { font-family: monospace; background: #1a1a1a; color: #ccc; padding: 20px; }
        h1 { color: #fff; }
        .file { margin: 20px 0; padding: 15px; background: #252525; border-radius: 8px; }
        .file h2 { color: #4af; margin-top: 0; }
        .variations { display: flex; flex-wrap: wrap; gap: 10px; }
        .variation { text-align: center; }
        .variation img { border: 2px solid #444; }
        .variation img:hover { border-color: #4af; }
        .variation span { display: block; font-size: 10px; color: #888; }
    </style>
</head>
<body>
    <h1>B.O.B. Graphics Review - Manual Type Detection</h1>
"""
    
    for filename, data in results_by_file.items():
        html += f'<div class="file"><h2>{filename}</h2>\n'
        html += f'<p>Size: {data["size"]} bytes</p>\n'
        html += '<div class="variations">\n'
        
        for variant, path in data['variations'].items():
            html += f'<div class="variation"><img src="{path}" width="128"><span>{variant}</span></div>\n'
        
        html += '</div></div>\n'
    
    html += "</body></html>"
    
    with open(output_dir / "review_index.html", 'w') as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description="B.O.B. Graphics Format Test Suite")
    parser.add_argument("--input", "-i", help="Input file")
    parser.add_argument("--output", "-o", default="data/gfx_review", help="Output directory")
    parser.add_argument("--all", action="store_true", help="Process all decompressed files")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Limit files when using --all")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_by_file = {}
    
    if args.input:
        files = [Path(args.input)]
    elif args.all:
        files = sorted(Path("data").glob("decompressed_*.bin"))[:args.limit]
    else:
        print("Error: Specify --input or --all")
        return
    
    print(f"Processing {len(files)} files...")
    print("=" * 50)
    
    for f in files:
        try:
            all_results, size = test_all_formats(f, output_dir)
            results_by_file[f.name] = {
                'variations': all_results,
                'size': size
            }
            print(f"  Generated {len(all_results)} variations\n")
        except Exception as e:
            print(f"Error processing {f.name}: {e}\n")
    
    print("=" * 50)
    print(f"Creating review index...")
    create_review_index(results_by_file, output_dir)
    
    total_variants = sum(len(v['variations']) for v in results_by_file.values())
    print(f"\nDone! Processed {len(files)} files, generated {total_variants} total variations")
    print(f"Output: {output_dir}")
    print(f"Open {output_dir}/review_index.html for manual review")


if __name__ == "__main__":
    main()
