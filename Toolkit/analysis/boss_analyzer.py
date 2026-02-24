"""
Boss Analyzer for Space Funky B.O.B.

Analyzes boss battle data from source code.
Source: INITLEVE.A:fightboss, BOB.A boss mechanics
"""

from pathlib import Path

# 10 boss battles from INITLEVE.A:fightboss
BOSSES = [
    {'id': 1, 'name': 'Popeye Boss', 'level': 3, 'category': 'ancient', 'hp': 48},
    {'id': 2, 'name': 'Queen Bug', 'level': 13, 'category': 'bug', 'hp': 48},
    {'id': 3, 'name': 'Snake Boss', 'level': 14, 'category': 'borg', 'hp': 48},
    {'id': 4, 'name': 'Spider Boss', 'level': 17, 'category': 'borg', 'hp': 48},
    {'id': 5, 'name': 'Ancient Boss', 'level': 31, 'category': 'ancient', 'hp': 48},
    {'id': 6, 'name': 'Lava Boss', 'level': 33, 'category': 'lava', 'hp': 48},
    {'id': 7, 'name': 'Screen Lifter', 'level': 40, 'category': 'borg', 'hp': 48},
    {'id': 8, 'name': 'Puss Boss', 'level': 52, 'category': 'ultra', 'hp': 48},
    {'id': 9, 'name': 'Mutoid Man', 'level': 53, 'category': 'ultra', 'hp': 48},
    {'id': 10, 'name': 'Ultra Boss', 'level': 54, 'category': 'ultra', 'hp': 48},
]

# Boss sound effects from EQUATES.H
BOSS_SOUNDS = {
    1: ['SFXANCIENTBOSS'], 2: ['SFXQUEENSCREAM'],
    3: ['SFXSNAKEBOSS1', 'SFXSNAKEBOSS2', 'SFXSNAKEBOSS3'],
    4: ['SFXSPIDERBOSS'], 5: ['SFXFLOWERBOSS'], 6: ['SFXLAVABOSS'],
    7: ['SFXLIFTER'], 8: ['SFXPUSSMANBELCH'], 9: ['SFXMUTOID'],
    10: ['SFXULTRABOSS'],
}


def analyze_bosses():
    """Analyze all boss battles."""
    print("Analyzing boss battles...")
    
    analysis = {
        'total_bosses': len(BOSSES),
        'by_category': {},
        'hp_analysis': {'min': 48, 'max': 48, 'avg': 48},
        'sound_catalog': {}
    }
    
    # Group by category
    for boss in BOSSES:
        cat = boss['category']
        if cat not in analysis['by_category']:
            analysis['by_category'][cat] = []
        analysis['by_category'][cat].append(boss['name'])
        
        # Add sounds
        analysis['sound_catalog'][boss['name']] = BOSS_SOUNDS.get(boss['id'], [])
    
    return analysis


def get_boss_strategies():
    """Get boss battle strategies."""
    return {
        'general': {
            'hp': 'All bosses have 48 HP (bossstrength variable)',
            'screen_lock': 'Boss battles use centrescroll for screen locking',
            'variables': 'bossx/bossy (position), bossdir/bossdirv (direction)'
        },
        'specific': {
            'Snake Boss': 'Three-part battle: head, body, turret',
            'Queen Bug': 'Dripping guts attack (SFXDRIP)',
            'Lava Boss': 'Rises from lava streams',
            'Ultra Boss': 'Final boss with multiple phases'
        }
    }


if __name__ == '__main__':
    analysis = analyze_bosses()
    print(f"Total bosses: {analysis['total_bosses']}")
    print(f"By category: {analysis['by_category']}")
