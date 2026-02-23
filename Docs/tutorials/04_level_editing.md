# Tutorial 4: Level Editing Workflow

**Duration:** 30 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Tutorial 2 (Finding Compressed Blocks), Tutorial 3 (Graphics Extraction)

---

## Overview

This tutorial teaches you how to edit level tilemaps in B.O.B. You'll learn:

- How level tilemaps are structured
- How to extract and view tilemaps
- How to modify tilemaps safely
- How to inject changes back into the ROM

---

## Understanding Level Tilemaps

### Tilemap Structure

B.O.B. uses 32x32 tilemaps (1024 tiles):

```
Offset: 0x028000, 0x028800, 0x029000, etc.
Size: 0x800 bytes (2048 bytes)
Format: 16-bit SNES tilemap entries
```

### 16-bit Entry Format

```
Bits:    [YFlip][XFlip][Palette][CHR Bank][Tile ID]
         15     14     13-12   11-10      9-0

Example: 0xB005 = 1011000000000101
  Tile ID:   0x005 (5)
  CHR Bank:  0b00 (0)
  Palette:   0b11 (3)
  X-Flip:    0 (no)
  Y-Flip:    1 (yes)
```

---

## Extracting Tilemaps

### Using the Level Editor CLI

```bash
# List all detected tilemaps
python toolkit/bob_level_editor.py --rom rom/B.O.B..smc list
```

Expected output:
```
============================================================
B.O.B. Level Tilemaps
============================================================

Found 10 potential tilemaps:

#    Offset       Size       Non-zero   Unique    
------------------------------------------------------------
0    0x028000     0x800      512        128       
1    0x028800     0x800      480        115       
...

Known locations:
  0: Tilemap 1 at 0x028000
  1: Tilemap 2 at 0x028800
  ...
```

### Export Tilemap

```bash
# Export as JSON (editable)
python toolkit/bob_level_editor.py --rom rom/B.O.B..smc export 0 level_0.json

# Export as binary
python toolkit/bob_level_editor.py --rom rom/B.O.B..smc export 0 level_0.bin
```

### View Tilemap

```bash
# View as ASCII grid
python toolkit/bob_level_editor.py --rom rom/B.O.B..smc view 0
```

Expected output:
```
============================================================
Tilemap: Tilemap 1 (0x028000)
============================================================

32x32 Tile Grid (showing tile IDs mod 10):

01234567890123456789012345678901
23456789012345678901234567890123
...

Statistics:
  Unique tiles: 128
  Max tile ID: 512
  Min tile ID: 0
```

---

## Editing Tilemaps

### Interactive Mode

```bash
python toolkit/bob_level_editor.py --rom rom/B.O.B..smc
```

Commands:
```
> list              # List all tilemaps
> view 0            # View tilemap 0
> export 0 level.json  # Export tilemap 0
> import 0 modified.json  # Import modified tilemap
> help              # Show help
> quit              # Exit
```

### Manual Editing (JSON)

1. Export tilemap:
```bash
python toolkit/bob_level_editor.py --rom rom/B.O.B..smc export 0 level_0.json
```

2. Edit `level_0.json`:
```json
{
  "name": "Tilemap 1",
  "offset": 163840,
  "tiles": [
    {
      "raw": 5,
      "id": 5,
      "chr_bank": 0,
      "palette": 3,
      "x_flip": 0,
      "y_flip": 1
    },
    ...
  ]
}
```

3. Modify tile entries:
   - Change `id` to use different tile
   - Change `palette` for different colors
   - Set `x_flip` or `y_flip` to 1 for mirroring

### Programmatic Editing

```python
import json

# Load tilemap
with open('level_0.json') as f:
    data = json.load(f)

# Modify: Replace all tile ID 5 with tile ID 10
for tile in data['tiles']:
    if tile['id'] == 5:
        tile['id'] = 10
        tile['raw'] = (tile['raw'] & ~0x3FF) | 10  # Update raw value

# Save
with open('level_0_modified.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Modified tilemap saved to level_0_modified.json")
```

---

## Injecting Changes

### With Backup (Recommended)

```bash
python toolkit/bob_level_editor.py --rom rom/B.O.B..smc import 0 level_0_modified.json --output rom_modified.sfc
```

This will:
1. Validate the injection
2. Create a backup automatically
3. Inject the modified tilemap
4. Save as `rom_modified.sfc`

### Manual Injection

```python
from toolkit.bob_inject import inject_tilemap, create_backup, validate_injection

# Load ROM
rom_data = open('rom/B.O.B..smc', 'rb').read()

# Load modified tilemap
import json
with open('level_0_modified.json') as f:
    data = json.load(f)

# Reconstruct binary
tilemap_data = bytearray(0x800)
for i, tile in enumerate(data['tiles'][:1024]):
    val = tile['raw']
    tilemap_data[i * 2] = val & 0xFF
    tilemap_data[i * 2 + 1] = (val >> 8) & 0xFF

# Validate
errors = validate_injection(rom_data, 0x028000, tilemap_data)
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    # Create backup
    create_backup('rom/B.O.B..smc')
    
    # Inject
    result = inject_tilemap(rom_data, 'level_0_modified.json', 0x028000, 'rom_modified.sfc')
    if result:
        print("Injection successful!")
```

---

## Testing Your Changes

### Step 1: Verify Injection

```bash
# Re-extract the modified tilemap
python toolkit/bob_level_editor.py --rom rom_modified.sfc export 0 level_0_verify.json

# Compare with original
diff level_0.json level_0_verify.json
```

### Step 2: Test in Emulator

1. Load `rom_modified.sfc` in your SNES emulator
2. Navigate to the modified level
3. Verify your changes appear correctly

### Step 3: Check for Crashes

If the game crashes:
- Tilemap may reference invalid tile IDs
- CHR bank may be wrong
- Palette may be invalid

**Solution:** Revert to backup and try again.

---

## Troubleshooting

### Game crashes after injection

**Possible causes:**
- Invalid tile ID (>1023)
- Invalid CHR bank (>3)
- Invalid palette (>3)
- Wrong tilemap size (must be 0x800 bytes)

**Solution:** Validate before injecting:
```bash
python toolkit/bob_level_editor.py --rom rom/B.O.B..smc import 0 level.json
# Check for validation errors
```

### Graphics look wrong

**Possible causes:**
- Tile ID doesn't exist in graphics
- Wrong CHR bank selected
- Wrong palette

**Solution:** Check graphics data and verify tile IDs are valid.

### Changes don't appear

**Possible causes:**
- Wrong offset
- Tilemap not used in game
- Level uses different tilemap

**Solution:** Verify offset with `list` command and check which tilemaps are actually used.

---

## Expected Output

After completing this tutorial:

```
out/
├── level_0.json           # Exported tilemap
├── level_0_modified.json  # Modified tilemap
├── level_0_verify.json    # Verification export
└── rom_modified.sfc       # Modified ROM
backups/
└── B.O.B..backup.*.smc    # Automatic backup
```

---

## Next Steps

1. **Tutorial 5:** Ghidra/IDA Integration — Import your analysis into RE tools
2. **Advanced:** Create entirely new levels
3. **Advanced:** Modify graphics and update tilemaps together

---

**You're now a level editor!** 🎮✏️
