# QWEN.md — B.O.B. ROM Analysis Toolkit Operational Context

> **Project:** B.O.B. ROM Analysis Toolkit
> **Domain:** SNES Reverse Engineering / ROM Analysis
> **Language:** Python 3.8+ (stdlib only)
> **Target:** Space Funky B.O.B. (Electronic Arts / Gray Matter)
> **Current Branch:** `feature/rom-analysis-enhancement`
> **Status:** Planning Complete — Ready for Execution
> **Planning Directory:** `.planning/` (25 tasks across 5 squads)

---

## Part I: Project Overview

### Mission

This toolkit provides automated analysis of SNES ROMs, specifically targeting **Space Funky B.O.B.**. It locates compressed blocks, maps code vs data regions, and generates artifacts for reverse engineering workflows (Ghidra, IDA, radare2).

### Core Capabilities

| Component | Module | Purpose |
|-----------|--------|---------|
| **LZ77 Decoder** | `toolkit/bob_lz.py` | Decompress B.O.B.'s custom LZ77 variant |
| **ROM Scanner** | `toolkit/bob_lz_scan.py` | Detect compressed blocks via entropy analysis |
| **Region Mapper** | `toolkit/bob_map.py` | Classify ROM regions (code/data/compressed/graphics) |
| **Graphics Tools** | `toolkit/bob_graphics*.py` | Tile pattern detection and rendering |
| **Level Tools** | `toolkit/bob_extract*.py` | Level data extraction and injection |
| **Ghidra Import** | `toolkit/ImportBOBMap.py` | Load annotations into Ghidra |

### B.O.B. ROM Specifications

```
Title:        "B.O.B." (Space Funky B.O.B.)
Mapping:      LoROM Fast
ROM Size:     8 Mbits (1 MB / 0x100000 bytes)
Header:       0x7FC0 (LoROM standard)
Fixed Byte:   0x69
Checksum:     0x7379
Complement:   0x8C86
Known Block:  offset 0x1AD34, decompressed size 0x822 bytes
```

---

## Part II: Repository Structure

```
space-funky-bob/
├── .qwen/                          ← Qwen configuration
│   └── QWEN.md                     ← This file
│
├── .planning/                      ← Multi-squad deployment plans
│   ├── README.md                   ← Squad coordination guide
│   ├── squad-alpha/                ← Core Analysis Engine (5 tasks)
│   ├── squad-beta/                 ← Graphics & Visualization (5 tasks)
│   ├── squad-gamma/                ← Level Editor Tools (5 tasks)
│   ├── squad-delta/                ← Testing & QA (5 tasks)
│   └── squad-echo/                 ← Documentation & Integration (5 tasks)
│
├── toolkit/                        ← Core Python modules
│   ├── bob_lz.py                   # LZ77 decoder (core algorithm)
│   ├── bob_lz_encode.py            # LZ77 encoder (compression)
│   ├── bob_lz_scan.py              # ROM scanner for compressed blocks
│   ├── bob_map.py                  # Region classifier (code/data)
│   ├── bob_graphics.py             # Graphics/tile detection
│   ├── bob_graphics_v2.py          # Enhanced graphics detection
│   ├── bob_graphics_classifier.py  # ML-style graphics classifier
│   ├── bob_graphics_test_suite.py  # Graphics test harness
│   ├── bob_extract.py              # Level data extraction
│   ├── bob_extract_levels.py       # Level extraction logic
│   ├── bob_inject.py               # Data injection tools
│   ├── bob_render.py               # Tile rendering
│   ├── bob_visualize.py            # ROM visualization
│   ├── bob_analyze.py              # General analysis utilities
│   ├── ImportBOBMap.py             # Ghidra import script
│   ├── validate_known_block.py     # Validation against known data
│   └── USAGE.py                    # Usage examples
│
├── source/                         ← Original B.O.B. source code archives
│   ├── Disk A/                     # Music files, equates
│   ├── Disk B (CPBACKUP001)/       # Backup disk contents
│   ├── Disk C/                     # Additional source
│   ├── Disk D & E/                 # Combined disks
│   └── Disk F/                     # Additional source
│
├── tests/                          ← Unit tests (pytest)
│   ├── conftest.py                 # Pytest configuration
│   ├── test_bob_lz.py              # LZ77 decoder tests
│   └── test_bob_scan.py            # Scanner tests
│
├── test/                           ← Integration test scripts
│   └── test_workflow.sh            # End-to-end workflow
│
├── docs/                           ← Documentation
│   ├── README.md                   # User guide (this is root README)
│   ├── USER_GUIDE.md               # Comprehensive usage guide
│   ├── TECHNICAL.md                # Technical design document
│   ├── PRD.md                      # Product requirements
│   ├── STRUCTURE.md                # Directory structure docs
│   ├── DELIVERABLES.md             # Deliverables tracking
│   ├── EPICS.md                    # Epic-level feature tracking
│   ├── SPRINTS.md                  # Sprint planning
│   ├── GHIDRA_IMPORT.md            # Ghidra integration guide
│   ├── LEVEL_FORMAT.md             # Level data format docs
│   ├── LEVEL_FORMAT_ANALYSIS.md    # Level format reverse engineering
│   └── EDITOR_WORKFLOW.md          # Level editor workflow
│
├── rom/                            ← ROM files (user-provided, not in repo)
├── data/                           ← Analysis input/output data
├── backups/                        ← Backup files
├── scripts/                        ← Utility scripts
│
├── pyproject.toml                  # Python package configuration
├── requirements.txt                # Dependencies (stdlib only)
├── run_tests.py                    # Simple test runner (no pytest)
├── run_full_test_suite.py          # Full test suite runner
├── test_extraction.py              # Extraction tests
├── test_graphics.py                # Graphics tests
├── property_tests.py               # Property-based tests
│
├── .github/                        # GitHub configuration
│   └── workflows/
│       └── ci.yml                  # CI/CD pipeline
│
└── Space Funky B.O.B. Source Files/ ← Additional source archives
```

