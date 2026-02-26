# B.O.B. Level Editor - Inject Modified Tilemap
# Usage: .\inject_tilemap.ps1 -TilemapFile "tilemap_04_02A000.bin" -Offset 0x02A000

param(
    [Parameter(Mandatory=$true)]
    [string]$TilemapFile,
    
    [Parameter(Mandatory=$true)]
    [string]$Offset,
    
    [string]$OutputFile = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$ToolkitDir = Join-Path $ProjectDir "toolkit"
$RomDir = Join-Path $ProjectDir "rom"
$DataDir = Join-Path $ProjectDir "data\levels"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "B.O.B. Level Editor - Inject" -ForegroundColor Cyan
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

Write-Host "Source ROM: $($RomFile.Name)" -ForegroundColor Green
Write-Host "Tilemap: $TilemapFile" -ForegroundColor Green
Write-Host "Offset: $Offset" -ForegroundColor Green
Write-Host ""

# Resolve tilemap path
$TilemapPath = $TilemapFile
if (-not (Test-Path $TilemapFile)) {
    $TilemapPath = Join-Path $DataDir $TilemapFile
}

if (-not (Test-Path $TilemapPath)) {
    Write-Host "ERROR: Tilemap file not found: $TilemapFile" -ForegroundColor Red
    exit 1
}

# Determine output file
if (-not $OutputFile) {
    $RomName = [System.IO.Path]::GetFileNameWithoutExtension($RomFile.Name)
    $RomExt = $RomFile.Extension
    $OutputFile = Join-Path $RomDir "${RomName}_modified${RomExt}"
}

Write-Host "Output: $OutputFile" -ForegroundColor Yellow
Write-Host ""

# Run injection
python (Join-Path $ToolkitDir "bob_inject.py") `
    --rom $RomFile.FullName `
    --tilemap $TilemapPath `
    --offset $Offset `
    --output $OutputFile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Injection complete!" -ForegroundColor Green
    Write-Host "Modified ROM: $OutputFile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Test in emulator" -ForegroundColor Gray
    Write-Host "  2. Create patch: python bob_inject.py --patch original.mod.smc new.mod.smc --output patch.json" -ForegroundColor Gray
} else {
    Write-Host "Injection failed!" -ForegroundColor Red
    exit 1
}
