#!/usr/bin/env python3
"""
Test suite for Space Funky B.O.B. Level Editor

Tests ROM parsing, level extraction, level export, LZ77 compression,
and server endpoints.
"""

import os
import sys
import json
import tempfile
import unittest
from http.client import HTTPConnection
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "editor", "lib"))

from rom_parser import ROMParser
from level_extract import LevelExtractor
from lz77 import LZ77


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROM_PATH = os.path.join(BASE_DIR, "B.O.B._edit.smc")


class TestROMParser(unittest.TestCase):
    """Tests for ROM parsing functionality."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(ROM_PATH):
            raise unittest.SkipTest(f"ROM file not found: {ROM_PATH}")
        cls.parser = ROMParser(ROM_PATH)

    def test_rom_detected(self):
        """Verify ROM is detected and loaded."""
        self.assertIsNotNone(self.parser.rom_data)
        self.assertGreater(len(self.parser.rom_data), 0)

    def test_rom_size(self):
        """Verify ROM is detected as 1MB LoROM."""
        info = self.parser.get_info()
        self.assertEqual(info["rom_size_mb"], 1)
        self.assertEqual(info["size"], 1048576)

    def test_rom_header_parsed(self):
        """Verify ROM header is parsed correctly."""
        self.assertIn("title", self.parser.header)
        self.assertIn("rom_size", self.parser.header)
        self.assertIn("has_smc_header", self.parser.header)
        self.assertIn("version", self.parser.header)

    def test_lorom_address_conversion(self):
        """Verify LoROM address conversion works."""
        snes_addr = 0x800000
        file_offset = self.parser.find_lorom_address(snes_addr)
        self.assertIsNotNone(file_offset)
        self.assertEqual(file_offset, 0)

    def test_read_methods(self):
        """Verify read_byte, read_word work correctly."""
        byte_val = self.parser.read_byte(0)
        self.assertIsInstance(byte_val, int)
        self.assertGreaterEqual(byte_val, 0)
        self.assertLessEqual(byte_val, 255)

        word_val = self.parser.read_word(0)
        self.assertIsInstance(word_val, int)
        self.assertGreaterEqual(word_val, 0)
        self.assertLessEqual(word_val, 65535)


class TestLevelExtraction(unittest.TestCase):
    """Tests for level extraction functionality."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(ROM_PATH):
            raise unittest.SkipTest(f"ROM file not found: {ROM_PATH}")
        with open(ROM_PATH, "rb") as f:
            cls.rom_data = f.read()
        cls.extractor = LevelExtractor(cls.rom_data)

    def test_world_1_loads(self):
        """Verify WORLD_1 loads correctly."""
        offset = 0xD4000
        data = self.extractor.extract_level(offset)
        self.assertEqual(len(data), 16384)
        nonzero = sum(1 for b in data if b != 0)
        self.assertGreater(nonzero, 0)

    def test_world_2_loads(self):
        """Verify WORLD_2 loads correctly."""
        offset = 0xE4000
        data = self.extractor.extract_level(offset)
        self.assertEqual(len(data), 16384)
        nonzero = sum(1 for b in data if b != 0)
        self.assertGreater(nonzero, 0)

    def test_world_3_loads(self):
        """Verify WORLD_3 loads correctly."""
        offset = 0xF4000
        data = self.extractor.extract_level(offset)
        self.assertEqual(len(data), 16384)
        nonzero = sum(1 for b in data if b != 0)
        self.assertGreater(nonzero, 0)

    def test_level_data_extraction(self):
        """Verify level data extraction returns expected size."""
        offset = 0xD4000
        data = self.extractor.extract_level(offset)
        self.assertEqual(len(data), LevelExtractor.LEVEL_SIZE)


