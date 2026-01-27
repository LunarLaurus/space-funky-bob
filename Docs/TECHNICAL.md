# Technical Design Document (TDD)
## B.O.B. ROM Analysis Toolkit

**Document Version**: 1.0  
**Date**: January 27, 2026  
**Status**: Living Document  
**Audience**: Developers, Contributors, Technical Reviewers

---

## 1. System Overview

### 1.1 Purpose
This document describes the technical architecture, algorithms, and implementation details of the B.O.B. ROM Analysis Toolkit. It serves as a reference for developers contributing to or integrating with the project.

### 1.2 Scope
- LZ77 decompression algorithm
- ROM structure analysis
- Code/data classification heuristics
- Export format specifications
- Integration patterns

### 1.3 System Context

```
┌────────────────────────────────────────────────┐
│         User / Developer Environment            │
│  (Python 3.8+, Command Line, Ghidra/IDA)       │
└──────────────────┬─────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────┐
│       B.O.B. ROM Analysis Toolkit              │
│  ┌──────────────┬──────────────┬────────────┐  │
│  │  bob_lz.py   │bob_lz_scan.py│ bob_map.py │  │
│  │  (Decoder)   │  (Scanner)   │ (Mapper)   │  │
│  └──────────────┴──────────────┴────────────┘  │
└──────────────────┬─────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────┐
│          Output Artifacts                      │
│  (JSON, HTML, Decompressed Binary Files)       │
└──────────────────┬─────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────┐
│       Reverse Engineering Tools                │
│  (Ghidra, IDA Pro, radare2, Hex Editors)       │
└────────────────────────────────────────────────┘
```

---

## 2. Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Presentation Layer                  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   CLI       │  │ HTML Output  │  │ JSON Output  │   │
│  │ (argparse)  │  │ (Jinja2-like)│  │  (stdlib)    │   │
│  └─────────────┘  └──────────────┘  └──────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   Business Logic Layer                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │          ROM Analysis Orchestrator               │   │
│  │  (test_workflow.sh, future: Python orchestrator) │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐    │
│  │ Decompressor │  │   Scanner    │  │   Mapper   │    │
│  │  (bob_lz.py) │  │(bob_lz_scan) │  │(bob_map.py)│    │
│  └──────────────┘  └──────────────┘  └────────────┘    │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    Data Access Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐    │
│  │ ROM Loader   │  │ Header Parser│  │ File I/O   │    │
│  │  (pathlib)   │  │   (struct)   │  │ (pathlib)  │    │
│  └──────────────┘  └──────────────┘  └────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Module Descriptions

#### 2.2.1 bob_lz.py - Decompression Module
**Purpose**: Implements B.O.B. LZ77 decompression algorithm  
**Dependencies**: None (stdlib only)  
**Exports**:
- `bob_lz_decompress(src_bytes, dec_len) -> (bytes, int)`
- `bob_lz_decompress_exploratory(src_bytes, max_dec_len) -> (bytes, int, str)`

**Key Responsibilities**:
- Parse LZ77 chunk headers (8-bit status bytes)
- Handle literal byte copying
- Handle distance/length pair decoding
- Validate distance constraints
- Support overlapping copies

#### 2.2.2 bob_lz_scan.py - Scanner Module
**Purpose**: Locate compressed blocks within ROM  
**Dependencies**: bob_lz  
**Exports**:
- `scan_rom_for_compressed_blocks(rom_data, header_offset, outdir) -> list`
- `detect_rom_header(rom_data) -> (bool, int, str)`
- `detect_rom_mapping(rom_data, header_offset) -> str`

**Key Responsibilities**:
- Detect ROM header presence (512-byte copier header)
- Determine LoROM vs HiROM mapping
- Scan ROM with configurable stride
- Apply entropy heuristics to filter candidates
- Validate decompression success
- Export decompressed data to files

#### 2.2.3 bob_map.py - Mapping Module
**Purpose**: Classify ROM regions as code/data/compressed  
**Dependencies**: bob_lz_scan (for candidates.json)  
**Exports**:
- `classify_regions(rom_data, header_offset, candidates_data, mapping) -> list`
- `analyze_opcode_density(rom, offset, length) -> (float, float)`
- `trace_code_from_vectors(rom, header_offset, mapping) -> set`

