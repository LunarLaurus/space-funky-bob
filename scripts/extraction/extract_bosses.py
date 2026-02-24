"""
Extract Boss Data from B.O.B. ROM

Extracts 10 boss battles from INITLEVE.A:fightboss table.
Output: data/bosses.json
"""

import json
from pathlib import Path

# 10 boss battles from INITLEVE.A:fightboss
BOSS_DATA = [
    {'id': 1, 'name': 'Popeye Boss', 'level_index': 3, 'category': 'ancient', 'hp': 48},
    {'id': 2, 'name': 'Queen Bug', 'level_index': 13, 'category': 'bug', 'hp': 48},
    {'id': 3, 'name': 'Snake Boss', 'level_index': 14, 'category': 'borg', 'hp': 48},
    {'id': 4, 'name': 'Spider Boss', 'level_index': 17, 'category': 'borg', 'hp': 48},
    {'id': 5, 'name': 'Ancient Boss', 'level_index': 31, 'category': 'ancient', 'hp': 48},
    {'id': 6, 'name': 'Lava Boss', 'level_index': 33, 'category': 'lava', 'hp': 48},
    {'id': 7, 'name': 'Screen Lifter', 'level_index': 40, 'category': 'borg', 'hp': 48},
    {'id': 8, 'name': 'Puss Boss', 'level_index': 52, 'category': 'ultra', 'hp': 48},
    {'id': 9, 'name': 'Mutoid Man', 'level_index': 53, 'category': 'ultra', 'hp': 48},
    {'id': 10, 'name': 'Ultra Boss', 'level_index': 54, 'category': 'ultra', 'hp': 48},
]

# Boss sound effects from EQUATES.H
BOSS_SOUNDS = {
    1: ['SFXANCIENTBOSS'],
    2: ['SFXQUEENSCREAM'],
    3: ['SFXSNAKEBOSS1', 'SFXSNAKEBOSS2', 'SFXSNAKEBOSS3'],
    4: ['SFXSPIDERBOSS'],
    5: ['SFXFLOWERBOSS'],
    6: ['SFXLAVABOSS'],
    7: ['SFXLIFTER'],
    8: ['SFXPUSSMANBELCH'],
    9: ['SFXMUTOID'],
    10: ['SFXULTRABOSS'],
}


def extract_bosses(output_dir):
    """Extract boss data to JSON."""
    print("Extracting boss data...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Add sounds to boss data
    bosses = []
    for boss in BOSS_DATA:
        boss_with_sounds = boss.copy()
        boss_with_sounds['sounds'] = BOSS_SOUNDS.get(boss['id'], [])
        bosses.append(boss_with_sounds)
    
    # Create boss data file
    boss_data = {
        'metadata': {
            'total_bosses': 10,
            'source': 'INITLEVE.A:fightboss',
            'hp_max': 48,
            'hp_variable': 'bossstrength'
        },
        'bosses': bosses,
        'mechanics': {
            'position_vars': ['bossx', 'bossy'],
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
    }
    
    output_file = output_dir / 'bosses.json'
    with open(output_file, 'w') as f:
        json.dump(boss_data, f, indent=2)
    
    print(f"Extracted {len(bosses)} bosses to {output_file}")
    return bosses


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract boss data from B.O.B.')
    parser.add_argument('--output', default='../data', help='Output directory')
    
    args = parser.parse_args()
    extract_bosses(args.output)
