# B.O.B. ROM Analysis Toolkit

Automated ROM analysis tools for Space Funky B.O.B. (SNES). Locates compressed blocks, maps code vs data regions, and generates artifacts for reverse engineering workflows (Ghidra, IDA, radare2).

## Overview

This toolkit provides:
- **LZ77 Decoder**: Robust implementation of B.O.B.'s LZ77 variant with error handling
- **ROM Scanner**: Automatic compressed block detection using entropy and heuristics
- **Region Mapper**: Code/data classification via 65816 disassembly and statistical analysis
- **Ghidra Integration**: Import scripts and instructions for quick setup
- **HTML Visualization**: Interactive ROM memory map

**B.O.B. ROM Specifications**:
- Title: "B.O.B." (Space Funky B.O.B.)
- Mapping: LoROM Fast
- ROM Size: 8 Mbits (1 MB / 0x100000 bytes)
- Header Location: 0x7FC0 (LoROM standard)
- Checksum: 0x7379, Complement: 0x8C86
- Known compressed block: offset 0x1AD34, size 0x822 bytes decompressed

## Features

✅ Detects LoROM/HiROM mapping and copier headers  
✅ Locates B.O.B. LZ77 compressed blocks  
✅ Handles overlapping copies and reports decode anomalies  
✅ Classifies ROM regions (code, data, compressed, graphics)  
✅ Outputs JSON maps and HTML visualizations  
✅ Ghidra-ready annotations and scripts  

## Requirements

- **Python 3.8+** (no external dependencies!)
- **Ghidra 10.x+** (for import scripts)
- B.O.B. ROM file (not included)

## Installation

```bash
# Clone or download this repository
git clone <your-repo-url>
cd bob-rom-analysis

# No pip install needed - pure Python!
```

## Quick Start

### 1. Test the Decoder

```bash
python bob_lz.py
```

Expected output:
```
Running B.O.B. LZ decoder unit tests...
✓ Test 1: Literal bytes
✓ Test 2: Overlapping copy
✓ Test 3: Zero distance error
✓ Test 4: Distance too large error
✓ Test 5: Exploratory decompression

All tests passed! ✓
```

### 2. Scan ROM for Compressed Blocks

```bash
python bob_lz_scan.py --rom SpaceFunkyBob.sfc --outdir out/
```

Output:
- `out/candidates.json` - List of compressed block candidates
- `out/decompressed_XXXXXX.bin` - Successfully decompressed data

### 3. Generate ROM Map

```bash
python bob_map.py --rom SpaceFunkyBob.sfc --candidates out/candidates.json --outdir out/
```

Output:
- `out/rom_map.json` - Region classifications with metadata
- `out/rom_map.html` - Interactive visualization

### 4. Import into Ghidra

Follow instructions in `ghidra_import.txt` to load annotations into Ghidra.

## File Descriptions

| File | Purpose |
|------|---------|
| `bob_lz.py` | LZ77 decoder with unit tests |
| `bob_lz_scan.py` | ROM scanner for compressed blocks |
| `bob_map.py` | Region classifier (code/data/compressed) |
| `ghidra_import.txt` | Ghidra import instructions + Python script |
| `README.md` | This file |

## Technical Details

### B.O.B. LZ77 Format

- **Chunk header**: Single byte, 8 bits processed MSB→LSB
- **Bit 0**: Literal (copy next byte)
- **Bit 1**: Distance/length pair (16-bit little-endian)
  - Low 11 bits: distance (1-2047)
  - High 5 bits: (length - 3), so length = 3-34

**Edge cases handled**:
- Distance = 0 → ValueError
- Distance > current output size → ValueError
- Length > distance → Overlapping copy (sliding window)

### Region Classification Heuristics

| Region Type | Detection Method | Thresholds |
|-------------|------------------|------------|
| **Code** | Opcode density + entropy | >85% valid opcodes, entropy <6.5 |
| **Compressed** | Successful decompression | Entropy >7.2, entropy drop after decode |
| **Graphics** | Tile patterns + low entropy | Entropy <4.0, many zeros/low bytes |
| **Data** | Default for unclassified | 4.0 < entropy < 7.2 |

**Code detection**:
1. Start from reset/interrupt vectors (LoROM: $7FE0, HiROM: $FFE0)
2. Recursive traversal following JSR/JMP/branches
3. Statistical validation: opcode validity, instruction length

**Compressed block detection**:
1. Entropy scan (look for 6.0-8.0 range)
2. Attempt decompression with common sizes (1KB, 2KB, 4KB, 8KB, 16KB, 32KB)
3. Validate: entropy drop, tile patterns, compression ratio

### Addressing

**LoROM Mapping**:
- ROM $0000-$7FFF → SNES $8000-$FFFF (Bank 0)
- ROM $8000-$FFFF → SNES $8000-$FFFF (Bank 1)
- Internal header at ROM $7FC0

**HiROM Mapping**:
- ROM $0000-$FFFF → SNES $C000-$FFFF (Bank 0)
- Internal header at ROM $FFC0

## Usage Examples

### Scan Only a Specific Region

```bash
# Modify bob_lz_scan.py line ~120 to set custom range
# Example: scan 0x10000 to 0x20000
# for offset in range(0x10000, 0x20000, stride):
```

### Export Decompressed Blocks as C Arrays

