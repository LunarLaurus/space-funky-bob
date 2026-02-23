"""Tests for SNES graphics renderer (BETA-002)"""
import pytest
import sys
import os
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from bob_graphics import (
    render_snes_tile_2bpp,
    render_snes_tile_4bpp,
    render_snes_tile_8bpp,
    SNESGraphicsRenderer,
    get_palette_2bpp_color,
    get_palette_4bpp,
    get_palette_8bpp_grayscale,
    tile_to_image
)


class Test2bppRendering:
    """Test 2bpp tile rendering."""

    def test_render_2bpp_tile_basic(self):
        """Should render basic 2bpp tile."""
        # Create simple 2bpp tile data (16 bytes for 8x8)
        data = bytes(range(16))
        result = render_snes_tile_2bpp(data, 0)
        
        assert result is not None
        assert len(result) == 64  # 8x8 pixels

    def test_render_2bpp_tile_offset(self):
        """Should render 2bpp tile at offset."""
        data = bytes(range(32))  # 2 tiles worth
        result = render_snes_tile_2bpp(data, 16)
        
        assert result is not None
        assert len(result) == 64

    def test_render_2bpp_insufficient_data(self):
        """Should return None for insufficient data."""
        data = bytes(range(8))  # Only 8 bytes, need 16
        result = render_snes_tile_2bpp(data, 0)
        
        assert result is None

    def test_render_2bpp_pixel_values(self):
        """Should produce correct pixel values."""
        # Create tile where bitplanes produce known values
        # Row 0: b0=0x00, b1=0x00 → all pixels = 0
        data = bytes([0x00] * 16)
        result = render_snes_tile_2bpp(data, 0)
        
        assert all(p == 0 for p in result)


class Test4bppRendering:
    """Test 4bpp tile rendering."""

    def test_render_4bpp_tile_basic(self):
        """Should render basic 4bpp tile."""
        data = bytes(range(32))  # 32 bytes for 8x8 4bpp
        result = render_snes_tile_4bpp(data, 0)
        
        assert result is not None
        assert len(result) == 64

    def test_render_4bpp_insufficient_data(self):
        """Should return None for insufficient data."""
        data = bytes(range(16))  # Only 16 bytes, need 32
        result = render_snes_tile_4bpp(data, 0)
        
        assert result is None


class Test8bppRendering:
    """Test 8bpp tile rendering."""

    def test_render_8bpp_tile_basic(self):
        """Should render basic 8bpp tile."""
        data = bytes(range(64))  # 64 bytes for 8x8 8bpp
        result = render_snes_tile_8bpp(data, 0)
        
        assert result is not None
        assert len(result) == 64

    def test_render_8bpp_pixel_values(self):
        """Should produce correct pixel values (direct byte mapping)."""
        data = bytes(range(64))
        result = render_snes_tile_8bpp(data, 0)
        
        assert result == list(range(64))

    def test_render_8bpp_insufficient_data(self):
        """Should return None for insufficient data."""
        data = bytes(range(32))  # Only 32 bytes, need 64
        result = render_snes_tile_8bpp(data, 0)
        
        assert result is None


class TestSNESGraphicsRenderer:
    """Test unified SNESGraphicsRenderer class."""

    def test_renderer_init_2bpp(self):
        """Should initialize with 2bpp format."""
        renderer = SNESGraphicsRenderer(format='2bpp')
        assert renderer.format == '2bpp'
        assert renderer.palette is not None
        assert len(renderer.palette) == 16

    def test_renderer_init_4bpp(self):
        """Should initialize with 4bpp format."""
        renderer = SNESGraphicsRenderer(format='4bpp')
        assert renderer.format == '4bpp'
        assert renderer.palette is not None
        assert len(renderer.palette) == 16

    def test_renderer_init_8bpp(self):
        """Should initialize with 8bpp format."""
        renderer = SNESGraphicsRenderer(format='8bpp')
        assert renderer.format == '8bpp'
        assert renderer.palette is not None
        assert len(renderer.palette) == 256

    def test_renderer_render_tile_2bpp(self):
        """Should render tile in 2bpp mode."""
        renderer = SNESGraphicsRenderer(format='2bpp')
        data = bytes(range(16))
        result = renderer.render_tile(data)
        
        assert result is not None
        assert len(result) == 64

    def test_renderer_render_tile_4bpp(self):
        """Should render tile in 4bpp mode."""
        renderer = SNESGraphicsRenderer(format='4bpp')
        data = bytes(range(32))
        result = renderer.render_tile(data)
        
        assert result is not None
        assert len(result) == 64

    def test_renderer_render_tile_8bpp(self):
        """Should render tile in 8bpp mode."""
        renderer = SNESGraphicsRenderer(format='8bpp')
        data = bytes(range(64))
        result = renderer.render_tile(data)
        
        assert result is not None
        assert len(result) == 64

    def test_renderer_render_tiles_sheet(self):
        """Should render multiple tiles to sheet."""
        renderer = SNESGraphicsRenderer(format='2bpp')
        data = bytes(range(16 * 4))  # 4 tiles
        result = renderer.render_tiles(data, count=4, cols=2)
        
        assert result is not None
        # Should be PIL Image
        assert hasattr(result, 'save')

    def test_renderer_render_to_file(self, tmp_path):
        """Should render and save to file."""
        renderer = SNESGraphicsRenderer(format='2bpp')
        data = bytes(range(16))
        output_path = str(tmp_path / 'test.png')
        
        result_path = renderer.render_to_file(data, output_path)
        
        assert result_path == output_path
        assert tmp_path.joinpath('test.png').exists()


class TestPalettes:
    """Test palette functions."""

    def test_palette_2bpp_color_size(self):
        """2bpp color palette should have 16 colors."""
        palette = get_palette_2bpp_color()
        assert len(palette) == 16
        assert all(len(c) == 3 for c in palette)

    def test_palette_4bpp_size(self):
        """4bpp palette should have 16 colors."""
        palette = get_palette_4bpp()
        assert len(palette) == 16

    def test_palette_8bpp_grayscale_size(self):
        """8bpp grayscale palette should have 256 colors."""
        palette = get_palette_8bpp_grayscale()
        assert len(palette) == 256
        # Should be grayscale (R=G=B)
        assert all(c[0] == c[1] == c[2] for c in palette)


class TestTileToImage:
    """Test tile to image conversion."""

    def test_tile_to_image_basic(self):
        """Should convert tile to image."""
        tile_data = [0] * 64  # All black
        palette = [(0, 0, 0)] * 16
        result = tile_to_image(tile_data, 8, 8, palette)
        
        assert result is not None
        assert result.size == (8, 8)

    def test_tile_to_image_no_palette(self):
        """Should convert tile to grayscale without palette."""
        tile_data = list(range(64))
        result = tile_to_image(tile_data, 8, 8, None)
        
        assert result is not None
        assert result.size == (8, 8)

    def test_tile_to_image_wrong_size(self):
        """Should return None for wrong tile size."""
        tile_data = [0] * 32  # Too small for 8x8
        palette = [(0, 0, 0)] * 16
        result = tile_to_image(tile_data, 8, 8, palette)
        
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
