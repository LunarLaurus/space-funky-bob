# B.O.B. Level Editor - Extract All Levels
# Usage: .\extract_levels.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$ToolkitDir = Join-Path $ProjectDir "toolkit"
$RomDir = Join-Path $ProjectDir "rom"
$DataDir = Join-Path $ProjectDir "data\levels"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "B.O.B. Level Editor - Extract" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find ROM
$RomFile = Get-ChildItem -Path $RomDir -Filter "*.smc" | Select-Object -First 1
if (-not $RomFile) {
    $RomFile = Get-ChildItem -Path $RomDir -Filter "*.sfc" | Select-Object -First 1
}

if (-not $RomFile) {
    Write-Host "ERROR: No ROM file found in $RomDir" -ForegroundColor Red
    exit 1
}

Write-Host "ROM: $($RomFile.Name)" -ForegroundColor Green
Write-Host "Output: $DataDir" -ForegroundColor Green
Write-Host ""

# Create output directory
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
}

# Run extraction
Write-Host "Extracting tilemaps..." -ForegroundColor Yellow
python (Join-Path $ToolkitDir "bob_extract_levels.py") --rom $RomFile.FullName --outdir $DataDir

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Extraction complete!" -ForegroundColor Green
    Write-Host "Found tilemaps in: $DataDir" -ForegroundColor Green
    
    # Count files
    $Count = (Get-ChildItem -Path $DataDir -Filter "tilemap_*.bin").Count
    Write-Host "Extracted: $Count tilemaps" -ForegroundColor Cyan
} else {
    Write-Host "Extraction failed!" -ForegroundColor Red
    exit 1
}
