# test_workflow.ps1 - Example workflow for analyzing B.O.B. ROM
# Compatible with Windows PowerShell 5.1

$ErrorActionPreference = "Stop"

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$RomDir     = Join-Path $ScriptDir "..\rom"
$ToolkitDir = Join-Path $ScriptDir "..\Toolkit"
$OutputDir  = Join-Path $ScriptDir "analysis_output"

Write-Host "========================================"
Write-Host "B.O.B. ROM Analysis Workflow"
Write-Host "========================================"
Write-Host ""

# Check if ROM file provided
$DefaultRom = "B.O.B. (U) [!].smc"

if ($args.Count -eq 0) {
    Write-Host "No ROM specified, using default: $DefaultRom"
    $RomArg = $DefaultRom
}
else {
    $RomArg = $args[0]
}

# Resolve ROM path
if (Test-Path $RomArg -PathType Leaf) {
    $RomFile = $RomArg
}
elseif (Test-Path (Join-Path $RomDir $RomArg) -PathType Leaf) {
    $RomFile = Join-Path $RomDir $RomArg
}
else {
    Write-Error "Error: ROM file not found: $RomArg"
    exit 1
}

Write-Host ("✓ ROM file: {0}" -f $RomFile)
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}
Write-Host ("✓ Output directory: {0}\" -f $OutputDir)
Write-Host ""

# Step 1: Run decoder unit tests
Write-Host "Step 1: Testing LZ decoder..."
python (Join-Path $ToolkitDir "bob_lz.py")
Write-Host ""

# Step 2: Scan ROM for compressed blocks
Write-Host "Step 2: Scanning ROM for compressed blocks..."
python (Join-Path $ToolkitDir "bob_lz_scan.py") `
    --rom "$RomFile" `
    --outdir "$OutputDir"
Write-Host ""

# Step 3: Generate ROM map
Write-Host "Step 3: Generating ROM memory map..."
python (Join-Path $ToolkitDir "bob_map.py") `
    --rom "$RomFile" `
    --candidates (Join-Path $OutputDir "candidates.json") `
    --outdir "$OutputDir"
Write-Host ""

# Summary
Write-Host "========================================"
Write-Host "Analysis Complete!"
Write-Host "========================================"
Write-Host ""
Write-Host "Generated files:"
Write-Host "  $OutputDir\candidates.json      - Compressed block candidates"
Write-Host "  $OutputDir\rom_map.json         - ROM region classifications"
Write-Host "  $OutputDir\rom_map.html         - Interactive visualization"
Write-Host "  $OutputDir\decompressed_*.bin   - Decompressed data files"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Open $OutputDir\rom_map.html in your browser"
Write-Host "  2. Review $OutputDir\candidates.json for compressed blocks"
Write-Host "  3. Import $OutputDir\rom_map.json into Ghidra (see ghidra_import.txt)"
Write-Host ""
Write-Host "For Ghidra import instructions, see: ghidra_import.txt"
Write-Host ""