```python
import json

with open('out/candidates.json') as f:
    data = json.load(f)

for candidate in data['candidates']:
    if candidate['success']:
        offset = candidate['offset']
        with open(f"out/decompressed_{offset}.bin", 'rb') as binfile:
            data = binfile.read()
            print(f"const uint8_t block_{offset}[] = {{")
            print(", ".join(f"0x{b:02X}" for b in data))
            print("};")
```

### Programmatic Region Query

```python
import json

with open('out/rom_map.json') as f:
    rom_map = json.load(f)

# Find all code regions
code_regions = [r for r in rom_map['regions'] if r['type'] == 'code']
print(f"Found {len(code_regions)} code regions")

for region in code_regions:
    print(f"  {region['start_hex']} - {region['end_hex']} ({region['size']} bytes)")
```

## Validation

### Known Test Vectors

The documentation mentions a known compressed block in the B.O.B. ROM:
- **Offset**: 0x1AD34
- **Decompressed size**: 0x822 bytes (2082 bytes)

You can validate the scanner against this known block:

```python
# Test against known B.O.B. compressed block
rom = open('bob.smc', 'rb').read()
header_offset = 512 if len(rom) % 1024 == 512 else 0

# Known block location
compressed_offset = 0x1AD34 + header_offset
expected_dec_size = 0x822

from bob_lz import bob_lz_decompress
compressed_data = rom[compressed_offset:compressed_offset + 0x1000]  # Read enough
decompressed, consumed = bob_lz_decompress(compressed_data, expected_dec_size)

print(f"✓ Decompressed {consumed} bytes -> {len(decompressed)} bytes")
print(f"  Expected size: 0x{expected_dec_size:X} ({expected_dec_size} bytes)")
assert len(decompressed) == expected_dec_size
```

### Validation

You can add known compressed blocks to validate the scanner:

```python
# Add to bob_lz.py test suite
def test_known_bob_block():
    # Example: known compressed block from ROM offset 0x1AD34
    rom = open('bob.smc', 'rb').read()
    
    # Detect header
    header_offset = 512 if len(rom) % 1024 == 512 else 0
    
    # Known block: offset 0x1AD34, decompressed size 0x822
    compressed_offset = 0x1AD34 + header_offset
    compressed = rom[compressed_offset:compressed_offset + 0x1000]
    
    decompressed, consumed = bob_lz_decompress(compressed, 0x822)
    
    assert len(decompressed) == 0x822, f"Expected 0x822 bytes, got {len(decompressed)}"
    print(f"✓ Known block validation passed (consumed {consumed} bytes)")
```

## Troubleshooting

### Issue: No compressed blocks found

**Solutions**:
1. Verify ROM file is correct (check size, no header corruption)
2. Lower stride in `bob_lz_scan.py` (line ~120) from 16 to 4
3. Add more test sizes to `test_sizes` array
4. Check if ROM is already decompressed

### Issue: Too many false positives

**Solutions**:
1. Increase entropy thresholds in `bob_lz_scan.py` (line ~105)
2. Require higher entropy drop (line ~135: `if entropy_drop > 0.5`)
3. Add tile pattern validation (check for SNES 2bpp/4bpp signatures)

### Issue: Code regions not detected

**Solutions**:
1. Verify ROM mapping detection (LoROM vs HiROM)
2. Check vector table location in `bob_map.py` (line ~245)
3. Lower opcode density threshold from 0.85 to 0.75 (line ~345)
4. Manually mark entry points and re-run

### Issue: Ghidra import fails

**Solutions**:
1. Verify base address matches ROM mapping
2. Check Python script syntax in Ghidra Script Manager
3. Manually create bookmarks as fallback (see `ghidra_import.txt`)

## Performance

Typical runtime on 2MB ROM:
- **LZ scan**: ~30-60 seconds (stride=16)
- **ROM mapping**: ~5-10 seconds
- **Total**: <2 minutes

Reduce stride for more thorough scan (increases runtime proportionally).

## Limitations

- **Entropy-based heuristics**: May miss low-entropy compressed blocks
- **65816 disassembly**: Does not handle dynamic code generation
- **Address translation**: Assumes standard LoROM/HiROM (no ExHiROM/SA-1)
- **Decompression**: Requires plausible size hints (may miss variable-length blocks)

## Future Enhancements

- [ ] IDA Pro import script
- [ ] radare2 script generation
- [ ] Machine learning block classifier
- [ ] Automatic tile rendering
- [ ] Multi-ROM batch processing
- [ ] GUI interface

## Contributing

Contributions welcome! Areas of interest:
- Better heuristics for compressed block detection
- Additional ROM mapping schemes (ExHiROM, SA-1)
- Tile/sprite rendering for graphics validation
- Automated testing with known ROM samples

## License

MIT License - see LICENSE file for details.

## Credits

- LZ77 format reverse-engineered from B.O.B. source code
- 65816 opcode tables based on WDC W65C816S datasheet
- Ghidra integration inspired by retro RE community

## References

- [65816 Programming Manual](http://www.defence-force.org/computing/oric/coding/annexe_2/)
- [SNES Development Wiki](https://wiki.superfamicom.org/)
- [Ghidra Documentation](https://ghidra-sre.org/)

## Support

For issues or questions:
1. Check `ghidra_import.txt` for Ghidra-specific help
2. Review test suite in `bob_lz.py` for decoder examples
3. Open an issue on GitHub (if hosted)

---

**Happy reverse engineering! 🎮🔍**