---

## Part III: Building & Running

### Prerequisites

- **Python 3.8+** (no external dependencies required!)
- **Ghidra 10.x+** (optional, for import scripts)
- **B.O.B. ROM file** (not included — user must own legally)

### Installation

```bash
# Clone or navigate to repository
cd space-funky-bob

# No pip install needed - pure Python stdlib!
# Optional: install dev dependencies for testing
pip install pytest black flake8
```

### Quick Start

```bash
# 1. Run LZ77 decoder unit tests
python toolkit/bob_lz.py

# 2. Run full test suite
python run_tests.py

# 3. Scan ROM for compressed blocks
python toolkit/bob_lz_scan.py --rom path/to/B.O.B..smc --outdir out/

# 4. Generate ROM region map
python toolkit/bob_map.py --rom path/to/B.O.B..smc --candidates out/candidates.json --outdir out/

# 5. Validate against known block
python toolkit/validate_known_block.py path/to/B.O.B..smc

# 6. Run full workflow
bash test/test_workflow.sh "path/to/B.O.B..smc"
```

### Testing

```bash
# Simple test runner (no dependencies)
python run_tests.py

# Full test suite
python run_full_test_suite.py

# Pytest (if installed)
pytest tests/ -v

# With coverage
pytest tests/ --cov=toolkit --cov-report=html

# Specific test files
pytest tests/test_bob_lz.py -v
pytest tests/test_bob_scan.py -v
```

### Python API Usage

```python
from toolkit.bob_lz import bob_lz_decompress, bob_lz_decompress_exploratory
from toolkit.bob_lz_scan import calculate_entropy, looks_like_compressed

# Decompress known block
rom = open('B.O.B..smc', 'rb').read()
compressed = rom[0x1AD34:0x1AD34 + 0x1000]
decompressed, consumed = bob_lz_decompress(compressed, 0x822)

# Exploratory decompression (unknown size)
result, consumed, error = bob_lz_decompress_exploratory(compressed)

# Entropy analysis
entropy = calculate_entropy(some_data)
is_compressed = looks_like_compressed(some_data)
```

---

## Part IV: Technical Architecture

### B.O.B. LZ77 Format

```
Chunk Header: 8-bit status byte (processed MSB→LSB)

Bit 0 (literal): Copy next byte verbatim
Bit 1 (backref): 16-bit little-endian distance/length pair
  - Low 11 bits:  distance (1-2047)
  - High 5 bits:  (length - 3), so length = 3-34

Edge Cases:
  - Distance = 0 → ValueError
  - Distance > output size → ValueError
  - Length > distance → Overlapping copy (sliding window)
```

### Region Classification Heuristics

