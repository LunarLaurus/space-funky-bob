# B.O.B. ROM Analysis Toolkit - Claude Context

## Project Overview

**Project Name**: B.O.B. ROM Analysis Toolkit  
**Target Platform**: SNES (Super Nintendo Entertainment System)  
**Target ROM**: Space Funky B.O.B. (Electronic Arts / Gray Matter)  
**Language**: Python 3.8+  
**Primary Use Case**: Retro game reverse engineering and ROM analysis  

## Project Goals

### Primary Goals

1. **Automated ROM Structure Analysis**
   - Automatically detect and classify ROM regions (code vs data)
   - Identify compressed blocks without manual intervention
   - Generate machine-readable maps for reverse engineering tools

2. **B.O.B. LZ77 Decompression**
   - Implement robust decoder for B.O.B.'s custom LZ77 variant
   - Handle programmer quirks (overlapping copies, edge cases)
   - Provide both strict and exploratory decompression modes

3. **Reverse Engineering Workflow Integration**
   - Export annotations for Ghidra (primary), IDA Pro, radare2
   - Generate human-readable visualizations
   - Produce reproducible, scriptable workflows

4. **Knowledge Preservation**
   - Document the B.O.B. compression format
   - Preserve reverse engineering techniques for SNES ROMs
   - Create reusable tools for similar SNES games

### Secondary Goals

5. **Educational Resource**
   - Serve as reference implementation for LZ77 variants
   - Demonstrate SNES ROM analysis techniques
   - Provide well-documented, readable code

6. **Extensibility**
   - Design for adaptation to other SNES games
   - Support multiple ROM mapping modes (LoROM, HiROM, ExHiROM)
   - Enable community contributions

## Success Criteria

### Must Have (MVP)
- ✅ Working LZ77 decoder with unit tests
- ✅ ROM scanner that identifies compressed blocks
- ✅ Code/data classifier with configurable heuristics
- ✅ JSON output format for automation
- ✅ Ghidra import instructions
- ✅ Validation against known compressed block (0x1AD34)

### Should Have (v1.0)
- 🔄 HTML visualization of ROM map (in progress)
- 🔄 Comprehensive documentation
- 🔄 Automated test suite
- ⬜ IDA Pro import script
- ⬜ Performance optimization for large ROMs

### Could Have (Future)
- ⬜ GUI interface
- ⬜ Tile/sprite rendering for graphics validation
- ⬜ Machine learning-based block classification
- ⬜ Multi-ROM batch processing
- ⬜ Integration with emulator debugging tools

### Won't Have (Out of Scope)
- ❌ ROM editing/patching capabilities
- ❌ Game-specific logic analysis
- ❌ Audio/music extraction
- ❌ Real-time emulation
- ❌ Web-based interface

## Technical Architecture

### Core Components

```
bob-rom-analysis/
├── bob_lz.py              # LZ77 decoder (core algorithm)
├── bob_lz_scan.py         # ROM scanner (compressed block detection)
├── bob_map.py             # Region classifier (code/data analysis)
├── validate_known_block.py # Validation against known data
├── test_workflow.sh       # End-to-end automation
└── docs/
    ├── ghidra_import.txt  # Integration guide
    └── roadmap/           # Sprint planning
```

### Data Flow

```
ROM File (.smc/.sfc)
    ↓
[bob_lz_scan.py] → Detect header, mapping, compressed blocks
    ↓
candidates.json + decompressed_*.bin files
    ↓
[bob_map.py] → Classify regions using 65816 analysis
    ↓
rom_map.json + rom_map.html
    ↓
[Ghidra] → Import bookmarks and analyze
```

### Key Algorithms

1. **LZ77 Decompression** (bob_lz.py)
   - Chunk-based processing with 8-bit headers
   - Distance/length pair decoding (11-bit distance, 5-bit length)
   - Overlapping copy support with sliding window

2. **Compressed Block Detection** (bob_lz_scan.py)
   - Entropy scanning (6.0-8.0 range indicates compression)
   - Heuristic decompression attempts
   - Pattern matching for SNES tile data
   - Entropy drop validation (compressed → decompressed)

3. **Code/Data Classification** (bob_map.py)
   - Vector table analysis (reset/interrupt vectors)
   - Recursive 65816 disassembly from entry points
   - Opcode density thresholds (>85% = code)
   - Entropy-based discrimination (<6.5 = code, >7.2 = compressed)

## B.O.B. ROM Specifications

### ROM Properties
- **Title**: "B.O.B."
- **Mapping**: LoROM Fast
- **ROM Size**: 8 Mbits (1 MB / 0x100000 bytes)
- **Header Location**: 0x7FC0 (LoROM standard)
- **Fixed Byte**: 0x69
- **Checksum**: 0x7379
- **Checksum Complement**: 0x8C86

### Known Compressed Blocks
1. **Block at 0x1AD34**
   - Compressed offset: 0x1AD34
   - Decompressed size: 0x822 bytes (2082 bytes)
   - Status: ✅ Validated

### LZ77 Format Details
- **Chunk Header**: 8-bit status byte (MSB processed first)
- **Literal Bit (0)**: Copy next byte verbatim
- **Distance/Length Bit (1)**: 16-bit LE pair
  - Low 11 bits: distance (1-2047)
  - High 5 bits: (length - 3), effective length 3-34
