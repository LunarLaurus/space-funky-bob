# B.O.B. Level Editor - Visualize Levels
# Usage: .\visualize_levels.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$ToolkitDir = Join-Path $ProjectDir "toolkit"
$DataDir = Join-Path $ProjectDir "data\levels"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "B.O.B. Level Editor - Visualize" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for tilemaps
$Tilemaps = Get-ChildItem -Path $DataDir -Filter "tilemap_*.bin" -ErrorAction SilentlyContinue
if (-not $Tilemaps) {
    Write-Host "ERROR: No tilemaps found. Run extract_levels.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "Found $($Tilemaps.Count) tilemaps" -ForegroundColor Green
Write-Host ""

# Generate visualization
$OutputFile = Join-Path $DataDir "levels.html"
Write-Host "Generating HTML visualization..." -ForegroundColor Yellow

python (Join-Path $ToolkitDir "bob_visualize.py") --tiledir $DataDir --output $OutputFile --limit 50

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Visualization complete!" -ForegroundColor Green
    Write-Host "Open in browser: $OutputFile" -ForegroundColor Cyan
    
    # Try to open in browser
    try {
        Start-Process $OutputFile
    } catch {
        Write-Host "(Browser auto-open failed - open manually)" -ForegroundColor Yellow
    }
} else {
    Write-Host "Visualization failed!" -ForegroundColor Red
    exit 1
}
