#!/usr/bin/env python3
"""
Extract tileset data from Space Funky B.O.B. ROM.

Tileset format: SNES 4bpp (4 bits per pixel)
- 8x8 pixels, 16 colors per tile
- 32 bytes per tile
- 256 tiles per 8KB block

Known tileset locations from source analysis:
- 0x008000: Borg Tileset
- 0x008800: Bug Tileset
- 0x009000: Ancient Tileset
- 0x035800: Main Graphics 1
- 0x03D800: Main Graphics 2

Source: editor/wiki.html, source/Disk D & E/BOBSNE4/EQUATES.H
"""

import json
import os
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass

# Auto-detect paths relative to this script
SCRIPT_DIR = Path(__file__).parent.parent
ROM_PATH = SCRIPT_DIR / "rom" / "B.O.B._edit.smc"
OUTPUT_DIR = SCRIPT_DIR / "data" / "tilesets"

TILE_SIZE = 32

KNOWN_TILESETS = [
    {"offset": 0x035800, "size": 8192, "name": "main_graphics_1"},
    {"offset": 0x03D800, "size": 8192, "name": "main_graphics_2"},
]


@dataclass
class TilesetLocation:
    """Represents a found tileset location in the ROM."""

    rom_offset: int
    size_bytes: int
    num_tiles: int
    unique_tiles: int
    confidence: float
    reason: str


def read_rom_bytes(rom_path: str, offset: int, length: int) -> bytes:
    """Read bytes from ROM at given offset."""
    with open(rom_path, "rb") as f:
        f.seek(offset)
        return f.read(length)


def is_tileset_block(
    data: bytes, offset: int, num_tiles: int = 16
) -> Tuple[bool, dict]:
    """Check if there's a sequence of tiles at offset."""
    if offset + num_tiles * TILE_SIZE > len(data):
        return False, {}

    unique_tiles = set()
    zero_count = 0

    for i in range(num_tiles):
        tile = data[offset + i * TILE_SIZE : offset + (i + 1) * TILE_SIZE]
        unique_tiles.add(bytes(tile))
        if all(b == 0 for b in tile):
            zero_count += 1

    unique_ratio = len(unique_tiles) / num_tiles

    # Calculate byte density
    tile_data = data[offset : offset + num_tiles * TILE_SIZE]
    nonzero_bytes = sum(1 for b in tile_data if b != 0)
    byte_density = nonzero_bytes / len(tile_data)

    return_dict = {
        "unique_tiles": len(unique_tiles),
        "unique_ratio": unique_ratio,
        "zero_count": zero_count,
        "zero_ratio": zero_count / num_tiles,
        "byte_density": byte_density,
    }

    # Heuristics for valid tileset
    # Good tileset should have variation but not be random noise
    # Also should not be mostly empty
    if 0.25 < unique_ratio < 0.95 and zero_count < num_tiles * 0.4:
        return True, return_dict

    return False, return_dict


def find_tileset_candidates(rom_path: str) -> List[TilesetLocation]:
    """Search for tileset data in the ROM."""
    candidates = []

    print(f"Searching for tilesets in ROM: {rom_path}")

    with open(rom_path, "rb") as f:
        data = f.read()

    rom_size = len(data)
    print(f"ROM size: {rom_size} bytes ({rom_size / 1024 / 1024:.2f} MB)")

    # Scan for contiguous blocks of tiles
    print("Scanning for tileset blocks...")

    step = 256  # Scan every 256 bytes
    for offset in range(0, rom_size - 512, step):
        is_tile, stats = is_tileset_block(data, offset, 16)

        if is_tile:
            # Try to find the extent of this tileset
            ext_offset = offset
            ext_size = 256

            while ext_offset + ext_size + 256 < rom_size:
                # Check if next block is also tile-like
                next_is_tile, next_stats = is_tileset_block(
                    data, ext_offset + ext_size, 8
                )
                if next_is_tile and next_stats["unique_ratio"] > 0.2:
                    ext_size += 256
                else:
                    break

            # Calculate confidence
            confidence = 0.0
            reasons = []

            if 0.3 < stats["unique_ratio"] < 0.8:
                confidence += 0.4
                reasons.append("good_variation")

            if stats["zero_ratio"] < 0.3:
                confidence += 0.3
                reasons.append("not_mostly_empty")

            if 0.3 < stats["byte_density"] < 0.8:
                confidence += 0.2
                reasons.append("good_density")

            if ext_size >= 1024:
                confidence += 0.1
                reasons.append("large_block")

            candidates.append(
                TilesetLocation(
                    rom_offset=offset,
                    size_bytes=ext_size,
                    num_tiles=ext_size // TILE_SIZE,
                    unique_tiles=stats["unique_tiles"],
                    confidence=confidence,
                    reason=",".join(reasons) if reasons else "unknown",
                )
            )

    # Remove overlapping candidates (keep the larger ones)
    candidates.sort(key=lambda x: (x.confidence, x.size_bytes), reverse=True)

    filtered = []
    for c in candidates:
        overlaps = False
        for f in filtered:
            if abs(c.rom_offset - f.rom_offset) < f.size_bytes:
                overlaps = True
                break
        if not overlaps:
            filtered.append(c)

    return filtered[:20]


