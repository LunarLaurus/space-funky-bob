#!/usr/bin/env python3
"""
Level data extractor for Space Funky B.O.B.
Finds and extracts level data from the ROM.

Author: Null
"""

import struct
import os
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from lz77 import LZ77

# Known level types from source
LEVEL_TYPES = {
    0: "Borg",
    1: "Bug/Sand",
    2: "Unknown",
    3: "Unknown",
    4: "Ancient",
    5: "Unknown",
    6: "Lava",
    7: "Unknown",
    8: "Ultra",
    9: "Bubble",
    10: "World 0",
    11: "World 1",
    12: "World 2",
}

# Map dimensions from SCROLL.A
MAP_WIDTH = 80
MAP_HEIGHT = 80
MAP_SIZE = 8192 * 2  # 16KB per level

LEVEL_CATEGORIES = {
    "ANCMAPS": {"name": "Anc", "theme": "Ancient"},
    "BORGMAPS": {"name": "Borg", "theme": "Factory"},
    "BUGMAPS": {"name": "Bug", "theme": "Bug"},
    "JUNGLEMA": {"name": "Jungle", "theme": "Jungle"},
    "LAVAMAPS": {"name": "Lava", "theme": "Lava"},
    "SPACEMAP": {"name": "Space", "theme": "Space"},
    "ULTRAMPA": {"name": "Ultra", "theme": "Ultra"},
    "WORLDMAP": {"name": "World", "theme": "World"},
    "BORGMAP2": {"name": "Borg2", "theme": "Factory"},
    "BORGMAP3": {"name": "Borg3", "theme": "Factory"},
    "BORGMAP4": {"name": "Borg4", "theme": "Factory"},
    "BUBMAPS": {"name": "Bubble", "theme": "Bubble"},
}

# World progression sequences from INITLEVE.A
# Source: themapsequence1/2/3
WORLD_SEQUENCES = {
    0: [0, 1, 2, 9, 4, 22, 6, 5, 14, 20, 21, 18, 13, 11],       # World 0: 14 levels (Borg/Bug)
    1: [23, 15, 7, 24, 16, 51, 19, 29, 32, 55, 25, 3, 27, 28, 33, 30, 26, 40, 34],  # World 1: 19 levels (Ancient/Lava)
    2: [35, 48, 36, 38, 43, 53, 47, 44, 37, 49, 56, 52, 12, 50, 10, 54, 59],  # World 2: 17 levels (Ultra/Bubble)
}

# Level type equates from EQUATES.H
LEVEL_TYPE_EQUATES = {
    'borglevel': 0,
    'buglevel': 1,
    'spacelevel': 3,
    'ancientlevel': 4,
    'lavalevel': 6,
    'ultralevel': 8,
    'bubblelevel': 9,
    'worldlevel': 10,
    'worldlevel2': 11,
    'worldlevel3': 12,
    'borglevel2': 14,
    'borglevel3': 15,
    'borglevel4': 16,
}

# Music theme sharing from EQUATES.H
# Bug/Bubble share theme 4, Ancient/Lava share theme 5
MUSIC_THEMES = {
    'borgtheme': 3,
    'bugtheme': 4,      # Shared with Bubble
    'bubbletheme': 4,   # Shared with Bug
    'anctheme': 5,      # Shared with Lava
    'lavatheme': 5,     # Shared with Ancient
    'ultratheme': 6,
}

# Map file size to level count
# Each .MAP file is 131070 bytes
# In ROM, levels might be compressed


