# Tutorial 2: Finding Compressed Blocks

**Duration:** 20 minutes  
**Difficulty:** Beginner  
**Prerequisites:** Tutorial 1 (Getting Started)

---

## Overview

This tutorial teaches you how to find and analyze compressed blocks in B.O.B. ROM. You'll learn:

- How the LZ77 compression format works
- How to run the scanner with different settings
- How to interpret scan results
- How to validate against known blocks

---

## Understanding LZ77 Compression

### Format Overview

B.O.B. uses a custom LZ77 variant:

```
Chunk Header: 8 bits (processed MSB first)
  Bit 0: Literal byte (copy next byte)
  Bit 1: Distance/Length pair (16-bit LE)
    - Low 11 bits:  distance (1-2047)
    - High 5 bits:  (length - 3), so length = 3-34
```

### Example

```
Compressed: [0x10] [0x41] [0x42] [0x43] [0x03] [0x28]
            ^      ^      ^      ^      ^------^------ Backref: dist=3, len=8
            |      |      |      |
            |      |      |      Literal: 'C'
            |      |      Literal: 'B'
            |      Literal: 'A'
            Chunk header: 00010000 (literal, literal, literal, backref, ...)

Decompressed: "ABCABCAB"
```

---

## Running the Scanner

### Standard Scan

```bash
python toolkit/bob_lz_scan.py --rom rom/B.O.B..smc --outdir out/
```

**Speed:** ~30-60 seconds for 1 MB ROM  
**Accuracy:** Good for most cases

### Multi-Pass Scan (Recommended)

```bash
python toolkit/bob_lz_scan.py --rom rom/B.O.B..smc --outdir out/ --multipass
```

**Speed:** ~15-30 seconds (2x faster)  
**Accuracy:** Same as standard, but more efficient

**How it works:**
1. **Pass 1:** Coarse scan (stride=256) to find candidate regions
2. **Pass 2:** Fine scan (stride=16) only in candidate regions

### Thorough Scan

```bash
python toolkit/bob_lz_scan.py --rom rom/B.O.B..smc --outdir out/ --thorough
```

**Speed:** ~60-120 seconds  
**Accuracy:** Maximum (finds more blocks)

**Use when:** Standard scan misses expected blocks

---

## Interpreting Results

### candidates.json Structure

```json
{
  "rom_file": "rom/B.O.B..smc",
  "rom_size": 1048576,
  "rom_mapping": "LoROM",
  "header_offset": 0,
  "num_candidates": 24,
  "candidates": [
    {
      "offset": 104444,
      "offset_hex": "0x01AD34",
      "compressed_size": 256,
      "decompressed_size": 2082,
      "entropy": 7.1,
      "confidence": "high"
    }
  ]
}
```

### Key Fields

| Field | Meaning |
|-------|---------|
| `offset` | ROM offset (decimal) |
| `offset_hex` | ROM offset (hexadecimal) |
| `compressed_size` | Size of compressed data |
| `decompressed_size` | Size after decompression |
| `entropy` | Randomness measure (0-8) |
| `confidence` | Detection confidence |

### Entropy Interpretation

| Entropy | Interpretation |
|---------|----------------|
| 0.0-2.0 | Uniform data (likely empty/padding) |
| 2.0-4.5 | Graphics data (limited colors) |
| 4.5-6.5 | Code or structured data |
| 6.5-8.0 | Compressed data |

---

## Validating Against Known Block

### Known Block: 0x1AD34

The B.O.B. ROM has a documented compressed block:
- **Offset:** 0x1AD34 (104444 decimal)
- **Decompressed size:** 0x822 (2082 bytes)

### Step 1: Verify Detection

```bash
python toolkit/bob_lz_scan.py --rom rom/B.O.B..smc --outdir out/
```

Check `out/candidates.json` for offset `0x1AD34` or `104444`.

### Step 2: Manual Validation

```python
from toolkit.bob_lz import bob_lz_decompress

# Read ROM
rom = open('rom/B.O.B..smc', 'rb').read()

# Extract compressed block
compressed = rom[0x1AD34:0x1AD34 + 0x1000]

# Decompress
decompressed, consumed = bob_lz_decompress(compressed, 0x822)

# Verify
assert len(decompressed) == 0x822, f"Expected 0x822 bytes, got {len(decompressed)}"
print(f"✓ Known block validated (consumed {consumed} bytes)")
```

Expected output:
```
✓ Known block validated (consumed 256 bytes)
```

---

## Troubleshooting

### Block at known offset not detected

**Possible causes:**
- Block format differs from expected
- Entropy threshold too high
- Stride too large

**Solutions:**
```bash
# Try thorough scan
python toolkit/bob_lz_scan.py --rom rom/B.O.B..smc --outdir out/ --thorough

# Or lower entropy threshold in configs/thresholds.yaml
```

### Too many false positives

**Solution:** Increase entropy threshold:
```bash
# Edit configs/thresholds.yaml
scanner:
  compressed_min: 7.0  # Increase from 6.5
```

### Decompression fails

**Check:**
1. Offset is correct
2. Enough data available at offset
3. Data is actually compressed (check entropy)

---

## Next Steps

1. **Tutorial 3:** Graphics Extraction — Render the decompressed graphics
2. **Tutorial 4:** Level Editing — Find and modify level tilemaps
3. **Advanced:** Modify entropy thresholds for your specific ROM

---

**You now understand compressed block detection!** 🎯