**Key Responsibilities**:
- Parse SNES reset/interrupt vectors
- Recursive code tracing from entry points
- 65816 opcode validation
- Entropy-based discrimination
- Region consolidation
- HTML visualization generation

---

## 3. Data Models

### 3.1 ROM Structure

```python
ROM File (.smc/.sfc)
├── [Optional: 512-byte Copier Header]
└── ROM Data
    ├── Bank 0 ($00xxxx in LoROM)
    │   ├── Code regions
    │   ├── Data regions
    │   └── Header at $7FC0 (LoROM) or $FFC0 (HiROM)
    ├── Bank 1 ($01xxxx)
    ├── ...
    └── Bank N
```

### 3.2 SNES Header Format (32 bytes at 0x7FC0/0xFFC0)

```
Offset  Size  Description
------  ----  -----------
+0      21    ROM Title (ASCII, space-padded)
+21     1     Makeup/Speed byte (0x69 for B.O.B.)
+22     1     ROM Type
+23     1     ROM Size (log2(size) - 10)
+24     1     SRAM Size
+25     1     Destination Code (0x01 = USA)
+26     1     Fixed value (0x33)
+27     1     Version number
+28     2     Checksum complement (little-endian)
+30     2     Checksum (little-endian)
```

### 3.3 LZ77 Compressed Block Format

```
Chunk:
  [1 byte]   Status byte (8 bits, processed MSB first)
  For each bit in status byte:
    If bit == 0:
      [1 byte]   Literal byte
    If bit == 1:
      [2 bytes]  Distance/Length pair (little-endian)
                 Bits 0-10:  Distance (1-2047)
                 Bits 11-15: Length - 3 (effective length 3-34)

Next chunk follows immediately...
```

### 3.4 JSON Output Schemas

#### candidates.json
```json
{
  "rom_file": "path/to/rom.smc",
  "rom_size": 1048576,
  "rom_title": "B.O.B.",
  "has_header": true,
  "header_offset": 512,
  "rom_mapping": "LoROM",
  "num_candidates": 42,
  "candidates": [
    {
      "offset": "0x1AD34",
      "offset_int": 109876,
      "compressed_size": 1234,
      "decompressed_size": 4096,
      "success": true,
      "entropy_compressed": 7.45,
      "entropy_decompressed": 4.82,
      "looks_like_tiles": true,
      "reason": "successful decompression with entropy drop",
      "output_file": "decompressed_01AD34.bin"
    }
  ]
}
```

#### rom_map.json
```json
{
  "rom_file": "path/to/rom.smc",
  "rom_size": 1048576,
  "header_offset": 512,
  "rom_mapping": "LoROM",
  "num_regions": 156,
  "regions": [
    {
      "start": 0,
      "end": 32768,
      "start_hex": "0x0",
      "end_hex": "0x8000",
      "size": 32768,
      "size_hex": "0x8000",
      "type": "code",
      "confidence": 92
    }
  ]
}
```

---

## 4. Algorithms

### 4.1 LZ77 Decompression

**Algorithm**: B.O.B. LZ77 Variant  
**Complexity**: O(n) where n = decompressed size  
**Memory**: O(n) for output buffer

```python
def bob_lz_decompress(src_bytes, dec_len):
    """
    Pseudocode:
    1. Initialize source position s=0, destination position d=0
    2. Allocate output buffer of size dec_len
    3. While d < dec_len:
        a. Read chunk header byte
        b. For each of 8 bits (MSB first):
            i.  If bit == 0: copy literal byte
            ii. If bit == 1: decode distance/length, copy with overlap
        c. Break if d >= dec_len
    4. Return (output_buffer, consumed_bytes)
    """
    # Implementation in bob_lz.py
```

**Edge Cases**:
- Distance == 0: ERROR (invalid)
- Distance > current_output_size: ERROR (invalid)
- Length > distance: OK (overlapping copy with sliding window)
- Output overrun: Stop copying, return what we have

### 4.2 Entropy Calculation

