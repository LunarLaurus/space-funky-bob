#!/usr/bin/env python3
"""
bob_visualize.py - Visualize tilemaps from B.O.B. ROM

Generates an HTML file with visual representations of level tilemaps.

Usage:
    python bob_visualize.py --rom "rom/B.O.B..smc" --output levels.html
    python bob_visualize.py --tilemap data/levels/tilemap_04_02A000.bin --output level_04.html
"""

import argparse
import html
from pathlib import Path


def parse_tilemap(tilemap_data):
    """Parse tilemap into tile grid."""
    tiles = []
    for i in range(0, len(tilemap_data), 2):
        if i + 1 >= len(tilemap_data):
            break
        val = (tilemap_data[i+1] << 8) | tilemap_data[i]
        tile_id = val & 0x3FF
        chr_bank = (val >> 10) & 0x3
        palette = (val >> 12) & 0x3
        x_flip = (val >> 14) & 1
        y_flip = (val >> 15) & 1
        
        tiles.append({
            'id': tile_id,
            'chr_bank': chr_bank,
            'palette': palette,
            'x_flip': x_flip,
            'y_flip': y_flip,
            'raw': f"{val:04X}"
        })
    
    return tiles


def get_tile_color(tile_id, palette_idx):
    """Generate a color based on tile ID and palette."""
    # Create pseudo-random colors based on tile ID
    # This is for visualization only - not actual graphics
    hue = (tile_id * 37 + palette_idx * 123) % 360
    saturation = 60 + (tile_id % 40)
    lightness = 30 + (tile_id % 50)
    
    return f"hsl({hue}, {saturation}%, {lightness}%)"


def visualize_tilemap(tiles, index, offset):
    """Generate HTML for a single tilemap."""
    html_parts = []
    html_parts.append(f'<div class="tilemap">')
    html_parts.append(f'<h3>Tilemap #{index} at 0x{offset:06X}</h3>')
    html_parts.append(f'<div class="grid">')
    
    # Render as 32x32 grid
    for row in range(32):
        html_parts.append(f'<div class="row">')
        for col in range(32):
            idx = row * 32 + col
            if idx < len(tiles):
                tile = tiles[idx]
                color = get_tile_color(tile['id'], tile['palette'])
                flip = ""
                if tile['x_flip']:
                    flip += "X"
                if tile['y_flip']:
                    flip += "Y"
                
                title = f"ID: {tile['id']}, CHR: {tile['chr_bank']}, Pal: {tile['palette']}, Flip: {flip or 'None'}"
                html_parts.append(f'<div class="tile" style="background:{color}" title="{title}">{tile["id"]:03d}</div>')
            else:
                html_parts.append(f'<div class="tile empty"></div>')
        html_parts.append(f'</div>')
    
    html_parts.append(f'</div>')
    html_parts.append(f'</div>')
    
    return '\n'.join(html_parts)


def generate_html(tilemaps_data, output_path):
    """Generate complete HTML visualization."""
    html_parts = []
    
    html_parts.append("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>B.O.B. Level Tilemaps</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a2e;
            color: #eee;
            padding: 20px;
        }
        h1 { color: #00ff88; }
        h2 { color: #ff6b6b; margin-top: 40px; }
        h3 { color: #4ecdc4; margin: 10px 0; }
        .tilemap {
            background: #16213e;
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
            border: 1px solid #0f3460;
        }
        .grid {
            display: inline-block;
            background: #000;
            padding: 2px;
        }
        .row { display: flex; }
        .tile {
            width: 16px;
            height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 6px;
            color: rgba(255,255,255,0.7);
            border: 1px solid rgba(0,0,0,0.3);
            box-sizing: border-box;
        }
        .tile.empty { background: #222; }
        .legend {
            display: flex;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }
        .info {
            background: #0f3460;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>B.O.B. Level Tilemaps</h1>
    
    <div class="info">
        <h3>Format: SNES 16-bit Tilemap</h3>
        <p>Each tile: YFlip | XFlip | Palette(2bit) | CHR Bank(2bit) | Tile ID(10bit)</p>
        <p>Grid size: 32x32 (1024 tiles per tilemap)</p>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <span>Palette:</span>
            <div class="legend-color" style="background:hsl(0,70%,40%)"></div> 0
            <div class="legend-color" style="background:hsl(90,70%,40%)"></div> 1
            <div class="legend-color" style="background:hsl(180,70%,40%)"></div> 2
            <div class="legend-color" style="background:hsl(270,70%,40%)"></div> 3
        </div>
    </div>
""")
    
    for i, (data, offset) in enumerate(tilemaps_data):
        tiles = parse_tilemap(data)
        html_parts.append(visualize_tilemap(tiles, i, offset))
    
    html_parts.append("""
</body>
</html>
""")
    
    html_content = '\n'.join(html_parts)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated: {output_path}")
    return len(tilemaps_data)


def main():
    parser = argparse.ArgumentParser(description="Visualize B.O.B. tilemaps")
    parser.add_argument("--rom", help="ROM file to extract tilemaps from")
    parser.add_argument("--tilemap", help="Single tilemap file to visualize")
    parser.add_argument("--tiledir", help="Directory with tilemap files")
    parser.add_argument("--output", default="tilemaps.html", help="Output HTML file")
    parser.add_argument("--limit", type=int, default=20, help="Max tilemaps to visualize")
    
    args = parser.parse_args()
    
    tilemaps_data = []
    
    if args.tiledir:
        # Load from directory
        tilemap_dir = Path(args.tiledir)
        for tf in sorted(tilemap_dir.glob("tilemap_*.bin"))[:args.limit]:
            # Extract offset from filename
            parts = tf.stem.split('_')
            if len(parts) >= 2:
                try:
                    offset = int(parts[-1], 16)
                    data = tf.read_bytes()
                    tilemaps_data.append((data, offset))
                    print(f"Loaded: {tf.name}")
                except:
                    pass
    
    elif args.tilemap:
        # Single tilemap
        data = Path(args.tilemap).read_bytes()
        offset = 0
        tilemaps_data.append((data, offset))
        print(f"Loaded: {args.tilemap}")
    
    elif args.rom:
        # Extract from ROM
        from bob_extract_levels import find_tilemaps
        
        rom_data = Path(args.rom).read_bytes()
        tilemaps = find_tilemaps(rom_data)
        
        for tm in tilemaps[:args.limit]:
            addr = tm['offset']
            data = rom_data[addr:addr+0x800]
            tilemaps_data.append((data, addr))
            print(f"Found tilemap at 0x{addr:06X}")
    
    if not tilemaps_data:
        print("No tilemaps to visualize")
        return 1
    
    count = generate_html(tilemaps_data, args.output)
    print(f"Visualized {count} tilemaps")
    return 0


if __name__ == "__main__":
    exit(main())
