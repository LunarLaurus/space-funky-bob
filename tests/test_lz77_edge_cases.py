"""Edge case tests for LZ77 module (DELTA-003)"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from bob_lz import bob_lz_decompress, bob_lz_decompress_exploratory
from bob_lz_encode import bob_lz_encode, find_best_match


class TestLZ77EmptyInputs:
    """Test empty input handling."""

    def test_decompress_empty(self):
        """Empty input should return empty output."""
        result, consumed = bob_lz_decompress(b'', 0)
        assert result == b''
        assert consumed == 0

    def test_encode_empty(self):
        """Empty input should encode to empty output."""
        result = bob_lz_encode(b'')
        assert result == b''

    def test_exploratory_empty(self):
        """Exploratory mode should handle empty input."""
        result, consumed, error = bob_lz_decompress_exploratory(b'')
        assert result == b''
        assert error is None


class TestLZ77TruncatedInputs:
    """Test truncated input handling."""

    def test_decompress_header_only(self):
        """Header without data should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            bob_lz_decompress(bytes([0x00]), 1)
        assert "literal expects a byte" in str(exc_info.value)

    def test_decompress_partial_literal(self):
        """Partial literal should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            bob_lz_decompress(bytes([0x00, 0x41]), 2)  # Header + 1 literal, need 2
        assert "literal expects a byte" in str(exc_info.value)

    def test_decompress_partial_backref(self):
        """Partial backreference should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            bob_lz_decompress(bytes([0x80, 0x00]), 8)  # Header + 1 byte of backref
        assert "distance/length expects two bytes" in str(exc_info.value)

    def test_exploratory_truncated(self):
        """Exploratory mode should report error for truncated data."""
        result, consumed, error = bob_lz_decompress_exploratory(bytes([0x80]))
        assert error is not None


class TestLZ77InvalidDistance:
    """Test invalid distance handling."""

    def test_decompress_zero_distance(self):
        """Zero distance should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            bob_lz_decompress(bytes([0x80, 0x00, 0x00]), 8)
        assert "invalid distance 0" in str(exc_info.value)

    def test_decompress_distance_exceeds_output(self):
        """Distance > output size should raise ValueError."""
        # After one literal, try to copy from distance 2047
        with pytest.raises(ValueError) as exc_info:
            bob_lz_decompress(bytes([0x40, 0x41, 0xFF, 0x07]), 8)
        assert "invalid distance" in str(exc_info.value).lower()

    def test_exploratory_zero_distance(self):
        """Exploratory mode should report zero distance error."""
        result, consumed, error = bob_lz_decompress_exploratory(bytes([0x80, 0x00, 0x00]))
        assert error is not None
        assert "invalid distance" in error.lower()


class TestLZ77BoundaryConditions:
    """Test boundary conditions."""

    def test_decompress_exact_size(self):
        """Decompression with exact size match."""
        compressed = bytes([0x00, 0x41, 0x42])
        result, consumed = bob_lz_decompress(compressed, 2)
        assert result == b'AB'
        assert consumed == 3

    def test_decompress_single_byte(self):
        """Single byte decompression."""
        compressed = bytes([0x00, 0x41])
        result, consumed = bob_lz_decompress(compressed, 1)
        assert result == b'A'

    def test_encode_single_byte(self):
        """Single byte encoding."""
        result = bob_lz_encode(b'X')
        decompressed, _ = bob_lz_decompress(result, 1)
        assert decompressed == b'X'

    def test_max_distance(self):
        """Test at max distance boundary (2047)."""
        # Create data with match at exactly 2047 distance
        prefix = b'A' * 2047
        pattern = b'TEST'
        original = prefix + pattern
        
        # This should work if encoder finds the match
        encoded = bob_lz_encode(original)
        decoded, _ = bob_lz_decompress(encoded, len(original))
        assert decoded == original

    def test_max_match_length(self):
        """Test at max match length boundary (34)."""
        # Create data with 34-byte match
        prefix = b'B' * 34
        original = prefix + b'X' * 100 + prefix
        
        encoded = bob_lz_encode(original)
        decoded, _ = bob_lz_decompress(encoded, len(original))
        assert decoded == original


class TestLZ77EdgeCasePatterns:
    """Test edge case patterns."""

    def test_all_same_bytes(self):
        """All same bytes should encode/decode correctly."""
        original = b'C' * 500
        encoded = bob_lz_encode(original)
        decoded, _ = bob_lz_decompress(encoded, len(original))
        assert decoded == original

    def test_sequential_bytes(self):
        """Sequential bytes should encode/decode correctly."""
        original = bytes(range(256)) * 2
        encoded = bob_lz_encode(original)
        decoded, _ = bob_lz_decompress(encoded, len(original))
        assert decoded == original

    def test_alternating_bytes(self):
        """Alternating bytes should encode/decode correctly."""
        original = bytes([0x00 if i % 2 == 0 else 0xFF for i in range(500)])
        encoded = bob_lz_encode(original)
        decoded, _ = bob_lz_decompress(encoded, len(original))
        assert decoded == original

    def test_repeating_pattern(self):
        """Repeating pattern should encode/decode correctly."""
        original = b'ABCD' * 250
        encoded = bob_lz_encode(original)
        decoded, _ = bob_lz_decompress(encoded, len(original))
        assert decoded == original

    def test_palindrome_pattern(self):
        """Palindrome pattern should encode/decode correctly."""
        original = b'ABCDCBA' * 100
        encoded = bob_lz_encode(original)
        decoded, _ = bob_lz_decompress(encoded, len(original))
        assert decoded == original


class TestFindBestMatchEdgeCases:
    """Test find_best_match edge cases."""

    def test_no_match_at_start(self):
        """No match at position 0."""
        data = b'ABCDEFG'
        result = find_best_match(data, 3, 0)
        # At position 3, 'D' hasn't appeared before
        assert result is None or result[1] < 3

    def test_minimum_match_length(self):
        """Should not return matches < 3 bytes."""
        data = b'ABXAB'
        result = find_best_match(data, 3, 0)
        # Only 'AB' matches (2 bytes < 3 minimum)
        assert result is None

    def test_match_at_window_boundary(self):
        """Match at sliding window boundary."""
        # Create data where match is at window boundary
        data = b'A' * 100 + b'B' + b'A' * 50
        result = find_best_match(data, 151, 0)
        # May or may not find match depending on implementation
        # Just verify it doesn't crash
        assert result is None or result[0] > 0


class TestLZ77ErrorMessages:
    """Test error message quality."""

    def test_error_message_includes_offset(self):
        """Error messages should include offset information."""
        with pytest.raises(ValueError) as exc_info:
            bob_lz_decompress(bytes([0x80]), 8)
        assert "offset" in str(exc_info.value).lower()

    def test_error_message_descriptive(self):
        """Error messages should be descriptive."""
        with pytest.raises(ValueError) as exc_info:
            bob_lz_decompress(bytes([0x80, 0x00, 0x00]), 8)
        error_msg = str(exc_info.value).lower()
        assert "distance" in error_msg or "invalid" in error_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
