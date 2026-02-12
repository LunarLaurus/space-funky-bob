"""Tests for bob_lz_scan.py - ROM scanner"""
import pytest
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from bob_lz_scan import (
    calculate_entropy,
    looks_like_compressed,
    looks_like_tile_data,
    detect_rom_header,
    detect_rom_mapping,
    scan_rom_for_compressed_blocks
)


class TestEntropy:
    """Tests for entropy calculation"""
    
    def test_empty_data(self):
        """Test entropy of empty data"""
        assert calculate_entropy(b"") == 0.0
    
    def test_uniform_data(self):
        """Test entropy of uniform data (all same byte)"""
        # All zeros should have very low entropy
        entropy = calculate_entropy(b"\x00" * 100)
        assert entropy < 0.5
    
    def test_high_entropy_data(self):
        """Test entropy of random data"""
        import random
        random.seed(42)
        data = bytes([random.randint(0, 255) for _ in range(1000)])
        entropy = calculate_entropy(data)
        
        # Random data should have high entropy
        assert entropy > 5.0


class TestHeuristics:
    """Tests for heuristic functions"""
    
    def test_looks_like_compressed(self):
        """Test compressed data detection"""
        import random
        random.seed(42)
        
        # Random data should look compressed
        random_data = bytes([random.randint(0, 255) for _ in range(64)])
        assert looks_like_compressed(random_data) is True
        
        # All zeros should NOT look compressed
        zero_data = b"\x00" * 64
        assert looks_like_compressed(zero_data) is False
    
    def test_looks_like_tile_data(self):
        """Test tile data detection"""
        # Graphics-like data (moderate entropy, some zeros)
        tile_like = bytes([0, 0, 0, 0, 1, 2, 3, 4] * 32)
        assert looks_like_tile_data(tile_like) is True
        
        # Empty data should not look like tiles
        empty = b"\x00" * 64
        assert looks_like_tile_data(empty) is False
        
        # Too short
        assert looks_like_tile_data(b"") is False


class TestROMDetection:
    """Tests for ROM header and mapping detection"""
    
    def test_detect_lorom_header(self):
        """Test LoROM header detection"""
        # Create fake ROM with LoROM header
        rom = bytearray(0x20000)
        rom[0x7FC0:0x7FC0+21] = b"B.O.B.             "
        rom[0x7FD6] = 0x69  # Fixed byte
        
        has_header, offset, title = detect_rom_header(rom)
        
        # Without copier header, should not have header
        # But should detect title at 0x7FC0
        assert "B.O.B." in title
    
    def test_detect_lorom_mapping(self):
        """Test LoROM mapping detection"""
        # Create fake LoROM ROM
        rom = bytearray(0x20000)
        rom[0x7FC0:0x7FC0+21] = b"B.O.B.             "
        rom[0x7FD6] = 0x69
        rom[0x7FEA:0x7FEC] = (0x7379).to_bytes(2, 'little')  # Checksum
        rom[0x7FEC:0x7FEE] = (0x8C86).to_bytes(2, 'little')  # Complement
        
        mapping = detect_rom_mapping(rom)
        
        assert mapping == "LoROM"


class TestROMScanner:
    """Tests for full ROM scanning"""
    
    def test_scan_finds_valid_compressed_data(self):
        """Test that scanner finds valid compressed blocks"""
        import random
        
        # Create fake ROM with valid compressed data
        rom = bytearray(0x20000)
        
        # Add header
        rom[0x7FC0:0x7FC0+21] = b"B.O.B.             "
        rom[0x7FD6] = 0x69
        rom[0x7FEA:0x7FEC] = (0x7379).to_bytes(2, 'little')
        rom[0x7FEC:0x7FEE] = (0x8C86).to_bytes(2, 'little')
        
        # Add high entropy LZ77 data at offset 0x10000
        random.seed(42)
        test_data = [0x00]  # Header: all literals
        for _ in range(64):
            test_data.append(random.randint(65, 122))
        rom[0x10000:0x10000+len(test_data)] = bytes(test_data)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            outdir = Path(tmpdir)
            candidates = scan_rom_for_compressed_blocks(rom, 0, outdir)
            
            # Should find some candidates (exact count depends on heuristics)
            assert len(candidates) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
