# B.O.B. Level Editor - Scan for Compressed Blocks
# Usage: .\scan_compressed.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$ToolkitDir = Join-Path $ProjectDir "toolkit"
$RomDir = Join-Path $ProjectDir "rom"
$OutputDir = Join-Path $ProjectDir "data\compressed"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "B.O.B. Level Editor - Scan Compressed" -ForegroundColor Cyan
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
Write-Host "Output: $OutputDir" -ForegroundColor Green
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Run scanner
Write-Host "Scanning for compressed blocks..." -ForegroundColor Yellow

python (Join-Path $ToolkitDir "bob_lz_scan.py") --rom $RomFile.FullName --outdir $OutputDir

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Scan complete!" -ForegroundColor Green
    
    # Show results
    $CandidatesFile = Join-Path $OutputDir "candidates.json"
    if (Test-Path $CandidatesFile) {
        $Data = Get-Content $CandidatesFile | ConvertFrom-Json
        Write-Host "Found: $($Data.num_candidates) compressed blocks" -ForegroundColor Cyan
        
        Write-Host ""
        Write-Host "Compressed blocks found:" -ForegroundColor Yellow
        foreach ($cand in $Data.candidates) {
            Write-Host "  $($cand.offset): $($cand.compressed_size) -> $($cand.decompressed_size) bytes [$($cand.reason)]"
        }
    }
    
    Write-Host ""
    Write-Host "Files saved to: $OutputDir" -ForegroundColor Green
} else {
    Write-Host "Scan failed!" -ForegroundColor Red
    exit 1
}
