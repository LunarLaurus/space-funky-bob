"""
Task System Analyzer for Space Funky B.O.B.

Analyzes 36-slot task system from NINSYS.A.
Source: NINSYS.A task scheduler, DATA.A task structures
"""

# Task type allocation from NINSYS.A
TASK_TYPES = {
    0: {'name': 'type_bob', 'slots': 2, 'description': 'Bob tasks'},
    1: {'name': 'type_enemy', 'slots': 15, 'description': 'Enemies (borgs, boxes)'},
    2: {'name': 'type_remote', 'slots': 3, 'description': 'Remotes'},
    3: {'name': 'type_weapon', 'slots': 3, 'description': 'Weapons'},
    4: {'name': 'type_walk', 'slots': 4, 'description': 'Platforms'},
    5: {'name': 'type_item', 'slots': 3, 'description': 'Items'},
    6: {'name': 'type_inven', 'slots': 3, 'description': 'Inventory'},
}

# Task data structure (64 bytes per task)
TASK_STRUCTURE = {
    'TSKflags': {'offset': 0, 'size': 1, 'description': 'Active ($80), Waiting ($40)'},
    'TSKadrLo/Hi': {'offset': 1, 'size': 2, 'description': 'Resume address'},
    'TSKwaitLo': {'offset': 3, 'size': 1, 'description': 'Wait counter'},
    'TSKbank': {'offset': 4, 'size': 1, 'description': 'ROM bank'},
    'PICxlo/hi': {'offset': 5, 'size': 2, 'description': 'X position'},
    'PICylo/hi': {'offset': 7, 'size': 2, 'description': 'Y position'},
    'PICadrLo/Hi': {'offset': 9, 'size': 2, 'description': 'Sprite address'},
    'PICattr': {'offset': 11, 'size': 1, 'description': 'Attributes (hflip/vflip)'},
    'PICbank': {'offset': 12, 'size': 1, 'description': 'Sprite bank'},
    'PICflag': {'offset': 13, 'size': 1, 'description': 'General flags'},
    'PICanim': {'offset': 14, 'size': 1, 'description': 'Animation frame'},
    'PICstatus': {'offset': 15, 'size': 1, 'description': 'Status/state'},
    'PICdir': {'offset': 16, 'size': 1, 'description': 'Direction (horizontal)'},
    'PIClogic': {'offset': 17, 'size': 1, 'description': 'Logic/type'},
    'PICcount': {'offset': 18, 'size': 1, 'description': 'General counter'},
    'PIChealth': {'offset': 43, 'size': 1, 'description': 'Health/strength'},
}


def analyze_task_system():
    """Analyze task system architecture."""
    total_slots = sum(t['slots'] for t in TASK_TYPES.values())
    
    return {
        'total_slots': total_slots,
        'max_constant': 'TSKmax = 36',
        'task_types': TASK_TYPES,
        'structure_size': 64,
        'structure_fields': len(TASK_STRUCTURE)
    }


def get_task_functions():
    """Get task scheduler functions."""
    return {
        'TSKschedule': 'Schedule new task in type range',
        'TSKsuspend': 'Suspend task, save PC',
        'TSKwait': 'Wait for N ticks',
        'TSKcancel': 'Cancel task, clear flags',
        'TSKhandler': 'Main task driver (VBLANK)'
    }


if __name__ == '__main__':
    analysis = analyze_task_system()
    print(f"Task System Analysis:")
    print(f"  Total slots: {analysis['total_slots']}")
    print(f"  Structure size: {analysis['structure_size']} bytes")
    print(f"  Task types: {len(analysis['task_types'])}")