- **Quirks**: 
  - Distance can be 0 (error condition)
  - Length may exceed distance (overlapping copy)
  - No explicit end-of-stream marker

## Development Guidelines

### Code Quality Standards
- **Type Safety**: Use type hints where beneficial
- **Error Handling**: Graceful failures with descriptive messages
- **Testing**: Unit tests for all core functions
- **Documentation**: Docstrings for all public functions
- **Performance**: Handle 4MB ROMs in <2 minutes

### Testing Requirements
- Unit tests for LZ77 decoder (5+ test cases)
- Integration test with known B.O.B. block
- Edge case testing (invalid distance, truncated data)
- Performance benchmarks on reference hardware

### Documentation Requirements
- README with quick start guide
- API documentation for all public functions
- Ghidra integration step-by-step guide
- Troubleshooting section with common issues

## Project Constraints

### Technical Constraints
- **Pure Python**: No compiled dependencies (portability)
- **Python 3.8+**: Minimum version for compatibility
- **Memory**: Must handle 4MB ROMs without streaming (fits in RAM)
- **Cross-platform**: Linux, macOS, Windows support

### Legal Constraints
- **ROM Ownership**: Users must own ROM files legally
- **No Distribution**: Do not distribute copyrighted ROM data
- **Clean Room**: Implementation based on published documentation
- **Attribution**: Credit GuyPerfect for LZ77 reverse engineering

### Design Constraints
- **Command-line First**: GUI is optional, CLI is primary interface
- **Reproducible**: Same inputs always produce same outputs
- **Scriptable**: All functionality accessible via Python imports
- **Tool Agnostic**: Support multiple RE tools (Ghidra, IDA, r2)

## Dependencies

### Python Standard Library Only
- `argparse` - CLI argument parsing
- `json` - Data serialization
- `math` - Entropy calculations
- `pathlib` - File path handling
- `struct` - Binary data unpacking
- `collections` - Data structures

### External Tools (Optional)
- **Ghidra 10.x+** - Primary RE tool
- **IDA Pro** - Alternative RE tool
- **radare2** - Alternative RE tool
- **7-Zip** - For .7z source code archive

## Known Issues & Limitations

### Current Limitations
1. **Entropy-based Heuristics**: May miss low-entropy compressed blocks
2. **65816 Disassembly**: Does not handle self-modifying code
3. **Address Translation**: Assumes standard LoROM (no ExHiROM/SA-1)
4. **Decompression**: Requires size hints (cannot auto-detect block boundaries)
5. **Performance**: Stride-based scanning may miss blocks (configurable)

### Known Bugs
- None reported (as of initial release)

### Future Improvements Needed
- Better heuristics for variable-length compressed blocks
- Support for additional SNES ROM mapping schemes
- Automatic tile rendering for graphics validation
- More sophisticated code/data discrimination

## Community & Attribution

### Original Research
- **LZ77 Format**: Reverse engineered by GuyPerfect
- **Source Code**: Originally posted on eludevisibility.org
- **Documentation**: Consolidated on superfamicom.org by Matthew Callis

### This Implementation
- **Author**: Claude (Anthropic AI)
- **Date**: January 2026
- **License**: MIT (see LICENSE file)
- **Purpose**: Educational and reverse engineering research

### Contributing
- Improvements to heuristics algorithms
- Additional ROM mapping support
- Bug fixes and optimizations
- Documentation enhancements
- Test case additions

## References

### Documentation
- [65816 Programming Manual](http://www.defence-force.org/computing/oric/coding/annexe_2/)
- [SNES Development Wiki](https://wiki.superfamicom.org/)
- [B.O.B. Source Code Archive](https://superfamicom.org/) - Matthew Callis
- [Ghidra Documentation](https://ghidra-sre.org/)

### Related Projects
- SNES ROM disassemblers (DiztinGUIsh, etc.)
- LZ77 compression tools
- SNES development suites (bass, asar)

## Changelog

### v0.1.0 (Initial Release - January 2026)
- ✅ LZ77 decoder implementation
- ✅ ROM scanner with entropy-based detection
- ✅ Code/data classifier with 65816 analysis
- ✅ JSON output format
- ✅ Ghidra import instructions
- ✅ Validation script for known block
- ✅ Comprehensive documentation

### Roadmap
See `docs/roadmap/` for detailed sprint planning and feature tracking.

---

## Quick Reference

### Running the Toolkit
```bash
# Full analysis pipeline
bash test/test_workflow.sh "B.O.B. (U) [!].smc"

# Individual steps
python toolkit/bob_lz.py                              # Run unit tests
python toolkit/bob_lz_scan.py --rom rom/B.O.B..smc --outdir out/
python toolkit/bob_map.py --rom rom/B.O.B..smc --candidates out/candidates.json --outdir out/
python toolkit/validate_known_block.py rom/B.O.B..smc
```

### Key Files Generated
- `candidates.json` - Compressed block metadata
- `rom_map.json` - Region classifications
- `rom_map.html` - Interactive visualization
- `decompressed_*.bin` - Extracted data

### Heuristic Thresholds
| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| Opcode density | >85% | Code region |
| Entropy | <6.5 | Code/structured data |
| Entropy | >7.2 | Compressed/encrypted |
| Entropy | 2.0-8.0 | Compression candidate (relaxed range) |

---

**Last Updated**: February 12, 2026  
**Status**: Production Ready - All Critical Bugs Fixed  
**Maintainer**: Available for community contributions
