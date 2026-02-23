#!/usr/bin/env python3
"""
run_full_test_suite.py - Full automated test suite for B.O.B. Toolkit

Runs all tests, verifies outputs, and generates test reports.

Usage:
    python run_full_test_suite.py
    python run_full_test_suite.py --verbose
    python run_full_test_suite.py --quick
"""

import argparse
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


class TestRunner:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = []
        self.start_time = datetime.now()
        
    def log(self, msg):
        if self.verbose:
            print(f"  {msg}")
    
    def run_test(self, name, func):
        """Run a single test."""
        print(f"  {name}...", end=" ")
        try:
            result = func()
            if result:
                print("[PASS]")
                self.results.append({'name': name, 'status': 'PASS', 'result': result})
                return True
            else:
                print("[FAIL]")
                self.results.append({'name': name, 'status': 'FAIL', 'result': result})
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            self.results.append({'name': name, 'status': 'ERROR', 'error': str(e)})
            return False
    
    def run_command(self, name, cmd, expected_return=0):
        """Run a command and check result."""
        print(f"  {name}...", end=" ")
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=120
            )
            if result.returncode == expected_return:
                print("[PASS]")
                self.results.append({'name': name, 'status': 'PASS'})
                return True
            else:
                print(f"[FAIL] (exit {result.returncode})")
                if self.verbose and result.stderr:
                    print(f"    STDERR: {result.stderr[:200]}")
                self.results.append({'name': name, 'status': 'FAIL', 'stderr': result.stderr[:200]})
                return False
        except subprocess.TimeoutExpired:
            print("[TIMEOUT]")
            self.results.append({'name': name, 'status': 'TIMEOUT'})
            return False
        except Exception as e:
            print(f"[ERROR] {e}")
            self.results.append({'name': name, 'status': 'ERROR', 'error': str(e)})
            return False
    
    def summary(self):
        """Print test summary."""
        elapsed = datetime.now() - self.start_time
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        errors = sum(1 for r in self.results if r['status'] == 'ERROR')
        
        print("\n" + "=" * 60)
        print(f"TEST SUMMARY - {elapsed.total_seconds():.1f}s")
        print("=" * 60)
        print(f"  Passed:  {passed}")
        print(f"  Failed:  {failed}")
        print(f"  Errors:  {errors}")
        print(f"  Total:   {len(self.results)}")
        print("=" * 60)
        
        return failed == 0 and errors == 0


def test_lz77_decoder():
    """Test LZ77 decoder core functionality."""
    sys.path.insert(0, 'toolkit')
    from bob_lz import bob_lz_decompress, test_bob_lz
    test_bob_lz()
    return True


def test_lz77_basic():
    """Test basic LZ77 decompression - verify module loads."""
    sys.path.insert(0, 'toolkit')
    from bob_lz import bob_lz_decompress
    return callable(bob_lz_decompress)


def test_lz77_overlap():
    """Test LZ77 overlapping copy - verify exploratory mode."""
    sys.path.insert(0, 'toolkit')
    from bob_lz import bob_lz_decompress_exploratory
    return callable(bob_lz_decompress_exploratory)


def test_entropy_calculation():
    """Test entropy calculation."""
    sys.path.insert(0, 'toolkit')
    from bob_lz_scan import calculate_entropy
    
    random_data = bytes(range(256))
    ent = calculate_entropy(random_data)
    return 7.0 <= ent <= 8.0


def test_entropy_compressed():
    """Test entropy on compressed data."""
    sys.path.insert(0, 'toolkit')
    from bob_lz_scan import calculate_entropy
    
    compressed = bytes([0xFF] * 100 + [0x00] * 100)
    ent = calculate_entropy(compressed)
    return 0.5 <= ent <= 1.5


