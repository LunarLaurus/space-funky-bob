#!/usr/bin/env python3
"""
Test suite for data validation in Space Funky B.O.B. Level Editor

Validates JSON files and referential integrity.
"""

import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestJSONValidation(unittest.TestCase):
    """Tests for JSON file validation."""

    def _get_json_files(self):
        """Get all JSON files from levels and tilesets directories."""
        json_files = []

        levels_dir = os.path.join(BASE_DIR, "levels")
        if os.path.exists(levels_dir):
            for f in os.listdir(levels_dir):
                if f.endswith(".json"):
                    json_files.append(os.path.join(levels_dir, f))

        tilesets_dir = os.path.join(BASE_DIR, "tilesets")
        if os.path.exists(tilesets_dir):
            for f in os.listdir(tilesets_dir):
                if f.endswith(".json"):
                    json_files.append(os.path.join(tilesets_dir, f))

        return json_files

    def test_all_json_files_valid(self):
        """Validate all JSON files in data directories are valid JSON."""
        json_files = self._get_json_files()
        self.assertGreater(len(json_files), 0, "No JSON files found")

        invalid_files = []
        for json_file in json_files:
            try:
                with open(json_file, "r") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                invalid_files.append((json_file, str(e)))
            except Exception as e:
                invalid_files.append((json_file, str(e)))

        if invalid_files:
            error_msg = "\n".join([f"{f}: {e}" for f, e in invalid_files])
            self.fail(f"Invalid JSON files found:\n{error_msg}")

    def test_level_json_structure(self):
        """Validate level JSON files have expected structure."""
        levels_dir = os.path.join(BASE_DIR, "levels")
        if not os.path.exists(levels_dir):
            raise unittest.SkipTest("Levels directory not found")

        for f in os.listdir(levels_dir):
            if f.endswith(".json"):
                filepath = os.path.join(levels_dir, f)
                with open(filepath, "r") as fp:
                    data = json.load(fp)

                if f == "all_levels.json":
                    self.assertIn("levels", data, f"Missing 'levels' in {f}")
                    self.assertIn("metadata", data, f"Missing 'metadata' in {f}")
                else:
                    self.assertIn("width", data, f"Missing 'width' in {f}")
                    self.assertIn("height", data, f"Missing 'height' in {f}")
                    self.assertIn("tiles", data, f"Missing 'tiles' in {f}")
                    self.assertIsInstance(
                        data["tiles"], list, f"'tiles' should be a list in {f}"
                    )

    def test_tileset_json_structure(self):
        """Validate tileset JSON files have expected structure."""
        tilesets_dir = os.path.join(BASE_DIR, "tilesets")
        if not os.path.exists(tilesets_dir):
            raise unittest.SkipTest("Tilesets directory not found")

        for f in os.listdir(tilesets_dir):
            if f.endswith(".json") and f != "candidates_report.json":
                filepath = os.path.join(tilesets_dir, f)
                with open(filepath, "r") as fp:
                    data = json.load(fp)

                self.assertIn("metadata", data, f"Missing 'metadata' in {f}")
                self.assertIn("tiles", data, f"Missing 'tiles' in {f}")
                self.assertIsInstance(
                    data["tiles"], list, f"'tiles' should be a list in {f}"
                )


