"""
Spawn Pattern Analyzer for Space Funky B.O.B.

Analyzes enemy spawn patterns from whichtasklist.
Source: INITLEVE.A:whichtasklist, NINSYS.A task system
"""

# Task system capacity
TSK_MAX = 36

# Task type allocation
TASK_TYPES = {
    0: 'type_bob', 1: 'type_enemy', 2: 'type_remote',
    3: 'type_weapon', 4: 'type_walk', 5: 'type_item', 6: 'type_inven'
}

# Enemy types by category
ENEMY_CATEGORIES = {
    'borg': ['Borg Guard', 'Borg Patrol', 'Borg Shooter', 'Borg Jumper',
             'Borg Small', 'Borg Flyer', 'Borg Ducker', 'Borg Tosser'],
    'bug': ['Cockroach', 'Worker', 'Crab', 'Scorpion', 'Dropper', 'Larvae'],
    'ancient': ['Ancient Brick', 'Ancient Trap', 'Ancient Guardian'],
    'lava': ['Fire Imp', 'Lava Man', 'Volcano'],
    'ultra': ['Cell Man', 'Puss Mine', 'Mutoid'],
    'bubble': ['Bubble', 'Venus Trap', 'Shroom'],
}


def analyze_spawn_patterns():
    """Analyze enemy spawn patterns."""
    return {
        'task_system': {
            'max_slots': TSK_MAX,
            'enemy_slots': TASK_TYPES[1],
            'format': '7 bytes per spawn entry'
        },
        'enemy_categories': ENEMY_CATEGORIES,
        'total_enemy_types': sum(len(enemies) for enemies in ENEMY_CATEGORIES.values())
    }


def get_spawn_format():
    """Get spawn entry format."""
    return {
        'bytes_0_1': 'Task routine address (low, high)',
        'byte_2': 'Task type reference',
        'byte_3': 'Task-specific variable (tempflag)',
        'byte_4': 'X offset (tmpx)',
        'byte_5': 'Y offset (tmpy)',
        'byte_6': 'ROM bank (tempbank)'
    }


def get_enemies_by_category(category):
    """Get enemy list for category."""
    return ENEMY_CATEGORIES.get(category, [])


if __name__ == '__main__':
    analysis = analyze_spawn_patterns()
    print(f"Spawn Pattern Analysis:")
    print(f"  Task system: {analysis['task_system']['max_slots']} slots")
    print(f"  Enemy categories: {len(analysis['enemy_categories'])}")
    print(f"  Total enemy types: {analysis['total_enemy_types']}")
