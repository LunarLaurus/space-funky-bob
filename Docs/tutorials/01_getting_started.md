# Tutorial 1: Getting Started with B.O.B. ROM Analysis Toolkit

**Duration:** 15 minutes  
**Difficulty:** Beginner  
**Prerequisites:** None

---

## Overview

This tutorial walks you through setting up the B.O.B. ROM Analysis Toolkit and running your first analysis. By the end, you'll have:

- Installed and tested the toolkit
- Scanned a ROM for compressed blocks
- Generated a visual ROM map
- Understood the basic workflow

---

## Setup

### Step 1: Verify Python Installation

The toolkit requires Python 3.8 or later.

```bash
python --version
```

Expected output: `Python 3.8.x` or higher.

### Step 2: Clone or Download the Toolkit

```bash
# If using git
git clone https://github.com/LunarLaurus/space-funky-bob.git
cd space-funky-bob

# Or download and extract the ZIP file
```

### Step 3: Verify Installation

No installation required! The toolkit uses only Python standard library.

```bash
# Run the test suite to verify everything works
python -m tests
```

Expected output:
```
============================================================
B.O.B. ROM TOOLKIT — TEST RESULTS
============================================================
[PASS] pytest
[PASS] simple
[PASS] property
------------------------------------------------------------
Summary: 3 passed, 0 failed
============================================================
```

---

## Your First ROM Analysis

### Step 4: Prepare Your ROM File

Place your B.O.B. ROM file in the project directory:

```
space-funky-bob/
├── rom/
│   └── B.O.B..smc    # Your ROM file
├── toolkit/
└── ...
```

**Note:** You must own a legal copy of the ROM.

### Step 5: Scan for Compressed Blocks

```bash
python toolkit/bob_lz_scan.py --rom rom/B.O.B..smc --outdir out/
```

Expected output:
```
Loaded ROM: 1048576 bytes (1.00 MB)
ROM title: 'B.O.B.'
Copier header: no (offset: 0)
ROM mapping: LoROM
Scanning ROM for compressed blocks...
Progress: 0.0% (found 0)
Progress: 25.0% (found 5)
Progress: 50.0% (found 12)
Progress: 75.0% (found 18)
Progress: 100.0% (found 24)

Scan complete! Found 24 compressed blocks.
Results saved to out/candidates.json
```

### Step 6: Review Results

Open `out/candidates.json` in a text editor:

```json
{
  "rom_file": "rom/B.O.B..smc",
  "num_candidates": 24,
  "candidates": [
    {
      "offset": 98304,
      "compressed_size": 512,
      "decompressed_size": 2048,
      "entropy": 7.2
    },
    ...
  ]
}
```

### Step 7: Generate ROM Map

```bash
python toolkit/bob_map.py --rom rom/B.O.B..smc --candidates out/candidates.json --outdir out/
```

Expected output:
```
Loaded ROM: 1048576 bytes
Loaded 24 compressed block candidates
ROM mapping: LoROM
Header offset: 0
Classifying regions...
Identified 50 distinct regions
Saved ROM map to out/rom_map.json
Saved visualization to out/rom_map.html
```

### Step 8: View Interactive Visualization

Open `out/rom_map.html` in your web browser.

You'll see:
- **Color-coded regions** (code, data, compressed, graphics)
- **Search box** — Filter by offset or type
- **Filter buttons** — Show/hide region types
- **Interactive tooltips** — Hover for details
- **Clickable regions** — Click to navigate

---

## Expected Output

After completing this tutorial, you should have:

```
out/
├── candidates.json          # Compressed block list
├── rom_map.json             # Region classifications
├── rom_map.html             # Interactive visualization
└── decompressed_*.bin       # Decompressed data files
```

---

## Troubleshooting

### "Python not found"

**Solution:** Install Python 3.8+ from [python.org](https://python.org)

### "Module not found" errors

**Solution:** The toolkit uses only standard library. Ensure you're running from the project directory.

### "ROM file not found"

**Solution:** Check the path to your ROM file. Use absolute path if needed:
```bash
python toolkit/bob_lz_scan.py --rom /full/path/to/B.O.B..smc --outdir out/
```

### No compressed blocks found

**Possible causes:**
- ROM file is corrupted
- ROM has unusual header
- Wrong ROM version

**Solution:** Try with `--thorough` flag:
```bash
python toolkit/bob_lz_scan.py --rom rom/B.O.B..smc --outdir out/ --thorough
```

---

## Next Steps

Now that you've completed the basic workflow, try:

1. **Tutorial 2:** Finding Compressed Blocks — Deep dive into compression detection
2. **Tutorial 3:** Graphics Extraction — Render graphics from decompressed data
3. **Tutorial 4:** Level Editing — Modify level tilemaps
4. **Tutorial 5:** Ghidra/IDA Integration — Import analysis into reverse engineering tools

---

**Congratulations!** You've completed your first ROM analysis. 🎮
