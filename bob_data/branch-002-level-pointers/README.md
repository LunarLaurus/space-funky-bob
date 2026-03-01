# Space Funky B.O.B. Level Editor - Branch 002

## Level Pointer Research

### CONFIRMED Level Data Locations

| PC Offset | SNES Address | Zero % | Confidence |
|-----------|--------------|--------|------------|
| **0xD4000** | 0x9AC000 | 89.5% | **HIGH** |
| **0xE4000** | 0x9CC000 | 91.2% | **HIGH** |
| **0xF4000** | 0x9EC000 | 90.1% | **HIGH** |

### Verified Details
- These are the ONLY sparse data regions in the entire 1MB ROM
- 16-bit tile IDs (not 8-bit like source MAP files)
- 740-878 non-zero tiles per 16KB block
- NOT LZ77 compressed
- Likely World 1, World 2, World 3 level data

### Level Types
- 0 = Borg (Factory)
- 1 = Bug/Sand
- 4 = Ancient
- 6 = Lava
- 8 = Ultra
- 9 = Bubble
- 10-12 = World maps

### Map Dimensions
- 80x80 tiles
- 16KB per level

### Files
- `find_level_pointers.py` - Level pointer finder tool
- `level_import.py` - Level import tool

### Next Steps
1. Extract levels from confirmed ROM locations
2. Build tileset extractor from ROM CHR files
3. Implement export back to ROM
4. Connect web editor to ROM data
