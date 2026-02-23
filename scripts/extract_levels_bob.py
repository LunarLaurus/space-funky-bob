#!/usr/bin/env python3
"""
Extract level data from Space Funky B.O.B. ROM.

Level types from source/Disk D & E/BOBSNE4/EQUATES.H:
    borglevel     equ 0    ; World 1 - Borg Factory (0xD4000)
    buglevel      equ 1    ; World 2 - Bug Planet (0xE4000)
    ancientlevel  equ 4    ; World 3 - Ancient Ruins (0xF4000)
    lavalevel     equ 6    ; World 4 - Lava (TBD)
    ultralevel    equ 8    ; World 5 - Ultra Force (TBD)
    bubblelevel   equ 9    ; World 6 - Bubble Forest (TBD)
    worldlevel    equ 10   ; World 7 - World Maps (N/A)
    spacelevel    equ 3    ; World 8 - Space (TBD)

Confirmed ROM offsets:
- 0xD4000: World 1 (Borg Factory)
- 0xE4000: World 2 (Bug Planet)
- 0xF4000: World 3 (Ancient Ruins)

Worlds 4-8: Source MAP files exist in source/Disk C/ but ROM
locations not yet confirmed.

Source MAP file counts (Disk C/):
- BORGMAPS: 29 files | BUGMAPS: 9 files | ANCMAPS: 16 files
- LAVAMAPS: 6 files | ULTRAMPA: 11 files | JUNGLEMA: 5 files
- WORLDMAP: 4 files | SPACEMAP: 2 files | TOTAL: 82 files
"""

import struct
import json
import os
from pathlib import Path

# Auto-detect paths relative to this script
SCRIPT_DIR = Path(__file__).parent.parent
ROM_PATH = SCRIPT_DIR / "rom" / "B.O.B._edit.smc"
OUTPUT_DIR = SCRIPT_DIR / "data" / "levels"

LEVEL_LOCATIONS = {
    "world_1": 0xD4000,
    "world_2": 0xE4000,
    "world_3": 0xF4000,
}

LEVEL_WIDTH = 80
LEVEL_HEIGHT = 80
LEVEL_SIZE = 0x4000


def extract_level(rom_path: str, offset: int) -> dict:
    """Extract a single level from ROM at given offset.

    Format: 8-bit tile IDs, 80x80 tiles, row-major order.
    Each row is 80 bytes.
    """
    with open(rom_path, "rb") as f:
        f.seek(offset)
        level_data = f.read(LEVEL_SIZE)

    # 8-bit tile format
    sparse_tiles = []
    for i, tile_id in enumerate(level_data[: LEVEL_WIDTH * LEVEL_HEIGHT]):
        if tile_id != 0:
            x = i % LEVEL_WIDTH
            y = i // LEVEL_WIDTH
            sparse_tiles.append({"x": x, "y": y, "tile": tile_id})

    return {
        "offset": f"0x{offset:06x}",
        "width": LEVEL_WIDTH,
        "height": LEVEL_HEIGHT,
        "total_tiles": LEVEL_WIDTH * LEVEL_HEIGHT,
        "non_zero_tiles": len(sparse_tiles),
        "tiles": sparse_tiles,
    }


def extract_all_levels(rom_path: str) -> dict:
    """Extract all levels from ROM."""
    all_levels = {
        "metadata": {
            "rom_path": rom_path,
            "level_size": f"0x{LEVEL_SIZE}",
            "dimensions": f"{LEVEL_WIDTH}x{LEVEL_HEIGHT}",
            "format": "sparse (x, y, tile_id)",
            "tile_format": "little-endian 16-bit",
        },
        "levels": {},
    }

    for level_name, offset in LEVEL_LOCATIONS.items():
        print(f"Extracting {level_name} from offset 0x{offset:06x}...")
        level_data = extract_level(rom_path, offset)
        all_levels["levels"][level_name] = level_data
        print(f"  Found {level_data['non_zero_tiles']} non-zero tiles")

    return all_levels


def save_levels(levels: dict, output_dir: Path):
    """Save levels to JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    combined_path = output_dir / "all_levels.json"
    with open(combined_path, "w") as f:
        json.dump(levels, f, indent=2)
    print(f"Saved combined levels to {combined_path}")

    for level_name, level_data in levels["levels"].items():
        level_path = output_dir / f"{level_name}.json"
        with open(level_path, "w") as f:
            json.dump(level_data, f, indent=2)
        print(f"Saved {level_name} to {level_path}")


def verify_extraction(levels: dict):
    """Verify extraction produces valid tile data."""
    print("\n=== Verification ===")

    for level_name, level_data in levels["levels"].items():
        print(f"\n{level_name}:")
        print(f"  Offset: {level_data['offset']}")
        print(f"  Dimensions: {level_data['width']}x{level_data['height']}")
        print(f"  Non-zero tiles: {level_data['non_zero_tiles']}")

        tiles = level_data["tiles"]
        if tiles:
            first = tiles[0]
            last = tiles[-1]
            print(
                f"  First tile: x={first['x']}, y={first['y']}, tile_id={first['tile_id']}"
            )
            print(
                f"  Last tile: x={last['x']}, y={last['y']}, tile_id={last['tile_id']}"
            )

            ids = [t["tile_id"] for t in tiles]
            print(f"  Tile ID range: {min(ids)} - {max(ids)}")

            xs = [t["x"] for t in tiles]
            ys = [t["y"] for t in tiles]
            print(f"  X range: {min(xs)} - {max(xs)}")
            print(f"  Y range: {min(ys)} - {max(ys)}")

            if max(xs) >= level_data["width"] or max(ys) >= level_data["height"]:
                print(f"  WARNING: Coordinates out of bounds!")
                return False

    print("\nAll levels extracted successfully!")
    return True


def main():
    print("Space Funky B.O.B. Level Extractor")
    print("=" * 40)

    if not os.path.exists(ROM_PATH):
        print(f"ERROR: ROM not found at {ROM_PATH}")
        return 1

    levels = extract_all_levels(ROM_PATH)
    save_levels(levels, OUTPUT_DIR)

    if not verify_extraction(levels):
        print("WARNING: Verification failed!")
        return 1

    print("\nExtraction complete!")
    return 0


if __name__ == "__main__":
    exit(main())
