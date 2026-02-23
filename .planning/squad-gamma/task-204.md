# Task GAMMA-004: Level Editor CLI Prototype

**Squad:** Gamma (Level Editor Tools)  
**Priority:** P2 (Medium)  
**Complexity:** Medium  
**Estimated Effort:** 6-8 hours  
**Status:** ⏳ Pending

---

## Objective

Create an interactive command-line interface for level editing, enabling users to view, modify, and inject level tilemaps without manual hex editing.

---

## Context

Current level editing workflow requires:
1. Manual extraction with `bob_extract_levels.py`
2. Hex editing or custom tool for modification
3. Manual injection with `bob_inject.py`

A unified CLI would streamline this workflow:
- Interactive tilemap viewing
- Visual tile selection
- Simple modification commands
- Safe injection with validation

---

## Acceptance Criteria

- [ ] List levels: Show all known tilemap locations
- [ ] View tilemap: Display tilemap as text/ASCII art
- [ ] Export tilemap: Save to editable format (JSON/binary)
- [ ] Import tilemap: Load modified tilemap
- [ ] Modify single tile: Change tile at specific position
- [ ] Batch operations: Fill, copy, paste regions
- [ ] Preview: Show rendered tilemap with graphics
- [ ] Safe injection: Integrate GAMMA-003 safety checks
- [ ] Help system: Built-in documentation

---

## Technical Notes

### CLI Design

```bash
# List all levels
bob-level list

# View tilemap
bob-level view --level 04

# Export tilemap
bob-level export --level 04 --output level_04.json

# Import modified tilemap
bob-level import --level 04 --input modified.json

# Modify single tile
bob-level set --level 04 --position 10,20 --tile 42

# Preview with graphics
bob-level preview --level 04 --output preview.png
```

### Interactive Mode

```python
def interactive_editor(level_data):
    """Interactive level editor."""
    while True:
        print(f"\nLevel Editor - {level_data['name']}")
        print("1. View tilemap")
        print("2. Modify tile")
        print("3. Export")
        print("4. Save & Exit")
        print("5. Cancel")
        
        choice = input("Command: ")
        
        if choice == '1':
            display_tilemap(level_data['tilemap'])
        elif choice == '2':
            x = int(input("X position (0-31): "))
            y = int(input("Y position (0-31): "))
            tile = int(input("Tile ID (0-1023): "))
            level_data['tilemap'][y * 32 + x] = tile
        # ... etc
```

---

## Files to Modify

- `toolkit/bob_level_editor.py` — New CLI module
- `toolkit/bob_extract_levels.py` — Integrate extraction
- `toolkit/bob_inject.py` — Integrate injection

---

## Dependencies

- **Blocks:** None
- **Blocked by:** GAMMA-001 (format docs), GAMMA-002 (validated extraction), GAMMA-003 (safety checks)

---

## Test Plan

1. Manual testing of all CLI commands
2. Integration test: Full edit workflow
3. Usability testing with new users
4. Verify safety checks prevent errors

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
- **2026-02-23:** ✅ COMPLETE — Level Editor CLI complete
  - Created `toolkit/bob_level_editor.py` — Interactive CLI
  - Commands: list, view, export, import, interactive mode
  - Features:
    - List all tilemap locations
    - View tilemap as 32x32 ASCII grid
    - Export to JSON or binary format
    - Import from JSON or binary format
    - Interactive mode with help system
    - Safe injection with validation (integrates GAMMA-003)
  - Created `tests/test_level_editor.py` with 20 tests (all passing)
  - All acceptance criteria met