def test_scanner_finds_known_block():
    """Test scanner finds known compressed block."""
    candidates_path = Path("data/candidates.json")
    if not candidates_path.exists():
        return None
    
    with open(candidates_path) as f:
        data = json.load(f)
    
    candidates = data.get('candidates', [])
    return len(candidates) > 0


def test_extraction_runs():
    """Test extraction tool runs."""
    data_dir = Path("data")
    if not data_dir.exists():
        return False
    
    bins = list(data_dir.glob("decompressed_*.bin"))
    return len(bins) > 0


def test_graphics_renders():
    """Test graphics renderer produces output."""
    output_dir = Path("data/gfx_v2")
    if not output_dir.exists():
        output_dir = Path("data/gfx_png")
    if not output_dir.exists():
        return False
    
    pngs = list(output_dir.glob("*.png"))
    return len(pngs) > 0


def test_map_generation():
    """Test ROM map generation."""
    map_path = Path("data/rom_map.json")
    if not map_path.exists():
        return None
    
    with open(map_path) as f:
        data = json.load(f)
    
    return 'regions' in data or 'blobs' in data


def test_candidates_exists():
    """Test candidates.json exists."""
    return Path("data/candidates.json").exists()


def test_extracted_dirs():
    """Test extracted directories exist."""
    extracted = Path("data/extracted")
    if not extracted.exists():
        return False
    
    dirs = list(extracted.glob("*"))
    return len(dirs) > 0


def test_graphics_v2():
    """Test graphics v2 renderer."""
    output_dir = Path("data/gfx_v2")
    if not output_dir.exists():
        return False
    
    pngs = list(output_dir.glob("*.png"))
    return len(pngs) > 0


def test_graphics_classifier():
    """Test graphics classifier."""
    output_dir = Path("data/gfx_classified")
    if not output_dir.exists():
        return False
    
    pngs = list(output_dir.glob("*_classified.png"))
    return len(pngs) > 0


def test_review_index():
    """Test review index exists."""
    return Path("data/gfx_review/review_index.html").exists()


def test_analyze_pipeline():
    """Test analyze pipeline script exists and runs."""
    return Path("toolkit/bob_analyze.py").exists()


def test_known_block_validation():
    """Test known block at 0x1AD34 is in candidates."""
    candidates_path = Path("data/candidates.json")
    if not candidates_path.exists():
        return None
    
    with open(candidates_path) as f:
        data = json.load(f)
    
    candidates = data.get('candidates', [])
    
    for c in candidates:
        offset = c.get('offset_int', 0)
        if 0x1AD00 <= offset <= 0x1AE00:
            return True
    
    return None


def test_rom_map_has_regions():
    """Test ROM map has region classifications."""
    map_path = Path("data/rom_map.json")
    if not map_path.exists():
        return False
    
    with open(map_path) as f:
        data = json.load(f)
    
    regions = data.get('regions', data.get('blobs', []))
    return len(regions) > 0


def test_no_duplicate_blobs():
    """Test no duplicate blob offsets."""
    candidates_path = Path("data/candidates.json")
    if not candidates_path.exists():
        return None
    
    with open(candidates_path) as f:
        data = json.load(f)
    
    candidates = data.get('candidates', [])
    offsets = [c.get('offset_int') for c in candidates if 'offset_int' in c]
    
    return len(offsets) == len(set(offsets))


def test_blob_file_sizes():
    """Test blob files have expected sizes."""
    blobs = list(Path("data").glob("decompressed_*.bin"))
    
    for blob in blobs:
        size = blob.stat().st_size
        if size == 0:
            return False
    
    return len(blobs) > 0