def decode_4bpp_tile(tile_data: bytes) -> List[List[int]]:
    """Decode a single 4bpp SNES tile (8x8 pixels) to a 2D array of palette indices."""
    if len(tile_data) < 32:
        return [[0] * 8 for _ in range(8)]

    pixels = [[0] * 8 for _ in range(8)]

    for row in range(8):
        for col in range(8):
            bit_pos = 7 - col  # MSB first

            plane0 = (tile_data[row] >> bit_pos) & 1
            plane1 = (tile_data[row + 8] >> bit_pos) & 1
            plane2 = (tile_data[row + 16] >> bit_pos) & 1
            plane3 = (tile_data[row + 24] >> bit_pos) & 1

            pixel_value = (plane3 << 3) | (plane2 << 2) | (plane1 << 1) | plane0
            pixels[row][col] = pixel_value

    return pixels


def extract_tiles(rom_path: str, offset: int, num_tiles: int) -> List[List[List[int]]]:
    """Extract multiple tiles from ROM."""
    tiles = []
    data = read_rom_bytes(rom_path, offset, num_tiles * TILE_SIZE)

    for i in range(num_tiles):
        tile_data = data[i * TILE_SIZE : (i + 1) * TILE_SIZE]
        tile = decode_4bpp_tile(tile_data)
        tiles.append(tile)

    return tiles


def save_tileset_png(
    tiles: List[List[List[int]]], output_path: Path, tiles_per_row: int = 16
) -> bool:
    """Save tileset as a PNG image."""
    try:
        from PIL import Image
    except ImportError:
        print("PIL not available, skipping PNG export")
        return False

    if not tiles:
        return False

    rows = (len(tiles) + tiles_per_row - 1) // tiles_per_row
    img_height = rows * 8
    img_width = tiles_per_row * 8

    img = Image.new("L", (img_width, img_height))

    for i, tile in enumerate(tiles):
        row = i // tiles_per_row
        col = i % tiles_per_row
        start_y = row * 8
        start_x = col * 8

        for y in range(8):
            for x in range(8):
                pixel_val = tile[y][x]
                gray = pixel_val * 17
                img.putpixel((start_x + x, start_y + y), gray)

    img.save(output_path)
    print(f"Saved PNG to {output_path}")
    return True


def save_tileset_json(tiles: List[List[List[int]]], output_path: Path, metadata: dict):
    """Save tileset as JSON."""
    simplified = {"metadata": metadata, "tiles": []}

    for i, tile in enumerate(tiles[:256]):
        simplified["tiles"].append({"index": i, "pixels": tile})

    with open(output_path, "w") as f:
        json.dump(simplified, f, indent=2)
    print(f"Saved JSON to {output_path}")


def save_candidates_report(candidates: List[TilesetLocation], output_path: Path):
    """Save a report of found tileset candidates."""
    import json

    report = {"total_candidates": len(candidates), "candidates": []}

    for c in candidates:
        report["candidates"].append(
            {
                "rom_offset": f"0x{c.rom_offset:06X}",
                "size_bytes": c.size_bytes,
                "num_tiles": c.num_tiles,
                "unique_tiles": c.unique_tiles,
                "confidence": round(c.confidence, 2),
                "reason": c.reason,
            }
        )

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Saved candidates report to {output_path}")


def main():
    import json

    print("=" * 60)
    print("Space Funky B.O.B. Tileset Extractor")
    print("=" * 60)

    if not os.path.exists(ROM_PATH):
        print(f"ERROR: ROM not found at {ROM_PATH}")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    candidates = find_tileset_candidates(ROM_PATH)

    print(f"\nFound {len(candidates)} tileset candidates")

    save_candidates_report(candidates, OUTPUT_DIR / "candidates_report.json")

    print("\n--- Extracting known tilesets ---")
    for known in KNOWN_TILESETS:
        offset = known["offset"]
        size = known["size"]
        name = known.get("name", f"known_{offset:06X}")

        tiles = extract_tiles(ROM_PATH, offset, size // TILE_SIZE)

        metadata = {
            "rom_offset": f"0x{offset:06X}",
            "size_bytes": size,
            "num_tiles": len(tiles),
            "source": "known_location",
        }

        save_tileset_png(tiles, OUTPUT_DIR / f"tileset_{name}.png")
        save_tileset_json(tiles, OUTPUT_DIR / f"tileset_{name}.json", metadata)

    print(
        f"\n--- Extracting auto-detected tilesets ({len(candidates[:10])} candidates) ---"
    )
    for i, candidate in enumerate(candidates[:10]):
        print(f"\n--- Candidate {i + 1} ---")
        print(f"  ROM offset: 0x{candidate.rom_offset:06X}")
        print(f"  Size: {candidate.size_bytes} bytes ({candidate.num_tiles} tiles)")
        print(f"  Confidence: {candidate.confidence:.2f}")
        print(f"  Reason: {candidate.reason}")

        tiles = extract_tiles(
            ROM_PATH, candidate.rom_offset, min(candidate.num_tiles, 256)
        )

        base_name = f"tileset_{candidate.rom_offset:06X}"

        metadata = {
            "rom_offset": f"0x{candidate.rom_offset:06X}",
            "size_bytes": candidate.size_bytes,
            "num_tiles": len(tiles),
            "confidence": candidate.confidence,
            "reason": candidate.reason,
        }

        save_tileset_png(tiles, OUTPUT_DIR / f"{base_name}.png")
        save_tileset_json(tiles, OUTPUT_DIR / f"{base_name}.json", metadata)

    print("\n" + "=" * 60)
    print("Extraction complete!")
    print(f"Output directory: {OUTPUT_DIR}")

    return 0


if __name__ == "__main__":
    exit(main())
