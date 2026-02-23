# Tutorial 3: Graphics Extraction & Rendering

**Duration:** 25 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Tutorial 2 (Finding Compressed Blocks)

---

## Overview

This tutorial shows you how to extract and render graphics from B.O.B. ROM. You'll learn:

- How SNES graphics formats work (2bpp, 4bpp, 8bpp)
- How to extract graphics data
- How to render tiles with palettes
- How to generate sprite sheets

---

## Understanding SNES Graphics

### Bit Planes

SNES uses bit-plane graphics:

| Format | Colors | Bytes per Tile | Bit Planes |
|--------|--------|----------------|------------|
| 2bpp | 4 | 16 | 2 |
| 4bpp | 16 | 32 | 4 |
| 8bpp | 256 | 64 | 8 |

### 2bpp Example

```
Tile (8x8 pixels):     Bit plane 0:    Bit plane 1:
[0][1][0][2]...        [0][1][0][0]    [0][0][0][1]
[3][1][2][0]...        [1][1][0][0]    [1][0][1][0]
...                    ...             ...

Pixel value = (bitplane1 << 1) | bitplane0
Pixel [0,0] = (0 << 1) | 0 = 0
Pixel [0,1] = (0 << 1) | 1 = 1
Pixel [0,3] = (1 << 1) | 0 = 2
Pixel [1,0] = (1 << 1) | 1 = 3
```

---

## Extracting Graphics

### Step 1: Identify Graphics Data

From Tutorial 2, you have `out/candidates.json`. Look for blocks with:
- Entropy 2.0-4.5 (graphics range)
- Size 0x800-0x2000 (typical graphics size)

### Step 2: Decompress (if compressed)

```python
from toolkit.bob_lz import bob_lz_decompress

rom = open('rom/B.O.B..smc', 'rb').read()
compressed = rom[0x018000:0x018000 + 0x1000]

# Decompress
decompressed, consumed = bob_lz_decompress(compressed, 0x800)

# Save decompressed data
with open('out/graphics_0x018000.bin', 'wb') as f:
    f.write(decompressed)

print(f"Decompressed {consumed} bytes → {len(decompressed)} bytes")
```

### Step 3: Render with Python

```python
from toolkit.bob_graphics import SNESGraphicsRenderer

# Load graphics data
with open('out/graphics_0x018000.bin', 'rb') as f:
    data = f.read()

# Create renderer (2bpp format)
renderer = SNESGraphicsRenderer(format='2bpp')

# Render all tiles (32 tiles per row)
img = renderer.render_tiles(data, count=32, cols=32)

# Save as PNG
img.save('out/graphics_0x018000.png')
print("Saved: out/graphics_0x018000.png")
```

---

## Using the Graphics CLI

### Render All Decompressed Files

```bash
python toolkit/bob_graphics.py --input out/ --output out/gfx_rendered --all
```

### Render Specific File

```bash
python toolkit/bob_graphics.py --input out/decompressed_018000.bin --output out/gfx_rendered
```

### Specify Format

```bash
# 2bpp (default)
python toolkit/bob_graphics.py -i out/decompressed_018000.bin -o out/gfx --format 2bpp

# 4bpp
python toolkit/bob_graphics.py -i out/decompressed_018000.bin -o out/gfx --format 4bpp

# 8bpp
python toolkit/bob_graphics.py -i out/decompressed_018000.bin -o out/gfx --format 8bpp

# Auto-detect
python toolkit/bob_graphics.py -i out/decompressed_018000.bin -o out/gfx --format auto
```

---

## Applying Palettes

### Extract Palette from ROM

```python
from toolkit.bob_graphics import extract_palette

rom = open('rom/B.O.B..smc', 'rb').read()

# Palettes are typically at known offsets
# For B.O.B., try 0x020000 area
palette = extract_palette(rom, offset=0x020000, num_colors=16)

print(f"Extracted {len(palette)} colors:")
for i, color in enumerate(palette):
    print(f"  {i}: RGB{color}")
```

### Save Palette

```python
from toolkit.bob_graphics import save_palette

save_palette(palette, 'out/palette.json')
print("Saved: out/palette.json")
```

### Load and Apply Palette

```python
from toolkit.bob_graphics import load_palette, SNESGraphicsRenderer

# Load palette
palette = load_palette('out/palette.json')

# Render with palette
renderer = SNESGraphicsRenderer(format='2bpp')
renderer.palette = palette

img = renderer.render_tiles(data, count=32, cols=32)
img.save('out/graphics_with_palette.png')
```

---

## Generating Sprite Sheets

### Basic Sprite Sheet

```python
from toolkit.bob_graphics import SNESGraphicsRenderer

renderer = SNESGraphicsRenderer(format='2bpp')

# Render 64 tiles in 8x8 grid
img = renderer.render_tiles(data, count=64, cols=8)
img.save('out/sprite_sheet_8x8.png')
```

### Custom Tile Size

```python
# 16x16 pixel tiles (2x2 of 8x8)
renderer = SNESGraphicsRenderer(format='2bpp', tile_size=16)
img = renderer.render_tiles(data, count=16, cols=4)
img.save('out/sprite_sheet_16x16.png')
```

---

## Troubleshooting

### Garbled graphics

**Possible causes:**
- Wrong format (try 2bpp/4bpp/8bpp)
- Wrong offset (data not aligned)
- Data not graphics (check entropy)

**Solutions:**
```bash
# Try different formats
python toolkit/bob_graphics.py -i file.bin -o out --format 2bpp
python toolkit/bob_graphics.py -i file.bin -o out --format 4bpp
python toolkit/bob_graphics.py -i file.bin -o out --format 8bpp
```

### Colors look wrong

**Cause:** Missing or wrong palette

**Solution:** Extract and apply correct palette (see above)

### Only black/white output

**Cause:** Data may be all zeros or uniform

**Check:**
```python
data = open('file.bin', 'rb').read()
unique_bytes = len(set(data))
print(f"Unique bytes: {unique_bytes}")
# Should be > 8 for valid graphics
```

---

## Expected Output

After completing this tutorial:

```
out/
├── graphics_0x018000.bin     # Decompressed graphics
├── graphics_0x018000.png     # Rendered tiles
├── graphics_with_palette.png # With correct colors
├── sprite_sheet_8x8.png      # 8x8 grid
├── sprite_sheet_16x16.png    # 16x16 grid
└── palette.json              # Extracted palette
```

---

## Next Steps

1. **Tutorial 4:** Level Editing — Modify level tilemaps using extracted graphics
2. **Advanced:** Create custom palette for your graphics
3. **Advanced:** Batch process multiple graphics blocks

---

**Your graphics are now rendered!** 🎨
