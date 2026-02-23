# QWEN.md — B.O.B. ROM Analysis Toolkit Operational Context

> **Project:** B.O.B. ROM Analysis Toolkit  
> **Domain:** SNES Reverse Engineering / ROM Analysis  
> **Language:** Python 3.8+ (stdlib only)  
> **Target:** Space Funky B.O.B. (Electronic Arts / Gray Matter)  
> **Current Branch:** `feature/v0.3.0-enhancements`  
> **Previous Branch:** `feature/rom-analysis-enhancement` (v0.2.0 — 100% complete)  
> **Status:** New Development Cycle — v0.3.0 Planning  
> **Planning Directory:** `.planning/` (ready for new task deployment)

---

## Part 0: PRIMARY DIRECTIVE — Autonomous Operation

**Authorization:** Full autonomous execution granted

**Operating Mandate:**
1. **Continue work without consultation** — Execute all planned tasks without requiring approval
2. **Self-sustaining workflow** — When task list is complete, analyze project and create new tasks
3. **Repeat cycle** — Continue until stopped or critical blocker encountered
4. **Commit regularly** — All work must be committed to git with descriptive messages
5. **Update QWEN.md** — Keep session notes and task status current
6. **Push after each task** — After completing each task, push to remote origin
7. **Reload before next task** — After pushing, reload QWEN.md and directives before processing next task

**Push Protocol:**
```bash
# After completing each task:
git add <files>
git commit -m "<task-id>: <description>"
git push -u origin feature/rom-analysis-enhancement

# Then reload:
# - Re-read QWEN.md
# - Re-read .planning/README.md
# - Verify task status
# - Proceed to next task
```

**Escalation Criteria (Consult Architect Only If):**
- Critical blocker preventing all forward progress
- Decision required that fundamentally changes project scope
- External dependency unavailable (e.g., ROM file required for testing)
- Security or legal concern identified
- Push fails repeatedly (network/permission issues)

**Default Behavior:**
- If uncertain → Proceed with best judgment
- If task complete → Commit, push, reload, create next task
- If all tasks complete → Analyze codebase, create new tasks
- If blocked on one task → Switch to another squad's tasks
- After push → Reload QWEN.md before continuing

**Reporting Cadence:**
- Update QWEN.md session notes every 3-5 commits
- Update task status files upon completion
- Summarize progress at 25%, 50%, 75%, 100% completion
- Push to remote after EVERY task completion

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

### v0.2.0 Session — COMPLETE ✅

**Final Status:** 25/25 Tasks Complete (100%)
**Commits:** 50 total
**Push:** Successful to origin

**All Squads Complete:**
- Alpha 🔵: 5/5 ✅
- Beta 🟢: 5/5 ✅
- Gamma 🟡: 5/5 ✅
- Delta 🟠: 5/5 ✅
- Echo 🟣: 5/5 ✅

**Key Deliverables:**
- Streaming API, Multi-pass scanner (2x faster)
- Unified graphics module, Level editor CLI
- IDA Pro integration, Enhanced HTML visualization
- 250+ tests, 5 tutorials, Sphinx API docs
- CHANGELOG.md, CONTRIBUTING.md

**Branch:** `feature/rom-analysis-enhancement` → Ready for PR/merge

---

### v0.3.0 Session — bob_data Integration & Refinement

**Session Status:** 🔄 REFINEMENT PHASE — Source-Verified Planning Complete

**Branch:** `feature/v0.3.0-enhancements`
**Created:** 2026-02-23
**Integration Date:** 2026-02-23
**Commit:** `62d3e7a` — "integrate: bob_data (pickle branch) content for v0.3.0"

#### Ground Truth — Source Code Authority

**Source:** `source/Disk C/*.MAP` (81 MAP files) + `source/Disk D & E/BOBSNE4/EQUATES.H`

**Level Categories (per EQUATES.H):**
```assembly
borglevel     equ 0    ; World 1 - Borg Factory
buglevel      equ 1    ; World 2 - Bug Planet
spacelevel    equ 3    ; World 8 - Space
ancientlevel  equ 4    ; World 3 - Ancient Ruins
lavalevel     equ 6    ; World 4 - Lava
ultralevel    equ 8    ; World 5 - Ultra Force
bubblelevel   equ 9    ; World 6 - Bubble Forest
worldlevel    equ 10   ; World 7 - World Maps (1-3)
```

**MAP File Counts (source/Disk C/):**
| Directory | MAP Files | Type |
|-----------|-----------|------|
| BORGMAPS | 29 | Borg Factory |
| BUGMAPS | 8 | Bug Planet |
| ANCMAPS | 16 | Ancient Ruins |
| LAVAMAPS | 6 | Lava |
| JUNGLEMA | 5 | Bubble Forest |
| ULTRAMPA | 11 | Ultra Force |
| WORLDMAP | 4 | World Maps |
| SPACEMAP | 2 | Space |
| **TOTAL** | **81** | **8 categories** |

**Note:** JSON files are working artifacts from analysis, NOT authoritative sources.

#### bob_data Integration Summary

