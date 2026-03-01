#!/usr/bin/env python3
"""
Level Import Tool for Space Funky B.O.B.
Writes edited levels back to ROM.

Author: Null
"""

import struct
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from lz77 import LZ77


class LevelImporter:
    """Import level data back to ROM."""

    LEVEL_SIZE = 8192 * 2  # 16KB per level

    # Known level pointer locations from exploration
    LEVEL_POINTERS = {
        "borg": 0x006AC2,
        "bug": 0x007030,
        "ancient": 0x006AC2,
        "lava": 0x006AC2,
        "ultra": 0x006AC2,
    }

    def __init__(self, rom_path):
        self.rom_path = rom_path
        with open(rom_path, "rb") as f:
            self.rom = bytearray(f.read())

    def import_level(self, level_data, offset):
        """Import level data to ROM at offset."""
        if len(level_data) > self.LEVEL_SIZE:
            level_data = level_data[: self.LEVEL_SIZE]
        elif len(level_data) < self.LEVEL_SIZE:
            level_data = level_data + bytes(self.LEVEL_SIZE - len(level_data))

        for i, b in enumerate(level_data):
            self.rom[offset + i] = b

    def find_level_offset(self, level_type, level_index):
        """Find the ROM offset for a specific level."""
        ptr_offset = self.LEVEL_POINTERS.get(level_type, 0)

        if ptr_offset == 0:
            return None

        # Read pointer at calculated offset
        ptr_offset += level_index * 3  # 3 bytes per pointer (24-bit)

        if ptr_offset + 3 > len(self.rom):
            return None

        # Read 24-bit pointer
        bank = self.rom[ptr_offset + 2]
        addr = struct.unpack("<H", self.rom[ptr_offset : ptr_offset + 2])[0]

        # Convert to file offset (LoROM)
        if bank >= 0x80:
            file_offset = (bank - 0x80) * 0x8000 + addr
            if addr >= 0x8000:
                file_offset += 0x8000
            return file_offset

        return None

    def save(self, output_path=None):
        """Save the modified ROM."""
        if output_path is None:
            output_path = self.rom_path

        with open(output_path, "wb") as f:
            f.write(self.rom)

    def get_level(self, offset, size=None):
        """Get level data from ROM."""
        if size is None:
            size = self.LEVEL_SIZE
        return bytes(self.rom[offset : offset + size])


def main():
    """Test level import."""
    rom_path = "/usr/workspace/space-funky-bob/B.O.B._edit.smc"

    if not os.path.exists(rom_path):
        print(f"ROM not found: {rom_path}")
        return

    importer = LevelImporter(rom_path)

    print("=== Level Import Tool ===")
    print(f"ROM: {rom_path}")
    print(f"Size: {len(importer.rom)} bytes")

    # Try to find level offsets
    for level_type in ["borg", "bug", "ancient", "lava", "ultra"]:
        for idx in range(8):
            offset = importer.find_level_offset(level_type, idx)
            if offset and offset < len(importer.rom):
                print(f"  {level_type}_{idx}: ROM offset 0x{offset:06X}")
                break


if __name__ == "__main__":
    main()
