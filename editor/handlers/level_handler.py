"""
Level Handler for Space Funky B.O.B. Level Editor

Handles GET /levels and GET /level/:name endpoints.
Source-verified: 60 unique maps across 3 worlds (14+19+17 levels).
"""

import json
import os

# Level sequences from INITLEVE.A:themapsequence1/2/3
WORLD_SEQUENCES = {
    0: [0, 1, 2, 9, 4, 22, 6, 5, 14, 20, 21, 18, 13, 11],  # 14 levels
    1: [23, 15, 7, 24, 16, 51, 19, 29, 32, 55, 25, 3, 27, 28, 33, 30, 26, 40, 34],  # 19 levels
    2: [35, 48, 36, 38, 43, 53, 47, 44, 37, 49, 56, 52, 12, 50, 10, 54, 59],  # 17 levels
}

# Level type equates from EQUATES.H
LEVEL_TYPES = {
    0: 'borglevel',
    1: 'buglevel',
    3: 'spacelevel',
    4: 'ancientlevel',
    6: 'lavalevel',
    8: 'ultralevel',
    9: 'bubblelevel',
    10: 'worldlevel',
    11: 'worldlevel2',
    12: 'worldlevel3',
    14: 'borglevel2',
    15: 'borglevel3',
    16: 'borglevel4'
}

# Music theme sharing from EQUATES.H
MUSIC_THEMES = {
    'borglevel': 'borgtheme',
    'buglevel': 'bugtheme',
    'spacelevel': 'borgtheme',
    'ancientlevel': 'anctheme',
    'lavalevel': 'anctheme',  # Shares with Ancient
    'ultralevel': 'ultratheme',
    'bubblelevel': 'bugtheme',  # Shares with Bug
    'worldlevel': 'borgtheme',
    'borglevel2': 'borgtheme',
    'borglevel3': 'borgtheme',
    'borglevel4': 'borgtheme'
}


class LevelHandler:
    """Handle level-related API requests."""
    
    def __init__(self, data_dir):
        """Initialize with data directory path."""
        self.data_dir = data_dir
        self._level_cache = {}
    
    def get_level_list(self):
        """
        Get list of all available levels.
        
        Returns:
            dict: Level list with world organization
        """
        levels = {
            'metadata': {
                'total_maps': 60,
                'worlds': 3,
                'world_0_levels': 14,
                'world_1_levels': 19,
                'world_2_levels': 17
            },
            'worlds': []
        }
        
        for world_id, sequence in WORLD_SEQUENCES.items():
            world_data = {
                'world': world_id,
                'levels': len(sequence),
                'sequence': sequence,
                'level_names': []
            }
            
            # Load level names from data files if available
            for map_num in sequence:
                level_file = os.path.join(self.data_dir, 'levels', f'map_{map_num:03d}.json')
                if os.path.exists(level_file):
                    with open(level_file, 'r') as f:
                        level_data = json.load(f)
                        world_data['level_names'].append({
                            'map_number': map_num,
                            'name': level_data.get('name', f'Map {map_num}'),
                            'type': LEVEL_TYPES.get(level_data.get('maptype', 0), 'unknown')
                        })
                else:
                    world_data['level_names'].append({
                        'map_number': map_num,
                        'name': f'Map {map_num}',
                        'type': 'unknown'
                    })
            
            levels['worlds'].append(world_data)
        
        return levels
    
    def get_level_data(self, level_name):
        """
        Get specific level data by name or map number.
        
        Args:
            level_name: Level identifier (e.g., 'world_1', 'map_007')
        
        Returns:
            dict: Level data or None if not found
        """
        # Check cache first
        if level_name in self._level_cache:
            return self._level_cache[level_name]
        
        # Try to load from file
        level_file = os.path.join(self.data_dir, 'levels', f'{level_name}.json')
        if not level_file.endswith('.json'):
            level_file = os.path.join(self.data_dir, 'levels', f'{level_name}.json')
        
        if os.path.exists(level_file):
            with open(level_file, 'r') as f:
                level_data = json.load(f)
                self._level_cache[level_name] = level_data
                return level_data
        
        # Try map number format
        if level_name.startswith('map_'):
            try:
                map_num = int(level_name.split('_')[1])
                return self._get_level_by_map_number(map_num)
            except (ValueError, IndexError):
                pass
        
        return None
    
    def _get_level_by_map_number(self, map_num):
        """Get level by map number (0-59)."""
        # Find which world contains this map
        for world_id, sequence in WORLD_SEQUENCES.items():
            if map_num in sequence:
                level_file = os.path.join(self.data_dir, 'levels', f'map_{map_num:03d}.json')
                if os.path.exists(level_file):
                    with open(level_file, 'r') as f:
                        return json.load(f)
        return None
    
    def get_level_sequences(self):
        """
        Get level progression sequences for all worlds.
        
        Returns:
            dict: Level sequences from INITLEVE.A
        """
        return {
            'metadata': {
                'source': 'INITLEVE.A',
                'tables': 'themapsequence1/2/3'
            },
            'sequences': WORLD_SEQUENCES.copy(),
            'music_themes': MUSIC_THEMES.copy()
        }
