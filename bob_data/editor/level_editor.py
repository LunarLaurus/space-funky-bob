#!/usr/bin/env python3
"""
Space Funky B.O.B. Level Editor
A level editor for the SNES game Space Funky B.O.B.
"""

import os
import struct
import json
import http.server
import socketserver
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
ROM_PATH = PROJECT_DIR / "B.O.B..smc"
MAP_DIR = PROJECT_DIR / "Space Funky B.O.B. Source Files" / "Disk C"

# Level map metadata
LEVEL_CATEGORIES = {
    "ANCMAPS": {"name": "Anc", "theme": "Ancient"},
    "BORGMAPS": {"name": "Borg", "theme": "Factory"},
    "BUGMAPS": {"name": "Bug", "theme": "Bug"},
    "JUNGLEMA": {"name": "Jungle", "theme": "Jungle"},
    "LAVAMAPS": {"name": "Lava", "theme": "Lava"},
    "SPACEMAP": {"name": "Space", "theme": "Space"},
    "ULTRAMPA": {"name": "Ultra", "theme": "Ultra"},
    "WORLDMAP": {"name": "World", "theme": "World"},
}


def parse_map_file(filepath):
    """Parse a .MAP file and extract level data"""
    with open(filepath, "rb") as f:
        data = f.read()

    # Skip header (first 514 bytes seem to be empty/padding)
    level_data_start = 0x202
    level_data = data[level_data_start:]

    # Map is likely 128x256 or similar tile arrangement
    # Each tile is 1 byte (tile ID)
    tiles = []
    for i, byte in enumerate(level_data):
        if byte != 0:
            x = i % 512
            y = i // 512
            tiles.append(
                {
                    "offset": level_data_start + i,
                    "x": x,
                    "y": y,
                    "tile_id": byte,
                    "hex": f"0x{byte:02x}",
                }
            )

    return {
        "filename": os.path.basename(filepath),
        "size": len(data),
        "data_offset": level_data_start,
        "total_tiles": len(tiles),
        "unique_tiles": len(set(t["tile_id"] for t in tiles)),
        "tiles": tiles[:100],  # First 100 non-empty tiles
    }


def get_all_maps():
    """Get all map files from Disk C"""
    maps = []
    for category in LEVEL_CATEGORIES:
        category_path = MAP_DIR / category
        if category_path.exists():
            for mapfile in sorted(category_path.glob("*.MAP")):
                info = parse_map_file(mapfile)
                info["category"] = category
                info["category_info"] = LEVEL_CATEGORIES[category]
                maps.append(info)
    return maps


def generate_tileset():
    """Generate a basic tileset for the editor"""
    # 16x16 tile grid (256 possible tiles)
    tiles = []
    for i in range(256):
        tiles.append(
            {
                "id": i,
                "hex": f"0x{i:02x}",
                "color": f"#{i:02x}{i:02x}{i:02x}" if i < 250 else "#ff00ff",
            }
        )
    return tiles


def build_editor_data():
    """Build all data needed for the editor"""
    return {
        "rom": {
            "name": "B.O.B. (U)",
            "size": os.path.getsize(ROM_PATH) if ROM_PATH.exists() else 0,
            "path": str(ROM_PATH.name),
        },
        "maps": get_all_maps(),
        "tileset": generate_tileset(),
        "categories": LEVEL_CATEGORIES,
    }


if __name__ == "__main__":
    data = build_editor_data()
    print(json.dumps(data, indent=2))