| Region Type | Detection Method | Thresholds |
|-------------|------------------|------------|
| **Code** | 65816 opcode density + entropy | >85% valid opcodes, entropy <6.5 |
| **Compressed** | Successful decompression | Entropy >7.2, entropy drop after decode |
| **Graphics** | Tile patterns + low entropy | Entropy <4.0, many zeros/low bytes |
| **Data** | Default unclassified | 4.0 < entropy < 7.2 |

### ROM Mapping Detection

**LoROM Mapping:**
- ROM $0000-$7FFF → SNES $8000-$FFFF (Bank 0)
- ROM $8000-$FFFF → SNES $8000-$FFFF (Bank 1)
- Header at ROM $7FC0

**HiROM Mapping:**
- ROM $0000-$FFFF → SNES $C000-$FFFF (Bank 0)
- Header at ROM $FFC0

**Header Detection:**
- 512-byte copier header if `size % 1024 == 512`
- Check title at 0x7FC0 + header_offset
- Validate fixed byte 0x69 at offset +21

---

## Part V: Development Conventions

### Code Style

| Tool | Purpose | Command |
|------|---------|---------|
| **Black** | Formatting | `black toolkit/ tests/` |
| **Flake8** | Linting | `flake8 toolkit/ tests/` |
| **MyPy** | Type checking | `mypy toolkit/` |

**Line Length:** 100 characters (configured in `pyproject.toml`)

### Testing Practices

1. **Unit Tests:** All core functions have unit tests in `tests/`
2. **Integration Tests:** Full workflow tested via `test/test_workflow.sh`
3. **Property Tests:** Invariant-based testing in `property_tests.py`
4. **Zero-Dependency Runner:** `run_tests.py` works without pytest

### Documentation Standards

- **Docstrings:** All public functions have docstrings
- **Type Hints:** Encouraged for function signatures
- **README:** User-facing quick start
- **docs/:** Comprehensive technical documentation

### Commit Conventions

- Prefix with component: `bob_lz:`, `bob_map:`, `docs:`, `tests:`
- Use imperative mood: "Add feature" not "Added feature"
- Reference issues: "Fix #123: Handle edge case"

---

## Part VI: Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `toolkit/bob_lz.py` | ~226 | Core LZ77 decoder + unit tests |
| `toolkit/bob_lz_scan.py` | ~365 | ROM scanner with entropy analysis |
| `toolkit/bob_map.py` | ~420 | Region classifier with 65816 analysis |
| `toolkit/bob_graphics.py` | varies | Graphics/tile detection |
| `toolkit/ImportBOBMap.py` | varies | Ghidra import script |
| `tests/test_bob_lz.py` | ~100 | LZ77 decoder pytest suite |
| `tests/test_bob_scan.py` | varies | Scanner pytest suite |
| `run_tests.py` | ~150 | Zero-dependency test runner |
| `docs/GHIDRA_IMPORT.md` | varies | Ghidra integration guide |
| `docs/LEVEL_FORMAT.md` | varies | Level data format documentation |

---

## Part VII: Common Operations

### Scan ROM for Compressed Blocks

```bash
python toolkit/bob_lz_scan.py --rom B.O.B..smc --outdir out/
# Output: out/candidates.json, out/decompressed_*.bin
```

### Generate Full ROM Map

```bash
python toolkit/bob_map.py --rom B.O.B..smc --candidates out/candidates.json --outdir out/
# Output: out/rom_map.json, out/rom_map.html
```

### Extract Level Data

```bash
python toolkit/bob_extract.py --rom B.O.B..smc --outdir levels/
```

### Import into Ghidra

1. Generate ROM map: `python toolkit/bob_map.py ...`
2. Open Ghidra, load ROM
3. Run script: `toolkit/ImportBOBMap.py` with `out/rom_map.json`
4. See `docs/GHIDRA_IMPORT.md` for detailed instructions

### Validate Known Block

```python
# Test against known B.O.B. compressed block
rom = open('B.O.B..smc', 'rb').read()
from toolkit.bob_lz import bob_lz_decompress

compressed = rom[0x1AD34:0x1AD34 + 0x1000]
decompressed, consumed = bob_lz_decompress(compressed, 0x822)

assert len(decompressed) == 0x822
print(f"✓ Known block validated (consumed {consumed} bytes)")
```

---

## Part VIII: Troubleshooting Matrix