**Algorithm**: Shannon Entropy  
**Complexity**: O(n) where n = data length  
**Memory**: O(1) (fixed 256-element frequency array)

```python
def calculate_entropy(data):
    """
    Pseudocode:
    1. Count frequency of each byte value (0-255)
    2. For each non-zero frequency:
        a. Calculate probability p = freq / total_bytes
        b. Add -p * log2(p) to entropy sum
    3. Return entropy (range: 0.0 to 8.0 bits/byte)
    
    High entropy (7-8): Compressed/encrypted data
    Medium entropy (4-7): Mixed code/data
    Low entropy (0-4): Repetitive data, graphics
    """
    # Implementation in bob_lz_scan.py and bob_map.py
```

### 4.3 Compressed Block Detection

**Algorithm**: Entropy-based Sliding Window with Validation  
**Complexity**: O(m * n * k) where m=ROM size, n=test sizes, k=decompression cost  
**Memory**: O(max_decompressed_size)

```python
def scan_rom_for_compressed_blocks(rom_data, header_offset, outdir):
    """
    Pseudocode:
    1. For each offset in ROM (stride-based):
        a. Calculate entropy of 64-byte window
        b. If entropy in range [6.0, 8.0]:
            i.  For each test decompressed size (1KB, 2KB, 4KB, ...):
                - Attempt decompression
                - If successful:
                    * Calculate entropy of decompressed data
                    * If entropy_compressed > entropy_decompressed:
                        + Record as candidate
                        + Save decompressed data
                        + Break to next offset
    2. Return list of candidates
    
    Optimization: Configurable stride (default: 16 bytes)
    False positive reduction: Require entropy drop + tile patterns
    """
    # Implementation in bob_lz_scan.py
```

### 4.4 Code/Data Classification

**Algorithm**: Multi-Heuristic Region Classification  
**Complexity**: O(n) where n = ROM size  
**Memory**: O(n) for region map

```python
def classify_regions(rom_data, header_offset, candidates_data, mapping):
    """
    Pseudocode:
    1. Initialize region_map[rom_size] = "unknown"
    
    2. Mark compressed regions from candidates.json
    
    3. Trace code from reset/interrupt vectors:
        a. Read vector table at 0x7FE0 (LoROM) or 0xFFE0 (HiROM)
        b. Mark region around reset vector as code
    
    4. For each unmapped block (512 bytes):
        a. Calculate entropy
        b. Calculate opcode density (valid 65816 opcodes / total)
        c. Calculate average instruction length
        d. Classify:
            - If opcode_density > 0.85 AND entropy < 6.5: CODE
            - If entropy > 7.2: COMPRESSED_CANDIDATE
            - If entropy < 4.0: GRAPHICS_CANDIDATE
            - Else: DATA
    
    5. Consolidate adjacent regions of same type
    
    6. Return list of regions with metadata
    
    Thresholds (tunable):
    - Opcode density: 85% (balance precision vs recall)
    - Code entropy: <6.5 bits/byte
    - Compressed entropy: >7.2 bits/byte
    - Graphics entropy: <4.0 bits/byte
    """
    # Implementation in bob_map.py
```

### 4.5 65816 Opcode Validation

**Algorithm**: Instruction Length Validation  
**Complexity**: O(n) where n = block size  
**Memory**: O(1)

```python
def analyze_opcode_density(rom, offset, length=256):
    """
    Pseudocode:
    1. Initialize valid_count = 0, total_instructions = 0
    2. Position pos = 0
    3. While pos < length:
        a. Read byte at pos
        b. If byte is valid opcode in OPCODES table:
            i.  Increment valid_count
            ii. Skip ahead by instruction length
        c. Else: Skip 1 byte
        d. Increment total_instructions
    4. Return (valid_count / total_instructions, avg_instruction_length)
    
    Valid opcodes: Subset of 65816 instruction set
    Instruction lengths: 1-4 bytes (varies by opcode and M/X flags)
    Limitation: Does not track M/X flag changes (future enhancement)
    """
    # Implementation in bob_map.py
```

---

## 5. Data Flow Diagrams

