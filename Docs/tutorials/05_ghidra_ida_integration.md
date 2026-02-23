# Tutorial 5: Ghidra and IDA Pro Integration

**Duration:** 20 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Tutorial 2 (Finding Compressed Blocks)

---

## Overview

This tutorial shows you how to import ROM analysis results into reverse engineering tools. You'll learn:

- How to prepare analysis data for import
- How to import into Ghidra
- How to import into IDA Pro
- How to use the imported annotations

---

## Preparing Analysis Data

### Step 1: Run Full Analysis

```bash
# Scan for compressed blocks
python toolkit/bob_lz_scan.py --rom rom/B.O.B..smc --outdir out/ --multipass

# Generate ROM map
python toolkit/bob_map.py --rom rom/B.O.B..smc --candidates out/candidates.json --outdir out/
```

### Step 2: Verify Output

Check `out/rom_map.json`:

```json
{
  "rom_file": "rom/B.O.B..smc",
  "rom_size": 1048576,
  "rom_mapping": "LoROM",
  "header_offset": 0,
  "num_regions": 50,
  "regions": [
    {
      "type": "code",
      "start": 0,
      "end": 65536,
      "size": 65536,
      "start_hex": "0x000000",
      "end_hex": "0x010000",
      "size_hex": "0x10000",
      "confidence": 0.95
    },
    ...
  ]
}
```

---

## Importing into Ghidra

### Step 1: Open ROM in Ghidra

1. Launch Ghidra
2. File → New Project
3. File → Import File...
4. Select your `B.O.B..smc` ROM
5. Set format to "Binary"
6. Set language to "65816" (SNES)
7. Click OK

### Step 2: Run Import Script

1. Window → Script Manager
2. Click "Refresh" (if needed)
3. Find `ImportBOBMap.py` in the list
4. Double-click to run
5. Select `out/rom_map.json` when prompted

### Step 3: Review Imported Data

The script will:
- **Create segments** for each region
- **Add bookmarks** at region starts
- **Add comments** describing regions
- **Create TilemapEntry data type**
- **Mark vector table** (0x7FE0-0x7FFF)

### Step 4: Navigate Analysis

**View Bookmarks:**
- Window → Open Subviews → Bookmarks
- Browse regions by type

**View Data Types:**
- Window → Data Type Manager
- Find `TilemapEntry` structure

**View Comments:**
- Hover over addresses to see comments
- Or press `E` to edit/view comments

---

## Importing into IDA Pro

### Step 1: Open ROM in IDA

1. Launch IDA Pro
2. File → Open
3. Select your `B.O.B..smc` ROM
4. Set processor type to "65816"
5. Click OK

### Step 2: Run Import Script

1. File → Script file... (or Alt+F7)
2. Select `ImportBOBMapIDA.py`
3. Select `out/rom_map.json` when prompted

### Step 3: Review Imported Data

The script will:
- **Create segments** for each region
- **Add bookmarks** at region starts
- **Add comments** describing regions
- **Create TilemapEntry type**
- **Mark vector table**

### Step 4: Navigate Analysis

**View Bookmarks:**
- View → Open subviews → Bookmarks
- Browse regions by type

**View Local Types:**
- View → Open subviews → Local Types
- Find `TilemapEntry` structure

**View Comments:**
- Press `:` to view/edit comments at address

---

## Using the Imported Data

### Analyzing Code Regions

1. Navigate to a code region bookmark
2. Press `C` to create code (if not auto-detected)
3. Press `A` to analyze
4. Rename functions as you discover them

### Analyzing Compressed Blocks

1. Navigate to compressed block bookmark
2. Comment indicates it's compressed
3. Use decompressed data from `out/decompressed_*.bin`
4. Import decompressed data as separate binary

### Analyzing Tilemaps

1. Navigate to tilemap region
2. Select the region
3. Edit → Create → Array
4. Choose `TilemapEntry` data type
5. Set count to 1024 (32x32 tilemap)

---

## Troubleshooting

### Script not found in Ghidra

**Solution:**
1. Ensure script is in Ghidra's script directory
2. Window → Script Manager → Refresh
3. Or run manually: File → Run Script...

### Import fails in IDA

**Possible causes:**
- Wrong ROM size
- Wrong processor type
- JSON format error

**Solution:**
1. Verify ROM loaded correctly
2. Check `rom_map.json` is valid JSON
3. Re-run analysis if needed

### Segments overlap

**Cause:** ROM already has segments defined

**Solution:**
1. Delete existing segments first
2. Or manually adjust segment boundaries

### No bookmarks appear

**Cause:** Import script may have failed silently

**Solution:**
1. Check Ghidra/IDA console for errors
2. Verify `rom_map.json` exists and is valid
3. Re-run import script

---

## Expected Output

After importing:

### Ghidra
- Segments for each region type
- Bookmarks at region starts
- Comments with region info
- TilemapEntry data type
- Vector table marked

### IDA Pro
- Segments for each region type
- Bookmarks at region starts
- Comments with region info
- TilemapEntry in Local Types
- Vector table marked

---

## Tips for Efficient Analysis

### 1. Start with Vector Table

The vector table (0x7FE0-0x7FFF) contains:
- RESET vector → Entry point
- NMI vector → Interrupt handler
- IRQ vector → Interrupt handler

Start analysis from RESET vector.

### 2. Use Bookmarks for Navigation

Bookmark types:
- **Code regions** — Start disassembly here
- **Compressed blocks** — Reference decompressed data
- **Tilemaps** — Apply TilemapEntry array

### 3. Cross-Reference with JSON

Keep `out/rom_map.json` open while analyzing:
- Check region confidence
- See exact boundaries
- Reference entropy values

### 4. Document as You Go

Add your own comments and labels:
- Function names
- Data structures
- Algorithm notes

---

## Next Steps

1. **Advanced:** Create custom data types for game structures
2. **Advanced:** Script automated analysis tasks
3. **Advanced:** Share analysis with team via project files

---

**Your RE tools are now integrated!** 🔧