| Symptom | Solution |
|---------|----------|
| No compressed blocks found | Lower stride in `bob_lz_scan.py`, verify ROM has no header corruption |
| Too many false positives | Increase entropy thresholds, require higher entropy drop |
| Code regions not detected | Verify LoROM/HiROM detection, lower opcode density threshold from 0.85 |
| Ghidra import fails | Check base address matches ROM mapping, verify JSON format |
| Distance error in decompression | Verify offset is correct, check for header offset issues |
| Import errors | Ensure `PYTHONPATH` includes project root or use `python -m toolkit.module` |

---

## Part IX: Performance Benchmarks

| Operation | ROM Size | Runtime |
|-----------|----------|---------|
| LZ scan (stride=16) | 1 MB | ~30-60 seconds |
| ROM mapping | 1 MB | ~5-10 seconds |
| Full pipeline | 1 MB | <2 minutes |
| Graphics detection | 1 MB | ~15-30 seconds |

**Optimization Tips:**
- Increase stride for faster (less thorough) scanning
- Use `bob_lz_decompress_exploratory` for unknown block sizes
- Batch process multiple ROMs with custom scripts

---

## Part X: Source Code Archives

The `source/` directory contains original B.O.B. source code disks:

| Disk | Contents |
|------|----------|
| **Disk A** | Music files, wave samples, equates.h |
| **Disk B** | CPBACKUP backup disk |
| **Disk C** | Additional source files |
| **Disk D & E** | Combined disk contents |
| **Disk F** | Additional source files |

**Note:** These are historical archives from the original development. Use for reference and format analysis.

---

## Part XI: References

