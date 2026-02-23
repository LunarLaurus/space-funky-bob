"""
Export Handler for Space Funky B.O.B. Level Editor

Handles POST /export-level endpoint.
Exports level data back to ROM file.
"""

import os


class ExportHandler:
    """Handle level export API requests."""
    
    def __init__(self, rom_path=None):
        """
        Initialize with optional ROM path.
        
        Args:
            rom_path: Path to ROM file for export
        """
        self.rom_path = rom_path
    
    def export_level(self, level_data):
        """
        Export level data to ROM.
        
        Args:
            level_data: dict with level data including:
                - map_number: Map number (0-59)
                - offset: ROM offset to write
                - data: Level tile data
        
        Returns:
            dict: Export result with success status
        """
        if not self.rom_path:
            return {
                'success': False,
                'error': 'ROM path not configured'
            }
        
        if not os.path.exists(self.rom_path):
            return {
                'success': False,
                'error': f'ROM file not found: {self.rom_path}'
            }
        
        # Validate level data
        if 'map_number' not in level_data:
            return {
                'success': False,
                'error': 'Missing map_number in level data'
            }
        
        if 'data' not in level_data:
            return {
                'success': False,
                'error': 'Missing data in level data'
            }
        
        # Get ROM offset
        rom_offset = level_data.get('offset')
        if rom_offset is None:
            return {
                'success': False,
                'error': 'Missing ROM offset in level data'
            }
        
        # Convert offset if string
        if isinstance(rom_offset, str):
            try:
                rom_offset = int(rom_offset, 16)
            except ValueError:
                return {
                    'success': False,
                    'error': 'Invalid ROM offset format'
                }
        
        # Write to ROM
        try:
            with open(self.rom_path, 'r+b') as f:
                f.seek(rom_offset)
                level_bytes = level_data['data']
                
                # Convert list to bytes if needed
                if isinstance(level_bytes, list):
                    level_bytes = bytes(level_bytes)
                elif isinstance(level_bytes, str):
                    level_bytes = bytes.fromhex(level_bytes)
                
                f.write(level_bytes)
            
            return {
                'success': True,
                'map_number': level_data['map_number'],
                'offset': f'0x{rom_offset:06X}',
                'bytes_written': len(level_bytes)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Export failed: {str(e)}'
            }
    
    def validate_export(self, level_data):
        """
        Validate level data before export.
        
        Args:
            level_data: Level data to validate
        
        Returns:
            dict: Validation result with errors list
        """
        errors = []
        
        # Check required fields
        if 'map_number' not in level_data:
            errors.append('Missing map_number')
        
        if 'data' not in level_data:
            errors.append('Missing data')
        
        if 'offset' not in level_data:
            errors.append('Missing ROM offset')
        
        # Validate data size (16KB per level)
        if 'data' in level_data:
            data_size = len(level_data['data'])
            if data_size != 16384:
                errors.append(f'Invalid data size: {data_size} (expected 16384)')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