class LevelExtractor:
    """Extract level data from B.O.B. ROM."""

    # From SCROLL.A: mapsize = 8192*2 = 16KB
    LEVEL_SIZE = 8192 * 2  # 16KB per level
    MAP_WIDTH = 80
    MAP_HEIGHT = 80

    def __init__(self, rom_data):
        self.rom = rom_data

    def find_level_data(self):
        """
        Find potential level data locations in ROM.
        Based on common patterns and the source code insights.
        """
        levels = []

        # Known from source: scrollmap = $7e3000 in RAM
        # ROM addresses for levels typically in banks 0x80-0xC0

        # Search for level data patterns
        # Levels are 16KB each, uncompressed
        for bank in range(0x80, 0xC0):
            for offset in range(0x8000, 0x10000, 0x4000):  # Check every 16KB
                file_offset = (bank - 0x80) * 0x8000 + (offset - 0x8000)

                if file_offset + self.LEVEL_SIZE > len(self.rom):
                    continue

                # Check if this looks like level data
                data = self.rom[file_offset : file_offset + self.LEVEL_SIZE]

                # Count non-zero bytes (levels have sparse data)
                nonzero = sum(1 for b in data if b != 0)
                nonzero_ratio = nonzero / len(data)

                # Level data typically has 10-40% non-zero
                if 0.08 < nonzero_ratio < 0.5:
                    levels.append(
                        {
                            "bank": bank,
                            "offset": offset,
                            "file_offset": file_offset,
                            "snes_addr": (bank << 16) | offset,
                            "nonzero_ratio": nonzero_ratio,
                            "likely": "high" if 0.1 < nonzero_ratio < 0.4 else "medium",
                        }
                    )

        return levels

    def extract_level(self, file_offset, decompress=False):
        """Extract a level from ROM."""
        if decompress:
            # Try LZ77 decompression
            compressed = self.rom[file_offset : file_offset + 0x4000]
            try:
                data = LZ77.decompress(compressed, 0x4000)
            except:
                data = compressed
        else:
            data = self.rom[file_offset : file_offset + self.LEVEL_SIZE]

        return data

    def find_compressed_levels(self):
        """Find LZ77 compressed level data."""
        compressed = []

        # Scan ROM for compressed data
        for offset in range(0, len(self.rom) - 256, 1):
            # Look for compressed blocks
            try:
                data = self.rom[offset : offset + 256]
                decompressed = LZ77.decompress(data, 8192)

                if len(decompressed) >= 4096:  # At least 4KB decompressed
                    # Check if decompressed data looks like level data
                    nonzero = sum(1 for b in decompressed if b != 0)
                    ratio = nonzero / len(decompressed)

                    if 0.1 < ratio < 0.6:  # Looks like level data
                        compressed.append(
                            {
                                "offset": offset,
                                "compressed_size": len(data),
                                "decompressed_size": len(decompressed),
                                "ratio": len(decompressed) / len(data),
                                "nonzero_ratio": ratio,
                                "snes_addr": (offset // 0x8000 + 0x80) << 16
                                | (offset % 0x8000),
                            }
                        )
            except:
                pass

        return compressed[:20]

    def analyze_map_files(self):
        """Analyze the source MAP files for format info."""
        map_dir = (
            "/usr/workspace/space-funky-bob/Space Funky B.O.B. Source Files/Disk C"
        )

        if not os.path.exists(map_dir):
            return None

        results = []

        for category in LEVEL_CATEGORIES:
            cat_path = os.path.join(map_dir, category)
            if os.path.exists(cat_path):
                for f in sorted(os.listdir(cat_path)):
                    if f.endswith(".MAP"):
                        fpath = os.path.join(cat_path, f)
                        size = os.path.getsize(fpath)

                        # Analyze file
                        with open(fpath, "rb") as fp:
                            data = fp.read()

                        # Find data region
                        nonzero_offsets = [i for i, b in enumerate(data) if b != 0]

                        results.append(
                            {
                                "category": category,
                                "file": f,
                                "size": size,
                                "first_data": nonzero_offsets[0]
                                if nonzero_offsets
                                else -1,
                                "data_bytes": len(nonzero_offsets),
                            }
                        )

        return results


def main():
    """Test level extraction."""
    rom_path = "/usr/workspace/space-funky-bob/B.O.B._edit.smc"

    with open(rom_path, "rb") as f:
        rom = f.read()

    extractor = LevelExtractor(rom)

    print("=== Analyzing Source MAP Files ===")
    maps = extractor.analyze_map_files()
    if maps:
        for m in maps[:10]:
            print(
                f"  {m['category']}/{m['file']}: {m['size']} bytes, first data at 0x{m['first_data']:X}, {m['data_bytes']} non-zero"
            )

    print("\n=== Finding Compressed Levels ===")
    compressed = extractor.find_compressed_levels()
    for c in compressed[:10]:
        print(
            f"  Offset 0x{c['offset']:06X}: {c['compressed_size']} -> {c['decompressed_size']} bytes (SNES: 0x{c['snes_addr']:06X})"
        )


if __name__ == "__main__":
    main()
