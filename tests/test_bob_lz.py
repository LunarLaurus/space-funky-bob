"""Tests for bob_lz.py - LZ77 decompression"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from bob_lz import bob_lz_decompress, bob_lz_decompress_exploratory


class TestBobLZDecompress:
    """Test cases for bob_lz_decompress function"""
    
    def test_literal_bytes_simple(self):
        """Test simple literal byte decompression"""
        compressed = bytes([0x00, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48])
        expected = b"ABCDEFGH"
        result, consumed = bob_lz_decompress(compressed, 8)
        
        assert result == expected
        assert consumed == 9
    
    def test_literal_bytes_partial(self):
        """Test decompression with fewer input bytes than expected output"""
        compressed = bytes([0x00, 0x41, 0x42, 0x43])
        expected = b"ABCD"
        result, consumed = bob_lz_decompress(compressed, 8)
        
        assert result == expected
        assert consumed == 4
    
    def test_overlapping_copy(self):
        """Test overlapping copy (LZ77 backreference)"""
        # Create "ABC" then copy dist=3, len=8 to get "ABCABCAB"
        compressed = bytes([
            0x10,  # chunk header with backref
            0x41, 0x42, 0x43,  # 3 literals: "ABC"
            0x03, 0x28  # backref: dist=3, len=8
        ])
        expected = b"ABCABCAB"
        result, consumed = bob_lz_decompress(compressed, 8)
        
        assert result == expected
    
    def test_zero_distance_error(self):
        """Test that zero distance raises ValueError"""
        compressed = bytes([0x80, 0x00, 0x00])
        
        with pytest.raises(ValueError) as exc_info:
            bob_lz_decompress(compressed, 8)
        
        assert "invalid distance 0" in str(exc_info.value)
    
    def test_distance_too_large_error(self):
        """Test that distance > output size raises ValueError"""
        compressed = bytes([0x40, 0x41, 0xFF, 0x07])  # "A" + backref(dist=2047, len=3)
        
        with pytest.raises(ValueError) as exc_info:
            bob_lz_decompress(compressed, 8)
        
        assert "invalid distance" in str(exc_info.value).lower()
    
    def test_exploratory_mode_success(self):
        """Test exploratory decompression mode"""
        compressed = bytes([0x00, 0x48, 0x45, 0x4C, 0x4C, 0x4F, 0x20, 0x42, 0x4F])
        result, consumed, error = bob_lz_decompress_exploratory(compressed)
        
        assert error is None
        assert result == b"HELLO BO"
        assert consumed == 9
    
    def test_multiple_chunks(self):
        """Test multiple chunks in sequence"""
        # Two chunks: first with 4 literals, second with 4 literals
        compressed = bytes([
            0x00, 0x41, 0x42, 0x43, 0x44,  # chunk 1: 4 literals
            0x00, 0x45, 0x46, 0x47, 0x48,  # chunk 2: 4 literals
        ])
        expected = b"ABCDEFGH"
        result, consumed = bob_lz_decompress(compressed, 8)
        
        assert result == expected
    
    def test_empty_input(self):
        """Test with minimal input"""
        compressed = bytes([0x00])  # Just header, no literals
        result, consumed = bob_lz_decompress(compressed, 8)
        
        assert result == b""
        assert consumed == 1


class TestBobLZEdgeCases:
    """Edge case tests for LZ77 decompression"""
    
    def test_truncated_input(self):
        """Test handling of truncated input"""
        compressed = bytes([0x80])  # Expects backref but no data
        
        with pytest.raises(ValueError) as exc_info:
            bob_lz_decompress(compressed, 8)
        
        assert "distance/length expects two bytes" in str(exc_info.value)
    
    def test_exact_size_match(self):
        """Test when compressed data exactly matches expected size"""
        compressed = bytes([0x00, 0x41, 0x42])
        result, consumed = bob_lz_decompress(compressed, 2)
        
        assert result == b"AB"
        assert consumed == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