class TestReferentialIntegrity(unittest.TestCase):
    """Tests for referential integrity between data files."""

    def test_level_offsets_valid(self):
        """Verify level offsets in JSON files are valid."""
        levels_dir = os.path.join(BASE_DIR, "levels")
        if not os.path.exists(levels_dir):
            raise unittest.SkipTest("Levels directory not found")

        for f in os.listdir(levels_dir):
            if f.endswith(".json"):
                filepath = os.path.join(levels_dir, f)
                with open(filepath, "r") as fp:
                    data = json.load(fp)

                if f == "all_levels.json":
                    for level_name, level_data in data.get("levels", {}).items():
                        if "offset" in level_data:
                            offset_str = level_data["offset"]
                            if isinstance(offset_str, str) and offset_str.startswith(
                                "0x"
                            ):
                                offset_val = int(offset_str, 16)
                                self.assertGreater(
                                    offset_val, 0, f"Invalid offset in {f}"
                                )
                else:
                    if "offset" in data:
                        offset_str = data["offset"]
                        if isinstance(offset_str, str) and offset_str.startswith("0x"):
                            offset_val = int(offset_str, 16)
                            self.assertGreater(offset_val, 0, f"Invalid offset in {f}")

    def test_level_tile_coordinates_valid(self):
        """Verify level tile coordinates are within bounds."""
        levels_dir = os.path.join(BASE_DIR, "levels")
        if not os.path.exists(levels_dir):
            raise unittest.SkipTest("Levels directory not found")

        for f in os.listdir(levels_dir):
            if f.endswith(".json"):
                filepath = os.path.join(levels_dir, f)
                with open(filepath, "r") as fp:
                    data = json.load(fp)

                if f == "all_levels.json":
                    for level_name, level_data in data.get("levels", {}).items():
                        width = level_data.get("width", 80)
                        height = level_data.get("height", 80)
                        for tile in level_data.get("tiles", []):
                            x = tile.get("x", -1)
                            y = tile.get("y", -1)
                            self.assertGreaterEqual(x, 0, f"Tile x < 0 in {f}")
                            self.assertGreaterEqual(y, 0, f"Tile y < 0 in {f}")
                            self.assertLess(x, width, f"Tile x >= width in {f}")
                            self.assertLess(y, height, f"Tile y >= height in {f}")
                else:
                    width = data.get("width", 80)
                    height = data.get("height", 80)

                    for tile in data.get("tiles", []):
                        x = tile.get("x", -1)
                        y = tile.get("y", -1)

                        self.assertGreaterEqual(x, 0, f"Tile x < 0 in {f}")
                        self.assertGreaterEqual(y, 0, f"Tile y < 0 in {f}")
                        self.assertLess(x, width, f"Tile x >= width in {f}")
                        self.assertLess(y, height, f"Tile y >= height in {f}")

    def test_tileset_tiles_have_valid_indices(self):
        """Verify tileset tiles have valid indices."""
        tilesets_dir = os.path.join(BASE_DIR, "tilesets")
        if not os.path.exists(tilesets_dir):
            raise unittest.SkipTest("Tilesets directory not found")

        for f in os.listdir(tilesets_dir):
            if f.endswith(".json") and f != "candidates_report.json":
                filepath = os.path.join(tilesets_dir, f)
                with open(filepath, "r") as fp:
                    data = json.load(fp)

                for tile in data.get("tiles", []):
                    self.assertIn("index", tile, f"Missing 'index' in {f}")
                    self.assertIsInstance(
                        tile["index"], int, f"Tile index not int in {f}"
                    )
                    self.assertGreaterEqual(tile["index"], 0, f"Tile index < 0 in {f}")

    def test_level_tile_tileset_references(self):
        """Verify tileset references in level data are valid."""
        levels_dir = os.path.join(BASE_DIR, "levels")
        tilesets_dir = os.path.join(BASE_DIR, "tilesets")

        if not os.path.exists(levels_dir) or not os.path.exists(tilesets_dir):
            raise unittest.SkipTest("Levels or tilesets directory not found")

        tileset_files = set()
        for f in os.listdir(tilesets_dir):
            if f.endswith(".json") and f != "candidates_report.json":
                tileset_files.add(f)

        references_found = False
        for f in os.listdir(levels_dir):
            if f.endswith(".json"):
                filepath = os.path.join(levels_dir, f)
                with open(filepath, "r") as fp:
                    data = json.load(fp)

                tileset_refs = data.get("tileset_references", [])
                if tileset_refs:
                    references_found = True
                    for ref in tileset_refs:
                        ref_file = ref if ref.endswith(".json") else f"{ref}.json"
                        self.assertIn(
                            ref_file,
                            tileset_files,
                            f"Invalid tileset reference '{ref}' in {f}",
                        )

        if not references_found:
            raise unittest.SkipTest(
                "No tileset_references field found in level files (feature not implemented)"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
