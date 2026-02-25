#!/usr/bin/env python3
"""
Web server for Space Funky B.O.B. Level Editor
Serves level data to the web editor.

Author: Null
"""

import http.server
import socketserver
import json
import os
import sys

# Add lib to path
sys.path.insert(0, os.path.dirname(__file__) + "/lib")

from level_extract import LevelExtractor, LEVEL_CATEGORIES

PORT = 8000
EDITOR_DIR = os.path.dirname(__file__)

# In-memory cache (5 minute TTL)
_cache = {}
_cache_enabled = True
_cache_ttl = 300  # 5 minutes in seconds


def get_cached(key):
    if not _cache_enabled:
        return None
    if key in _cache:
        entry = _cache[key]
        import time

        if time.time() - entry["time"] < _cache_ttl:
            return entry["data"]
        else:
            del _cache[key]
    return None


def set_cached(key, value):
    if _cache_enabled:
        import time

        _cache[key] = {"data": value, "time": time.time()}


class EditorHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for editor requests."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/data.json":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            data = self.generate_editor_data()
            self.wfile.write(json.dumps(data, indent=2).encode())

        elif self.path == "/levels":
            # List available levels - use cache
            cache_key = "levels_list"
            cached = get_cached(cache_key)
            if cached:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("X-Cache", "HIT")
                self.end_headers()
                self.wfile.write(cached)
                return

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("X-Cache", "MISS")
            self.end_headers()

            levels = self.get_level_list()
            data = json.dumps(levels).encode()
            set_cached(cache_key, data)
            self.wfile.write(data)

        elif self.path.startswith("/level/"):
            # Get specific level data
            level_name = self.path[7:]  # Remove /level/
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            level_data = self.get_level_data(level_name)
            self.wfile.write(json.dumps(level_data, indent=2).encode())

        elif self.path == "/":
            self.path = "/index.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        elif self.path.startswith("/data/"):
            filename = self.path[6:]
            data_path = os.path.join(EDITOR_DIR, "..", "data", filename)
            if os.path.exists(data_path):
                self.send_response(200)
                if filename.endswith(".json"):
                    self.send_header("Content-type", "application/json")
                else:
                    self.send_header("Content-type", "text/plain")
                self.end_headers()
                with open(data_path, "r") as f:
                    self.wfile.write(f.read().encode())
            else:
                self.send_error(404, "Data file not found")

        elif self.path.startswith("/tileset/custom"):
            # Parse offset from query string
            import urllib.parse

            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            offset = int(params.get("offset", ["0x35800"])[0], 16)
            self.handle_tileset_by_offset(offset)

        elif self.path.startswith("/tileset/"):
            tileset_name = self.path[9:]
            self.handle_tileset(tileset_name)

        elif self.path == "/tilesets":
            self.handle_all_tilesets()

        elif self.path == "/midi" or self.path.startswith("/midi?"):
            print(f"[DEBUG] MIDI list request: {self.path}")
            self.handle_midi_list()

        elif self.path.startswith("/midi/"):
            print(f"[DEBUG] MIDI file request: {self.path}")
            filename = self.path[6:]
            self.handle_midi_file(filename)

        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/export-level":
            self.handle_export_level()
        else:
            self.send_error(404, "Not found")

    def handle_export_level(self):
        """Export level data back to ROM."""
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            level_data = json.loads(post_data.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        level_name = level_data.get("name", "").upper()
        tiles = level_data.get("tiles", [])
        offset = level_data.get("offset")

        if not level_name or offset is None:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Missing level name or offset"}).encode()
            )
            return

        ROM_LEVEL_OFFSETS = {
            "WORLD_1": 0xD4000,
            "WORLD_2": 0xE4000,
            "WORLD_3": 0xF4000,
        }

        rom_offset = ROM_LEVEL_OFFSETS.get(level_name)
        if rom_offset is None:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": f"Unknown ROM level: {level_name}"}).encode()
            )
            return

        rom_path = os.path.join(EDITOR_DIR, "..", "B.O.B._edit.smc")
        if not os.path.exists(rom_path):
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "ROM file not found"}).encode())
            return

        with open(rom_path, "r+b") as f:
            f.seek(rom_offset)

            level_bytes = bytearray(0x4000)

            for tile in tiles:
                x = tile.get("x", 0)
                y = tile.get("y", 0)
                tile_id = tile.get("tile", 0)

                if 0 <= x < 80 and 0 <= y < 80:
                    idx = y * 80 + x
                    if idx < len(level_bytes):
                        level_bytes[idx] = tile_id

            f.write(level_bytes)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "success": True,
                    "level": level_name,
                    "offset": hex(rom_offset),
                    "tiles_written": len(tiles),
                }
            ).encode()
        )

    def generate_palette_for_offset(self, offset):
        """Generate a unique palette based on the tileset offset."""
        palettes_by_range = {
            (0x008800, 0x008FFF): [  # bug range - organic/green
                [0, 0, 0],
                [255, 255, 255],
                [34, 139, 34],
                [50, 205, 50],
                [60, 179, 113],
                [102, 205, 170],
                [143, 188, 143],
                [154, 205, 50],
                [107, 142, 35],
                [85, 107, 47],
                [124, 252, 0],
                [173, 255, 47],
                [0, 128, 0],
                [0, 100, 0],
                [0, 50, 0],
                [192, 192, 192],
            ],
            (0x008000, 0x0087FF): [  # borg range - robotic/industrial
                [0, 0, 0],
                [255, 255, 255],
                [192, 192, 192],
                [128, 128, 128],
                [64, 64, 64],
                [0, 128, 128],
                [0, 192, 192],
                [0, 255, 255],
                [0, 128, 0],
                [0, 192, 0],
                [0, 255, 0],
                [128, 128, 0],
                [192, 192, 0],
                [255, 255, 0],
                [128, 0, 0],
                [192, 0, 0],
            ],
            (0x009000, 0x009FFF): [  # ancient range - browns, golds
                [0, 0, 0],
                [255, 255, 255],
                [139, 69, 19],
                [160, 82, 45],
                [139, 90, 43],
                [205, 133, 63],
                [210, 180, 140],
                [245, 222, 179],
                [85, 107, 47],
                [107, 142, 35],
                [154, 205, 50],
                [128, 128, 0],
                [184, 134, 11],
                [218, 165, 32],
                [240, 230, 140],
                [192, 192, 192],
            ],
            (0x009800, 0x009FFF): [  # lava range - reds, oranges
                [0, 0, 0],
                [255, 255, 255],
                [139, 0, 0],
                [178, 34, 34],
                [220, 20, 60],
                [255, 0, 0],
                [255, 69, 0],
                [255, 140, 0],
                [255, 165, 0],
                [255, 215, 0],
                [255, 255, 0],
                [128, 0, 0],
                [64, 0, 0],
                [48, 48, 48],
                [96, 96, 96],
                [192, 192, 192],
            ],
            (0x00A000, 0x00AFFF): [  # ultra range - purples, neons
                [0, 0, 0],
                [255, 255, 255],
                [128, 0, 128],
                [148, 0, 211],
                [186, 85, 211],
                [238, 130, 238],
                [255, 0, 255],
                [0, 255, 255],
                [0, 255, 127],
                [57, 255, 20],
                [154, 255, 154],
                [255, 255, 0],
                [192, 192, 192],
                [128, 128, 128],
                [64, 64, 64],
                [32, 32, 32],
            ],
            (0x035800, 0x035FFF): [  # main_1 - earthy/natural
                [0, 0, 0],
                [255, 255, 255],
                [34, 139, 34],
                [0, 100, 0],
                [0, 128, 0],
                [107, 142, 35],
                [85, 107, 47],
                [124, 252, 0],
                [0, 250, 154],
                [72, 209, 204],
                [32, 178, 170],
                [175, 238, 238],
                [139, 69, 19],
                [160, 82, 45],
                [210, 105, 30],
                [192, 192, 192],
            ],
            (0x03D800, 0x03DFFF): [  # main_2 - varied/secondary
                [0, 0, 0],
                [255, 255, 255],
                [70, 130, 180],
                [100, 149, 237],
                [65, 105, 225],
                [30, 144, 255],
                [135, 206, 250],
                [176, 224, 230],
                [255, 127, 80],
                [255, 99, 71],
                [220, 20, 60],
                [255, 20, 147],
                [199, 21, 133],
                [218, 112, 214],
                [216, 191, 216],
                [192, 192, 192],
            ],
        }

        for (start, end), palette in palettes_by_range.items():
            if start <= offset <= end:
                return palette

        offset_seed = (offset >> 8) & 0xFF
        base_hue = (offset_seed * 37) % 360
        palette = [[0, 0, 0], [255, 255, 255]]
        for i in range(14):
            hue = (base_hue + i * 30) % 360
            sat = 60 + (i % 3) * 20
            val = 180 + (i % 4) * 20
            r, g, b = self.hsv_to_rgb(hue, sat, val)
            palette.append([r, g, b])
        return palette

    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB."""
        s, v = s / 100, v / 100
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return [int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)]

    def handle_tileset(self, tileset_name):
        """Return tileset color data for rendering with proper SNES 4bpp decoding."""
        # Check cache first
        cache_key = f"tileset_{tileset_name}"
        cached = get_cached(cache_key)
        if cached:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("X-Cache", "HIT")
            self.end_headers()
            self.wfile.write(cached)
            return

        rom_path = os.path.join(EDITOR_DIR, "..", "B.O.B._edit.smc")

        tileset_offsets = {
            "main_1": 0x035800,
            "main_2": 0x03D800,
            "borg": 0x008000,
            "bug": 0x008800,
            "ancient": 0x009000,
            "lava": 0x009800,
            "ultra": 0x00A000,
        }

        offset = tileset_offsets.get(tileset_name, 0x035800)

        if not os.path.exists(rom_path):
            self.send_error(404, "ROM not found")
            return

        with open(rom_path, "rb") as f:
            f.seek(offset)
            data = f.read(8192)

        tiles = []

        # Generate unique palette based on offset
        palette = self.generate_palette_for_offset(offset)

        for i in range(256):
            tile_data = data[i * 32 : (i + 1) * 32]

            # Decode SNES 4bpp format - produce flat array of palette indices
            pixel_data = []
            for y in range(8):
                for x in range(8):
                    bit0 = (tile_data[y] >> (7 - x)) & 1
                    bit1 = (tile_data[y + 8] >> (7 - x)) & 1
                    bit2 = (tile_data[y + 16] >> (7 - x)) & 1
                    bit3 = (tile_data[y + 24] >> (7 - x)) & 1
                    color_idx = bit0 | (bit1 << 1) | (bit2 << 2) | (bit3 << 3)
                    pixel_data.append(color_idx)

            tiles.append(
                {
                    "id": i,
                    "pixels": pixel_data,  # 64 palette indices
                    "palette": palette,
                }
            )

        response_data = {"tileset": tileset_name, "offset": hex(offset), "tiles": tiles}

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("X-Cache", "MISS")
        self.end_headers()

        data = json.dumps(response_data).encode()
        set_cached(cache_key, data)
        self.wfile.write(data)

    def handle_tileset_by_offset(self, offset):
        """Return tileset at specific ROM offset with proper SNES 4bpp decoding."""
        # Check cache first
        cache_key = f"tileset_offset_{offset:x}"
        cached = get_cached(cache_key)
        if cached:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("X-Cache", "HIT")
            self.end_headers()
            self.wfile.write(cached)
            return

        rom_path = os.path.join(EDITOR_DIR, "..", "B.O.B._edit.smc")

        if not os.path.exists(rom_path):
            self.send_error(404, "ROM not found")
            return

        with open(rom_path, "rb") as f:
            f.seek(offset)
            data = f.read(8192)

        tiles = []
        # Generate unique palette based on offset
        palette = self.generate_palette_for_offset(offset)

        for i in range(256):
            tile_data = data[i * 32 : (i + 1) * 32]

            # Decode SNES 4bpp tile - produce flat array of palette indices
            pixel_data = []
            for y in range(8):
                for x in range(8):
                    bit0 = (tile_data[y] >> (7 - x)) & 1
                    bit1 = (tile_data[y + 8] >> (7 - x)) & 1
                    bit2 = (tile_data[y + 16] >> (7 - x)) & 1
                    bit3 = (tile_data[y + 24] >> (7 - x)) & 1
                    color_idx = bit0 | (bit1 << 1) | (bit2 << 2) | (bit3 << 3)
                    pixel_data.append(color_idx)

            tiles.append(
                {
                    "id": i,
                    "pixels": pixel_data,  # 64 palette indices
                    "palette": palette,
                }
            )

        response_data = {
            "tileset": f"custom_{offset:06x}",
            "offset": hex(offset),
            "tiles": tiles,
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("X-Cache", "MISS")
        self.end_headers()

        data = json.dumps(response_data).encode()
        set_cached(cache_key, data)
        self.wfile.write(data)

    def handle_all_tilesets(self):
        """Scan ROM for all possible tileset locations and return variations."""
        rom_path = os.path.join(EDITOR_DIR, "..", "B.O.B._edit.smc")

        # Common tileset offsets in SNES games (LoROM mapped)
        candidates = []

        # Known offsets from previous analysis
        known_offsets = [
            0x008000,
            0x008800,
            0x009000,
            0x009800,
            0x00A000,
            0x035800,
            0x03D800,
            0x100000,
            0x108000,
            0x110000,
            0x118000,
            0x200000,
            0x208000,
            0x210000,
            0x218000,
        ]

        if not os.path.exists(rom_path):
            self.send_error(404, "ROM not found")
            return

        with open(rom_path, "rb") as f:
            rom = f.read()

        tilesets = []
        for offset in known_offsets:
            # Each tileset is typically 8KB (8192 bytes) = 256 tiles * 32 bytes
            if offset + 8192 <= len(rom):
                data = rom[offset : offset + 8192]

                # Calculate variance to detect if it's actual tile data
                variance = sum(bytes(data)) / len(data) if data else 0

                # Generate colors based on raw data
                tiles = []
                for i in range(256):
                    tile_data = data[i * 32 : (i + 1) * 32]

                    # Simple color generation from tile data
                    r = sum(tile_data[0::4]) % 256
                    g = sum(tile_data[1::4]) % 256
                    b = sum(tile_data[2::4]) % 256

                    tiles.append({"id": i, "rgb": [r, g, b]})

                tilesets.append(
                    {
                        "id": f"tileset_{offset:06x}",
                        "name": f"Tileset 0x{offset:06X}",
                        "offset": offset,
                        "snes_addr": f"0x{offset:06X}",
                        "tiles": tiles,
                        "variance": variance,
                    }
                )

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"tilesets": tilesets}).encode())

    def generate_editor_data(self):
        """Generate all editor data."""
        # Load ROM
        rom_path = os.path.join(EDITOR_DIR, "..", "B.O.B._edit.smc")

        if os.path.exists(rom_path):
            with open(rom_path, "rb") as f:
                rom = f.read()
            extractor = LevelExtractor(rom)
            levels = extractor.analyze_map_files()
        else:
            levels = []

        return {
            "rom": {
                "path": "B.O.B._edit.smc",
                "size": os.path.getsize(rom_path) if os.path.exists(rom_path) else 0,
            },
            "categories": LEVEL_CATEGORIES,
            "levels": levels,
            "mapWidth": 80,
            "mapHeight": 80,
        }

    def get_level_list(self):
        """Get list of all available levels."""
        levels = []

        # ROM levels (confirmed locations)
        rom_levels = [
            {
                "name": "WORLD_1",
                "category": "ROM",
                "theme": "World 1",
                "source": "rom",
                "offset": 0xD4000,
            },
            {
                "name": "WORLD_2",
                "category": "ROM",
                "theme": "World 2",
                "source": "rom",
                "offset": 0xE4000,
            },
            {
                "name": "WORLD_3",
                "category": "ROM",
                "theme": "World 3",
                "source": "rom",
                "offset": 0xF4000,
            },
        ]

        # Check if ROM exists
        rom_path = os.path.join(EDITOR_DIR, "..", "B.O.B._edit.smc")
        if os.path.exists(rom_path):
            levels.extend(rom_levels)

        # Source MAP files (if available)
        map_dir = os.path.join(
            EDITOR_DIR, "..", "Space Funky B.O.B. Source Files", "Disk C"
        )

        if os.path.exists(map_dir):
            for category in LEVEL_CATEGORIES:
                cat_path = os.path.join(map_dir, category)
                if os.path.exists(cat_path):
                    for f in sorted(os.listdir(cat_path)):
                        if f.endswith(".MAP"):
                            levels.append(
                                {
                                    "name": f.replace(".MAP", ""),
                                    "category": category,
                                    "theme": LEVEL_CATEGORIES[category]["theme"],
                                    "path": f"Disk C/{category}/{f}",
                                    "source": "map",
                                }
                            )

        return levels

    def get_level_data(self, level_name):
        """Get data for a specific level."""
        # First check if it's a ROM level
        rom_levels = {
            "WORLD_1": 0xD4000,
            "WORLD_2": 0xE4000,
            "WORLD_3": 0xF4000,
        }

        level_upper = level_name.upper()
        if level_upper in rom_levels:
            rom_path = os.path.join(EDITOR_DIR, "..", "B.O.B._edit.smc")
            if os.path.exists(rom_path):
                with open(rom_path, "rb") as f:
                    f.seek(rom_levels[level_upper])
                    data = f.read(0x4000)  # 16KB

                # Parse 8-bit tile format, 80x80
                tiles = []
                for i, tile in enumerate(data[:6400]):
                    if tile != 0:
                        x = i % 80
                        y = i // 80
                        tiles.append({"x": x, "y": y, "tile": tile})

                return {
                    "name": level_name,
                    "category": "ROM",
                    "source": "rom",
                    "offset": hex(rom_levels[level_upper]),
                    "width": 80,
                    "height": 80,
                    "size": len(data),
                    "tiles": tiles,
                    "non_zero_tiles": len(tiles),
                }

        # Fall back to source MAP files
        map_dir = os.path.join(
            EDITOR_DIR, "..", "Space Funky B.O.B. Source Files", "Disk C"
        )

        # Find the level
        for category in LEVEL_CATEGORIES:
            cat_path = os.path.join(map_dir, category)
            if os.path.exists(cat_path):
                filepath = os.path.join(cat_path, f"{level_name}.MAP")
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        data = f.read()

                    # Parse the map data
                    # Format: sparse tile data at offset 0x202
                    tiles = []
                    for i in range(0x202, min(len(data), 0x20000), 1):
                        if data[i] != 0:
                            x = (i - 0x202) % 512
                            y = (i - 0x202) // 512
                            tiles.append({"offset": i, "x": x, "y": y, "tile": data[i]})

                    return {
                        "name": level_name,
                        "category": category,
                        "size": len(data),
                        "tiles": tiles,
                        "width": 512,
                        "height": (len(data) - 0x202) // 512 + 1,
                    }

        return {"error": "Level not found"}

    def handle_midi_list(self):
        """Return list of available MIDI files."""
        midi_dir = os.path.join(
            EDITOR_DIR,
            "..",
            "Space Funky B.O.B. Source Files",
            "Disk A",
            "bob music files \u0192 copy",
        )

        files = []
        if os.path.exists(midi_dir):
            for f in sorted(os.listdir(midi_dir)):
                if f.upper().endswith(".MID") and not f.startswith("._"):
                    files.append({"name": f, "url": "/midi/" + f})

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"files": files}).encode())

    def handle_midi_file(self, filename):
        """Serve a MIDI file with proper MIDI type."""
        print(f"[DEBUG] handle_midi_file called with filename: {filename}")

        # Try both directories
        midi_dirs = [
            os.path.join(
                EDITOR_DIR,
                "..",
                "Space Funky B.O.B. Source Files",
                "Disk A",
                "bob music files ƒ copy",
            ),
            os.path.join(
                EDITOR_DIR,
                "..",
                "Space Funky B.O.B. Source Files",
                "Disk A",
                "bob music files ƒ",
            ),
        ]

        filepath = None
        for midi_dir in midi_dirs:
            test_path = os.path.join(midi_dir, filename)
            print(
                f"[DEBUG] Checking path: {test_path}, exists: {os.path.exists(test_path)}"
            )
            if os.path.exists(test_path):
                filepath = test_path
                break

        if filepath:
            self.send_response(200)
            self.send_header("Content-type", "audio/midi")
            self.send_header("Content-Disposition", f"inline; filename={filename}")
            self.end_headers()
            with open(filepath, "rb") as f:
                self.wfile.write(f.read())
            print(f"[DEBUG] Served MIDI file: {filepath}")
        else:
            print(f"[DEBUG] MIDI file NOT FOUND: {filename}")
            self.send_error(404, "MIDI file not found")


def run_server(port=PORT):
    """Run the editor server."""
    os.chdir(EDITOR_DIR)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), EditorHandler) as httpd:
        print(f"Space Funky B.O.B. Level Editor")
        print(f"=" * 40)
        print(f"Server running at http://localhost:{port}")
        print(f"Press Ctrl+C to stop")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
