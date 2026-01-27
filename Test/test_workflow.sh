#!/bin/bash
# test_workflow.sh - Example workflow for analyzing B.O.B. ROM

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROM_DIR="$SCRIPT_DIR/../rom"
TOOLKIT_DIR="$SCRIPT_DIR/../Toolkit"
OUTPUT_DIR="$SCRIPT_DIR/analysis_output"

echo "========================================"
echo "B.O.B. ROM Analysis Workflow"
echo "========================================"
echo ""

# Check if ROM file provided as argument
DEFAULT_ROM="B.O.B. (U) [!].smc"

if [ $# -eq 0 ]; then
    echo "No ROM specified, using default: $DEFAULT_ROM"
    ROM_ARG="$DEFAULT_ROM"
else
    ROM_ARG="$1"
fi


ROM_ARG="$1"

# Resolve ROM path
if [ -f "$ROM_ARG" ]; then
    ROM_FILE="$ROM_ARG"
elif [ -f "$ROM_DIR/$ROM_ARG" ]; then
    ROM_FILE="$ROM_DIR/$ROM_ARG"
else
    echo "Error: ROM file not found: $ROM_ARG"
    exit 1
fi

echo "✓ ROM file: $ROM_FILE"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"
echo "✓ Output directory: $OUTPUT_DIR/"
echo ""

# Step 1: Run decoder unit tests
echo "Step 1: Testing LZ decoder..."
python "$TOOLKIT_DIR/bob_lz.py"
echo ""

# Step 2: Scan ROM for compressed blocks
echo "Step 2: Scanning ROM for compressed blocks..."
python "$TOOLKIT_DIR/bob_lz_scan.py" \
    --rom "$ROM_FILE" \
    --outdir "$OUTPUT_DIR"
echo ""

# Step 3: Generate ROM map
echo "Step 3: Generating ROM memory map..."
python "$TOOLKIT_DIR/bob_map.py" \
    --rom "$ROM_FILE" \
    --candidates "$OUTPUT_DIR/candidates.json" \
    --outdir "$OUTPUT_DIR"
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
