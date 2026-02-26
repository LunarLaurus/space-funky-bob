# B.O.B. Level Editor - Main Menu
# Usage: .\editor.ps1

$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

function Get-RomFile {
    $RomDir = Join-Path $ProjectDir "rom"
    $Rom = Get-ChildItem -Path $RomDir -Filter "*.smc" | Select-Object -First 1
    if (-not $Rom) {
        $Rom = Get-ChildItem -Path $RomDir -Filter "*.sfc" | Select-Object -First 1
    }
    return $Rom
}

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "      B.O.B. LEVEL EDITOR             " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Extract All Tilemaps" -ForegroundColor White
    Write-Host "  2. Visualize Tilemaps (HTML)" -ForegroundColor White
    Write-Host "  3. Scan Compressed Blocks" -ForegroundColor White
    Write-Host "  4. Inject Modified Tilemap" -ForegroundColor White
    Write-Host "  5. Compress and Inject Graphics" -ForegroundColor White
    Write-Host "  6. List Extracted Levels" -ForegroundColor White
    Write-Host ""
    Write-Host "  0. Exit" -ForegroundColor Gray
    Write-Host ""
}

while ($true) {
    Show-Menu
    
    $Choice = Read-Host "Select option"
    
    switch ($Choice) {
        "1" {
            Write-Host ""
            Write-Host "Extracting tilemaps..." -ForegroundColor Yellow
            & "$ProjectDir\scripts\extract_levels.ps1"
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        
        "2" {
            Write-Host ""
            Write-Host "Generating visualization..." -ForegroundColor Yellow
            & "$ProjectDir\scripts\visualize_levels.ps1"
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        
        "3" {
            Write-Host ""
            Write-Host "Scanning for compressed blocks..." -ForegroundColor Yellow
            & "$ProjectDir\scripts\scan_compressed.ps1"
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        
        "4" {
            Write-Host ""
            
            $DataDir = Join-Path $ProjectDir "data\levels"
            $Tilemaps = Get-ChildItem -Path $DataDir -Filter "tilemap_*.bin" -ErrorAction SilentlyContinue
            
            if (-not $Tilemaps) {
                Write-Host "No tilemaps found. Run option 1 first." -ForegroundColor Red
                Read-Host "Press Enter to continue"
                continue
            }
            
            Write-Host "Available tilemaps:" -ForegroundColor Cyan
            $i = 0
            foreach ($t in $Tilemaps) {
                $parts = $t.Name -split '_'
                if ($parts.Count -ge 3) {
                    $offset = $parts[-1] -replace '\.bin$',''
                    Write-Host "  [$i] $($t.Name) - Offset: 0x$offset" -ForegroundColor Gray
                }
                $i++
            }
            
            Write-Host ""
            $Sel = Read-Host "Enter tilemap number or filename"
            
            if ($Sel -match '^\d+$') {
                $Selected = $Tilemaps[$Sel]
            } else {
                $Selected = $Tilemaps | Where-Object { $_.Name -like "*$Sel*" } | Select-Object -First 1
            }
            
            if ($Selected) {
                $parts = $Selected.Name -split '_'
                $Offset = $parts[-1] -replace '\.bin$',''
                
                Write-Host "Selected: $($Selected.Name)" -ForegroundColor Green
                $OffsetInput = Read-Host "Offset (press Enter for 0x$Offset)"
                
                if (-not $OffsetInput) {
                    $OffsetInput = "0x$Offset"
                }
                
                & "$ProjectDir\scripts\inject_tilemap.ps1" -TilemapFile $Selected.Name -Offset $OffsetInput
            } else {
                Write-Host "Tilemap not found" -ForegroundColor Red
            }
            
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        
        "5" {
            Write-Host ""
            Write-Host "Compress and inject graphics..." -ForegroundColor Yellow
            
            $SourceFile = Read-Host "Uncompressed file path (or Enter to cancel)"
            
            if ($SourceFile -and (Test-Path $SourceFile)) {
                $Offset = Read-Host "Target offset (hex, e.g. 0x030000)"
                
                $Rom = Get-RomFile
                if ($Rom) {
                    $OutFile = $Rom.FullName -replace '(\.smc|\.sfc)$', '_modified$1'
                    
                    python "$ProjectDir\toolkit\bob_inject.py" --rom $Rom.FullName --uncompressed $SourceFile --offset $Offset --output $OutFile
                }
            }
            
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        
        "6" {
            Write-Host ""
            $DataDir = Join-Path $ProjectDir "data\levels"
            $Tilemaps = Get-ChildItem -Path $DataDir -Filter "tilemap_*.bin" -ErrorAction SilentlyContinue
            
            if ($Tilemaps) {
                Write-Host "Extracted tilemaps ($($Tilemaps.Count)):" -ForegroundColor Cyan
                Write-Host ""
                
                $i = 0
                foreach ($t in $Tilemaps) {
                    $sizeKB = [math]::Round($t.Length / 1KB, 1)
                    Write-Host "  [$i] $($t.Name) ($sizeKB KB)" -ForegroundColor Gray
                    $i++
                }
            } else {
                Write-Host "No tilemaps extracted yet. Run option 1." -ForegroundColor Yellow
            }
            
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        
        "0" {
            Write-Host ""
            Write-Host "Goodbye, Commander!" -ForegroundColor Cyan
            Write-Host ""
            break
        }
        
        default {
            Write-Host "Invalid option" -ForegroundColor Red
            Start-Sleep -Milliseconds 500
        }
    }
}