### 5.1 End-to-End Analysis Flow

```
┌───────────┐
│ ROM File  │
│ (.smc)    │
└─────┬─────┘
      │
      ▼
┌──────────────────┐
│ Detect Header    │  (512 bytes or headerless?)
│ Detect Mapping   │  (LoROM or HiROM?)
└────────┬─────────┘
         │
         ├─────────────────────────┐
         │                         │
         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐
│ Scan for        │      │ Read Candidates │
│ Compressed      │      │ (if provided)   │
│ Blocks          │      └────────┬────────┘
│                 │               │
│ • Entropy scan  │               │
│ • Decompress    │               │
│ • Validate      │               │
└────────┬────────┘               │
         │                        │
         ▼                        │
┌─────────────────┐               │
│ candidates.json │               │
│ decompressed_*  │               │
└────────┬────────┘               │
         │                        │
         └────────────┬───────────┘
                      │
                      ▼
           ┌──────────────────┐
           │ Classify Regions │
           │                  │
           │ • Vector trace   │
           │ • Opcode density │
           │ • Entropy        │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ rom_map.json     │
           │ rom_map.html     │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Import to Ghidra │
           │ or IDA Pro       │
           └──────────────────┘
```

### 5.2 LZ77 Decompression Flow

```
┌─────────────┐
│ Compressed  │
│ Data Stream │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Read Chunk Header│  (8 bits)
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────┐
│ Process 8 bits (MSB first)   │
│ ┌──────────┐  ┌────────────┐ │
│ │ Bit = 0? │  │  Bit = 1?  │ │
│ │  (literal)│  │ (dist/len) │ │
│ └────┬─────┘  └──────┬─────┘ │
│      │                │       │
│      ▼                ▼       │
│ ┌─────────┐     ┌───────────┐│
│ │Copy byte│     │Parse 16bit││
│ │to output│     │LE value   ││
│ └────┬────┘     └──────┬────┘│
│      │                 │     │
│      │                 ▼     │
│      │          ┌────────────┐│
│      │          │Extract:    ││
│      │          │ dist=low11││
│      │          │ len=hi5+3 ││
│      │          └──────┬─────┘│
│      │                 │      │
│      │                 ▼      │
│      │          ┌────────────┐│
│      │          │Copy len    ││
│      │          │bytes from  ││
│      │          │out[d-dist] ││
│      │          └──────┬─────┘│
│      │                 │      │
│      └─────────┬───────┘      │
│                │              │
└────────────────┼──────────────┘
                 │
                 ▼
           ┌──────────┐
           │ d >= len?│
           └────┬─┬───┘
              No│ │Yes
                │ │
                │ └──► Return output
                │
                └──► Read next chunk header
```

---

## 6. Interface Specifications

### 6.1 Command-Line Interface

#### bob_lz.py
```bash
python bob_lz.py
# Runs unit tests, exits with 0 on success
```

#### bob_lz_scan.py
```bash
python bob_lz_scan.py --rom ROM_FILE [--outdir OUTPUT_DIR]

Arguments:
  --rom ROM_FILE       Path to SNES ROM file (.smc, .sfc)
  --outdir OUTPUT_DIR  Output directory (default: "out")

Outputs:
  - {outdir}/candidates.json
  - {outdir}/decompressed_XXXXXX.bin (one per candidate)

Exit Codes:
  0 - Success
  1 - Error (missing ROM, invalid file, etc.)
```

#### bob_map.py
```bash
python bob_map.py --rom ROM_FILE [--candidates CANDIDATES_JSON] [--outdir OUTPUT_DIR]

Arguments:
  --rom ROM_FILE            Path to SNES ROM file
  --candidates CANDIDATES   Path to candidates.json (optional)
  --outdir OUTPUT_DIR       Output directory (default: "out")

Outputs:
  - {outdir}/rom_map.json
  - {outdir}/rom_map.html

Exit Codes:
  0 - Success
  1 - Error
```

#### validate_known_block.py
```bash
python validate_known_block.py ROM_FILE

Arguments:
  ROM_FILE  Path to B.O.B. ROM file

Outputs:
  - Console output with validation results

Exit Codes:
  0 - Validation successful
  1 - Validation failed or error
```

