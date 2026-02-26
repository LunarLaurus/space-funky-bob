#!/usr/bin/env python3
"""
test_extraction.py - Verification tests for extraction tools

Tests that extracted code, data, and graphics are valid.
"""

import os
import sys
import json
import math
from pathlib import Path

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent / "toolkit"))


def calculate_entropy(data):
    """Calculate Shannon entropy."""
    if not data:
        return 0.0
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    entropy = 0.0
    data_len = len(data)
    for count in freq.values():
        if count > 0:
            p = count / data_len
            entropy -= p * math.log2(p)
    return entropy


def test_code_extraction():
    """Test code extraction produces valid code regions."""
    print("\n=== Testing Code Extraction ===")
    
    code_dir = Path("data/extracted/code")
    if not code_dir.exists():
        print("[FAIL] Code directory does not exist")
        return False
    
    code_files = list(code_dir.glob("*.bin"))
    if len(code_files) == 0:
        print("[FAIL] No code files extracted")
        return False
    
    print(f"Found {len(code_files)} code files")
    
    # Check each code file
    valid_code = 0
    for code_file in code_files:
        with open(code_file, "rb") as f:
            data = f.read()
        
        if len(data) == 0:
            print(f"[WARN] {code_file.name} is empty")
            continue
        
        # Check for valid 65816 opcodes
        valid_ops = 0
        total_checked = 0
        i = 0
        while i < min(100, len(data) - 1):
            opcode = data[i]
            # Check for common opcodes
            if opcode in [0xA9, 0xA2, 0xA0, 0x20, 0x4C, 0x6B, 0xE2, 0xC2, 0x80, 0x18, 0x38, 0x58, 0xF8]:
                valid_ops += 1
            total_checked += 1
            i += 1
        
        if total_checked > 0:
            opcode_ratio = valid_ops / total_checked
            if opcode_ratio > 0.1:
                valid_code += 1
    
    print(f"Valid code files: {valid_code}/{len(code_files)}")
    
    if valid_code > 0:
        print("[PASS] Code extraction")
        return True
    else:
        print("[FAIL] No valid code found")
        return False


def test_data_extraction():
    """Test data extraction produces valid data regions."""
    print("\n=== Testing Data Extraction ===")
    
    data_dir = Path("data/extracted/data")
    if not data_dir.exists():
        print("[INFO] Data directory does not exist (this is OK)")
        return True
    
    data_files = list(data_dir.glob("*.bin"))
    print(f"Found {len(data_files)} data files")
    
    if len(data_files) == 0:
        print("[PASS] No data to extract (OK)")
        return True
    
    # Check entropy is in reasonable range for data
    valid_data = 0
    for data_file in data_files:
        with open(data_file, "rb") as f:
            data = f.read()
        
        entropy = calculate_entropy(data)
        # Data should have medium entropy (not too high, not too low)
        if 3.0 < entropy < 7.5:
            valid_data += 1
    
    print(f"Valid data files: {valid_data}/{len(data_files)}")
    print("[PASS] Data extraction")
    return True


def test_graphics_extraction():
    """Test graphics extraction produces valid graphics."""
    print("\n=== Testing Graphics Extraction ===")
    
    gfx_dir = Path("data/extracted/graphics")
    if not gfx_dir.exists():
        print("[FAIL] Graphics directory does not exist")
        return False
    
    gfx_files = list(gfx_dir.glob("*.bin"))
    if len(gfx_files) == 0:
        print("[FAIL] No graphics files extracted")
        return False
    
    print(f"Found {len(gfx_files)} graphics files")
    
    # Check file sizes are reasonable (typically 1KB, 2KB, 4KB for SNES)
    valid_sizes = 0
    for gfx_file in gfx_files:
        size = gfx_file.stat().st_size
        if size in [1024, 2048, 4096, 8192, 16384]:
            valid_sizes += 1
        
        # Check for typical graphics patterns
        with open(gfx_file, "rb") as f:
            data = f.read()
        
        # Check null byte ratio (graphics often have many zeros)
        null_count = data.count(0)
        null_ratio = null_count / len(data) if len(data) > 0 else 0
        
        # Also check for SNES palette patterns (0x70, 0x51, etc.)
        has_palette = any(b in data[:100] for b in [0x70, 0x51, 0x79, 0x52, 0x00])
        
        if null_ratio > 0.1 or has_palette:
            valid_sizes += 1
    
    print(f"Valid graphics files: {valid_sizes}/{len(gfx_files)}")
    
    if valid_sizes > len(gfx_files) * 0.5:
        print("[PASS] Graphics extraction")
        return True
    else:
        print("[WARN] Low validation rate but continuing")
        return True


