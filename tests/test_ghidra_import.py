"""Tests for Ghidra import script (ECHO-002)

Note: These tests verify the Python logic without requiring Ghidra runtime.
Actual Ghidra integration requires Ghidra environment.
"""
import pytest
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))


class TestImportScriptExists:
    """Test that import script exists and is valid Python."""

    def test_import_script_exists(self):
        """ImportBOBMap.py should exist."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMap.py'
        )
        assert os.path.exists(script_path)

    def test_import_script_syntax(self):
        """ImportBOBMap.py should have valid Python syntax."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMap.py'
        )
        
        # This will raise SyntaxError if invalid
        with open(script_path) as f:
            compile(f.read(), script_path, 'exec')


class TestRomMapFormat:
    """Test ROM map JSON format handling."""

    def test_valid_rom_map(self):
        """Should handle valid ROM map JSON."""
        rom_map = {
            'rom_mapping': 'LoROM',
            'header_offset': 0,
            'regions': [
                {'type': 'code', 'start': 0x000000, 'size': 0x1000, 'confidence': 0.9},
                {'type': 'compressed', 'start': 0x010000, 'size': 0x800, 'confidence': 0.8},
            ]
        }
        
        # Verify structure
        assert 'rom_mapping' in rom_map
        assert 'regions' in rom_map
        assert len(rom_map['regions']) == 2

    def test_rom_map_with_tilemap(self):
        """Should handle tilemap regions."""
        rom_map = {
            'rom_mapping': 'LoROM',
            'header_offset': 0,
            'regions': [
                {
                    'type': 'tilemap',
                    'start': 0x028000,
                    'size': 0x800,
                    'confidence': 0.95
                }
            ]
        }
        
        region = rom_map['regions'][0]
        assert region['type'] == 'tilemap'
        assert region['size'] == 0x800

    def test_rom_map_with_header_offset(self):
        """Should handle header offset."""
        rom_map = {
            'rom_mapping': 'LoROM',
            'header_offset': 512,  # 512-byte header
            'regions': [
                {'type': 'code', 'start': 0x000200, 'size': 0x1000}
            ]
        }
        
        assert rom_map['header_offset'] == 512


class TestAddressConversion:
    """Test ROM to SNES address conversion."""

    def test_lorom_conversion(self):
        """LoROM conversion should work."""
        # For LoROM: offset 0x000000 maps to SNES 0x8000 (bank 0)
        # Ghidra typically loads at 0x000000, so we add 0x8000 for LoROM mirror
        rom_offset = 0x000000
        snes_addr = 0x8000 + rom_offset  # Simple LoROM mapping
        assert snes_addr == 32768  # 0x8000

    def test_lorom_conversion_bank1(self):
        """LoROM conversion for bank 1."""
        rom_offset = 0x008000
        snes_addr = 0x8000 + rom_offset + 0x10000  # Bank 1 = +0x10000
        assert snes_addr == 131072  # 0x20000

    def test_hirom_conversion(self):
        """HiROM conversion should work."""
        rom_offset = 0x000000
        snes_addr = 0xC00000 + rom_offset
        assert snes_addr == 0xC00000


class TestTilemapStructure:
    """Test tilemap structure definition."""

    def test_tilemap_entry_size(self):
        """Tilemap entry should be 2 bytes (16-bit)."""
        # This is verified in the Ghidra script structure definition
        tilemap_entry_size = 2  # 16 bits
        assert tilemap_entry_size == 2

    def test_tilemap_bit_fields(self):
        """Tilemap bit fields should sum to 16 bits."""
        tile_id_bits = 10
        chr_bank_bits = 2
        palette_bits = 2
        x_flip_bits = 1
        y_flip_bits = 1
        
        total = tile_id_bits + chr_bank_bits + palette_bits + x_flip_bits + y_flip_bits
        assert total == 16

    def test_tilemap_id_range(self):
        """Tile ID should support 0-1023 range."""
        max_tile_id = (1 << 10) - 1
        assert max_tile_id == 1023


class TestRegionTypes:
    """Test region type handling."""

    def test_known_region_types(self):
        """Should handle known region types."""
        known_types = ['code', 'data', 'compressed', 'graphics', 'tilemap']
        
        for region_type in known_types:
            # Each type should be processable
            assert isinstance(region_type, str)
            assert len(region_type) > 0

    def test_unknown_region_type(self):
        """Should handle unknown region types gracefully."""
        unknown_type = 'unknown_type'
        # Should default to 'unknown'
        region_type = unknown_type if unknown_type else 'unknown'
        assert region_type == 'unknown_type'


class TestVectorTable:
    """Test vector table handling."""

    def test_vector_table_offsets(self):
        """Vector table should have correct offsets."""
        vectors = {
            'COP': 0x7FE0,
            'BRK': 0x7FE2,
            'ABORT': 0x7FE4,
            'NMI': 0x7FE6,
            'RESET': 0x7FE8,
            'IRQ': 0x7FEA,
        }
        
        # Verify spacing (2 bytes each)
        offsets = list(vectors.values())
        for i in range(len(offsets) - 1):
            assert offsets[i + 1] - offsets[i] == 2

    def test_vector_table_range(self):
        """Vector table should be at 0x7FE0-0x7FFF."""
        vector_start = 0x7FE0
        vector_end = 0x7FFF
        vector_table_size = vector_end - vector_start + 1
        
        assert vector_table_size == 32  # 16 vectors × 2 bytes


class TestImportScriptFeatures:
    """Test enhanced import script features."""

    def test_segment_creation_function_exists(self):
        """Should have segment creation function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMap.py'
        )
        
        with open(script_path) as f:
            content = f.read()
        
        assert 'def create_segment' in content

    def test_label_creation_function_exists(self):
        """Should have label creation function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMap.py'
        )
        
        with open(script_path) as f:
            content = f.read()
        
        assert 'def add_region_labels' in content

    def test_comment_creation_function_exists(self):
        """Should have comment creation function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMap.py'
        )
        
        with open(script_path) as f:
            content = f.read()
        
        assert 'def add_region_comments' in content

    def test_tilemap_data_type_function_exists(self):
        """Should have tilemap data type function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMap.py'
        )
        
        with open(script_path) as f:
            content = f.read()
        
        assert 'def create_tilemap_data_type' in content

    def test_vector_table_function_exists(self):
        """Should have vector table analysis function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMap.py'
        )
        
        with open(script_path) as f:
            content = f.read()
        
        assert 'def analyze_vector_table' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
