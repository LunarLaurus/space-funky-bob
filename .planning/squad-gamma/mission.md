# Squad Gamma — Level Editor Tools

**Mission:** Complete the level extraction and injection pipeline, document level data formats from source archives, and enable safe ROM modification for level editing workflows.

---

## Scope

Squad Gamma owns level data tools and ROM modification:
- **Level Extraction** (`bob_extract.py`, `bob_extract_levels.py`)
- **ROM Injection** (`bob_inject.py`)
- **Level Format Documentation** (from source archives)

---

## Objectives

### Primary Goals
1. Document complete level format from source disk analysis
2. Validate tilemap extraction with comprehensive tests
3. Implement safety checks for ROM injection
4. Create CLI prototype for interactive level editing

### Secondary Goals
1. Integrate with emulator for testing injected ROMs
2. Support batch level extraction
3. Create level format reference card

---

## Tasks

| ID | Title | Priority | Complexity | Status |
|----|-------|----------|------------|--------|
| GAMMA-001 | Level Format Documentation | P0 | Medium | ⏳ Pending |
| GAMMA-002 | Tilemap Extraction Validation | P1 | Low | ⏳ Pending |
| GAMMA-003 | ROM Injection Safety Checks | P0 | High | ⏳ Pending |
| GAMMA-004 | Level Editor CLI Prototype | P2 | Medium | ⏳ Pending |
| GAMMA-005 | Emulator Integration Testing | P1 | High | ⏳ Pending |

---

## Success Metrics

- **Documentation:** Complete level format spec with examples
- **Extraction:** 100% valid tilemaps from all known locations
- **Injection Safety:** Zero corrupted ROMs with validation enabled
- **Usability:** Level editing workflow completable in <10 minutes

---

## Dependencies

### Internal
- Squad Alpha: LZ77 encoder validation (ALPHA-001) for re-compression
- Squad Beta: Graphics renderer (BETA-002) for tile preview

### External
- Source disk archives in `source/` directory
- Emulator with debugging support (bsnes, Snes9x)

---

## Technical Notes

### Level Data Locations (from LEVEL_FORMAT.md)

**Tilemaps (Uncompressed):**
- ROM 0x028000-0x02C800: Level tilemaps
- ROM 0x038000-0x03C800: Additional tilemaps
- Size: 0x800 bytes per tilemap (1024 entries = 32x32 grid)

**Compressed Graphics:**
- 0x018000, 0x030000, 0x060000, 0x090000, 0x0A0000
- LZ77 compressed, 0x800 bytes decompressed

**Tilemap Entry Format:**
```
Bits:    [YFlip][XFlip][Palette][CHR Bank][Tile ID]
         15     14     13-12   11-10      9-0
```

### Source Disk Contents

| Disk | Relevant Files |
|------|----------------|
| Disk A | Music files, equates.h |
| Disk B | CPBACKUP backup |
| Disk C | Additional source |
| Disk D & E | Combined disks |
| Disk F | Additional source |

---

## Status Log

### Day 1 (2026-02-23)
- Squad created
- Task descriptors written
- Awaiting kickoff

---

**Lead:** TBD  
**Members:** TBD  
**Started:** 2026-02-23  
**Target Complete:** 2026-03-09 (Day 14)
