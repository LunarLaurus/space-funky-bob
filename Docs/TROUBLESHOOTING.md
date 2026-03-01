# B.O.B. ROM Analysis Toolkit - Troubleshooting Guide

**Version**: 0.5.0  
**Last Updated**: February 26, 2026

---

## Quick Reference

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| No compressed blocks found | Wrong ROM file or corrupted header | Verify ROM is B.O.B. (U) [!], check for 512-byte header |
| Too many false positives | Entropy thresholds too low | Increase `MIN_ENTROPY` in `bob_lz_scan.py` from 6.0 to 6.5 |
| Code regions not detected | Wrong ROM mapping detected | Check LoROM/HiROM detection in `bob_map.py` |
| Ghidra import fails | Base address mismatch | Verify ROM mapping matches import script settings |
| Import errors | PYTHONPATH not set | Use `python -m toolkit.module` or add `src/` to PYTHONPATH |
| CUDA OOM errors | GPU VRAM exceeded | Reduce `max_batch_size` in config or use CPU mode |
| Slow extraction | Low worker count | Increase `num_workers` in config (default: 4) |
| LLM filtering fails | Model unavailable | Set `use_llm: false` in config for rules-only filtering |

---

## Common Issues

### 1. No Compressed Blocks Found

**Symptoms:**
```
$ python toolkit/bob_lz_scan.py --rom B.O.B..smc --outdir out/
Scanning ROM...
No compressed blocks found.
```

**Possible Causes:**

1. **Wrong ROM file**
   - Verify you're using Space Funky B.O.B. (U) [!]
   - Check ROM size: should be 1MB (0x100000 bytes) or 1MB + 512 byte header

2. **Header detection issue**
   - Some ROMs have 512-byte copier headers
   - The scanner auto-detects, but may fail on corrupted headers

3. **Stride too large**
   - Default stride=16 may skip small blocks
   - Try `--stride 4` for more thorough scanning

**Solutions:**

```bash
# Verify ROM file
python toolkit/validate_known_block.py B.O.B..smc

# Try more thorough scan
python toolkit/bob_lz_scan.py --rom B.O.B..smc --stride 4 --thorough

# Check ROM info
python -c "
rom = open('B.O.B..smc', 'rb').read()
print(f'Size: {len(rom)} bytes ({len(rom)/1024/1024:.2f} MB)')
header = 512 if len(rom) % 1024 == 512 else 0
print(f'Header: {header} bytes')
print(f'Title: {rom[0x7FC0+header:0x7FC0+header+21]}')
"
```

---

### 2. Too Many False Positives

**Symptoms:**
```
Found 500+ candidate blocks
Most fail decompression validation
```

**Possible Causes:**

1. **Entropy thresholds too low**
   - Default `MIN_ENTROPY = 6.0` may be too permissive
   - High-entropy data isn't always compressed

2. **Missing entropy drop validation**
   - Compressed data should have lower entropy after decompression
   - Ensure `entropy_drop > 0.3` check is enabled

**Solutions:**

Edit `toolkit/bob_lz_scan.py`:

```python
# Line ~105: Increase entropy threshold
MIN_ENTROPY = 6.5  # Was 6.0

# Line ~135: Require entropy drop
if entropy_drop > 0.5:  # Was 0.3
    candidates.append(...)
```

Then re-run:
```bash
python toolkit/bob_lz_scan.py --rom B.O.B..smc --outdir out/
```

---

### 3. Code Regions Not Detected

**Symptoms:**
```
ROM map shows mostly "data" regions
Few or no "code" regions detected
```

**Possible Causes:**

1. **Wrong ROM mapping**
   - B.O.B. uses LoROM Fast mapping
   - HiROM detection will fail

2. **Vector table location**
   - LoROM: vectors at 0x7FE0
   - HiROM: vectors at 0xFFE0

3. **Opcode density threshold**
   - Default 0.85 may be too strict

**Solutions:**

Check ROM mapping in `toolkit/bob_map.py`:

```python
# Line ~245: Verify vector table location
if rom_mapping == 'LoROM':
    vector_table = 0x7FE0
elif rom_mapping == 'HiROM':
    vector_table = 0xFFE0
```

Lower opcode density threshold:

```python
# Line ~345: Reduce threshold
if opcode_density > 0.75:  # Was 0.85
    mark_as_code()
```