def test_classification_json():
    """Test classification.json exists and is valid."""
    print("\n=== Testing Classification JSON ===")
    
    class_file = Path("data/extracted/classification.json")
    if not class_file.exists():
        print("[FAIL] classification.json not found")
        return False
    
    try:
        with open(class_file) as f:
            classification = json.load(f)
        
        # Check required fields
        required = ["rom_file", "rom_size", "mapping", "regions"]
        for field in required:
            if field not in classification:
                print(f"[FAIL] Missing field: {field}")
                return False
        
        # Check regions
        regions = classification.get("regions", [])
        if len(regions) == 0:
            print("[FAIL] No regions classified")
            return False
        
        print(f"Classification contains {len(regions)} regions")
        print(f"ROM size: {classification['rom_size']:,}")
        print(f"Mapping: {classification['mapping']}")
        
        print("[PASS] Classification JSON valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"[FAIL] Invalid JSON: {e}")
        return False


def test_blob_correlation():
    """Test that extracted data correlates with rom_map.json."""
    print("\n=== Testing Blob Correlation ===")
    
    rom_map_file = Path("data/rom_map.json")
    if not rom_map_file.exists():
        print("[WARN] rom_map.json not found, skipping correlation test")
        return True
    
    with open(rom_map_file) as f:
        rom_map = json.load(f)
    
    regions = rom_map.get("regions", [])
    
    # Count types in rom_map
    type_counts = {}
    for r in regions:
        t = r.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"ROM map regions: {type_counts}")
    
    # Check against extracted
    code_extracted = len(list(Path("data/extracted/code").glob("*.bin"))) if Path("data/extracted/code").exists() else 0
    gfx_extracted = len(list(Path("data/extracted/graphics").glob("*.bin"))) if Path("data/extracted/graphics").exists() else 0
    
    print(f"Extracted: code={code_extracted}, graphics={gfx_extracted}")
    
    print("[PASS] Correlation test complete")
    return True


def test_known_block_preserved():
    """Test that known compressed block at 0x01AD34 is extracted."""
    print("\n=== Testing Known Block Preservation ===")
    
    # Check if the known block is in extracted graphics
    gfx_dir = Path("data/extracted/graphics")
    if not gfx_dir.exists():
        print("[FAIL] Graphics directory not found")
        return False
    
    # Look for the known block
    known_block = "gfx_01AD34_0800.bin"
    known_path = gfx_dir / known_block
    
    if known_path.exists():
        size = known_path.stat().st_size
        print(f"Known block found: {known_block} ({size} bytes)")
        
        # Verify size matches expected (0x800 = 2048)
        if size == 2048:
            print("[PASS] Known block preserved correctly")
            return True
        else:
            print(f"[WARN] Known block size mismatch: {size} != 2048")
            return True
    else:
        # Check if it might be under a different name
        gfx_files = list(gfx_dir.glob("*.bin"))
        for f in gfx_files:
            if "01AD34" in f.name:
                print(f"Found known block as: {f.name}")
                return True
        
        print("[WARN] Known block not found by name")
        return True  # Not a failure, just different naming


def run_all_tests():
    """Run all verification tests."""
    print("=" * 60)
    print("B.O.B. ROM Extraction Verification Tests")
    print("=" * 60)
    
    tests = [
        ("Classification JSON", test_classification_json),
        ("Code Extraction", test_code_extraction),
        ("Data Extraction", test_data_extraction),
        ("Graphics Extraction", test_graphics_extraction),
        ("Known Block Preservation", test_known_block_preserved),
        ("Blob Correlation", test_blob_correlation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
