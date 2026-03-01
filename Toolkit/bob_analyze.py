#!/usr/bin/env python3
"""
bob_analyze.py - End-to-end B.O.B. ROM Analysis Pipeline

Complete analysis pipeline: scan -> extract -> classify -> render.

Usage:
    python toolkit/bob_analyze.py rom/B.O.B..smc
    python toolkit/bob_analyze.py --rom rom/B.O.B..smc --output data
"""

import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run_step(name, cmd, required=True):
    """Run a pipeline step."""
    log(f"Running: {name}")
    log(f"  Command: {cmd}")
    
    import subprocess
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        log(f"  ERROR: {result.stderr[:200] if result.stderr else 'Unknown error'}")
        return False
    
    if result.stdout:
        for line in result.stdout.strip().split('\n')[:5]:
            log(f"  {line}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="B.O.B. ROM Analysis Pipeline")
    parser.add_argument("--rom", "-r", help="ROM file path")
    parser.add_argument("--output", "-o", default="data", help="Output directory")
    parser.add_argument("--skip-scan", action="store_true", help="Skip scanning (use existing)")
    parser.add_argument("--skip-extract", action="store_true", help="Skip extraction")
    parser.add_argument("--skip-graphics", action="store_true", help="Skip graphics rendering")
    parser.add_argument("--graphics-only", action="store_true", help="Only render graphics")
    
    args = parser.parse_args()
    
    rom_path = args.rom
    output_dir = Path(args.output)
    
    print("=" * 60)
    print("B.O.B. ROM ANALYSIS PIPELINE")
    print("=" * 60)
    print(f"ROM: {rom_path}")
    print(f"Output: {output_dir}")
    print("=" * 60)
    
    if args.graphics_only:
        log("Mode: Graphics only")
        
        # Just run graphics
        run_step("Graphics v2", f"python toolkit/bob_graphics_v2.py --all --output {output_dir}/gfx_v2")
        run_step("Graphics classifier", f"python toolkit/bob_graphics_classifier.py --all --output {output_dir}/gfx_classified")
        
        log("Done!")
        return
    
    # Validate ROM path
    if not rom_path:
        log("Error: --rom required")
        return
    
    if not Path(rom_path).exists():
        log(f"Error: ROM file not found: {rom_path}")
        return
    
    # Step 1: Scan ROM for compressed blocks
    log("Step 1: Scanning ROM for compressed blocks...")
    if not run_step("Scanner", f"python toolkit/bob_lz_scan.py --rom {rom_path} --output {output_dir}"):
        log("Scanner failed, exiting")
        return
    
    if not args.skip_extract:
        # Step 2: Extract all blobs
        log("Step 2: Extracting all regions...")
        if not run_step("Extractor", f"python toolkit/bob_extract.py --candidates {output_dir}/candidates.json --output {output_dir}"):
            log("Extractor failed")
    
    if not args.skip_graphics:
        # Step 3: Render graphics
        log("Step 3: Rendering graphics...")
        run_step("Graphics v2", f"python toolkit/bob_graphics_v2.py --all --output {output_dir}/gfx_v2")
        run_step("Graphics classifier", f"python toolkit/bob_graphics_classifier.py --all --output {output_dir}/gfx_classified")
        run_step("Graphics test suite", f"python toolkit/bob_graphics_test_suite.py --all --limit 10 --output {output_dir}/gfx_review")
    
    # Step 4: Generate reports
    log("Step 4: Generating reports...")
    
    # Count outputs
    blobs = list(output_dir.glob("decompressed_*.bin"))
    pngs_v2 = list(output_dir.glob("gfx_v2/*.png"))
    pngs_classified = list(output_dir.glob("gfx_classified/*.png"))
    candidates = output_dir / "candidates.json"
    
    if candidates.exists():
        with open(candidates) as f:
            cand_data = json.load(f)
        num_blocks = len(cand_data.get('blocks', []))
    else:
        num_blocks = 0
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Compressed blocks found: {num_blocks}")
    print(f"  Decompressed blobs: {len(blobs)}")
    print(f"  Graphics v2 rendered: {len(pngs_v2)}")
    print(f"  Graphics classified: {len(pngs_classified)}")
    print("=" * 60)
    
    log("Analysis complete!")


if __name__ == "__main__":
    main()
