# Task GAMMA-005: Emulator Integration Testing

**Squad:** Gamma (Level Editor Tools)  
**Priority:** P1 (High)  
**Complexity:** High  
**Estimated Effort:** 8-10 hours  
**Status:** ⏳ Pending

---

## Objective

Establish emulator integration testing workflow that validates injected ROM modifications by running them in an SNES emulator, ensuring modified ROMs are bootable and changes appear correctly.

---

## Context

After injecting level modifications, the ultimate test is running the ROM in an emulator. This task will:
1. Set up automated emulator testing
2. Capture screenshots/video for visual verification
3. Verify ROM boots without crashes
4. Navigate to modified levels for visual confirmation

---

## Acceptance Criteria

- [ ] Emulator setup: Configure headless SNES emulator (bsnes/higan)
- [ ] ROM boot test: Verify modified ROM boots to title screen
- [ ] Screenshot capture: Capture frames at specific points
- [ ] Level navigation: Auto-navigate to modified level
- [ ] Visual comparison: Compare screenshots with expected output
- [ ] Crash detection: Detect freezes/crashes automatically
- [ ] Documentation: Emulator integration guide
- [ ] Tests: End-to-end injection → emulation workflow

---

## Technical Notes

### Emulator Options

**bsnes/higan:**
- Accurate SNES emulation
- Command-line interface available
- Screenshot support
- Lua scripting for automation

**Snes9x:**
- Faster emulation
- CLI support varies by platform
- Screenshot support

**Mesen-S:**
- Good debugging features
- Screenshot support
- Less accurate than bsnes

### Automation Approach

```python
import subprocess
import time

def test_rom_in_emulator(rom_path, test_script=None):
    """
    Test ROM in headless emulator.
    
    Args:
        rom_path: Path to modified ROM
        test_script: Optional Lua script for automation
    
    Returns:
        dict: Test results (booted, screenshots, errors)
    """
    # Start emulator in background
    cmd = [
        'bsnes',
        '--fullscreen',
        '--quit-after-frames', '60',  # Run 60 frames (~1 second)
        rom_path
    ]
    
    if test_script:
        cmd.extend(['--lua-script', test_script])
    
    process = subprocess.Popen(cmd, capture_output=True)
    stdout, stderr = process.communicate(timeout=120)
    
    # Check for crashes
    if process.returncode != 0:
        return {'booted': False, 'error': stderr.decode()}
    
    return {'booted': True, 'frames_rendered': 60}
```

### Visual Verification

```lua
-- test_script.lua
-- Navigate to level 4 and capture screenshot

frame_count = 0
function main()
    frame_count = frame_count + 1
    
    -- Press start at frame 30
    if frame_count == 30 then
        joypad.set({start=true})
    end
    
    -- Navigate to level select at frame 60
    if frame_count == 60 then
        joypad.set({up=true})
    end
    
    -- Capture at frame 120
    if frame_count == 120 then
        screenshot.save("output/level4_test.png")
    end
end
```

---

## Files to Modify

- `tests/test_emulator_integration.py` — New test file
- `scripts/run_emulator_test.sh` — Emulator automation script
- `docs/EMULATOR_TESTING.md` — New documentation

---

## Dependencies

- **Blocks:** None
- **Blocked by:** GAMMA-003 (safe injection required for testing)

---

## Test Plan

1. Set up emulator automation environment
2. Test unmodified ROM (baseline)
3. Inject known-good modification
4. Verify modification appears in emulator
5. Test crash detection with invalid ROM

---

## Status Log

- **2026-02-23:** Task created, awaiting assignment
