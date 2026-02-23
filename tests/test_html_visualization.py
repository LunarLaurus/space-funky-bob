"""Tests for enhanced HTML ROM map visualization (BETA-004)"""
import pytest
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))


class TestHTMLVisualizationExists:
    """Test that HTML visualization function exists."""

    def test_generate_html_function_exists(self):
        """generate_html_visualization should exist."""
        from bob_map import generate_html_visualization
        assert callable(generate_html_visualization)


class TestHTMLEnhancedFeatures:
    """Test enhanced HTML features."""

    def test_html_has_filter_function(self):
        """HTML should have filter function."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100, 
                    'start_hex': '0x000000', 'end_hex': '0x000064', 
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            f.flush()
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert 'function filterRegions' in html

    def test_html_has_search_function(self):
        """HTML should have search function."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100,
                    'start_hex': '0x000000', 'end_hex': '0x000064',
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert 'function searchRegions' in html

    def test_html_has_search_box(self):
        """HTML should have search input."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100,
                    'start_hex': '0x000000', 'end_hex': '0x000064',
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert 'id="searchBox"' in html

    def test_html_has_region_count(self):
        """HTML should have region count display."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100,
                    'start_hex': '0x000000', 'end_hex': '0x000064',
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert 'id="regionCount"' in html


class TestHTMLInteractiveLegend:
    """Test interactive legend."""

    def test_legend_has_onclick_handlers(self):
        """Legend items should have onclick handlers."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100,
                    'start_hex': '0x000000', 'end_hex': '0x000064',
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert 'onclick="filterRegions' in html

    def test_legend_has_data_types(self):
        """Legend should have data-type attributes."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100,
                    'start_hex': '0x000000', 'end_hex': '0x000064',
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert 'data-type="all"' in html
        assert 'data-type="code"' in html
        assert 'data-type="compressed"' in html


class TestHTMLCSSStyles:
    """Test CSS styles for enhanced features."""

    def test_css_has_legend_active(self):
        """CSS should have .legend-item.active style."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100,
                    'start_hex': '0x000000', 'end_hex': '0x000064',
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert '.legend-item.active' in html

    def test_css_has_controls(self):
        """CSS should have .controls style."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100,
                    'start_hex': '0x000000', 'end_hex': '0x000064',
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert '.controls' in html

    def test_css_has_searchbox(self):
        """CSS should have #searchBox style."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100,
                    'start_hex': '0x000000', 'end_hex': '0x000064',
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert '#searchBox' in html


class TestHTMLTypeNames:
    """Test type name mapping."""

    def test_html_has_type_names(self):
        """HTML should have typeNames mapping."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100,
                    'start_hex': '0x000000', 'end_hex': '0x000064',
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert 'const typeNames' in html
        assert "'code': 'Code'" in html


class TestHTMLMatchesFilter:
    """Test filter matching logic."""

    def test_matches_filter_all(self):
        """Filter 'all' should match everything."""
        from bob_map import generate_html_visualization
        
        regions = [{'type': 'code', 'start': 0, 'end': 100, 'size': 100,
                    'start_hex': '0x000000', 'end_hex': '0x000064',
                    'size_hex': '0x64', 'confidence': 90}]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            generate_html_visualization(regions, 1000, f.name)
            temp_path = f.name
        
        with open(temp_path) as rf:
            html = rf.read()
        os.unlink(temp_path)
        
        assert 'function matchesFilter' in html
        assert "currentFilter === 'all'" in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
