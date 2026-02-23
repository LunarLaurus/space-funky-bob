# Space Funky B.O.B. Level Editor Guide

**Version:** v0.3.0  
**Last Updated:** 2026-02-23

---

## Quick Start

### Prerequisites

- Python 3.8+
- B.O.B. ROM file (`rom/B.O.B._edit.smc`)
- Web browser (Chrome, Firefox recommended)

### Starting the Editor

```bash
# Navigate to editor directory
cd editor

# Start the server
python server.py

# Open in browser
# http://localhost:8000
```

---

## Editor Features

### Level Editing

- **Click and drag** to paint tiles on the canvas
- **Right-click** to erase tiles (quick erase)
- **80x80 tile grid** with real-time minimap overview
- **Layer support** — Background (BG) and Foreground (FG)

### Tileset Selection

| Tileset | ROM Offset | Theme |
|---------|------------|-------|
| Main Graphics 1 | 0x035800 | Earthy/Natural |
| Main Graphics 2 | 0x03D800 | Varied/Secondary |
| Borg Tileset | 0x008000 | Factory/Industrial |
| Bug Tileset | 0x008800 | Organic/Green |
| Ancient Tileset | 0x009000 | Ruins/Brown |
| Lava Tileset | 0x009800 | Volcanic/Red |
| Ultra Tileset | 0x00A000 | Sci-fi/Purple |

### Keyboard Controls

| Key | Action |
|-----|--------|
| `Ctrl+S` | Export/Save current level |
| `Ctrl+Z` | Undo last action |
| `Ctrl+Y` | Redo undone action |
| `+` / `-` | Zoom in/out |
| `G` | Toggle grid overlay |
| `S` | Toggle snap to grid |
| `0-9` | Quick tile selection |
| `R` | Rotate tile |

---

## API Reference

### Server Endpoints

The editor runs a Python HTTP server on port 8000 with the following API:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Serve index.html |
| GET | `/data.json` | Generate editor data |
| GET | `/levels` | List available levels |
| GET | `/level/:name` | Get specific level data |
| GET | `/tileset/:name` | Get tileset (SNES 4bpp decode) |
| GET | `/tileset/custom?offset=0x...` | Tileset at custom offset |
| GET | `/tilesets` | Scan ROM for tilesets |
| GET | `/midi` | List MIDI files |
| GET | `/midi/:filename` | Serve MIDI file |
| GET | `/data/:file` | Serve JSON data files |
| POST | `/export-level` | Export level to ROM |

### Example API Calls

```javascript
// Get all levels
fetch('/levels')
  .then(r => r.json())
  .then(data => console.log(data));

// Get specific level
fetch('/level/world_1')
  .then(r => r.json())
  .then(data => console.log(data));

// Get tileset
fetch('/tileset/main_graphics_1')
  .then(r => r.json())
  .then(data => console.log(data));

// Export level to ROM
fetch('/export-level', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'world_1',
    data: levelData,
    offset: 0xD4000
  })
});
```

---

## Data Files

### Extracted Data

The `data/` directory contains extracted game data:

| Directory | Contents |
|-----------|----------|
| `data/levels/` | Extracted level tile data (4 files) |
| `data/tilesets/` | Tileset images and metadata (24 files) |
| `data/extracted/` | Enemy, tile, level definitions (4 files) |

### JSON File Formats

**ENEMIES.json** — Enemy database:
```json
{
  "enemies": [
    {
      "id": 1,
      "name": "Borg Guard",
      "category": "borg",
      "health": 4,
      "speed": 2,
      "behavior": "Patrols and shoots at player"
    }
  ]
}
```

**TILESETS.json** — Tileset metadata:
```json
{
  "tilesets": [
    {
      "id": "main_graphics_1",
      "name": "Main Graphics Set 1",
      "rom_offset": "0x035800",
      "snes_offset": "0x035800",
      "size": 8192,
      "tiles": 256
    }
  ]
}
```

**LEVELS.json** — Level definitions:
```json
{
  "worlds": [
    {
      "id": 1,
      "name": "World 1 - Borg Factory",
      "type": "borg",
      "offset": "0x0D4000",
      "levels": [...]
    }
  ]
}
```

---

## Extraction Scripts

### Extract Levels

```bash
python scripts/extract_levels_bob.py
```

**Output:**
- `data/levels/all_levels.json` — Combined level data
- `data/levels/world_1.json` — World 1 tile data
- `data/levels/world_2.json` — World 2 tile data
- `data/levels/world_3.json` — World 3 tile data

### Extract Tilesets

```bash
python scripts/extract_tilesets_bob.py
```

**Output:**
- `data/tilesets/tileset_*.png` — Rendered tileset images
- `data/tilesets/tileset_*.json` — Tile metadata

---

## Technical Details

### ROM Specification

| Property | Value |
|----------|-------|
| File | B.O.B._edit.smc |
| Size | 1MB (1,048,576 bytes) |
| Format | Headerless LoROM |
| Region | USA/NTSC |

### Level Data Format

| Property | Value |
|----------|-------|
| Dimensions | 80 × 80 tiles |
| Size | 16,384 bytes (0x4000) per level |
| Format | 8-bit tile IDs (0-255) |
| Storage | Sparse — only non-zero tiles stored |

### Tileset Format

| Property | Value |
|----------|-------|
| Tile Size | 8×8 pixels |
| Color Depth | 4bpp (16 colors) |
| Bytes per Tile | 32 bytes |
| Tiles per 8KB | 256 tiles |

### SNES 4bpp Tile Layout

```
Plane 0: bytes 0-7   (bit 0 of each pixel)
Plane 1: bytes 8-15  (bit 1)
Plane 2: bytes 16-23 (bit 2)
Plane 3: bytes 24-31 (bit 3)

Pixel(x,y) = ((plane0[y] >> x) & 1)
           | (((plane1[y] >> x) & 1) << 1)
           | (((plane2[y] >> x) & 1) << 2)
           | (((plane3[y] >> x) & 1) << 3)
```

---

## Troubleshooting

### Server Won't Start

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process or use a different port
python server.py --port 8080
```

### ROM Not Found

Ensure the ROM file exists at `rom/B.O.B._edit.smc`:

```bash
# Create rom directory if needed
mkdir rom

# Copy your legally-owned ROM
cp /path/to/your/rom.smc rom/B.O.B._edit.smc
```

### Canvas Not Rendering

- Check browser console for JavaScript errors
- Ensure `js/app.js`, `js/renderer.js` are loaded
- Clear browser cache and reload

---

## References

- `editor/wiki.html` — Complete technical wiki (897 lines)
- `editor/WIKI.md` — Condensed wiki (293 lines)
- `editor/CORRELATION_MAP.md` — Architecture documentation
- `docs/WIKI_INTEGRATION.md` — Integration report

---

*For more detailed technical information, see `editor/wiki.html`*
