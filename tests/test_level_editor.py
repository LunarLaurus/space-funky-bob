"""Tests for level editor CLI (GAMMA-004)"""
import pytest
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from bob_level_editor import (
    load_rom,
    list_levels,
    view_tilemap,
    export_tilemap,
    import_tilemap,
    KNOWN_TILEMAPS
)


class TestKnownTilemaps:
    """Test known tilemap definitions."""

    def test_known_tilemaps_count(self):
        """Should have 10 known tilemaps."""
        assert len(KNOWN_TILEMAPS) == 10

    def test_known_tilemaps_format(self):
        """Each tilemap should have offset and name."""
        for tm in KNOWN_TILEMAPS:
            assert 'offset' in tm
            assert 'name' in tm
            assert isinstance(tm['offset'], int)
            assert isinstance(tm['name'], str)

    def test_known_tilemaps_offsets(self):
        """Tilemap offsets should be in valid ranges."""
        for tm in KNOWN_TILEMAPS:
            # Should be in ROM addressable range
            assert 0 <= tm['offset'] < 0x100000


class TestLoadRom:
    """Test ROM loading."""

    def test_load_rom_nonexistent(self, capsys):
        """Should handle nonexistent ROM file."""
        result = load_rom('/nonexistent/path/rom.sfc')
        assert result is None
        captured = capsys.readouterr()
        assert 'not found' in captured.out

    def test_load_rom_valid(self, tmp_path):
        """Should load valid ROM file."""
        rom_file = tmp_path / 'test.sfc'
        rom_data = bytes([0x00] * 1024)
        rom_file.write_bytes(rom_data)
        
        result = load_rom(str(rom_file))
        assert result == rom_data


class TestListLevels:
    """Test level listing functionality."""

    def test_list_levels_returns_list(self):
        """Should return a list."""
        rom_data = bytes([0x00] * 0x100000)
        result = list_levels(rom_data)
        assert isinstance(result, list)


class TestViewTilemap:
    """Test tilemap viewing."""

    def test_view_tilemap_invalid_index(self, capsys):
        """Should handle invalid index."""
        rom_data = bytes([0x00] * 0x100000)
        view_tilemap(rom_data, -1)
        captured = capsys.readouterr()
        assert 'Invalid' in captured.out

    def test_view_tilemap_beyond_rom(self, capsys):
        """Should handle tilemap beyond ROM size."""
        rom_data = bytes([0x00] * 0x1000)  # Very small ROM
        view_tilemap(rom_data, 0)
        captured = capsys.readouterr()
        assert 'beyond' in captured.out.lower()


class TestExportTilemap:
    """Test tilemap export."""

    def test_export_tilemap_invalid_index(self, capsys):
        """Should handle invalid index."""
        rom_data = bytes([0x00] * 0x100000)
        result = export_tilemap(rom_data, -1, '/tmp/test.bin')
        assert result is False

    def test_export_tilemap_json(self, tmp_path):
        """Should export to JSON format."""
        rom_data = bytes([0x00] * 0x100000)
        output_path = tmp_path / 'test.json'
        
        result = export_tilemap(rom_data, 0, str(output_path))
        
        assert result is True
        assert output_path.exists()
        
        with open(output_path) as f:
            data = json.load(f)
        
        assert 'tiles' in data
        assert 'offset' in data
        assert 'format' in data

    def test_export_tilemap_binary(self, tmp_path):
        """Should export to binary format."""
        rom_data = bytes([0x00] * 0x100000)
        output_path = tmp_path / 'test.bin'
        
        result = export_tilemap(rom_data, 0, str(output_path))
        
        assert result is True
        assert output_path.exists()
        assert output_path.stat().st_size == 0x800


class TestImportTilemap:
    """Test tilemap import."""

    def test_import_tilemap_invalid_index(self, capsys):
        """Should handle invalid index."""
        rom_data = bytes([0x00] * 0x100000)
        result = import_tilemap(rom_data, -1, '/tmp/test.bin')
        assert result is False

    def test_import_tilemap_nonexistent_file(self, capsys):
        """Should handle nonexistent input file."""
        rom_data = bytes([0x00] * 0x100000)
        result = import_tilemap(rom_data, 0, '/nonexistent/file.bin')
        assert result is False


class TestLevelEditorModule:
    """Test level editor module structure."""

    def test_module_exists(self):
        """bob_level_editor.py should exist."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'bob_level_editor.py'
        )
        assert os.path.exists(module_path)

    def test_module_syntax(self):
        """bob_level_editor.py should have valid Python syntax."""
        module_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'bob_level_editor.py'
        )
        
        with open(module_path) as f:
            compile(f.read(), module_path, 'exec')

    def test_main_function_exists(self):
        """Should have main function."""
        from bob_level_editor import main
        assert callable(main)


class TestCLICommands:
    """Test CLI command structure."""

    def test_cli_has_list_command(self):
        """Should support list command."""
        from bob_level_editor import list_levels
        assert callable(list_levels)

    def test_cli_has_view_command(self):
        """Should support view command."""
        from bob_level_editor import view_tilemap
        assert callable(view_tilemap)

    def test_cli_has_export_command(self):
        """Should support export command."""
        from bob_level_editor import export_tilemap
        assert callable(export_tilemap)

    def test_cli_has_import_command(self):
        """Should support import command."""
        from bob_level_editor import import_tilemap
        assert callable(import_tilemap)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
