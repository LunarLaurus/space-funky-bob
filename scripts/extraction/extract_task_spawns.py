"""
Extract Task/Enemy Spawns from B.O.B. ROM

Extracts enemy spawn points from whichtasklist table.
Output: data/task_spawns/:mapnumber.json
"""

import json
import os
from pathlib import Path

# Task type allocation from NINSYS.A
TASK_TYPES = {
    0: 'type_bob',       # 2 slots
    1: 'type_enemy',     # 15 slots (borgs, boxes)
    2: 'type_remote',    # 3 slots
    3: 'type_weapon',    # 3 slots
    4: 'type_walk',      # 4 slots (platforms)
    5: 'type_item',      # 3 slots
    6: 'type_inven',     # 3 slots (inventory)
}

# 36-slot task system capacity
TSK_MAX = 36


def extract_task_spawns(rom_path, output_dir):
    """Extract task spawn data from ROM."""
    print(f"Extracting task spawns from {rom_path}...")
    
    with open(rom_path, 'rb') as f:
        rom_data = f.read()
    
    output_dir = Path(output_dir) / 'task_spawns'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Placeholder extraction (actual implementation reads whichtasklist)
    # This is a simplified version showing the structure
    
    for map_num in range(60):
        # Task spawn data structure
        spawn_data = {
            'map_number': map_num,
            'task_system': {
                'max_slots': TSK_MAX,
                'task_types': TASK_TYPES
            },
            'spawns': [],
            'metadata': {
                'source': 'INITLEVE.A:whichtasklist',
                'format': '7 bytes per spawn entry'
            }
        }
        
        # Save spawn data
        output_file = output_dir / f'spawns_{map_num:03d}.json'
        with open(output_file, 'w') as f:
            json.dump(spawn_data, f, indent=2)
    
    print(f"Task spawn templates created in {output_dir}")
    print("Note: Full implementation reads whichtasklist table from ROM")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract task spawns from B.O.B. ROM')
    parser.add_argument('--rom', required=True, help='ROM file path')
    parser.add_argument('--output', default='../data', help='Output directory')
    
    args = parser.parse_args()
    extract_task_spawns(args.rom, args.output)
