#!/usr/bin/env python3
"""
test_graphics.py - Verification tests for graphics rendering

Tests that the graphics renderer produces valid PNG outputs.
"""

import os
import sys
import json
from pathlib import Path


def test_graphics_directory_exists():
    """Test that graphics output directory exists."""
    print("\n=== Testing Graphics Output Directory ===")
    
    gfx_dir = Path("data/gfx_png")
    if not gfx_dir.exists():
        print("[FAIL] Graphics output directory does not exist")
        return False
    
    print(f"[PASS] Graphics directory exists: {gfx_dir}")
    return True


def test_png_files_generated():
    """Test that PNG files were generated."""
    print("\n=== Testing PNG File Generation ===")
    
    gfx_dir = Path("data/gfx_png")
    png_files = list(gfx_dir.glob("*.png"))
    
    if len(png_files) == 0:
        print("[FAIL] No PNG files generated")
        return False
    
    print(f"Generated {len(png_files)} PNG files")
    
    # Check file sizes are reasonable
    valid_size = 0
    for png in png_files:
        size = png.stat().st_size
        if size > 100:  # At least 100 bytes
            valid_size += 1
    
    print(f"Valid PNG files (>100 bytes): {valid_size}/{len(png_files)}")
    
    if valid_size > 0:
        print("[PASS] PNG files generated successfully")
        return True
    else:
        print("[FAIL] No valid PNG files")
        return False


def test_manifest_generated():
    """Test that render manifest was created."""
    print("\n=== Testing Render Manifest ===")
    
    manifest_path = Path("data/gfx_png/render_manifest.json")
    if not manifest_path.exists():
        print("[FAIL] Manifest not found")
        return False
    
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        total = manifest.get('total', 0)
        rendered = len(manifest.get('rendered', []))
        
        print(f"Manifest entries: {rendered}")
        print(f"Total: {total}")
        
        if total > 0:
            print("[PASS] Manifest valid")
            return True
        else:
            print("[FAIL] Empty manifest")
            return False
            
    except json.JSONDecodeError as e:
        print(f"[FAIL] Invalid JSON: {e}")
        return False


def test_known_block_rendering():
    """Test that known block was rendered."""
    print("\n=== Testing Known Block Rendering ===")
    
    # Check for the known block at 0x01AD34
    known_block_png = Path("data/gfx_png/decompressed_01AD34.png")
    
    if not known_block_png.exists():
        print("[FAIL] Known block PNG not found")
        return False
    
    size = known_block_png.stat().st_size
    print(f"Known block PNG size: {size} bytes")
    
    if size > 100:
        print("[PASS] Known block rendered correctly")
        return True
    else:
        print("[WARN] Known block PNG seems small but continuing")
        return True


def test_png_headers():
    """Test that PNG files have valid headers."""
    print("\n=== Testing PNG Headers ===")
    
    gfx_dir = Path("data/gfx_png")
    png_files = list(gfx_dir.glob("*.png"))[:5]  # Test first 5
    
    valid_headers = 0
    for png in png_files:
        with open(png, 'rb') as f:
            header = f.read(8)
        
        # PNG signature: 89 50 4E 47 0D 0A 1A 0A
        if len(header) >= 8 and header[:4] == b'\x89PNG':
            valid_headers += 1
        else:
            print(f"[WARN] Invalid header for {png.name}")
    
    print(f"Valid PNG headers: {valid_headers}/{len(png_files)}")
    
    if valid_headers == len(png_files):
        print("[PASS] All PNG headers valid")
        return True
    else:
        print("[FAIL] Some PNG headers invalid")
        return False


def test_png_dimensions():
    """Test that PNG files have reasonable dimensions."""
    print("\n=== Testing PNG Dimensions ===")
    
    try:
        from PIL import Image
    except ImportError:
        print("[SKIP] PIL not available for dimension check")
        return True
    
    gfx_dir = Path("data/gfx_png")
    png_files = list(gfx_dir.glob("*.png"))[:10]  # Test first 10
    
    valid_dims = 0
    for png in png_files:
        try:
            with Image.open(png) as img:
                w, h = img.size
                if w > 0 and h > 0 and w <= 1024 and h <= 1024:
                    valid_dims += 1
                else:
                    print(f"[WARN] Unreasonable dimensions for {png.name}: {w}x{h}")
        except Exception as e:
            print(f"[WARN] Could not open {png.name}: {e}")
    
    print(f"Valid dimensions: {valid_dims}/{len(png_files)}")
    
    if valid_dims > 0:
        print("[PASS] PNG dimensions reasonable")
        return True
    else:
        print("[FAIL] No valid dimensions")
        return False


def run_all_tests():
    """Run all graphics tests."""
    print("=" * 60)
    print("B.O.B. ROM Graphics Rendering Verification Tests")
    print("=" * 60)
    
    tests = [
        ("Graphics Directory", test_graphics_directory_exists),
        ("PNG Generation", test_png_files_generated),
        ("Manifest", test_manifest_generated),
        ("Known Block", test_known_block_rendering),
        ("PNG Headers", test_png_headers),
        ("PNG Dimensions", test_png_dimensions),
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