### 6.2 Python API

#### bob_lz Module
```python
from bob_lz import bob_lz_decompress, bob_lz_decompress_exploratory

# Strict decompression (requires exact size)
decompressed, consumed = bob_lz_decompress(
    src_bytes=compressed_data,
    dec_len=expected_size
)

# Exploratory decompression (auto-detect size)
decompressed, consumed, error = bob_lz_decompress_exploratory(
    src_bytes=compressed_data,
    max_dec_len=65536
)
```

#### bob_lz_scan Module
```python
from bob_lz_scan import (
    detect_rom_header,
    detect_rom_mapping,
    scan_rom_for_compressed_blocks
)

# Detect ROM properties
has_header, header_offset, title = detect_rom_header(rom_data)
mapping = detect_rom_mapping(rom_data, header_offset)

# Scan for compressed blocks
candidates = scan_rom_for_compressed_blocks(
    rom_data=rom_bytes,
    header_offset=header_offset,
    outdir=Path("output")
)
```

#### bob_map Module
```python
from bob_map import classify_regions, generate_html_visualization

# Classify ROM regions
regions = classify_regions(
    rom_data=rom_bytes,
    header_offset=header_offset,
    candidates_data=candidates_json,
    mapping="LoROM"
)

# Generate visualization
generate_html_visualization(
    regions=regions,
    rom_size=len(rom_data),
    output_path=Path("rom_map.html")
)
```

---

## 7. Error Handling

### 7.1 Error Categories

#### User Errors (Recoverable)
- **Missing ROM file**: Clear error message, exit code 1
- **Invalid ROM format**: Warn, attempt graceful degradation
- **Insufficient permissions**: Clear error message, suggest fix

#### Data Errors (Partially Recoverable)
- **Invalid LZ77 stream**: Report error, continue with other blocks
- **Truncated compressed data**: Mark as failed, continue scanning
- **Corrupted ROM header**: Use defaults, warn user

#### System Errors (Non-Recoverable)
- **Out of memory**: Clear error, suggest reducing scope
- **Disk full**: Clear error, can't write outputs
- **Python version mismatch**: Check at startup, fail fast

### 7.2 Error Reporting

```python
# Error message format
ERROR: {Component} - {Brief description}
  Cause: {Detailed explanation}
  Suggestion: {How to fix}
  
# Example
ERROR: LZ77 Decoder - Invalid distance in compressed stream
  Cause: Distance value (2047) exceeds current output buffer size (142)
  Suggestion: This block may not be valid compressed data. Check offset 0x1234.
```

### 7.3 Validation Strategy

```python
def validate_input(rom_path):
    """Input validation checklist"""
    # 1. File exists
    if not rom_path.exists():
        raise FileNotFoundError(f"ROM file not found: {rom_path}")
    
    # 2. File is readable
    if not os.access(rom_path, os.R_OK):
        raise PermissionError(f"Cannot read ROM file: {rom_path}")
    
    # 3. File size reasonable (not empty, not > 8MB)
    size = rom_path.stat().st_size
    if size < 1024:
        raise ValueError(f"ROM file too small: {size} bytes")
    if size > 8 * 1024 * 1024:
        print(f"WARNING: Large ROM ({size / 1024 / 1024:.1f} MB), analysis may be slow")
    
    # 4. File extension reasonable
    if rom_path.suffix.lower() not in ['.smc', '.sfc', '.bin']:
        print(f"WARNING: Unusual file extension: {rom_path.suffix}")
```

---

## 8. Performance Considerations

### 8.1 Bottlenecks

| Operation | Complexity | Typical Time (1MB ROM) | Optimization |
|-----------|------------|------------------------|--------------|
| ROM scanning | O(n*m) | 30-60 seconds | Increase stride, parallelize |
| LZ77 decompress | O(n) | <1ms per block | Optimize hot path, use C extension |
| Entropy calc | O(n) | <1ms per block | Cache results |
| Opcode analysis | O(n) | 5-10 seconds | Limit sample size |
| JSON export | O(n) | <1 second | Use ujson if available |
| HTML render | O(n) | <1 second | Consolidate regions |