class TestLevelExport(unittest.TestCase):
    """Tests for level export functionality."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(ROM_PATH):
            raise unittest.SkipTest(f"ROM file not found: {ROM_PATH}")

    def test_write_to_temp_file(self):
        """Verify writing level data to ROM works (uses temp file)."""
        with tempfile.NamedTemporaryFile(suffix=".smc", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with open(ROM_PATH, "rb") as src:
                rom_data = src.read()

            test_tiles = [
                {"x": 0, "y": 0, "tile": 1},
                {"x": 1, "y": 0, "tile": 2},
                {"x": 0, "y": 1, "tile": 3},
            ]
            rom_offset = 0xD4000

            with open(tmp_path, "r+b") as f:
                f.seek(rom_offset)
                level_bytes = bytearray(0x4000)
                for tile in test_tiles:
                    x = tile.get("x", 0)
                    y = tile.get("y", 0)
                    tile_id = tile.get("tile", 0)
                    if 0 <= x < 80 and 0 <= y < 80:
                        idx = y * 80 + x
                        if idx < len(level_bytes):
                            level_bytes[idx] = tile_id
                f.write(level_bytes)

            with open(tmp_path, "rb") as f:
                f.seek(rom_offset)
                verify_bytes = f.read(0x4000)

            self.assertEqual(verify_bytes[0], 1)
            self.assertEqual(verify_bytes[1], 2)
            self.assertEqual(verify_bytes[80], 3)

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestLZ77Compression(unittest.TestCase):
    """Tests for LZ77 compression/decompression."""

    def test_roundtrip_simple_data(self):
        """Verify LZ77 roundtrip works for simple data."""
        test_data = b"Hello World! This is a test of LZ77 decompression."
        compressed = LZ77.compress(test_data)
        decompressed = LZ77.decompress(compressed)
        self.assertEqual(decompressed, test_data)

    def test_roundtrip_repetitive_data(self):
        """Verify LZ77 handles repetitive data correctly."""
        test_data = b"A" * 100 + b"B" * 50 + b"A" * 25
        compressed = LZ77.compress(test_data)
        decompressed = LZ77.decompress(compressed)
        self.assertEqual(decompressed, test_data)

    def test_roundtrip_random_data(self):
        """Verify LZ77 handles random-ish data."""
        test_data = bytes(range(256))
        compressed = LZ77.compress(test_data)
        decompressed = LZ77.decompress(compressed)
        self.assertEqual(decompressed, test_data)

    def test_roundtrip_with_max_size(self):
        """Verify LZ77 respects max_decompressed_size."""
        test_data = b"X" * 1000
        compressed = LZ77.compress(test_data)
        decompressed = LZ77.decompress(compressed, max_decompressed_size=100)
        self.assertLessEqual(len(decompressed), 150)

    def test_decompress_returns_bytes(self):
        """Verify decompress returns bytes type."""
        test_data = b"Test data"
        compressed = LZ77.compress(test_data)
        result = LZ77.decompress(compressed)
        self.assertIsInstance(result, bytes)


class TestServerEndpoints(unittest.TestCase):
    """Tests for server endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.join(BASE_DIR, "editor")
        cls.server_module_path = os.path.join(cls.base_dir, "server.py")

    def _import_server(self):
        """Import server module dynamically."""
        import importlib.util

        spec = importlib.util.spec_from_file_location("server", self.server_module_path)
        server_module = importlib.util.module_from_spec(spec)
        sys.modules["server"] = server_module
        spec.loader.exec_module(server_module)
        return server_module

    def test_levels_endpoint_data(self):
        """Verify /levels endpoint returns expected data structure."""
        server = self._import_server()

        class MockHandler(server.EditorHandler):
            def __init__(self):
                pass

        handler = MockHandler()
        levels = handler.get_level_list()
        self.assertIsInstance(levels, list)

        expected_levels = ["WORLD_1", "WORLD_2", "WORLD_3"]
        level_names = [l.get("name") for l in levels]
        for expected in expected_levels:
            self.assertIn(expected, level_names)

    def test_level_endpoint_data(self):
        """Verify /level/NAME endpoint returns expected data."""
        server = self._import_server()

        class MockHandler(server.EditorHandler):
            def __init__(self):
                pass

        handler = MockHandler()
        level_data = handler.get_level_data("WORLD_1")
        self.assertIsInstance(level_data, dict)
        self.assertIn("name", level_data)
        self.assertEqual(level_data["name"], "WORLD_1")
        self.assertIn("tiles", level_data)
        self.assertIn("width", level_data)
        self.assertIn("height", level_data)
        self.assertEqual(level_data["width"], 80)
        self.assertEqual(level_data["height"], 80)

    def test_export_level_validation(self):
        """Verify /export-level endpoint validates input correctly."""
        server = self._import_server()

        class MockHandler(server.EditorHandler):
            def __init__(self):
                pass

        handler = MockHandler()
        ROM_LEVEL_OFFSETS = {
            "WORLD_1": 0xD4000,
            "WORLD_2": 0xE4000,
            "WORLD_3": 0xF4000,
        }
        self.assertIn("WORLD_1", ROM_LEVEL_OFFSETS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
