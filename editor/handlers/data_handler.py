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
            midi_dir: Directory containing MIDI files (defaults to editor/midi/)
        """
        self.data_dir = data_dir
        self.midi_dir = midi_dir or os.path.join(os.path.dirname(__file__), '..', 'midi')
    
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
        if os.path.exists(self.midi_dir):
            for f in os.listdir(self.midi_dir):
                if f.upper().endswith('.MID') and not f.startswith('._'):
                    midi_files.append({
                        'filename': f,
                        'path': f'/midi/{f}'
                    })

        return {
            'directory': self.midi_dir,
            'count': len(midi_files),
            'files': midi_files
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

        file_path = os.path.join(self.midi_dir, filename)
        if os.path.exists(file_path):
            return file_path

        return None