### 8.2 Memory Usage

```python
# Worst-case memory usage for 1MB ROM:
ROM data:           1 MB (input)
Decompressed data:  ~2 MB (assuming 2:1 compression, multiple blocks)
Region map:         1 MB (one entry per byte, worst case)
Candidates list:    ~100 KB (100 candidates * ~1KB metadata)
Total:              ~4 MB

# For 4MB ROM: ~16 MB (acceptable for modern systems)
```

### 8.3 Optimization Opportunities

#### High Impact
1. **Parallelize ROM scanning**: Use multiprocessing for independent blocks
2. **Optimize entropy calculation**: Use numpy if available (optional dep)
3. **Cache decompression results**: Avoid re-decompressing same blocks
4. **Adaptive stride**: Use smaller stride near high-entropy regions

#### Medium Impact
5. **Early termination**: Skip regions already classified as compressed
6. **Lazy loading**: Only load ROM once, don't duplicate in memory
7. **Stream processing**: Process large ROMs in chunks

#### Low Impact
8. **Compile with Cython**: Optional for performance-critical users
9. **Profile-guided optimization**: Measure before optimizing

---

## 9. Testing Strategy

### 9.1 Unit Tests

```python
# bob_lz.py tests
test_literal_bytes()           # All-literal stream
test_overlapping_copy()        # Length > distance
test_zero_distance_error()     # Invalid distance=0
test_distance_too_large()      # Distance > output_size
test_exploratory_mode()        # Unknown decompressed size

# bob_lz_scan.py tests (future)
test_header_detection()        # With/without 512-byte header
test_lorom_vs_hirom()          # Mapping detection
test_entropy_filtering()       # False positive reduction

# bob_map.py tests (future)
test_opcode_density()          # Code vs data discrimination
test_vector_tracing()          # Entry point detection
test_region_consolidation()    # Adjacent region merging
```

### 9.2 Integration Tests

```python
# End-to-end workflow
test_full_bob_analysis()       # Complete analysis of B.O.B. ROM
test_known_block_validation()  # Validate against 0x1AD34 block
test_json_output_schema()      # Verify JSON structure
test_html_visualization()      # Ensure HTML renders

# Cross-platform
test_windows_paths()           # Backslash path handling
test_macos_execution()         # Ensure works on macOS
test_linux_execution()         # Ensure works on Linux
```

### 9.3 Performance Tests

```python
# Benchmarks
benchmark_1mb_rom_scan()       # Target: <60 seconds
benchmark_lz77_throughput()    # Target: >10 MB/s
benchmark_memory_usage()       # Target: <16 MB for 4MB ROM
```

### 9.4 Edge Case Tests

```python
# Malformed inputs
test_truncated_rom()           # Incomplete ROM file
test_corrupted_header()        # Invalid checksum
test_empty_file()              # 0-byte ROM
test_extremely_large_rom()     # 16MB+ ROM

# Decompression edge cases
test_maximum_distance()        # Distance = 2047
test_maximum_length()          # Length = 34
test_minimum_length()          # Length = 3
test_decompression_overrun()   # Output exceeds expected size
```

---

## 10. Security Considerations

### 10.1 Threat Model

**Attack Surface**: ROM file processing  
**Threat Actors**: Malicious ROM files (accidental or intentional)  
**Assets**: User's file system, CPU/memory resources

### 10.2 Security Controls

#### Input Validation
```python
# 1. File size limits
MAX_ROM_SIZE = 16 * 1024 * 1024  # 16 MB
if file_size > MAX_ROM_SIZE:
    raise ValueError("ROM too large")

# 2. Decompression bomb protection
MAX_DECOMPRESSED_SIZE = 256 * 1024  # 256 KB per block
if dec_len > MAX_DECOMPRESSED_SIZE:
    raise ValueError("Decompressed size too large")

# 3. Memory limits
MAX_MEMORY_USAGE = 512 * 1024 * 1024  # 512 MB total
# Monitor and enforce during processing

# 4. No arbitrary code execution
# Never eval(), exec(), or import from ROM data
# Never execute decompressed data
```

