# Task ECHO-002: Ghidra Script Enhancement

**Squad:** Echo (Documentation & Integration)  
**Priority:** P1 (High)  
**Complexity:** Medium  
**Estimated Effort:** 6-8 hours  
**Status:** ⏳ Pending

---

## Objective

Enhance the Ghidra import script (`ImportBOBMap.py`) with comprehensive annotations including region labels, compressed block markers, data type definitions, and analysis hints.

---

## Context

The current `ImportBOBMap.py` provides basic bookmark import but lacks:
- Automatic segment creation
- Data type definitions for structures
- Region-specific analysis hints
- Compressed block decompression markers
- Cross-references between related regions

Enhanced integration would make Ghidra analysis more productive.

---

## Acceptance Criteria

- [ ] Segment creation: Auto-create memory segments for regions
- [ ] Labels: Add function/data labels at key locations
- [ ] Comments: Region descriptions as comments
- [ ] Data types: Define structures for tilemaps, headers
- [ ] Compressed markers: Mark compressed blocks with pre/post comments
- [ ] Vector table: Auto-analyze interrupt/reset vectors
- [ ] Error handling: Graceful handling of import errors
- [ ] Documentation: Updated Ghidra import guide

---

## Technical Notes

### Enhanced Import Script

```python
# ImportBOBMap.py - Enhanced version
from ghidra.app.cmd.label import AddLabelCmd
from ghidra.program.model.address import AddressSet
from ghidra.program.model.data import StructureDataType, ByteDataType

def import_rom_map(json_path):
    """Import ROM map with full annotations."""
    
    with open(json_path) as f:
        rom_map = json.load(f)
    
    # Create segments for each region
    for region in rom_map['regions']:
        create_segment(region)
        add_labels(region)
        add_comments(region)
        
        if region['type'] == 'compressed':
            mark_compressed_block(region)
        elif region['type'] == 'code':
            suggest_function_starts(region)
        elif region['type'] == 'tilemap':
            define_tilemap_structure(region)
    
    # Analyze vector table
    analyze_vector_table()

def create_segment(region):
    """Create memory segment for region."""
    start = toAddr(region['start'])
    end = toAddr(region['end'])
    
    segment = currentProgram.getMemory().createInitializedBlock(
        region['name'],
        start,
        region['size'],
        0,
        False,
        monitor
    )
    segment.setRead(True)
    segment.setWrite(region['type'] != 'code')
    segment.setExecute(region['type'] == 'code')

def define_tilemap_structure(region):
    """Define SNES tilemap entry structure."""
    dtm = currentProgram.getDataTypeManager()
    
    tilemap_entry = StructureDataType('TilemapEntry', 2)
    tilemap_entry.add(BitFieldDataType('tile_id', 10), 'Tile ID (0-1023)')
    tilemap_entry.add(BitFieldDataType('chr_bank', 2), 'CHR Bank (0-3)')
    tilemap_entry.add(BitFieldDataType('palette', 2), 'Palette (0-3)')
    tilemap_entry.add(BitFieldDataType('x_flip', 1), 'X Flip')
    tilemap_entry.add(BitFieldDataType('y_flip', 1), 'Y Flip')
    
    dtm.addDataType(tilemap_entry, None)
```

### Region-Specific Annotations

**Code Regions:**
- Mark potential function entry points
- Add comments for known library functions
- Suggest parameter types

**Compressed Blocks:**
- Mark with "COMPRESSED" label
- Add comment with decompressed size
- Create reference to decompressed data file

**Tilemaps:**
- Define array of TilemapEntry structures
- Add comment with level name if known

---

## Files to Modify

- `toolkit/ImportBOBMap.py` — Enhanced import script
- `docs/GHIDRA_IMPORT.md` — Updated guide
- `tests/test_ghidra_import.py` — Import validation tests

---

## Dependencies

- **Blocks:** None
- **Blocked by:** None (standalone enhancement)

---

## Test Plan

1. Test import with sample ROM map
2. Verify all segments created correctly
3. Check labels and comments appear
4. Validate data types defined
5. Test error handling with invalid input

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** ✅ COMPLETE — Ghidra script enhancement complete
  - Enhanced ImportBOBMap.py with v2.0 features:
    - `create_segment()` — Auto-create memory segments for regions
    - `create_tilemap_data_type()` — Define SNES tilemap entry structure (16-bit)
    - `add_region_labels()` — Add labels and bookmarks at key locations
    - `add_region_comments()` — Add region description comments
    - `analyze_vector_table()` — Mark SNES vector table (0x7FE0-0x7FFF)
  - Compressed block markers with decompression hints
  - Type-specific processing (tilemap, compressed, code)
  - Error handling and progress reporting
  - Created `tests/test_ghidra_import.py` with 20 tests (all passing)
  - All acceptance criteria met
