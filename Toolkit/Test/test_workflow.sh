#!/bin/bash
# test_workflow.sh - Example workflow for analyzing B.O.B. ROM

set -e

echo "========================================"
echo "B.O.B. ROM Analysis Workflow"
echo "========================================"
echo ""

# Check if ROM file provided
if [ $# -eq 0 ]; then
    echo "Usage: ./test_workflow.sh <path_to_bob_rom.sfc>"
    echo ""
    echo "Example:"
    echo "  ./test_workflow.sh SpaceFunkyBob.sfc"
    exit 1
fi

ROM_FILE="$1"

if [ ! -f "$ROM_FILE" ]; then
    echo "Error: ROM file not found: $ROM_FILE"
    exit 1
fi

echo "✓ ROM file: $ROM_FILE"
echo ""

# Create output directory
OUTPUT_DIR="analysis_output"
mkdir -p "$OUTPUT_DIR"
echo "✓ Output directory: $OUTPUT_DIR/"
echo ""

# Step 1: Run decoder unit tests
echo "Step 1: Testing LZ decoder..."
python bob_lz.py
echo ""

# Step 2: Scan ROM for compressed blocks
echo "Step 2: Scanning ROM for compressed blocks..."
python bob_lz_scan.py --rom "$ROM_FILE" --outdir "$OUTPUT_DIR"
echo ""

# Step 3: Generate ROM map
echo "Step 3: Generating ROM memory map..."
python bob_map.py --rom "$ROM_FILE" --candidates "$OUTPUT_DIR/candidates.json" --outdir "$OUTPUT_DIR"
echo ""

# Summary
echo "========================================"
echo "Analysis Complete!"
echo "========================================"
echo ""
echo "Generated files:"
echo "  📄 $OUTPUT_DIR/candidates.json      - Compressed block candidates"
echo "  📄 $OUTPUT_DIR/rom_map.json         - ROM region classifications"
echo "  🌐 $OUTPUT_DIR/rom_map.html         - Interactive visualization"
echo "  📦 $OUTPUT_DIR/decompressed_*.bin   - Decompressed data files"
echo ""
echo "Next steps:"
echo "  1. Open $OUTPUT_DIR/rom_map.html in your browser"
echo "  2. Review $OUTPUT_DIR/candidates.json for compressed blocks"
echo "  3. Import $OUTPUT_DIR/rom_map.json into Ghidra (see ghidra_import.txt)"
echo ""
echo "For Ghidra import instructions, see: ghidra_import.txt"
echo ""
