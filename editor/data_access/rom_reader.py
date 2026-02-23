"""
ROM Reader for Space Funky B.O.B.

Provides ROM file I/O and offset calculations for LoROM mapping.
Source-verified: 1MB LoROM format from original Gray Matter source.
"""

import os


class ROMReader:
    """Read data from B.O.B. ROM file with LoROM mapping."""
    
    def __init__(self, rom_path):
        """
        Initialize ROM reader.
        
        Args:
            rom_path: Path to ROM file (B.O.B..smc or B.O.B._edit.smc)
        """
        self.rom_path = rom_path
        self._rom_data = None
        self._rom_size = 0
    
    def open(self):
        """
        Open ROM file and load into memory.
        
        Returns:
            bool: Success status
        """
        if not os.path.exists(self.rom_path):
            return False
        
        try:
            with open(self.rom_path, 'rb') as f:
                self._rom_data = f.read()
                self._rom_size = len(self._rom_data)
            return True
        except Exception:
            return False
    
    def close(self):
        """Close ROM and free memory."""
        self._rom_data = None
        self._rom_size = 0
    
    def read_bytes(self, offset, length):
        """
        Read bytes from ROM at specified offset.
        
        Args:
            offset: ROM file offset
            length: Number of bytes to read
        
        Returns:
            bytes: ROM data or None if out of bounds
        """
        if self._rom_data is None:
            if not self.open():
                return None
        
        if offset < 0 or offset + length > self._rom_size:
            return None
        
        return self._rom_data[offset:offset + length]
    
    def read_word(self, offset):
        """
        Read 16-bit little-endian word from ROM.
        
        Args:
            offset: ROM file offset
        
        Returns:
            int: 16-bit value or None if out of bounds
        """
        data = self.read_bytes(offset, 2)
        if data is None:
            return None
        return data[0] | (data[1] << 8)
    
    def snes_to_rom_offset(self, snes_address):
        """
        Convert SNES address to ROM file offset (LoROM mapping).
        
        LoROM mapping:
        - ROM $0000-$7FFF → SNES $8000-$FFFF (Bank 0)
        - ROM $8000-$FFFF → SNES $8000-$FFFF (Bank 1)
        
        Args:
            snes_address: SNES memory address (e.g., 0x808000)
        
        Returns:
            int: ROM file offset or None if invalid
        """
        bank = (snes_address >> 16) & 0xFF
        offset = snes_address & 0xFFFF
        
        # LoROM banks start at 0x80
        if bank < 0x80:
            return None
        
        # Calculate ROM offset
        rom_bank = bank - 0x80
        rom_offset = (rom_bank * 0x8000) + (offset if offset >= 0x8000 else offset + 0x8000)
        
        return rom_offset
    
    def rom_to_snes_address(self, rom_offset):
        """
        Convert ROM file offset to SNES address (LoROM mapping).
        
        Args:
            rom_offset: ROM file offset
        
        Returns:
            int: SNES address
        """
        rom_bank = rom_offset // 0x8000
        bank_offset = rom_offset % 0x8000
        
        snes_bank = rom_bank + 0x80
        snes_offset = bank_offset if bank_offset >= 0x8000 else bank_offset - 0x8000
        
        return (snes_bank << 16) | snes_offset
    
    def get_rom_size(self):
        """
        Get ROM file size.
        
        Returns:
            int: ROM size in bytes
        """
        if self._rom_size == 0:
            if not self.open():
                return 0
        return self._rom_size
    
    def get_rom_info(self):
        """
        Get ROM file information.
        
        Returns:
            dict: ROM metadata
        """
        if self._rom_size == 0:
            if not self.open():
                return None
        
        # Check for header (512-byte copier header if size % 1024 == 512)
        has_header = (self._rom_size % 1024) == 512
        
        # ROM size without header
        rom_size = self._rom_size - 512 if has_header else self._rom_size
        
        # Calculate ROM size in Mbits
        rom_mbits = (rom_size * 8) / (1024 * 1024)
        
        return {
            'file': self.rom_path,
            'size_bytes': self._rom_size,
            'size_mbits': rom_mbits,
            'has_header': has_header,
            'format': 'LoROM',
            'mapping': 'LoROM Fast'
        }