---

### 4. Ghidra Import Fails

**Symptoms:**
- Script errors in Ghidra Script Manager
- No bookmarks created
- Address translation errors

**Possible Causes:**

1. **Base address mismatch**
   - Ghidra may load ROM at different base address
   - Import script assumes 0x00000000

2. **JSON format error**
   - `rom_map.json` may be malformed
   - Check JSON validity

**Solutions:**

1. **Verify JSON:**
```bash
python -c "import json; json.load(open('out/rom_map.json'))"
echo "JSON is valid"
```

2. **Check Ghidra base address:**
   - In Ghidra: Window → Memory Map
   - Note base address of ROM block
   - Update import script if not 0x00000000

3. **Manual import fallback:**
   - See `docs/GHIDRA_IMPORT.md` for manual bookmark creation
   - Use `rom_map.json` as reference

---

### 5. Python Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'bob_lz'
```

**Possible Causes:**

1. **PYTHONPATH not set**
   - Toolkit modules need to be importable
   - Current directory not in path

2. **Wrong import style**
   - Some modules use relative imports
   - Others use absolute imports

**Solutions:**

```bash
# Option 1: Use python -m
python -m toolkit.bob_lz

# Option 2: Add toolkit to path
export PYTHONPATH=/path/to/space-funky-bob/toolkit:$PYTHONPATH  # Linux/Mac
set PYTHONPATH=C:\path\to\space-funky-bob\toolkit;%PYTHONPATH%  # Windows

# Option 3: Run from project root
cd /path/to/space-funky-bob
python toolkit/bob_lz.py
```

---

### 6. GPU/CUDA Issues (if using ML features)

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**

1. **Reduce batch size:**
```yaml
# configs/default.yaml
hardware:
  max_batch_size: 64  # Reduce from 128
```

2. **Use CPU mode:**
```yaml
hardware:
  device: cpu  # Force CPU mode
```

3. **Clear GPU cache:**
```bash
# Linux
sudo nvidia-smi --gpu-reset

# Windows: Restart GPU driver
Win + Ctrl + Shift + B
```

---

### 7. Slow Performance

**Symptoms:**
- Scanning takes >5 minutes
- Extraction is very slow

**Solutions:**

1. **Increase workers:**
```yaml
# configs/default.yaml
extraction:
  num_workers: 8  # Increase from 4
```

2. **Use multi-pass scanning:**
```bash
python toolkit/bob_lz_scan.py --rom B.O.B..smc --multipass
```

3. **Reduce thoroughness:**
```bash
# Faster but less thorough
python toolkit/bob_lz_scan.py --rom B.O.B..smc --stride 32
```

---

## Getting Help

If these solutions don't resolve your issue:

1. **Check logs:**
   - Most tools write to `out/analysis.log`
   - Look for error messages or stack traces

2. **Verify environment:**
```bash
python --version  # Should be 3.8+
pip list | grep -E "pytest|black|flake8"  # Dev dependencies
```

3. **Run tests:**
```bash
python run_tests.py  # Should show all tests passing
```

4. **Check documentation:**
   - `README.md` - Quick start guide
   - `docs/USER_GUIDE.md` - Comprehensive usage
   - `docs/TECHNICAL.md` - Technical details

5. **Open an issue:**
   - Include error messages
   - Attach `rom_map.json` if applicable
   - Note Python version and OS

---

## Appendix: Configuration Reference

### Environment Variables

```bash
DOC_PIPELINE_DEVICE=cuda          # 'cuda', 'cpu', or 'auto'
DOC_PIPELINE_GPU_TYPE=rtx4000     # 'rtx4000', 'm2000', 'k40', or 'auto'
DOC_PIPELINE_DATA_FOLDER=/path/to/data
DOC_PIPELINE_CHECKPOINT_FOLDER=/path/to/checkpoints
```

### Config File Locations

| Config | Purpose |
|--------|---------|
| `configs/default.yaml` | Default configuration |
| `configs/production.yaml` | RTX 4000 optimized |
| `configs/legacy_gpu.yaml` | M2000/K40 optimized |

### Log File Locations

| Tool | Log File |
|------|----------|
| Scanner | `out/scan.log` |
| Extractor | `out/extract.log` |
| Full pipeline | `out/pipeline.log` |

---

**End of Troubleshooting Guide**
