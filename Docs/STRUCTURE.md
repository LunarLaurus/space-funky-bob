# Project Directory Structure
## B.O.B. ROM Analysis Toolkit

This document describes the complete directory structure and file organization.

```
bob-rom-analysis/
│
├── README.md                      # Quick start guide (user-facing)
├── CLAUDE.md                      # Complete project context (AI context)
├── LICENSE                        # MIT License (to be added)
├── .gitignore                     # Git ignore rules (to be added)
│
├── bob_lz.py                      # Core: LZ77 decoder + unit tests
├── bob_lz_scan.py                 # Core: ROM scanner
├── bob_map.py                     # Core: Region classifier
├── validate_known_block.py        # Core: Validation script
├── test_workflow.sh               # Automation: Complete workflow script
│
├── docs/                          # All documentation
│   ├── USER_GUIDE.md              # End-user documentation
│   ├── TECHNICAL.md               # Technical design document
│   ├── PRD.md                     # Product requirements document
│   ├── ghidra_import.txt          # Ghidra integration instructions
│   │
│   └── roadmap/                   # Sprint planning & tracking
│       ├── SPRINTS.md             # Sprint plans and stories
│       └── EPICS.md               # Epic tracking and priorities
│
├── tests/                         # Unit tests (future)
│   ├── test_bob_lz.py             # LZ77 decoder tests
│   ├── test_bob_lz_scan.py        # Scanner tests
│   ├── test_bob_map.py            # Mapper tests
│   └── fixtures/                  # Test data
│       └── test_rom.smc           # Minimal test ROM
│
├── examples/                      # Example scripts (future)
│   ├── extract_specific_block.py  # Extract known block
│   ├── batch_analyze.py           # Batch processing
│   └── custom_heuristics.py       # Custom scanning
│
├── analysis_output/               # Default output directory (generated)
│   ├── candidates.json            # Found compressed blocks
│   ├── rom_map.json               # ROM structure map
│   ├── rom_map.html               # Interactive visualization
│   └── decompressed_*.bin         # Extracted data files
│
└── scripts/                       # Utility scripts (future)
    ├── benchmark.py               # Performance benchmarking
    ├── validate_all.py            # Validate all test ROMs
    └── generate_docs.py           # Auto-generate documentation
```

---

## File Descriptions

### Root Level

#### Core Analysis Scripts
- **bob_lz.py** (215 lines)
  - LZ77 decompression algorithm
  - Unit tests (5 test cases)
  - Exploratory decompression mode
  - Zero external dependencies

- **bob_lz_scan.py** (245 lines)
  - ROM structure detection (LoROM/HiROM)
  - Compressed block scanning
  - Entropy-based filtering
  - JSON output generation

- **bob_map.py** (420 lines)
  - Code/data classification
  - 65816 opcode analysis
  - HTML visualization generation
  - Region consolidation

- **validate_known_block.py** (115 lines)
  - Validates against known compressed block
  - Tests decoder correctness
  - Reports compression metrics

#### Automation
- **test_workflow.sh** (50 lines)
  - End-to-end automation script
  - Runs complete analysis pipeline
  - User-friendly output formatting

#### Documentation
- **README.md** (500 lines)
  - Quick start guide
  - Installation instructions
  - Usage examples
  - Troubleshooting

- **CLAUDE.md** (450 lines)
  - Complete project context
  - Goals and success criteria
  - Technical constraints
  - Known limitations

---

## Documentation Directory

### docs/

#### User Documentation
- **USER_GUIDE.md** (800 lines)
  - Comprehensive user manual
  - Step-by-step tutorials
  - Ghidra integration guide
  - FAQ and troubleshooting

#### Technical Documentation
- **TECHNICAL.md** (1200 lines)
  - System architecture
  - Algorithm specifications
  - API documentation
  - Performance analysis

#### Product Documentation
- **PRD.md** (1000 lines)
  - Product requirements
  - Market analysis
  - Feature specifications
  - Release roadmap

- **ghidra_import.txt** (250 lines)
  - Ghidra integration instructions
  - Manual import steps
  - Python import script
  - Troubleshooting

### docs/roadmap/

#### Planning Documents
- **SPRINTS.md** (400 lines)
  - Sprint plans (Sprint 0, 1, 2)
  - User stories with acceptance criteria
  - Velocity tracking
  - Definition of Done

- **EPICS.md** (600 lines)
  - 10 major epics
  - Epic dependencies
  - Priority matrix
  - Status tracking

---

## Output Directory Structure

### analysis_output/

Generated when running analysis. Not checked into version control.

```
analysis_output/
├── candidates.json              # Compressed block metadata
│   • List of all candidates
│   • Success/failure status
│   • Entropy metrics
│   • Output file references
│
├── rom_map.json                 # ROM structure map
│   • Region classifications
│   • Address ranges
│   • Confidence scores
│   • Type annotations
│
├── rom_map.html                 # Interactive visualization
│   • Color-coded memory map
│   • Hover tooltips
│   • Region details
│   • Self-contained (no external deps)
│
└── decompressed_XXXXXX.bin      # Extracted data (multiple files)
    • One file per successful decompression
    • Named by ROM offset (hex)
    • Raw binary data
```

---

## Future Directories