#### Resource Limits
```python
# CPU time limits (future enhancement)
import signal
signal.alarm(300)  # 5 minute timeout

# Memory monitoring
import psutil
if process.memory_info().rss > MAX_MEMORY_USAGE:
    raise MemoryError("Memory limit exceeded")
```

### 10.3 Privacy Considerations
- **No telemetry**: Do not phone home with ROM data
- **No cloud uploads**: All processing local only
- **No logging of ROM content**: Log metadata only, not actual bytes

---

## 11. Deployment

### 11.1 Installation

```bash
# Method 1: Direct use (no installation)
git clone https://github.com/user/bob-rom-analysis
cd bob-rom-analysis
python bob_lz.py

# Method 2: PyPI (future)
pip install bob-rom-analysis

# Method 3: System package (future)
# apt install bob-rom-analysis (Ubuntu)
# brew install bob-rom-analysis (macOS)
```

### 11.2 Dependencies

**Runtime**:
- Python 3.8+ (stdlib only, no pip packages)

**Development**:
- pytest (testing)
- pylint / flake8 (linting)
- black (formatting)
- mypy (type checking, optional)
- coverage.py (test coverage)

### 11.3 Configuration

```python
# config.py (future enhancement)
CONFIG = {
    "scanning": {
        "stride": 16,              # Bytes between scan positions
        "entropy_min": 6.0,        # Minimum entropy for candidates
        "entropy_max": 8.0,        # Maximum entropy for candidates
        "test_sizes": [0x400, 0x800, 0x1000, 0x2000, 0x4000, 0x8000]
    },
    "classification": {
        "opcode_density_threshold": 0.85,
        "code_entropy_max": 6.5,
        "compressed_entropy_min": 7.2,
        "graphics_entropy_max": 4.0
    },
    "performance": {
        "max_memory_mb": 512,
        "timeout_seconds": 300,
        "parallel_workers": 4
    }
}
```

---

## 12. Future Enhancements

### 12.1 Planned Improvements

#### Performance
- **Parallel scanning**: Use multiprocessing.Pool for block scanning
- **Cython compilation**: Compile hot paths (LZ77 decoder, entropy)
- **Memory-mapped files**: Use mmap for large ROM handling
- **Caching layer**: Cache entropy calculations, decompression results

#### Functionality
- **GUI application**: Electron or Qt desktop app
- **Additional formats**: Support other LZ variants, Huffman, RLE
- **Pattern recognition**: ML-based code/data classification
- **Tile rendering**: Render SNES graphics tiles as PNG

#### Integration
- **IDA Pro support**: Python plugin for IDA
- **radare2 support**: r2pipe integration
- **Emulator integration**: bsnes-plus debugging

#### Quality
- **Formal specification**: Mathematical model of LZ77 variant
- **Fuzzing**: AFL or similar for robustness testing
- **CI/CD**: Automated testing on commit
- **Benchmarking suite**: Standardized performance tests

---

## 13. References

### 13.1 External Documentation
- [65816 Instruction Set](http://www.defence-force.org/computing/oric/coding/annexe_2/)
- [SNES Memory Mapping](https://wiki.superfamicom.org/memory-mapping)
- [LZ77 Algorithm](https://en.wikipedia.org/wiki/LZ77_and_LZ78)
- [Shannon Entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory))

### 13.2 Related Tools
- **DiztinGUIsh**: SNES disassembler with GUI
- **Lunar Compress**: Multi-format compression tool
- **asar**: SNES assembler
- **bass**: SNES assembler by Near

### 13.3 Research Papers
- GuyPerfect: "B.O.B. Compression Format Reverse Engineering" (2010s)
- Various SNES development community forum posts

---

## 14. Appendix

### 14.1 Glossary

See CLAUDE.md Appendix for full glossary.

### 14.2 Change Log

**v1.0 (January 27, 2026)**
- Initial technical design document
- Core algorithms documented
- API specifications defined

---

**Document Approval**  
**Technical Lead**: TBD  
**Reviewed By**: TBD  
**Approved**: TBD  
**Next Review**: End of Sprint 1
