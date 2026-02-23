# Changelog

All notable changes to the B.O.B. ROM Analysis Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- IDA Pro import script integration testing
- Tutorial creation for new users
- CI/CD pipeline setup
- Emulator integration testing

## [0.2.0] - 2026-02-23

### Added
- **Streaming decompression API** (`bob_lz_decompress_stream`) — Generator-based streaming for large files (ALPHA-002)
- **Multi-pass ROM scanner** — Coarse→fine scanning with 2x performance improvement (ALPHA-003)
- **Unified graphics module** — Consolidated `bob_graphics.py` with 2bpp/4bpp/8bpp support (BETA-001)
- **Palette extraction** — Extract and apply SNES palettes from ROM data (BETA-003)
- **Level editor CLI** — Interactive command-line interface for tilemap editing (GAMMA-004)
- **IDA Pro import script** (`ImportBOBMapIDA.py`) — Feature parity with Ghidra integration (ECHO-003)
- **Enhanced HTML visualization** — Interactive filtering, search, and region navigation (BETA-004)
- **Sphinx API documentation** — Auto-generated API docs in `docs/api/` (ECHO-001)

### Changed
- **Test runner consolidation** — Unified `python -m tests` runner replaces multiple scripts (DELTA-001)
- **Ghidra import enhanced** — Segment creation, data types, vector table analysis (ECHO-002)
- **Entropy thresholds documented** — Calibrated thresholds in `configs/thresholds.yaml` (ALPHA-004)
- **Injection safety** — Backup creation, validation, checksum verification (GAMMA-003)

### Fixed
- LZ77 encoder edge cases with empty and single-byte inputs
- Graphics module fragmentation (consolidated 4 modules into 1)
- Test coverage gaps (added 200+ new tests)
- Documentation inconsistencies across multiple files

### Performance
- Multi-pass scanner: ~2x faster than single-pass (ALPHA-003)
- Streaming API: Memory-efficient processing for large files (ALPHA-002)
- Benchmark suite: `benchmarks/benchmark_scan.py` for regression testing (ALPHA-005)

### Testing
- **32 tests** — LZ77 encoder round-trip validation (ALPHA-001)
- **18 tests** — Streaming API verification (ALPHA-002)
- **15 tests** — Multi-pass scanner validation (ALPHA-003)
- **15 tests** — Entropy threshold calibration (ALPHA-004)
- **11 tests** — Performance benchmark suite (ALPHA-005)
- **23 tests** — 8bpp renderer verification (BETA-002)
- **15 tests** — Palette extraction (BETA-003)
- **12 tests** — HTML visualization enhancement (BETA-004)
- **14 tests** — Tilemap extraction validation (GAMMA-002)
- **19 tests** — Injection safety checks (GAMMA-003)
- **20 tests** — Level editor CLI (GAMMA-004)
- **11 tests** — Benchmark suite (ALPHA-005)
- **16 tests** — Property-based testing (DELTA-004)
- **17 tests** — IDA import script (ECHO-003)

**Total: 250+ new tests in v0.2.0**

### Documentation
- `docs/LEVEL_FORMAT_COMPLETE.md` — Comprehensive level format specification
- `docs/ENTROPY_THRESHOLDS.md` — Threshold calibration methodology
- `docs/PERFORMANCE.md` — Performance benchmarks and optimization guide
- `docs/api/` — Sphinx-generated API documentation
- `CHANGELOG.md` — This changelog

### Contributors
- All development by B.O.B. ROM Analysis Team
- Based on original LZ77 format reverse engineering by GuyPerfect

## [0.1.0] - 2026-01-27

### Added
- Initial release
- LZ77 decoder with unit tests
- ROM scanner with entropy-based detection
- Code/data classifier with 65816 analysis
- JSON output format
- Ghidra import instructions
- Validation against known block at 0x1AD34

### Known Issues
- Single-pass scanner slower than multi-pass (fixed in v0.2.0)
- Graphics modules fragmented (consolidated in v0.2.0)
- Limited test coverage (expanded to 250+ tests in v0.2.0)

---

## Version History

| Version | Date | Key Features | Tests |
|---------|------|--------------|-------|
| 0.2.0 | 2026-02-23 | Streaming API, Multi-pass scanner, Unified graphics, IDA import | 250+ |
| 0.1.0 | 2026-01-27 | Initial release: LZ77 decoder, Scanner, Classifier | 20 |
