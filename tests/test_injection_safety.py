"""Tests for injection safety (GAMMA-003)"""
import pytest
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'toolkit'))

from bob_inject import (
    create_backup,
    validate_injection,
    verify_checksum,
    verify_injection_area,
    dry_run_inject
)


class TestCreateBackup:
    """Test backup creation functionality."""

    def test_create_backup_creates_file(self, tmp_path):
        """Should create backup file."""
        # Create source ROM file
        rom_file = tmp_path / 'test.sfc'
        rom_file.write_bytes(bytes([0x00] * 1024))
        
        backup_path = create_backup(str(rom_file))
        
        assert Path(backup_path).exists()
        assert Path(backup_path).read_bytes() == bytes([0x00] * 1024)

    def test_create_backup_preserves_content(self, tmp_path):
        """Should preserve original file content."""
        rom_file = tmp_path / 'test.sfc'
        original_data = bytes(range(256)) * 4
        rom_file.write_bytes(original_data)
        
        backup_path = create_backup(str(rom_file))
        
        assert Path(backup_path).read_bytes() == original_data


class TestValidateInjection:
    """Test injection validation."""

    def test_validate_valid_injection(self):
        """Should return empty errors for valid injection."""
        rom_data = bytes([0x00] * 1024)
        errors = validate_injection(rom_data, 0x100, bytes([0xFF] * 16))
        assert len(errors) == 0

    def test_validate_negative_offset(self):
        """Should detect negative offset."""
        rom_data = bytes([0x00] * 1024)
        errors = validate_injection(rom_data, -1, bytes([0xFF]))
        assert len(errors) > 0
        assert "negative" in errors[0].lower()

    def test_validate_offset_exceeds_rom(self):
        """Should detect offset exceeding ROM size."""
        rom_data = bytes([0x00] * 1024)
        errors = validate_injection(rom_data, 2048, bytes([0xFF]))
        assert len(errors) > 0
        assert "exceeds" in errors[0].lower()

    def test_validate_data_exceeds_rom(self):
        """Should detect data exceeding ROM size."""
        rom_data = bytes([0x00] * 1024)
        errors = validate_injection(rom_data, 1020, bytes([0xFF] * 16))
        assert len(errors) > 0
        assert "exceeds" in errors[0].lower()

    def test_validate_max_size(self):
        """Should detect data exceeding max size."""
        rom_data = bytes([0x00] * 1024)
        errors = validate_injection(rom_data, 0x100, bytes([0xFF] * 100), max_size=50)
        assert len(errors) > 0
        assert "exceeds maximum" in errors[0].lower()

    def test_validate_boundary_exact(self):
        """Should allow injection at exact ROM boundary."""
        rom_data = bytes([0x00] * 1024)
        errors = validate_injection(rom_data, 1008, bytes([0xFF] * 16))
        assert len(errors) == 0


class TestVerifyChecksum:
    """Test checksum verification."""

    def test_verify_checksum_empty(self):
        """Should handle empty/invalid ROM."""
        is_valid, stored, calculated = verify_checksum(b'')
        assert is_valid == False

    def test_verify_checksum_small_rom(self):
        """Should handle ROM too small for checksum."""
        rom_data = bytes([0x00] * 100)
        is_valid, stored, calculated = verify_checksum(rom_data)
        assert is_valid == False


class TestVerifyInjectionArea:
    """Test injection area verification."""

    def test_verify_no_overlap(self):
        """Should return no warnings for non-overlapping injection."""
        rom_data = bytes([0x00] * 0x10000)
        warnings = verify_injection_area(rom_data, 0x1000, 0x100)
        assert len(warnings) == 0

    def test_verify_overlap_header(self):
        """Should warn about header overlap."""
        rom_data = bytes([0x00] * 0x10000)
        # Inject at 0x7FC0 (header location)
        warnings = verify_injection_area(rom_data, 0x7FC0, 0x40)
        assert len(warnings) > 0
        assert "protected region" in warnings[0].lower()

    def test_verify_custom_protected_regions(self):
        """Should use custom protected regions."""
        rom_data = bytes([0x00] * 0x10000)
        protected = [(0x5000, 0x6000)]
        warnings = verify_injection_area(rom_data, 0x5500, 0x100, protected)
        assert len(warnings) > 0


class TestDryRunInject:
    """Test dry-run injection."""

    def test_dry_run_valid(self):
        """Should return valid result for valid injection."""
        rom_data = bytes([0x00] * 1024)
        new_data = bytes([0xFF] * 16)
        result = dry_run_inject(rom_data, 0x100, new_data)
        
        assert result['valid'] == True
        assert result['offset'] == 0x100
        assert result['size'] == 16
        assert result['changed_bytes'] == 16
        assert result['would_modify'] == True

    def test_dry_run_invalid(self):
        """Should return invalid result for invalid injection."""
        rom_data = bytes([0x00] * 1024)
        new_data = bytes([0xFF] * 16)
        result = dry_run_inject(rom_data, 2048, new_data)
        
        assert result['valid'] == False
        assert len(result['errors']) > 0

    def test_dry_run_no_changes(self):
        """Should detect when no bytes would change."""
        rom_data = bytes([0xFF] * 1024)
        new_data = bytes([0xFF] * 16)
        result = dry_run_inject(rom_data, 0x100, new_data)
        
        assert result['valid'] == True
        assert result['changed_bytes'] == 0
        assert result['would_modify'] == False

    def test_dry_run_partial_changes(self):
        """Should count changed bytes correctly."""
        rom_data = bytes([0x00] * 1024)
        new_data = bytes([0xFF, 0x00] * 8)  # Alternating
        result = dry_run_inject(rom_data, 0x100, new_data)
        
        assert result['changed_bytes'] == 8  # Only 0xFF bytes change


class TestIntegrationSafety:
    """Integration tests for safety features."""

    def test_backup_before_injection(self, tmp_path):
        """Should create backup before injection."""
        rom_file = tmp_path / 'test.sfc'
        rom_file.write_bytes(bytes([0x00] * 1024))
        
        # Create backup
        backup_path = create_backup(str(rom_file))
        
        # Modify original
        rom_file.write_bytes(bytes([0xFF] * 1024))
        
        # Verify backup has original content
        assert Path(backup_path).read_bytes() == bytes([0x00] * 1024)

    def test_validate_then_inject(self, tmp_path):
        """Should validate before injection."""
        rom_data = bytes([0x00] * 1024)
        new_data = bytes([0xFF] * 16)
        
        # Validate first
        errors = validate_injection(rom_data, 0x100, new_data)
        assert len(errors) == 0
        
        # Then inject (manually)
        rom = bytearray(rom_data)
        rom[0x100:0x100+16] = new_data
        
        # Verify injection worked
        assert rom[0x100:0x110] == new_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
