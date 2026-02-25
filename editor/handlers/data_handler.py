"""
Data Handler for Space Funky B.O.B. Level Editor

Handles GET /data/:file and GET /midi/* endpoints.
"""

import json
import os


class DataHandler:
    """Handle data file and MIDI-related API requests."""

    def __init__(self, data_dir, midi_dir=None):
        """
        Initialize with data and MIDI directories.

        Args:
            data_dir: Directory containing data files (ENEMIES.json, etc.)
            midi_dir: Directory containing MIDI files (or parent directory to search)
        """
        self.data_dir = data_dir
        self.midi_dir = midi_dir or os.path.join(data_dir, 'midi')
        self.midi_parent_dir = midi_dir  # Store parent dir for searching
    
    def get_data_file(self, filename):
        """
        Get data file content by name.
        
        Args:
            filename: Data file name (e.g., 'ENEMIES.json', 'TILES.json')
        
        Returns:
            dict: File content or None if not found
        """
        # Security: prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            return {'error': 'Invalid filename'}
        
        file_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(file_path):
            return None
        
        # Only serve JSON files
        if not filename.endswith('.json'):
            return {'error': 'Only JSON files supported'}
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def list_data_files(self):
        """
        List available data files.
        
        Returns:
            dict: List of available JSON files
        """
        files = []
        if os.path.exists(self.data_dir):
            for f in os.listdir(self.data_dir):
                if f.endswith('.json'):
                    files.append(f)
        
        return {
            'directory': self.data_dir,
            'files': files
        }
    
    def get_midi_list(self):
        """
        Get list of available MIDI files.

        Returns:
            dict: MIDI file list
        """
        midi_files = []
        
        # Search in the midi_dir and all subdirectories
        dirs_to_search = [self.midi_dir] if self.midi_dir else []
        
        # Also search parent directory recursively if set
        if self.midi_parent_dir and os.path.exists(self.midi_parent_dir):
            for root, dirs, files in os.walk(self.midi_parent_dir):
                for f in files:
                    if f.upper().endswith('.MID') and not f.startswith('._'):
                        midi_files.append({
                            'filename': f,
                            'path': f'/midi/{f}'
                        })
        
        # Remove duplicates by filename
        seen = set()
        unique_files = []
        for f in midi_files:
            if f['filename'] not in seen:
                seen.add(f['filename'])
                unique_files.append(f)

        return {
            'directory': self.midi_parent_dir or self.midi_dir,
            'count': len(unique_files),
            'files': unique_files
        }
    
    def get_midi_file(self, filename):
        """
        Get MIDI file path for serving.

        Args:
            filename: MIDI filename

        Returns:
            str: File path or None if not found
        """
        # Security: prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            return None

        # Search in parent directory recursively
        if self.midi_parent_dir and os.path.exists(self.midi_parent_dir):
            for root, dirs, files in os.walk(self.midi_parent_dir):
                if filename in files:
                    return os.path.join(root, filename)
        
        # Fallback to original midi_dir
        if self.midi_dir:
            file_path = os.path.join(self.midi_dir, filename)
            if os.path.exists(file_path):
                return file_path

        return None
