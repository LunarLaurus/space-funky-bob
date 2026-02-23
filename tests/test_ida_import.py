"""Tests for IDA Pro import script (ECHO-003)

Note: These tests verify the Python script structure without requiring IDA runtime.
Actual IDA integration requires IDA Pro environment.
"""
import pytest
import sys
import os
import ast

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))


class TestIDAScriptExists:
    """Test that IDA import script exists."""

    def test_ida_script_exists(self):
        """ImportBOBMapIDA.py should exist."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        assert os.path.exists(script_path)

    def test_ida_script_syntax(self):
        """ImportBOBMapIDA.py should have valid Python syntax."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        # This will raise SyntaxError if invalid
        ast.parse(source)


class TestIDAScriptImports:
    """Test IDA script imports."""

    def test_has_ida_imports(self):
        """Should have IDA module imports."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'import idaapi' in source
        assert 'import ida_segment' in source
        assert 'import ida_bytes' in source
        assert 'import ida_struct' in source
        assert 'import ida_name' in source
        assert 'import json' in source


class TestIDAScriptFunctions:
    """Test IDA script functions."""

    def test_has_import_function(self):
        """Should have import_rom_map function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'def import_rom_map' in source

    def test_has_segment_function(self):
        """Should have create_segment function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'def create_segment' in source

    def test_has_bookmark_function(self):
        """Should have add_bookmark function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'def add_bookmark' in source

    def test_has_comment_function(self):
        """Should have add_comment function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'def add_comment' in source

    def test_has_tilemap_type_function(self):
        """Should have create_tilemap_entry_type function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'def create_tilemap_entry_type' in source

    def test_has_vector_table_function(self):
        """Should have analyze_vector_table function."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'def analyze_vector_table' in source


class TestIDAScriptFeatures:
    """Test IDA script features."""

    def test_has_error_handling(self):
        """Should have error handling."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'try:' in source
        assert 'except' in source

    def test_has_progress_reporting(self):
        """Should have progress reporting."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'print(' in source
        assert 'Processed' in source

    def test_has_summary_output(self):
        """Should have summary output."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'Import Complete' in source
        assert 'Segments created' in source


class TestIDAScriptDocumentation:
    """Test IDA script documentation."""

    def test_has_module_docstring(self):
        """Should have module docstring."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        tree = ast.parse(source)
        assert ast.get_docstring(tree) is not None

    def test_docstring_has_usage(self):
        """Docstring should have usage instructions."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'Usage:' in source
        assert 'IDA Pro' in source

    def test_docstring_has_features(self):
        """Docstring should list features."""
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(script_path) as f:
            source = f.read()
        
        assert 'segments' in source.lower()
        assert 'bookmarks' in source.lower()
        assert 'comments' in source.lower()


class TestIDAFeatureParity:
    """Test feature parity with Ghidra script."""

    def test_both_scripts_exist(self):
        """Both Ghidra and IDA scripts should exist."""
        ghidra_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMap.py'
        )
        ida_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        assert os.path.exists(ghidra_path)
        assert os.path.exists(ida_path)

    def test_both_have_tilemap_type(self):
        """Both scripts should define tilemap type."""
        ida_path = os.path.join(
            os.path.dirname(__file__), '..', 'toolkit', 'ImportBOBMapIDA.py'
        )
        
        with open(ida_path) as f:
            ida_source = f.read()
        
        assert 'TilemapEntry' in ida_source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