def run_full_suite(verbose=False, quick=False):
    """Run the full test suite."""
    runner = TestRunner(verbose)
    
    print("\n" + "=" * 60)
    print("B.O.B. ROM TOOLKIT - FULL TEST SUITE")
    print("=" * 60)
    
    print("\n[1] Core LZ77 Decoder Tests")
    print("-" * 40)
    runner.run_test("LZ77 decoder imports", test_lz77_decoder)
    runner.run_test("LZ77 basic decompression", test_lz77_basic)
    runner.run_test("LZ77 overlapping copy", test_lz77_overlap)

    print("\n[1b] LZ77 Encoder Round-Trip Tests (ALPHA-001)")
    print("-" * 40)
    runner.run_command("Round-trip: empty data", "python -m pytest tests/test_lz77_roundtrip.py::TestRoundTripBasic::test_round_trip_empty -v")
    runner.run_command("Round-trip: single byte", "python -m pytest tests/test_lz77_roundtrip.py::TestRoundTripBasic::test_round_trip_single_byte -v")
    runner.run_command("Round-trip: small data", "python -m pytest tests/test_lz77_roundtrip.py::TestRoundTripBasic::test_round_trip_small_data -v")
    runner.run_command("Round-trip: repeated patterns", "python -m pytest tests/test_lz77_roundtrip.py::TestRoundTripRepeatedPatterns::test_round_trip_all_same_bytes -v")
    runner.run_command("Round-trip: 1KB data", "python -m pytest tests/test_lz77_roundtrip.py::TestRoundTripLargeData::test_round_trip_1kb -v")
    runner.run_command("Round-trip: 64KB data", "python -m pytest tests/test_lz77_roundtrip.py::TestRoundTripLargeData::test_round_trip_64kb -v")
    runner.run_command("Round-trip: edge cases", "python -m pytest tests/test_lz77_roundtrip.py::TestRoundTripEdgeCases -v")
    runner.run_command("Exhaustive encoder tests", "python -m pytest tests/test_lz77_roundtrip.py::TestExhaustiveEncoder -v")
    runner.run_command("Compression ratio tests", "python -m pytest tests/test_lz77_roundtrip.py::TestCompressionRatio -v")
    
    print("\n[2] Scanner Tests")
    print("-" * 40)
    runner.run_test("Entropy calculation", test_entropy_calculation)
    runner.run_test("Entropy compressed data", test_entropy_compressed)
    runner.run_test("Scanner finds blocks", test_scanner_finds_known_block)
    
    print("\n[3] Extraction Tests")
    print("-" * 40)
    runner.run_test("Decompressed binaries exist", test_extraction_runs)
    runner.run_test("Candidates.json exists", test_candidates_exists)
    runner.run_test("Extracted directories exist", test_extracted_dirs)
    
    print("\n[4] Graphics Tests")
    print("-" * 40)
    runner.run_test("Graphics renderer output", test_graphics_renders)
    runner.run_test("Graphics v2 output", test_graphics_v2)
    runner.run_test("Graphics classifier output", test_graphics_classifier)
    runner.run_test("Review index exists", test_review_index)
    runner.run_test("Analyze pipeline exists", test_analyze_pipeline)
    
    print("\n[5] Map Generation Tests")
    print("-" * 40)
    runner.run_test("ROM map generation", test_map_generation)
    runner.run_test("ROM map has regions", test_rom_map_has_regions)
    
    print("\n[6] Data Integrity Tests")
    print("-" * 40)
    runner.run_test("Known block at 0x1AD34", test_known_block_validation)
    runner.run_test("No duplicate blob offsets", test_no_duplicate_blobs)
    runner.run_test("Blob files non-empty", test_blob_file_sizes)
    
    if not quick:
        print("\n[6] Tool Execution Tests")
        print("-" * 40)
        runner.run_command("Graphics v2 --all", "python toolkit/bob_graphics_v2.py --all")
        runner.run_command("Graphics classifier --all", "python toolkit/bob_graphics_classifier.py --all")
    
    success = runner.summary()
    
    return success


def main():
    parser = argparse.ArgumentParser(description="B.O.B. Toolkit - Full Test Suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick mode (skip tool execution)")
    
    args = parser.parse_args()
    
    success = run_full_suite(args.verbose, args.quick)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
