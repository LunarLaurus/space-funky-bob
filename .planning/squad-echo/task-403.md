# Task ECHO-003: IDA Pro Import Script

**Squad:** Echo (Documentation & Integration)  
**Priority:** P2 (Medium)  
**Complexity:** High  
**Estimated Effort:** 8-10 hours  
**Status:** ⏳ Pending

---

## Objective

Create IDA Pro import script that loads ROM map annotations (bookmarks, segments, comments, data types) equivalent to Ghidra integration, enabling IDA users to benefit from automated analysis.

---

## Context

IDA Pro is a popular alternative to Ghidra for reverse engineering. Currently, the toolkit only supports Ghidra import. IDA users must manually:
- Create segments for regions
- Add bookmarks for compressed blocks
- Enter comments for region types
- Define data structures

An IDA Python script would automate this workflow, making the toolkit accessible to IDA users.

---

## Acceptance Criteria

- [ ] IDA script: `ImportBOBMapIDA.py` for IDA Pro 7.x+
- [ ] Segment creation: Auto-create segments for regions
- [ ] Bookmarks: Add IDA bookmarks for key locations
- [ ] Comments: Add region comments at addresses
- [ ] Data types: Define tilemap entry structures
- [ ] Names: Add symbolic names for regions
- [ ] Documentation: IDA import guide
- [ ] Testing: Validate with IDA Free version

---

## Technical Notes

### IDA Python Script

```python
# ImportBOBMapIDA.py
import idaapi
import ida_segment
import ida_bytes
import ida_nalt
import ida_struct
import json

def import_rom_map(json_path):
    """Import ROM map into IDA Pro."""
    
    with open(json_path) as f:
        rom_map = json.load(f)
    
    # Create segments
    for region in rom_map['regions']:
        create_segment(region)
        add_bookmark(region)
        add_comment(region)
    
    # Define data types
    define_tilemap_structure()
    
    # Analyze entry points
    analyze_vectors()
    
    print(f"Imported {len(rom_map['regions'])} regions")

def create_segment(region):
    """Create segment for ROM region."""
    start = region['start']
    size = region['size']
    name = region['name']
    
    # Set segment permissions
    perm = ida_segment.SEGPERM_READ
    if region['type'] != 'code':
        perm |= ida_segment.SEGPERM_WRITE
    if region['type'] == 'code':
        perm |= ida_segment.SEGPERM_EXEC
    
    # Create segment
    seg = ida_segment.segment_t()
    seg.start_ea = start
    seg.end_ea = start + size
    seg.bitness = 0  # 16-bit
    seg.sel = ida_segment.setup_selector(0)
    seg.orgbase = 0
    
    ida_segment.add_segment_ex(seg, name, 0, perm, ida_segment.ADDSEG_OR_DIE)
    ida_segment.set_segment_type(seg, ida_segment.SEG_CODE if region['type'] == 'code' else ida_segment.SEG_DATA)

def add_bookmark(region):
    """Add IDA bookmark for region."""
    ea = region['start']
    name = region['name']
    type_char = 'C' if region['type'] == 'code' else 'D'
    
    ida_nalt.set_bookmark(ea, 0, f"[{type_char}] {name}")

def define_tilemap_structure():
    """Define SNES tilemap entry structure."""
    sid = ida_struct.get_struc_id('TilemapEntry')
    if sid == ida_struct.BADADDR:
        sid = ida_struct.add_struc(-1, 'TilemapEntry')
    
    s = ida_struct.get_struc(sid)
    ida_struct.add_bitfield(s, 'tile_id', 0, 10)      # 0-9: Tile ID
    ida_struct.add_bitfield(s, 'chr_bank', 10, 2)     # 10-11: CHR Bank
    ida_struct.add_bitfield(s, 'palette', 12, 2)      # 12-13: Palette
    ida_struct.add_bitfield(s, 'x_flip', 14, 1)       # 14: X Flip
    ida_struct.add_bitfield(s, 'y_flip', 15, 1)       # 15: Y Flip
```

### IDA vs Ghidra Differences

| Feature | Ghidra | IDA Pro |
|---------|--------|---------|
| Segment API | `createInitializedBlock()` | `add_segment_ex()` |
| Bookmarks | `BookmarkManager` | `set_bookmark()` |
| Data Types | `StructureDataType` | `add_struc()`, `add_bitfield()` |
| Comments | `setComment()` | `set_cmt()` |

---

## Files to Modify

- `toolkit/ImportBOBMapIDA.py` — New IDA import script
- `docs/IDA_IMPORT.md` — New IDA import guide
- `README.md` — Add IDA support mention

---

## Dependencies

- **Blocks:** None
- **Blocked by:** ECHO-002 (Ghidra script informs IDA design)

---

## Test Plan

1. Test with IDA Free 7.x
2. Verify segments created correctly
3. Check bookmarks appear in bookmark window
4. Validate data types defined
5. Test with sample ROM map

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