### tests/ (Planned)

Unit and integration tests using pytest.

```
tests/
├── __init__.py
├── conftest.py                  # pytest configuration
├── test_bob_lz.py               # Decoder tests
├── test_bob_lz_scan.py          # Scanner tests
├── test_bob_map.py              # Mapper tests
├── test_integration.py          # End-to-end tests
└── fixtures/
    ├── test_rom.smc             # Minimal test ROM (header)
    ├── test_rom_noheader.sfc    # Minimal test ROM (no header)
    ├── compressed_block.bin     # Known compressed data
    └── expected_output.json     # Expected analysis results
```

### examples/ (Planned)

Example scripts demonstrating library usage.

```
examples/
├── extract_specific_block.py    # Extract single known block
├── batch_analyze.py             # Process multiple ROMs
├── custom_heuristics.py         # Modify scanning parameters
├── export_to_csv.py             # Convert JSON to CSV
└── compare_versions.py          # Compare ROM versions
```

### scripts/ (Planned)

Development and maintenance utilities.

```
scripts/
├── benchmark.py                 # Performance benchmarking
├── validate_all.py              # Test suite runner
├── generate_docs.py             # Sphinx documentation
├── check_coverage.py            # Code coverage report
└── release.sh                   # Release preparation script
```

---

## File Size Guidelines

### Python Scripts
- **Small**: <100 lines (validate_known_block.py)
- **Medium**: 100-300 lines (bob_lz.py, bob_lz_scan.py)
- **Large**: 300-500 lines (bob_map.py)
- **Very Large**: >500 lines (should be split into modules)

### Documentation
- **README**: 400-600 lines (concise, action-oriented)
- **User Guide**: 600-1000 lines (comprehensive, examples)
- **Technical Docs**: 1000-1500 lines (detailed, specifications)

### JSON Output
- **candidates.json**: 10-100 KB (varies by ROM and findings)
- **rom_map.json**: 50-500 KB (varies by region granularity)

### Binary Output
- **Decompressed files**: 256 bytes - 256 KB typical (varies widely)

---

## Version Control

### .gitignore (Recommended)

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Output directories
analysis_output/
output/
out/
results/

# ROM files (do not commit)
*.smc
*.sfc
*.bin
*.rom

# OS files
.DS_Store
Thumbs.db

# Test coverage
.coverage
htmlcov/

# Distribution
dist/
build/
*.egg-info/
```

---

## Dependencies

### Python Standard Library Only
All core functionality uses **only** Python standard library:
- `argparse` - CLI parsing
- `json` - Data serialization
- `math` - Entropy calculations
- `pathlib` - File operations
- `struct` - Binary unpacking
- `collections` - Data structures

### Development Dependencies (Optional)
- `pytest` - Testing framework
- `pylint` - Code linting
- `black` - Code formatting
- `mypy` - Type checking
- `coverage` - Test coverage
- `sphinx` - Documentation generation

---

## Deployment

### Installation Methods

#### Method 1: Direct Clone (Current)
```bash
git clone https://github.com/user/bob-rom-analysis
cd bob-rom-analysis
python bob_lz.py  # Ready to use!
```

#### Method 2: PyPI (Future)
```bash
pip install bob-rom-analysis
bob-analyze rom.smc  # Command-line tool
```

#### Method 3: System Package (Future)
```bash
# Ubuntu
apt install bob-rom-analysis

# macOS
brew install bob-rom-analysis
```

---

## Documentation Standards

### File Headers

All Python files should include:
```python
#!/usr/bin/env python3
"""
filename.py — Brief Description

Longer description of purpose and functionality.

Usage:
    python filename.py [args]
"""
```

### Function Docstrings

```python
def function_name(param1, param2):
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When this exception occurs
    """
```

### Markdown Files

- Use ATX-style headers (`#`, `##`, `###`)
- Include table of contents for >500 lines
- Code blocks with language specification
- Links relative to repository root

---

## Maintenance

### Adding New Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Update documentation**
   - Add to appropriate docs/ file
   - Update USER_GUIDE.md if user-facing
   - Update TECHNICAL.md if API changes

3. **Write tests**
   - Unit tests in tests/
   - Integration test if needed
   - Update test_workflow.sh if relevant

4. **Update roadmap**
   - Move story from planned to done in SPRINTS.md
   - Update epic status in EPICS.md
   - Add to CHANGELOG (future)

### File Naming Conventions

- **Python scripts**: `lowercase_with_underscores.py`
- **Documentation**: `UPPERCASE.md` or `Titlecase_With_Underscores.md`
- **Output files**: `descriptive_name_HEX.ext` (e.g., `decompressed_01AD34.bin`)
- **Test files**: `test_module_name.py`

---

## Size Estimates (Current)

```
Total Size: ~150 KB
├── Python scripts: ~50 KB (5 files)
├── Documentation: ~100 KB (8 files)
├── Shell scripts: ~5 KB (1 file)
└── Test data: ~10 KB (1 file)

Generated Output: ~1-5 MB per ROM analysis
├── JSON files: ~100 KB
├── HTML: ~50 KB
└── Decompressed bins: ~1-5 MB
```

---

**Last Updated**: January 27, 2026  
**Maintained By**: Project Team
