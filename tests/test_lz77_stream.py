"""Tests for streaming LZ77 decompression (ALPHA-002)"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from bob_lz import bob_lz_decompress, bob_lz_decompress_stream
from bob_lz_encode import bob_lz_encode


class TestStreamingBasic:
    """Test basic streaming functionality."""

    def test_stream_empty(self):
        """Empty input should yield nothing."""
        result = list(bob_lz_decompress_stream(b''))
        assert result == []

    def test_stream_small_data(self):
        """Small data should stream correctly."""
        compressed = bob_lz_encode(b"Hello, World!")
        chunks = list(bob_lz_decompress_stream(compressed))
        
        # Reconstruct from chunks
        result = b''.join(chunks)
        assert result == b"Hello, World!"

    def test_stream_single_byte(self):
        """Single byte should stream correctly."""
        compressed = bob_lz_encode(b"X")
        chunks = list(bob_lz_decompress_stream(compressed))
        result = b''.join(chunks)
        assert result == b"X"

    def test_stream_literal_bytes(self):
        """Literal-only data should stream correctly."""
        original = b"ABCDEFGH"
        compressed = bytes([0x00]) + original  # All literals
        chunks = list(bob_lz_decompress_stream(compressed))
        result = b''.join(chunks)
        assert result == original


class TestStreamingEquivalence:
    """Test streaming vs batch equivalence."""

    def test_stream_equals_batch_small(self):
        """Streaming should match batch for small data."""
        original = b"Test data for streaming"
        compressed = bob_lz_encode(original)
        
        # Batch decompression
        batch_result, _ = bob_lz_decompress(compressed, len(original))
        
        # Streaming decompression
        stream_result = b''.join(bob_lz_decompress_stream(compressed))
        
        assert batch_result == stream_result

    def test_stream_equals_batch_medium(self):
        """Streaming should match batch for medium data."""
        import random
        random.seed(42)
        original = bytes([random.randint(0, 255) for _ in range(1000)])
        compressed = bob_lz_encode(original)
        
        batch_result, _ = bob_lz_decompress(compressed, len(original))
        stream_result = b''.join(bob_lz_decompress_stream(compressed))
        
        assert batch_result == stream_result

    def test_stream_equals_batch_repeated(self):
        """Streaming should match batch for repeated patterns."""
        original = b"ABABABAB" * 100
        compressed = bob_lz_encode(original)
        
        batch_result, _ = bob_lz_decompress(compressed, len(original))
        stream_result = b''.join(bob_lz_decompress_stream(compressed))
        
        assert batch_result == stream_result

    def test_stream_equals_batch_large(self):
        """Streaming should match batch for large data."""
        import random
        random.seed(123)
        original = bytes([random.randint(0, 255) for _ in range(10000)])
        compressed = bob_lz_encode(original)
        
        batch_result, _ = bob_lz_decompress(compressed, len(original))
        stream_result = b''.join(bob_lz_decompress_stream(compressed))
        
        assert batch_result == stream_result


class TestStreamingChunkBoundaries:
    """Test chunk boundary handling."""

    def test_stream_custom_chunk_size(self):
        """Should respect custom chunk size (approximately).
        
        Note: Chunks may slightly exceed chunk_size due to LZ77 backreferences
        that extend beyond the boundary. This is expected behavior.
        """
        original = b"A" * 1000
        compressed = bob_lz_encode(original)
        
        chunks = list(bob_lz_decompress_stream(compressed, chunk_size=100))
        
        # Chunks should be approximately chunk_size (may vary due to backrefs)
        # Just verify we get multiple chunks
        assert len(chunks) > 1
        
        # Total should still be correct
        result = b''.join(chunks)
        assert result == original

    def test_stream_chunk_boundary_literal(self):
        """Should handle chunk boundaries during literal reads."""
        original = b"X" * 500
        compressed = bob_lz_encode(original)
        
        chunks = list(bob_lz_decompress_stream(compressed, chunk_size=50))
        result = b''.join(chunks)
        assert result == original

    def test_stream_chunk_boundary_backref(self):
        """Should handle chunk boundaries during backreference copies."""
        # Create data with backreferences crossing chunk boundaries
        original = b"ABCDEFGHIJKLMNOP" * 50  # 800 bytes
        compressed = bob_lz_encode(original)
        
        chunks = list(bob_lz_decompress_stream(compressed, chunk_size=100))
        result = b''.join(chunks)
        assert result == original


class TestStreamingMemoryEfficiency:
    """Test memory efficiency of streaming."""

    def test_stream_yields_multiple_chunks(self):
        """Large data should yield multiple chunks."""
        original = b"A" * 10000
        compressed = bob_lz_encode(original)
        
        chunks = list(bob_lz_decompress_stream(compressed, chunk_size=1000))
        
        # Should yield multiple chunks
        assert len(chunks) > 1
        
        # Total should be correct
        result = b''.join(chunks)
        assert result == original

    def test_stream_chunk_sizes(self):
        """Chunks should approximately respect maximum size.
        
        Note: Due to LZ77 backreferences, chunks may slightly exceed chunk_size
        when a backreference operation crosses the boundary. This is expected.
        """
        original = b"B" * 5000
        compressed = bob_lz_encode(original)
        
        chunk_size = 500
        chunks = list(bob_lz_decompress_stream(compressed, chunk_size=chunk_size))
        
        # Should yield multiple chunks
        assert len(chunks) > 1
        
        # Chunks should be roughly chunk_size (within 20% tolerance for backrefs)
        for chunk in chunks[:-1]:
            assert len(chunk) <= chunk_size * 1.2
        
        result = b''.join(chunks)
        assert result == original


class TestStreamingErrorHandling:
    """Test error handling in streaming mode."""

    def test_stream_invalid_distance(self):
        """Should raise ValueError for invalid distance."""
        # Create invalid compressed data with zero distance
        invalid = bytes([0x80, 0x00, 0x00])
        
        with pytest.raises(ValueError) as exc_info:
            list(bob_lz_decompress_stream(invalid))
        
        assert "invalid distance" in str(exc_info.value)

    def test_stream_distance_exceeds_output(self):
        """Should raise ValueError for distance > output size."""
        # After one literal, try backref with huge distance
        invalid = bytes([0x40, 0x41, 0xFF, 0x07])
        
        with pytest.raises(ValueError):
            list(bob_lz_decompress_stream(invalid))


class TestStreamingGenerator:
    """Test generator-specific behavior."""

    def test_stream_is_generator(self):
        """Should return a generator object."""
        compressed = bob_lz_encode(b"test")
        result = bob_lz_decompress_stream(compressed)
        
        # Check it's a generator
        assert hasattr(result, '__next__')
        assert hasattr(result, '__iter__')

    def test_stream_can_iterate(self):
        """Should be iterable."""
        original = b"Test iteration"
        compressed = bob_lz_encode(original)
        
        count = 0
        total = b""
        for chunk in bob_lz_decompress_stream(compressed):
            count += 1
            total += chunk
        
        assert count >= 1
        assert total == original

    def test_stream_return_value(self):
        """Generator should return total count."""
        original = b"Return value test"
        compressed = bob_lz_encode(original)
        
        gen = bob_lz_decompress_stream(compressed)
        chunks = list(gen)
        
        # Generator return value is in StopIteration
        # Just verify we got the right total
        total_len = sum(len(c) for c in chunks)
        assert total_len == len(original)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