### Documentation
- [65816 Programming Manual](http://www.defence-force.org/computing/oric/coding/annexe_2/)
- [SNES Development Wiki](https://wiki.superfamicom.org/)
- [Ghidra Documentation](https://ghidra-sre.org/)
- B.O.B. Source Code — Matthew Callis (superfamicom.org)

### Original Research
- **LZ77 Format:** Reverse engineered by GuyPerfect
- **Source Code:** Originally posted on eludevisibility.org

---

## Part XII: Project Status

### Completed (v0.1.0)
- ✅ LZ77 decoder with unit tests
- ✅ ROM scanner with entropy detection
- ✅ Code/data classifier
- ✅ JSON output format
- ✅ Ghidra import instructions
- ✅ Validation against known block

### In Progress
- 🔄 HTML visualization enhancements
- 🔄 Graphics classifier improvements
- 🔄 Level extraction tools

### Future Enhancements
- ⬜ IDA Pro import script
- ⬜ radare2 script generation
- ⬜ GUI interface
- ⬜ Tile/sprite rendering
- ⬜ Multi-ROM batch processing

---

## Part XIII: Current Work Plan — ROM Analysis Enhancement

**Branch:** `feature/rom-analysis-enhancement`  
**Created:** 2026-02-23  
**Sprint Duration:** 2 weeks (estimated)  
**Architect:** Lauren

### Epic: Comprehensive ROM Analysis Pipeline

**Goal:** Enhance the B.O.B. ROM analysis toolkit with improved detection accuracy, expanded format support, and streamlined workflows for reverse engineering.

---

### Phase 1: Foundation & Codebase Deep-Dive (Days 1-3)

| ID | Task | Description | Priority | Status |
|----|------|-------------|----------|--------|
| 1.1 | Codebase Audit | Complete review of all toolkit modules, identify technical debt | P0 | ⏳ Pending |
| 1.2 | Test Coverage Analysis | Measure current test coverage, identify gaps | P0 | ⏳ Pending |
| 1.3 | Source Archive Analysis | Catalog and analyze original B.O.B. source disks | P1 | ⏳ Pending |
| 1.4 | Dependency Review | Verify stdlib-only compatibility, document optional deps | P1 | ⏳ Pending |

**Deliverables:**
- [ ] Codebase audit report (docs/CODEBASE_AUDIT.md)
- [ ] Test coverage report with gap analysis
- [ ] Source disk catalog (docs/SOURCE_CATALOG.md)

---

### Phase 2: LZ77 Decoder Enhancements (Days 4-6)

| ID | Task | Description | Priority | Status |
|----|------|-------------|----------|--------|
| 2.1 | Encoder Implementation | Complete LZ77 encoder for round-trip testing | P0 | ⏳ Pending |
| 2.2 | Streaming Decompression | Add streaming mode for large blocks | P1 | ⏳ Pending |
| 2.3 | Error Recovery | Implement graceful error recovery for corrupted streams | P1 | ⏳ Pending |
| 2.4 | Performance Optimization | Profile and optimize hot paths | P2 | ⏳ Pending |

**Deliverables:**
- [ ] Working LZ77 encoder (`toolkit/bob_lz_encode.py`)
- [ ] Streaming API with tests
- [ ] Performance benchmarks

---

### Phase 3: Scanner & Detection Improvements (Days 7-10)

| ID | Task | Description | Priority | Status |
|----|------|-------------|----------|--------|
| 3.1 | Multi-Pass Scanning | Implement coarse→fine scanning strategy | P0 | ⏳ Pending |
| 3.2 | Machine Learning Classifier | Train model for compressed block detection | P1 | ⏳ Pending |
| 3.3 | Batch Processing | Add multi-ROM batch processing support | P1 | ⏳ Pending |
| 3.4 | Progress Reporting | Add progress bars and ETA for long scans | P2 | ⏳ Pending |

**Deliverables:**
- [ ] Enhanced scanner with multi-pass support
- [ ] ML classifier integration (optional dependency)
- [ ] Batch processing CLI

---

### Phase 4: Graphics & Level Tools (Days 11-14)

| ID | Task | Description | Priority | Status |
|----|------|-------------|----------|--------|
| 4.1 | Graphics Pipeline Unification | Consolidate bob_graphics*.py modules | P0 | ⏳ Pending |
| 4.2 | Tile Renderer | Complete SNES tile/sprite renderer | P1 | ⏳ Pending |
| 4.3 | Level Format Documentation | Document level data structures from source | P0 | ⏳ Pending |
| 4.4 | Injection Testing | Test data injection with emulator validation | P1 | ⏳ Pending |

**Deliverables:**
- [ ] Unified graphics module
- [ ] Working tile renderer (PNG output)
- [ ] Comprehensive level format docs

---

### Phase 5: Integration & Documentation (Days 15-17)

| ID | Task | Description | Priority | Status |
|----|------|-------------|----------|--------|
| 5.1 | Ghidra Script Enhancement | Improve ImportBOBMap.py with more annotations | P1 | ⏳ Pending |
| 5.2 | IDA Pro Import Script | Create IDA Pro equivalent import script | P2 | ⏳ Pending |
| 5.3 | User Guide Update | Update all documentation for new features | P0 | ⏳ Pending |
| 5.4 | Tutorial Creation | Create step-by-step tutorial for new users | P1 | ⏳ Pending |

**Deliverables:**
- [ ] Enhanced Ghidra integration
- [ ] IDA Pro import script (optional)
- [ ] Updated documentation suite

---

### Phase 6: Testing & Release Prep (Days 18-20)

| ID | Task | Description | Priority | Status |
|----|------|-------------|----------|--------|
| 6.1 | Full Test Suite Run | Execute all tests, fix regressions | P0 | ⏳ Pending |
| 6.2 | Cross-Platform Testing | Test on Windows, Linux, macOS | P1 | ⏳ Pending |
| 6.3 | Performance Validation | Verify benchmarks meet targets | P1 | ⏳ Pending |
| 6.4 | Release Notes | Compile changelog and release notes | P0 | ⏳ Pending |

**Deliverables:**
- [ ] Clean test suite (0 failures)
- [ ] Cross-platform validation report
- [ ] Release notes for v0.2.0

---

## Part XIV: Commit & Push Tracking

**Branch:** `feature/rom-analysis-enhancement`  
**Parent:** `main` (2 commits ahead of origin)

### Commit Log

| # | Date | Commit Message | Files Changed | Status |
|---|------|----------------|---------------|--------|
| 1 | 2026-02-23 | `qwen: Add QWEN.md operational context with work plan` | QWEN.md | ✅ Committed |
| 2 | 2026-02-23 | `qwen: Update commit log and session notes` | QWEN.md | ✅ Committed |
| 3 | 2026-02-23 | `planning: Create multi-squad deployment structure` | .planning/** | ✅ Committed |
| 4 | 2026-02-23 | `archeology: Parallel codebase excavation complete` | .planning/** | ✅ Committed |

### Pending Changes (Not Yet Committed)

| File | Status | Description |
|------|--------|-------------|
| `toolkit/bob_lz_scan.py` | Modified | Scanner modifications (review pending) |
| `toolkit/*` | New | Multiple new toolkit modules |
| `docs/*` | New | Additional documentation files |
| `tests/*` | New | Test files |

### Push Schedule

| Milestone | Target Date | Commits | Push to Origin |
|-----------|-------------|---------|----------------|
| Phase 1 Complete | 2026-02-26 | 3-5 | ✅ Planned |
| Phase 2 Complete | 2026-03-01 | 4-6 | ✅ Planned |
| Phase 3 Complete | 2026-03-05 | 4-6 | ✅ Planned |
| Phase 4 Complete | 2026-03-09 | 4-6 | ✅ Planned |
| Phase 5 Complete | 2026-03-11 | 3-5 | ✅ Planned |
| Phase 6 Complete | 2026-03-15 | 2-4 | ✅ Planned + Merge |

### Git Workflow

```bash
# Daily work pattern
git checkout feature/rom-analysis-enhancement
git add <files>
git commit -m "<component>: <description>"
git log -n 3  # Review recent commits

# End of session
git status
git add -A
git commit -m "checkpoint: <session summary>"

# Milestone push
git push -u origin feature/rom-analysis-enhancement
```

### Branch Strategy

```
main ──────────────────────────────● (production)
                                    \
feature/rom-analysis-enhancement ───●──●──● (development)
```

**Merge Criteria:**
- All tests passing
- Documentation updated
- Performance benchmarks met
- Code review approved

---

## Part XV: Session Notes & Scratchpad

### Current Session (2026-02-23) — Execution Phase

**Objective:** Execute prioritized tasks from multi-squad deployment plan

**Completed:**
- ✅ Created branch `feature/rom-analysis-enhancement`
- ✅ Added QWEN.md operational context
- ✅ Integrated work plan with 6 phases, 26 tasks
- ✅ Set up commit/push tracking system
- ✅ Created `.planning/` directory structure
- ✅ Deployed 5 squads with 25 task descriptors
- ✅ Conducted parallel archeology across all squads
- ✅ Created ARCHEOLOGY_REPORT.md with findings

**Execution Progress:**

| Task | Squad | Status | Details |
|------|-------|--------|---------|
| ALPHA-001 | Alpha | ✅ COMPLETE | 32/32 round-trip tests passing |
| BETA-001 | Beta | ✅ COMPLETE | Module consolidated, deprecation added |
| DELTA-001 | Delta | ✅ COMPLETE | Unified runner created |
| GAMMA-001 | Gamma | ⏳ Pending | |
| ALPHA-003 | Alpha | ⏳ Pending | |

**Commits This Session:**
| Hash | Message |
|------|---------|
| 4d4c6e5 | DELTA-001: Test Runner Consolidation COMPLETE |
| 3d048c2 | BETA-001: Graphics Module Consolidation COMPLETE |
| c56ab7c | ALPHA-001: LZ77 Encoder Round-Trip Testing complete |
| b813c0d | BETA-001: Graphics Module Consolidation in progress |
| 563a58d | qwen: Update session notes with archeology summary |
| 25854d5 | archeology: Parallel codebase excavation complete |
| 0a248b0 | planning: Create multi-squad deployment structure |

**Squad Status Summary:**
| Squad | Status | Tasks Complete | Next Task |
|-------|--------|----------------|-----------|
| Alpha 🔵 | 🟢 Active | 1/5 | ALPHA-002 or ALPHA-003 |
| Beta 🟢 | 🟢 Active | 1/5 | BETA-002 (8bpp renderer) |
| Gamma 🟡 | ⏳ Ready | 0/5 | GAMMA-001 |
| Delta 🟠 | 🟢 Active | 1/5 | DELTA-002 (coverage) |
| Echo 🟣 | ⏳ Ready | 0/5 | ECHO-001 |

**Key Deliverables:**
- **ALPHA-001:** `tests/test_lz77_roundtrip.py` (32 tests), integrated in `run_full_test_suite.py`
- **BETA-001:** `toolkit/bob_graphics.py` (unified API with SNESGraphicsRenderer)
- **DELTA-001:** `tests/__main__.py` (unified test runner with filtering)

**Next Steps:**
1. Begin ALPHA-002 (Streaming Decompression) or ALPHA-003 (Multi-Pass Scanner)
2. Begin BETA-002 (8bpp Renderer Completion)
3. Begin DELTA-002 (Code Coverage Analysis)
4. Begin GAMMA-001 (Level Format Documentation)

**Blockers:** None

---

**Axiom reporting.** Execution advancing. 3 tasks complete (ALPHA-001, BETA-001, DELTA-001). 10 commits logged. All squads unblocked. Awaiting further orders, Architect.
