#!/usr/bin/env python3
"""
B.O.B. ROM Analysis Toolkit - Usage Guide

Quick Start:
    python toolkit/bob_analyze.py --rom "rom/B.O.B..smc"

Individual Tools:
    # Scan ROM for compressed blocks
    python toolkit/bob_lz_scan.py --rom "rom/B.O.B..smc" --output data

    # Extract all found blocks
    python toolkit/bob_extract.py --candidates data/candidates.json --output data

    # Render graphics (2bpp tiles, 32 tiles per row - confirmed format)
    python toolkit/bob_graphics_v2.py --all

    # Auto-detect graphics format
    python toolkit/bob_graphics_classifier.py --all

    # Generate manual review variants (45 per blob)
    python toolkit/bob_graphics_test_suite.py --all --limit 10

Test Suite:
    python run_full_test_suite.py          # Full test suite
    python run_full_test_suite.py --quick   # Quick mode

Output Directory Structure:
    data/
    ├── decompressed_*.bin          # 59 extracted blocks
    ├── candidates.json              # Block metadata
    ├── rom_map.json                 # Region classifications
    ├── rom_map.html                 # Interactive map
    ├── gfx_v2/                      # Confirmed format renderings
    ├── gfx_classified/              # Auto-detected formats
    └── gfx_review/                  # Manual review variants

Known Format:
    - Graphics: 2bpp SNES tiles, 32 tiles per row
    - Example: decompressed_0A0000.bin renders correctly

Troubleshooting:
    - If no blocks found: Check ROM path is correct
    - If graphics are garbled: Try different format in gfx_review/
    - Run tests: python run_full_test_suite.py
"""

if __name__ == "__main__":
    print(__doc__)
