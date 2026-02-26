# B.O.B. Level Editor - Full Workflow
# Usage: .\run_workflow.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  B.O.B. FULL WORKFLOW  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Extract
Write-Host "[1/3] Extracting tilemaps..." -ForegroundColor Yellow
& "$ProjectDir\scripts\extract_levels.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Extraction failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] Generating visualization..." -ForegroundColor Yellow
& "$ProjectDir\scripts\visualize_levels.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Visualization failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/3] Scanning for compressed blocks..." -ForegroundColor Yellow
& "$ProjectDir\scripts\scan_compressed.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  FULL WORKFLOW COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open data/levels/levels.html to view tilemaps" -ForegroundColor White
Write-Host "  2. Edit tilemap .bin files in data/levels/" -ForegroundColor White
Write-Host "  3. Run: .\scripts\inject_tilemap.ps1" -ForegroundColor White
Write-Host "  4. Test modified ROM in emulator" -ForegroundColor White
Write-Host ""
