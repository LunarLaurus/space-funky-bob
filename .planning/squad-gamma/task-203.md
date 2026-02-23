# Task GAMMA-003: ROM Injection Safety Checks

**Squad:** Gamma (Level Editor Tools)  
**Priority:** P0 (Critical)  
**Complexity:** High  
**Estimated Effort:** 8-10 hours  
**Status:** ⏳ Pending

---

## Objective

Implement comprehensive safety checks for ROM injection operations, preventing corrupted ROMs, data loss, and invalid modifications through validation, backup, and verification mechanisms.

---

## Context

The `bob_inject.py` tool allows modifying ROM data by injecting new tilemaps, graphics, or other data. Without proper safety checks, injection can:
- Corrupt ROM structure
- Overwrite adjacent data
- Create unbootable ROMs
- Lose original data permanently

This task will add safety mechanisms to prevent these issues.

---

## Acceptance Criteria

- [ ] Backup creation: Automatic backup before any modification
- [ ] Size validation: Verify injected data fits in allocated space
- [ ] Boundary checks: Prevent overwriting adjacent regions
- [ ] Checksum verification: Validate ROM checksums after injection
- [ ] Dry-run mode: Show what would change without modifying
- [ ] Rollback support: Restore from backup if injection fails
- [ ] Warning prompts: Confirm destructive operations
- [ ] Tests: Verify safety mechanisms work correctly

---

## Technical Notes

### Safety Check Implementation

**Backup Creation:**
```python
def create_backup(rom_path):
    """Create timestamped backup of ROM file."""
    backup_path = f"{rom_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(rom_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path
```

**Size Validation:**
```python
def validate_injection(rom_data, offset, new_data, max_size=None):
    """Validate injection is safe."""
    errors = []
    
    # Check bounds
    if offset < 0 or offset >= len(rom_data):
        errors.append(f"Offset 0x{offset:X} out of ROM bounds")
    
    if offset + len(new_data) > len(rom_data):
        errors.append(f"Data exceeds ROM size at offset 0x{offset:X}")
    
    # Check max size if specified
    if max_size and len(new_data) > max_size:
        errors.append(f"Data size {len(new_data)} exceeds max {max_size}")
    
    return errors
```

**Checksum Verification:**
```python
def verify_checksum(rom_data):
    """Verify SNES ROM checksum at 0x7FDC-0x7FDF."""
    header_offset = detect_header(rom_data)
    checksum_pos = 0x7FDC + header_offset
    
    stored_checksum = struct.unpack('<H', rom_data[checksum_pos:checksum_pos+2])[0]
    stored_complement = struct.unpack('<H', rom_data[checksum_pos+2:checksum_pos+4])[0]
    
    calculated = sum(rom_data[0:0x7FDC]) & 0xFFFF
    calculated_complement = 0xFFFF - calculated
    
    return (stored_checksum == calculated and 
            stored_complement == calculated_complement)
```

---

## Files to Modify

- `toolkit/bob_inject.py` — Add safety checks
- `toolkit/bob_extract.py` — Add backup support
- `tests/test_injection_safety.py` — New test file

---

## Dependencies

- **Blocks:** GAMMA-005 (emulator testing needs safe injection)
- **Blocked by:** GAMMA-001 (format docs inform safe boundaries)

---

## Test Plan

1. Create `tests/test_injection_safety.py`
2. Test cases:
   - `test_backup_creation()`
   - `test_size_validation()`
   - `test_boundary_checks()`
   - `test_checksum_verification()`
   - `test_dry_run_mode()`
   - `test_rollback_on_failure()`
3. Verify corrupted ROMs are prevented

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
