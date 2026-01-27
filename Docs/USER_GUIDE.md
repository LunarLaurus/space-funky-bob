# User Guide
## B.O.B. ROM Analysis Toolkit

**Version**: 1.0  
**Date**: January 27, 2026  
**Audience**: End Users, ROM Analysts, Hobbyists

---

## Welcome! 🎮

This guide will help you analyze SNES ROM files, specifically Space Funky B.O.B., using our automated toolkit. Whether you're a reverse engineer, ROM hacker, or just curious about how retro games work, this guide has you covered.

### What This Tool Does

✅ **Finds Hidden Data**: Automatically locates compressed graphics and level data  
✅ **Maps the ROM**: Identifies which parts are code vs data  
✅ **Works with Ghidra**: Exports results to professional analysis tools  
✅ **Saves Time**: Automates hours of manual work into minutes  

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Quick Start Guide](#2-quick-start-guide)
3. [Understanding the Output](#3-understanding-the-output)
4. [Working with Ghidra](#4-working-with-ghidra)
5. [Advanced Usage](#5-advanced-usage)
6. [Troubleshooting](#6-troubleshooting)
7. [FAQs](#7-faqs)
8. [Getting Help](#8-getting-help)

---

## 1. Getting Started

### 1.1 What You Need

#### Required
- **Python 3.8 or newer** - [Download here](https://www.python.org/downloads/)
- **B.O.B. ROM file** - You must own this legally
- **Command line** - Terminal (Mac/Linux) or Command Prompt (Windows)

#### Optional
- **Ghidra** - For advanced reverse engineering ([Download](https://ghidra-sre.org/))
- **IDA Pro** - Alternative to Ghidra (commercial)
- **Hex editor** - For viewing raw ROM data

### 1.2 Installation

**Step 1**: Download the toolkit
```bash
# Option A: Clone from GitHub
git clone https://github.com/yourname/bob-rom-analysis
cd bob-rom-analysis

# Option B: Download ZIP and extract
```

**Step 2**: Verify Python version
```bash
python --version
# Should show: Python 3.8.x or higher
```

**Step 3**: Test installation
```bash
python bob_lz.py
# Should show: "Running B.O.B. LZ decoder unit tests..."
# And end with: "All tests passed! ✓"
```

✅ If tests pass, you're ready to go!

### 1.3 Legal Note

⚠️ **Important**: You must legally own the B.O.B. ROM file. This toolkit does not include or distribute ROM files. Use this software only on ROMs you have the right to analyze.

---

## 2. Quick Start Guide

### 2.1 Basic Analysis (3 Steps)

#### Step 1: Run the Complete Analysis

The easiest way to analyze your ROM is with the automated workflow:

```bash
./test_workflow.sh bob.smc
```

**What happens?**
1. ✅ Validates the decoder (runs tests)
2. 🔍 Scans your ROM for compressed blocks
3. 🗺️ Creates a memory map
4. 📊 Generates visualization

**Output**:
```
analysis_output/
├── candidates.json          # Found compressed blocks
├── rom_map.json             # ROM structure map
├── rom_map.html             # Visual map (open in browser!)
└── decompressed_*.bin       # Extracted data
```

#### Step 2: View the Visualization

Open `analysis_output/rom_map.html` in your web browser.

**What you'll see**:
- 🟢 **Green regions** = Executable code
- 🟣 **Purple regions** = Compressed data
- 🟡 **Yellow regions** = Graphics candidates
- 🔵 **Blue regions** = Other data

**Hover over regions** to see details like:
- Memory address range
- Size in bytes
- Confidence level
- Type of data

#### Step 3: Review the Results

Check `analysis_output/candidates.json` to see all compressed blocks found:

```json
{
  "num_candidates": 42,
  "candidates": [
    {
      "offset": "0x1AD34",
      "decompressed_size": 2082,
      "success": true,
      "looks_like_tiles": true,
      "output_file": "decompressed_01AD34.bin"
    }
  ]
}
```

### 2.2 Individual Commands

If you prefer to run steps separately:

**Scan for compressed blocks**:
```bash
python bob_lz_scan.py --rom bob.smc --outdir output
```

**Generate ROM map**:
```bash
python bob_map.py --rom bob.smc --candidates output/candidates.json --outdir output
```

**Validate decoder**:
```bash
python validate_known_block.py bob.smc
```

---

## 3. Understanding the Output

### 3.1 candidates.json

This file lists all compressed blocks found in the ROM.

**Key Fields**:
```json
{
  "offset": "0x1AD34",              // Where in the ROM
  "compressed_size": 1234,          // How many bytes compressed
  "decompressed_size": 2082,        // How many bytes when decompressed
  "success": true,                  // Did decompression work?
  "entropy_compressed": 7.45,       // How random (7-8 = compressed)
  "entropy_decompressed": 4.82,     // After decompression (lower = data)
  "looks_like_tiles": true,         // Might be graphics?
  "output_file": "decompressed_01AD34.bin"  // Extracted file
}
```

**What to look for**:
- ✅ `success: true` - Block was successfully decompressed
- 📊 High entropy (>7.0) then low entropy (<5.0) = good candidate
- 🎨 `looks_like_tiles: true` - Likely graphics data
- 📁 Check the `output_file` to see the raw decompressed data

### 3.2 rom_map.json

This file describes the structure of the entire ROM.

**Region Types**:
- **code** - Executable 65816 CPU instructions
- **compressed** - Confirmed compressed blocks
- **compressed_candidate** - Possibly compressed (needs verification)
- **graphics_candidate** - Low entropy, possibly graphics
- **data** - Everything else

**Example Region**:
```json
{
  "start": 0,
  "end": 32768,
  "start_hex": "0x0",
  "end_hex": "0x8000",
  "size": 32768,
  "type": "code",
  "confidence": 92
}
```

**Confidence Levels**:
- **90-100%** - Very confident
- **70-89%** - Likely correct
- **50-69%** - Uncertain, verify manually
- **<50%** - Low confidence, probably needs review

### 3.3 rom_map.html

Interactive visualization of the ROM structure.

**Features**:
- **Linear bar** showing entire ROM from start to end
- **Color-coded regions** by type
- **Hover tooltips** with details
- **Legend** explaining colors
- **Region list** below the map

**How to use**:
1. Open in any modern web browser
2. Hover over colored sections for details
3. Scroll down to see complete region list
4. Use this to quickly identify interesting areas

### 3.4 Decompressed Files

Files like `decompressed_01AD34.bin` contain the raw extracted data.

**How to view**:
```bash
# Hex dump (first 256 bytes)
hexdump -C decompressed_01AD34.bin | head -16

# Open in hex editor (HxD, Hex Fiend, etc.)
# Look for patterns:
# - Graphics: Repeating small values (0x00-0x0F)
# - Text: ASCII characters (0x20-0x7E)
# - Level data: Structured patterns
```

---

## 4. Working with Ghidra

### 4.1 Import ROM into Ghidra

**Step 1**: Create new Ghidra project
- File → New Project
- Choose "Non-Shared Project"
- Pick a location

**Step 2**: Import ROM
- File → Import File
- Select your ROM (bob.smc)
- **Important settings**:
  - Language: **65816:LE:16:default**
  - Base Address: **0x808000** (for LoROM)
  - Click OK

**Step 3**: Analyze
- Click "Yes" when prompted to analyze
- Use default analyzers
- Wait for analysis to complete

### 4.2 Import ROM Map

**Method 1: Manual Bookmarks** (Simple, always works)

1. Open `rom_map.json` in a text editor
2. Window → Bookmarks in Ghidra
3. For each region, click **Add Bookmark** (+):
   - **Address**: Convert hex (e.g., 0x1000 → 808000:1000)
   - **Category**: Use region type (code, compressed, etc.)
   - **Description**: Copy from JSON

**Method 2: Python Script** (Automated, recommended)

1. Open Script Manager (Window → Script Manager)
2. Create new script: `ImportBOBMap.py`
3. Copy script from `ghidra_import.txt`
4. Run script, select `rom_map.json`
5. Script creates bookmarks automatically

**Verify**:
- Open Bookmarks window (Window → Bookmarks)
- You should see entries for each region
- Click bookmark to jump to that address

### 4.3 Analyzing Code Regions

**Step 1**: Navigate to code regions
- Check bookmarks with "code" category
- Press **G** to go to address
- Code should be disassembled already

**Step 2**: Create functions
- Press **F** on first instruction to create function
- Ghidra will analyze the function automatically
- Repeat for other entry points

**Step 3**: Add labels
- Press **L** to label important locations
- Use meaningful names (e.g., "InitGraphics", "MainLoop")
- Add comments with **;** key

### 4.4 Exploring Compressed Blocks

**Step 1**: Find compressed regions
- Look for "compressed" bookmarks
- Navigate to those addresses

**Step 2**: Load decompressed data
- Right-click in Listing
- Data → Load/Edit External File
- Select corresponding `decompressed_*.bin`
- Create Array or Undefined data as needed

**Step 3**: Analyze patterns
- If graphics: Look for tile patterns (8x8 or 16x16 grids)
- If level data: Look for structured arrays
- Use Data Type Manager to define structures

---

## 5. Advanced Usage

### 5.1 Customizing the Scan

You can modify scanning parameters by editing `bob_lz_scan.py`:

**Change scan stride** (line ~120):
```python
stride = 16  # Change to 4 for more thorough (slower) scan
```

**Adjust entropy thresholds** (line ~105):
```python
# Current: 6.0 < entropy < 8.0
# More strict: 6.5 < entropy < 7.8
if 6.5 < entropy < 7.8:
```

**Add custom test sizes** (line ~90):
```python
test_sizes = [
    0x1000,  # 4KB
    0x2000,  # 8KB
    0x4000,  # 16KB
    0x3000,  # 12KB (add custom size)
]
```

### 5.2 Batch Processing Multiple ROMs

Create a simple batch script:

```bash
#!/bin/bash
# batch_analyze.sh

for rom in roms/*.smc; do
    echo "Analyzing $rom..."
    basename=$(basename "$rom" .smc)
    ./test_workflow.sh "$rom" > "logs/${basename}.log" 2>&1
    mv analysis_output "results/${basename}"
done
```

### 5.3 Extracting Specific Blocks

If you know the exact offset of a compressed block:

```python
# extract_block.py
from bob_lz import bob_lz_decompress
from pathlib import Path

rom = Path("bob.smc").read_bytes()
offset = 0x1AD34 + 512  # Add header offset if present
compressed = rom[offset:offset + 0x10000]

decompressed, consumed = bob_lz_decompress(compressed, 0x822)
Path("my_extracted_block.bin").write_bytes(decompressed)
print(f"Extracted {len(decompressed)} bytes")
```

### 5.4 Comparing ROM Versions

To compare two ROM versions:

```bash
# Analyze both versions
./test_workflow.sh bob_v1.0.smc
mv analysis_output analysis_v1.0

./test_workflow.sh bob_v1.1.smc
mv analysis_output analysis_v1.1

# Compare candidates
diff analysis_v1.0/candidates.json analysis_v1.1/candidates.json
```

---

## 6. Troubleshooting

### 6.1 Common Issues

#### "ROM file not found"

**Problem**: Can't locate ROM file  
**Solution**:
```bash
# Check file exists
ls -l bob.smc

# Use absolute path
python bob_lz_scan.py --rom /full/path/to/bob.smc
```

#### "Python command not found"

**Problem**: Python not in PATH  
**Solution**:
```bash
# Try python3 instead
python3 bob_lz.py

# Or use full path
/usr/bin/python3 bob_lz.py

# Windows:
py bob_lz.py
```

#### "No compressed blocks found"

**Problem**: Scanner didn't find any blocks  
**Solution**:
1. **Verify it's the right ROM**: Run `validate_known_block.py bob.smc`
2. **Check for header**: ROM might have wrong header offset
3. **Lower stride**: Edit `bob_lz_scan.py`, change `stride = 16` to `stride = 4`
4. **Adjust thresholds**: Widen entropy range to `5.5 < entropy < 8.5`

#### "Too many false positives"

**Problem**: Found 500+ candidates, most are junk  
**Solution**:
1. **Increase confidence**: Raise entropy drop threshold
2. **Enable tile validation**: Uncomment tile pattern checks
3. **Filter by size**: Ignore very small blocks (<256 bytes)

#### "ROM map looks wrong"

**Problem**: Code regions marked as data or vice versa  
**Solution**:
1. **Check ROM mapping**: Should be LoROM for B.O.B.
2. **Verify header offset**: Should be 512 for .smc, 0 for .sfc
3. **Manual override**: Edit `rom_map.json` and re-import to Ghidra

#### "Ghidra import fails"

**Problem**: Python script doesn't work in Ghidra  
**Solution**:
1. **Check Ghidra version**: Need 10.0+
2. **Use manual method**: Follow step-by-step in `ghidra_import.txt`
3. **Verify base address**: Should be 0x808000 for LoROM
4. **Check JSON path**: Ensure `rom_map.json` path is correct

### 6.2 Performance Issues

#### Scanning takes too long (>5 minutes)

**Solutions**:
1. **Increase stride**: Change from 16 to 32 bytes
2. **Limit ROM size**: Process only first 1MB if testing
3. **Skip known regions**: Modify scanner to skip header/vectors
4. **Use PyPy**: Run with `pypy3` instead of `python3`

#### Out of memory errors

**Solutions**:
1. **Process in chunks**: Split large ROM into banks
2. **Reduce test sizes**: Remove large decompressed size tests
3. **Close other programs**: Free up RAM
4. **Upgrade RAM**: Or use machine with more memory

---

## 7. FAQs

### General Questions

**Q: Can I use this on other SNES games?**  
A: Yes, but results vary. The LZ77 decoder is B.O.B.-specific, but the ROM mapper works on any SNES ROM. Other games may use different compression.

**Q: Is this legal?**  
A: Yes, analyzing ROMs you own is legal. Distributing ROMs is not. We don't distribute any copyrighted material.

**Q: Can I contribute improvements?**  
A: Absolutely! See [CONTRIBUTING.md] for guidelines. We welcome bug fixes, documentation, and new features.

**Q: Does this work on ROM hacks?**  
A: Usually yes, but hacks may change compression or add new data. Results may vary.

### Technical Questions

**Q: What's the compression ratio for B.O.B. data?**  
A: Typically 40-60%, meaning compressed data is 40-60% of original size.

**Q: How accurate is the code/data classifier?**  
A: ~85-90% on B.O.B. ROM based on testing. Manual verification recommended for critical analysis.

**Q: Can I use this programmatically?**  
A: Yes! Import modules in your Python scripts:
```python
from bob_lz import bob_lz_decompress
from bob_lz_scan import scan_rom_for_compressed_blocks
```

**Q: What's the entropy score mean?**  
A: Shannon entropy from 0-8 bits/byte. Higher = more random/compressed. Lower = more patterns/structure.

### Usage Questions

**Q: How long does analysis take?**  
A: 1-2 minutes for 1MB ROM with default settings.

**Q: Can I pause and resume?**  
A: Not currently. Analysis is single-shot. Future versions may support resuming.

**Q: Where's my data stored?**  
A: All output goes to the directory you specify with `--outdir`. Nothing uploaded or saved elsewhere.

**Q: Can I delete decompressed files?**  
A: Yes, but you'll need to re-run the scan if you want them back. Keep them if you plan to use Ghidra.

---

## 8. Getting Help

### 8.1 Documentation

- **README.md** - Quick start and installation
- **CLAUDE.md** - Full project context and goals
- **TECHNICAL.md** - Detailed algorithms and architecture
- **ghidra_import.txt** - Ghidra integration guide

### 8.2 Community

- **GitHub Issues** - Report bugs or request features
- **GitHub Discussions** - Ask questions, share findings
- **SNES Discord** - Connect with other ROM analysts
- **[Forum Link]** - Community forum (if available)

### 8.3 Reporting Issues

When reporting bugs, please include:

1. **Command you ran**:
   ```bash
   python bob_lz_scan.py --rom bob.smc
   ```

2. **Error message** (full text):
   ```
   ERROR: LZ77 Decoder - Invalid distance
   ...
   ```

3. **ROM details**:
   - File size
   - File name
   - Result of `validate_known_block.py`

4. **Environment**:
   - Python version (`python --version`)
   - Operating system
   - Any modifications to scripts

### 8.4 Feature Requests

Have an idea? We'd love to hear it!

**Good feature request includes**:
- **Use case**: What problem does it solve?
- **Example**: How would you use it?
- **Alternatives**: What do you do now?

---

## Appendix A: File Reference

### Input Files
- **ROM file** (.smc, .sfc) - Your SNES ROM

### Output Files
- **candidates.json** - List of compressed blocks found
- **rom_map.json** - Complete ROM structure map
- **rom_map.html** - Interactive visualization
- **decompressed_XXXXXX.bin** - Extracted compressed data

### Script Files
- **bob_lz.py** - LZ77 decoder (run tests)
- **bob_lz_scan.py** - Find compressed blocks
- **bob_map.py** - Classify ROM regions
- **validate_known_block.py** - Verify decoder works
- **test_workflow.sh** - Run complete analysis

### Documentation
- **README.md** - Quick start guide
- **ghidra_import.txt** - Ghidra integration
- **CLAUDE.md** - Project context
- **docs/PRD.md** - Product requirements
- **docs/TECHNICAL.md** - Technical design

---

## Appendix B: Keyboard Shortcuts (Ghidra)

| Key | Action |
|-----|--------|
| **G** | Go to address |
| **L** | Create label |
| **F** | Create function |
| **D** | Create data |
| **;** | Add comment |
| **Ctrl+F** | Search |
| **Alt+←** | Navigate back |
| **Alt+→** | Navigate forward |

---

## Appendix C: Entropy Interpretation

| Entropy Range | Interpretation | Likely Content |
|---------------|----------------|----------------|
| 0.0 - 2.0 | Very low | Zeros, padding |
| 2.0 - 4.0 | Low | Graphics, repetitive data |
| 4.0 - 6.5 | Medium-low | Code, structured data |
| 6.5 - 7.2 | Medium-high | Mixed data |
| 7.2 - 8.0 | High | Compressed, encrypted |

---

**Need more help?** Check the [GitHub repository](https://github.com/) or open an issue!

**Happy analyzing!** 🎮🔍
