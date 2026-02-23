"""
Boss Handler for Space Funky B.O.B. Level Editor

Handles GET /bosses endpoint.
Source-verified: 10 boss battles from INITLEVE.A:fightboss table.
"""

# 10 boss battles from INITLEVE.A:fightboss table
BOSS_DATA = [
    {
        'id': 1,
        'name': 'Popeye Boss',
        'level_index': 3,
        'category': 'ancient',
        'hp': 48,
        'sounds': ['SFXANCIENTBOSS'],
        'description': 'Ancient Ruins boss'
    },
    {
        'id': 2,
        'name': 'Queen Bug',
        'level_index': 13,
        'category': 'bug',
        'hp': 48,
        'sounds': ['SFXQUEENSCREAM'],
        'description': 'Bug Planet queen boss'
    },
    {
        'id': 3,
        'name': 'Snake Boss',
        'level_index': 14,
        'category': 'borg',
        'hp': 48,
        'sounds': ['SFXSNAKEBOSS1', 'SFXSNAKEBOSS2', 'SFXSNAKEBOSS3'],
        'description': 'Borg Factory snake boss'
    },
    {
        'id': 4,
        'name': 'Spider Boss',
        'level_index': 17,
        'category': 'borg',
        'hp': 48,
        'sounds': ['SFXSPIDERBOSS'],
        'description': 'Borg Factory spider boss'
    },
    {
        'id': 5,
        'name': 'Ancient Boss / Flower',
        'level_index': 31,
        'category': 'ancient',
        'hp': 48,
        'sounds': ['SFXFLOWERBOSS'],
        'description': 'Ancient Ruins flower boss'
    },
    {
        'id': 6,
        'name': 'Lava Boss',
        'level_index': 33,
        'category': 'lava',
        'hp': 48,
        'sounds': ['SFXLAVABOSS'],
        'description': 'Lava World boss'
    },
    {
        'id': 7,
        'name': 'Screen Lifter',
        'level_index': 40,
        'category': 'borg',
        'hp': 48,
        'sounds': ['SFXLIFTER'],
        'description': 'Borg elevator boss'
    },
    {
        'id': 8,
        'name': 'Puss Boss',
        'level_index': 52,
        'category': 'ultra',
        'hp': 48,
        'sounds': ['SFXPUSSMANBELCH'],
        'description': 'Ultra Force puss man boss'
    },
    {
        'id': 9,
        'name': 'Mutoid Man',
        'level_index': 53,
        'category': 'ultra',
        'hp': 48,
        'sounds': ['SFXMUTOID'],
        'description': 'Ultra Force mutoid boss'
    },
    {
        'id': 10,
        'name': 'Ultra Boss',
        'level_index': 54,
        'category': 'ultra',
        'hp': 48,
        'sounds': ['SFXULTRABOSS'],
        'description': 'Ultra Force final boss'
    }
]

# Boss battle mechanics from BOB.A
BOSS_MECHANICS = {
    'hp_variable': 'bossstrength',
    'hp_max': 48,
    'position_vars': ['bossx', 'bossy'],  # 16-bit positions
    'direction_vars': ['bossdir', 'bossdirv'],
    'speed_vars': ['bosspeedh', 'bosspeedv'],
    'counter_vars': ['bosscount1', 'bosscount2', 'bosscount3'],
    'behavior_vars': ['bossangry', 'bossready', 'bosstarget'],
    'screen_locking': {
        'variable': 'centrescroll',
        'x_distance': 'centrescrx',
        'y_direction': 'centreydir'
    }
}


class BossHandler:
    """Handle boss-related API requests."""
    
    def __init__(self):
        """Initialize boss handler."""
        self._boss_cache = None
    
    def get_all_bosses(self):
        """
        Get all boss battle data.
        
        Returns:
            dict: Boss list with metadata
        """
        return {
            'metadata': {
                'total_bosses': 10,
                'source': 'INITLEVE.A:fightboss',
                'hp_max': 48,
                'hp_variable': 'bossstrength'
            },
            'bosses': BOSS_DATA,
            'mechanics': BOSS_MECHANICS
        }
    
    def get_boss_by_id(self, boss_id):
        """
        Get specific boss by ID.
        
        Args:
            boss_id: Boss ID (1-10)
        
        Returns:
            dict: Boss data or None if not found
        """
        if boss_id < 1 or boss_id > 10:
            return None
        
        return BOSS_DATA[boss_id - 1]
    
    def get_boss_by_level(self, level_index):
        """
        Get boss by level index.
        
        Args:
            level_index: Level index from fightboss table
        
        Returns:
            dict: Boss data or None if not found
        """
        for boss in BOSS_DATA:
            if boss['level_index'] == level_index:
                return boss
        return None
    
    def get_boss_sounds(self):
        """
        Get all boss sound effects.
        
        Returns:
            dict: Boss sound catalog
        """
        sounds = {}
        for boss in BOSS_DATA:
            for sound in boss['sounds']:
                if sound not in sounds:
                    sounds[sound] = []
                sounds[sound].append(boss['name'])
        
        return {
            'metadata': {
                'source': 'EQUATES.H:SFX*BOSS*'
            },
            'sounds': sounds
        }
