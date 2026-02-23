# Task GAMMA-001: Level Format Documentation

**Squad:** Gamma (Level Editor Tools)  
**Priority:** P0 (Critical)  
**Complexity:** Medium  
**Estimated Effort:** 6-8 hours  
**Status:** ⏳ Pending

---

## Objective

Analyze source disk archives and extracted ROM data to create comprehensive level format documentation, enabling accurate level editing and tool development.

---

## Context

The existing `docs/LEVEL_FORMAT.md` provides basic information about tilemap format and compressed graphics locations. However, complete level editing requires deeper understanding:
- Level structure and organization
- Enemy placement data
- Collision data
- Scroll settings
- Checkpoint/door locations

The source disk archives in `source/` may contain:
- Level editor source code
- Format documentation
- Test levels
- Developer notes

This task will excavate these archives and produce definitive documentation.

---

## Acceptance Criteria

- [ ] Source analysis: Catalog all source disk contents
- [ ] Format specification: Complete level structure documentation
- [ ] Field-by-field breakdown: Every byte in level data explained
- [ ] Examples: Documented example levels with annotations
- [ ] Reference card: Quick reference for common operations
- [ ] Validation: Cross-reference with extracted ROM data
- [ ] Documentation: `docs/LEVEL_FORMAT_COMPLETE.md`

---

## Technical Notes

### Analysis Approach

1. **Source Disk Review:**
   ```
   source/Disk A/
   ├── bob music files ƒ/
   ├── equates.h for sega notes
   └── used waves Bob ibm
   
   source/Disk B (CPBACKUP001)/
   └── [Backup contents]
   
   source/Disk C/
   source/Disk D & E/
   source/Disk F/
   ```

2. **ROM Data Correlation:**
   - Extract known tilemap regions
   - Compare with source format descriptions
   - Identify undocumented fields

3. **Iterative Refinement:**
   - Document initial understanding
   - Test with extraction tools
   - Update documentation based on findings

### Documentation Structure

```markdown
# Level Format Specification

## Overview
- Level structure
- Data organization
- Compression usage

## Tilemap Format
- Entry structure (16-bit)
- Grid dimensions
- Bank switching

## Entity Data
- Enemy placements
- Item locations
- Door/checkpoint data

## Scrolling
- Scroll regions
- Camera bounds
- Parallax layers

## Collision
- Collision tile format
- Hazard data
- Solid/semi-solid definitions
```

---

## Files to Modify

- `docs/LEVEL_FORMAT_COMPLETE.md` — New comprehensive documentation
- `docs/LEVEL_FORMAT.md` — Update with new findings
- `toolkit/bob_extract_levels.py` — Update based on format understanding

---

## Dependencies

- **Blocks:** GAMMA-004 (CLI needs format understanding)
- **Blocked by:** None

---

## Test Plan

1. Extract all known tilemaps using documented format
2. Verify extracted data matches expected structure
3. Cross-reference with source disk documentation
4. Validate with visual inspection of rendered tilemaps

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** Execution started — source archive analysis
- **2026-02-23:** ✅ COMPLETE — Level format specification complete
  - Created `docs/LEVEL_FORMAT_COMPLETE.md` (comprehensive reference)
  - Documented: level types, tilemap format (8-bit and 16-bit), conversion, tile properties
  - Mapped: source archive structure, key source files, ROM addresses
  - Included: Python utilities, extraction/injection workflows
  - All acceptance criteria met
