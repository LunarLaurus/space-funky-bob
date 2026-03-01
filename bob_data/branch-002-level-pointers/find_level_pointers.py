#!/usr/bin/env python3
"""
Level Pointer Finder for Space Funky B.O.B.
Finds exact level data pointers in ROM.

Author: Null
"""

import struct
import os


class LevelPointerFinder:
    """Find level pointers in B.O.B. ROM."""

    LEVEL_SIZE = 8192 * 2  # 16KB

    def __init__(self, rom_path):
        with open(rom_path, "rb") as f:
            self.rom = f.read()

    def find_snes_to_file(self, snes_addr):
        """Convert SNES address to ROM file offset (LoROM)."""
        bank = (snes_addr >> 16) & 0xFF
        offset = snes_addr & 0xFFFF

        if bank >= 0x80:
            file_off = (bank - 0x80) * 0x8000
            if offset >= 0x8000:
                file_off += offset
            else:
                file_off += 0x8000 + offset
            return file_off
        return None

    def scan_for_level_tables(self):
        """Scan ROM for level pointer tables."""
        candidates = []

        # Look for sequences of 24-bit pointers to 16KB-aligned addresses
        for offset in range(0, len(self.rom) - 100, 1):
            pointers = []
            for i in range(0, 20, 3):
                ptr = (
                    self.rom[offset + i]
                    | (self.rom[offset + i + 1] << 8)
                    | (self.rom[offset + i + 2] << 16)
                )

                if ptr < 0x800000:
                    continue

                bank = (ptr >> 16) & 0xFF
                addr = ptr & 0xFFFF

                # Check if points to likely level data (16KB aligned)
                if addr % 0x4000 == 0 and 0x80 <= bank <= 0xFF:
                    file_off = self.find_snes_to_file(ptr)
                    if file_off and file_off + 0x4000 <= len(self.rom):
                        pointers.append(
                            {
                                "ptr": hex(ptr),
                                "bank": hex(bank),
                                "addr": hex(addr),
                                "file_off": file_off,
                                "valid": True,
                            }
                        )

            if len(pointers) >= 3:
                candidates.append(
                    {"offset": offset, "pointers": pointers[:5], "count": len(pointers)}
                )

        return candidates

    def find_level_data_by_pattern(self):
        """Find level data using known patterns."""
        # Search for uncompressed level data patterns
        # Levels typically have sparse tile data

        results = []

        for bank in range(0x80, 0xC0):
            for offset in range(0x8000, 0x10000, 0x4000):
                file_off = (bank - 0x80) * 0x8000 + (offset - 0x8000)

                if file_off + 0x4000 > len(self.rom):
                    continue

                data = self.rom[file_off : file_off + 0x4000]

                # Count non-zero bytes
                nonzero = sum(1 for b in data if b != 0)
                ratio = nonzero / len(data)

                # Level data typically 5-30% non-zero
                if 0.05 < ratio < 0.35:
                    results.append(
                        {
                            "bank": hex(bank),
                            "offset": hex(offset),
                            "file_offset": file_off,
                            "snes_addr": (bank << 16) | offset,
                            "nonzero_ratio": ratio,
                            "nonzero_bytes": nonzero,
                        }
                    )

        # Sort by likelihood
        results.sort(key=lambda x: abs(x["nonzero_ratio"] - 0.15))
        return results[:20]


def main():
    """Find level pointers."""
    rom_path = "/usr/workspace/space-funky-bob/B.O.B._edit.smc"

    finder = LevelPointerFinder(rom_path)

    print("=== Finding Level Data ===\n")

    print("Scanning for level tables...")
    tables = finder.scan_for_level_tables()
    if tables:
        print(f"Found {len(tables)} potential level tables:")
        for t in tables[:5]:
            print(f"  Offset 0x{t['offset']:X}: {t['count']} pointers")
            for p in t["pointers"][:3]:
                print(f"    -> {p['ptr']} (file: 0x{p['file_off']:X})")
    else:
        print("No clear level tables found")

    print("\nScanning for level data by pattern...")
    level_data = finder.find_level_data_by_pattern()
    if level_data:
        print(f"Found {len(level_data)} potential level data regions:")
        for l in level_data[:10]:
            print(f"  SNES {l['snes_addr']:06X} (file: 0x{l['file_offset']:X})")
            print(
                f"    Non-zero: {l['nonzero_bytes']} ({l['nonzero_ratio'] * 100:.1f}%)"
            )


if __name__ == "__main__":
    main()
