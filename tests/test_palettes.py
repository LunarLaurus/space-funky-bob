"""Tests for palette functions (BETA-003)"""
import pytest
import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from bob_graphics import (
    extract_palette,
    save_palette,
    load_palette,
    find_palette_in_data,
    snes_color_to_rgb
)


class TestSNESColorConversion:
    """Test SNES RGB555 to RGB888 conversion."""

    def test_snes_color_black(self):
        """Should convert black (0) correctly."""
        result = snes_color_to_rgb(0x0000)
        assert result == (0, 0, 0)

    def test_snes_color_white(self):
        """Should convert white (0x7FFF) correctly."""
        result = snes_color_to_rgb(0x7FFF)
        assert result == (255, 255, 255)

    def test_snes_color_red(self):
        """Should convert pure red correctly."""
        result = snes_color_to_rgb(0x001F)
        assert result == (255, 0, 0)

    def test_snes_color_green(self):
        """Should convert pure green correctly."""
        result = snes_color_to_rgb(0x03E0)
        assert result == (0, 255, 0)

    def test_snes_color_blue(self):
        """Should convert pure blue correctly."""
        result = snes_color_to_rgb(0x7C00)
        assert result == (0, 0, 255)


class TestPaletteExtraction:
    """Test palette extraction from ROM data."""

    def test_extract_palette_basic(self):
        """Should extract basic palette."""
        # Create test palette data (4 colors, RGB555)
        # Black, Red, Green, Blue
        data = bytes([
            0x00, 0x00,  # Black
            0x1F, 0x00,  # Red
            0xE0, 0x03,  # Green
            0x00, 0x7C,  # Blue
        ])
        
        palette = extract_palette(data, 0, 4)
        
        assert len(palette) == 4
        assert palette[0] == (0, 0, 0)
        assert palette[1][0] > 200  # Red
        assert palette[2][1] > 200  # Green
        assert palette[3][2] > 200  # Blue

    def test_extract_palette_offset(self):
        """Should extract palette at offset."""
        data = bytes([0x00] * 16 + [0x00, 0x00] * 4)  # Palette at offset 16
        palette = extract_palette(data, 16, 4)
        assert len(palette) == 4

    def test_extract_palette_truncated(self):
        """Should handle truncated palette data."""
        data = bytes([0x00, 0x00, 0x1F, 0x00])  # Only 2 colors
        palette = extract_palette(data, 0, 4)
        assert len(palette) == 2

    def test_extract_palette_empty(self):
        """Should handle empty data."""
        palette = extract_palette(b'', 0, 4)
        assert len(palette) == 0


class TestPaletteSaveLoad:
    """Test palette save/load functionality."""

    def test_save_palette(self, tmp_path):
        """Should save palette to JSON."""
        palette = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        output_file = tmp_path / 'palette.json'
        
        save_palette(palette, str(output_file))
        
        # Verify file content
        with open(output_file) as f:
            data = json.load(f)
        
        assert data['num_colors'] == 3
        assert data['colors'][0] == {'r': 255, 'g': 0, 'b': 0}

    def test_load_palette(self, tmp_path):
        """Should load palette from JSON."""
        data = {
            'num_colors': 3,
            'colors': [
                {'r': 255, 'g': 0, 'b': 0},
                {'r': 0, 'g': 255, 'b': 0},
                {'r': 0, 'g': 0, 'b': 255}
            ]
        }
        
        input_file = tmp_path / 'palette.json'
        with open(input_file, 'w') as f:
            json.dump(data, f)
        
        palette = load_palette(str(input_file))
        
        assert len(palette) == 3
        assert palette[0] == (255, 0, 0)
        assert palette[1] == (0, 255, 0)
        assert palette[2] == (0, 0, 255)

    def test_save_load_roundtrip(self, tmp_path):
        """Should save and load back to same palette."""
        original = [(i, i*2, 255-i) for i in range(16)]
        output_file = tmp_path / 'palette.json'
        
        save_palette(original, str(output_file))
        loaded = load_palette(str(output_file))
        
        assert loaded == original


class TestFindPaletteInData:
    """Test palette detection in data."""

    def test_find_palette_basic(self):
        """Should find palette in data."""
        # Create data with embedded palette
        data = bytes([0x00] * 100 + [0x00, 0x00] * 16 + [0x00] * 100)
        offsets = find_palette_in_data(data, 16)
        assert 100 in offsets

    def test_find_palette_none(self):
        """Should return empty list when no palette found."""
        # Data with high bit set (not palette-like)
        data = bytes([0xFF] * 100)
        offsets = find_palette_in_data(data, 16)
        assert len(offsets) == 0

    def test_find_palette_multiple(self):
        """Should find multiple palettes."""
        # Create data with two palettes
        data = bytes([0x00, 0x00] * 16 + [0xFF] * 32 + [0x00, 0x00] * 16)
        offsets = find_palette_in_data(data, 16)
        assert len(offsets) >= 1
        assert 0 in offsets


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