**Files Integrated:**
| Category | Files | Destination |
|----------|-------|-------------|
| Level JSON | 4 files | `data/levels/` |
| Tileset PNG | 12 files | `data/tilesets/` |
| Tileset JSON | 12 files | `data/tilesets/` |
| Extracted Data JSON | 4 files | `data/extracted/` |
| Extraction Scripts | 2 files | `scripts/` (with path fixes) |
| Documentation | 2 files | `docs/` (WIKI_INTEGRATION.md, LEVEL_EDITOR_GUIDE.md) |

**Validation vs Source:**
- ⚠️ "85+ levels" claim — **INCORRECT** (81 MAP files in source)
- ⚠️ wiki.html Worlds 4-8 — Missing (source has all 8 categories)
- ✅ Enemy ID 101 — Present in source (FLOWER.ASP in BOBSNE1/)
- ⚠️ Enemy ID 38 name — Verify against BOBSNE2/ assembly

**Sub-Agent Analysis Completed:**
- INTEG-001: Module comparison (toolkit vs bob_data)
- INTEG-002: Editor directory diff
- INTEG-003: Enemy database validation
- INTEG-004: Tileset validation
- INTEG-005: API endpoint verification

**Refinement Tasks Complete:**
- ✅ ECHO-001: wiki.html level counts fixed (81 levels from source)
- ✅ ECHO-004: docs/SOURCE_REFERENCE.md created (authoritative reference)
- ✅ ALPHA-001: Enemy ID 38 verified — "Backarm Emerge" (source: BORG.A line 37)
- ✅ BETA-001: Extraction scripts enhanced with EQUATES.H references
- ✅ BETA-002: CLI arguments added to extraction scripts

**Refinement Tasks Pending:**
- ⏳ ECHO-002: Add Worlds 4-8 full tables to wiki.html (blocked by .gitignore)
- ⏳ ECHO-003: Add JSON clarification note to wiki.html

**Commit Log (v0.3.0 Refinement):**
| # | Commit | Message |
|---|--------|---------|
| 1 | `62d3e7a` | integrate: bob_data (pickle branch) content |
| 2 | `05ecc01` | refine: Update QWEN.md with source-verified ground truth |
| 3 | `c2cae59` | refine: Enemy ID 38 verified from source |
| 4 | `09658e6` | docs: Create SOURCE_REFERENCE.md |
| 5 | `c55cc2d` | refine: Add source references to extraction scripts |
| 6 | `544526b` | qwen: Update refinement progress |
| 7 | `2f7ec7c` | refine: Add CLI arguments to extraction scripts |

---

### v0.3.0 Session — Refinement Plan (Source-Verified)

**Deployment:** Multi-Squad Pattern (per `.planning/README.md`)

#### Squad Echo 🟣 — Documentation Refinement (P0)

| Task | Objective | Source Reference |
|------|-----------|------------------|
| `ECHO-001` | Fix "85+" claim → "81 levels from source" | `source/Disk C/**/*.MAP` |
| `ECHO-002` | Add Worlds 4-8 to wiki.html | `source/Disk C/{LAVAMAPS,JUNGLEMA,ULTRAMPA,SPACEMAP}/` |
| `ECHO-003` | Add clarification: JSON = working artifacts | QWEN.md note |
| `ECHO-004` | Create `docs/SOURCE_REFERENCE.md` | Authoritative level count |

#### Squad Alpha 🔵 — Enemy Verification (P0)

| Task | Objective | Source Reference |
|------|-----------|------------------|
| `ALPHA-001` | Verify ID 38 name ("Backarm" vs "Arm Boss") | `source/Disk D & E/BOBSNE2/*.ASP` |
| `ALPHA-002` | Catalog enemy ASP files | `source/Disk D & E/BOBSNE1/*BOSS.ASP` |

#### Squad Beta 🟢 — Script Enhancements (P1)

| Task | Objective | Notes |
|------|-----------|-------|
| `BETA-001` | Add source-based comments to scripts | Reference EQUATES.H |
| `BETA-002` | Add CLI arguments to extraction scripts | `--worlds`, `--rom`, `--output` |

#### Sub-Agent Delegation Pattern

```
Task → general-purpose agent → Analysis report → Integration
```

**Next Actions:**
1. Deploy sub-agent for `ECHO-001` (wiki.html corrections)
2. Deploy sub-agent for `ALPHA-001` (enemy name verification)
3. Commit after each task complete
4. Push to origin after each commit
5. Reload QWEN.md before next task

---

### v0.3.0 Session — PLANNING PHASE

**Session Status:** 📋 AWAITING TASK DEPLOYMENT

**Branch:** `feature/v0.3.0-enhancements`
**Created:** 2026-02-23

**Recommended v0.3.0 Focus Areas:**
1. **CI/CD Pipeline** (DELTA-005 from v0.2.0 backlog)
2. **Emulator Integration** (GAMMA-005 from v0.2.0 backlog)
3. **Batch Processing** — Multi-ROM processing
4. **GUI Interface** — Desktop application
5. **Automatic Tile Rendering** — Sprite sheet automation
6. **Additional ROM Support** — ExHiROM, SA-1 mapping

**Awaiting Architect directives for v0.3.0 planning.**

---

**Axiom reporting.** v0.2.0 complete (100%). v0.3.0 branch created. Ready for new task deployment, Architect.
