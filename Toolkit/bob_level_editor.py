#!/usr/bin/env python3
"""
bob_level_editor.py — B.O.B. Level Editor CLI

Interactive command-line interface for viewing, modifying, and injecting level tilemaps.

Usage:
    python bob_level_editor.py --rom "rom/B.O.B..smc"          # Interactive mode
    python bob_level_editor.py --rom "rom/B.O.B..smc" list     # List all levels
    python bob_level_editor.py --rom "rom/B.O.B..smc" view 0   # View level 0
    python bob_level_editor.py --rom "rom/B.O.B..smc" export 0 --output level_0.json
    python bob_level_editor.py --rom "rom/B.O.B..smc" import 0 --input modified.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent))

from bob_extract_levels import find_tilemaps, parse_tilemap
from bob_inject import inject_tilemap, validate_injection, create_backup


# Known tilemap locations for B.O.B.
KNOWN_TILEMAPS = [
    {'offset': 0x028000, 'name': 'Tilemap 1'},
    {'offset': 0x028800, 'name': 'Tilemap 2'},
    {'offset': 0x029000, 'name': 'Tilemap 3'},
    {'offset': 0x029800, 'name': 'Tilemap 4'},
    {'offset': 0x02A000, 'name': 'Tilemap 5'},
    {'offset': 0x02A800, 'name': 'Tilemap 6'},
    {'offset': 0x02B000, 'name': 'Tilemap 7'},
    {'offset': 0x02B800, 'name': 'Tilemap 8'},
    {'offset': 0x038000, 'name': 'Tilemap 9'},
    {'offset': 0x038800, 'name': 'Tilemap 10'},
]


def load_rom(rom_path):
    """Load ROM file."""
    rom_path = Path(rom_path)
    if not rom_path.exists():
        print(f"Error: ROM file not found: {rom_path}")
        return None
    
    print(f"Loading ROM: {rom_path.name}...")
    rom_data = rom_path.read_bytes()
    print(f"ROM size: {len(rom_data):,} bytes ({len(rom_data) / 1024 / 1024:.2f} MB)")
    return rom_data


def list_levels(rom_data):
    """List all known tilemap locations."""
    print("\n" + "=" * 60)
    print("B.O.B. Level Tilemaps")
    print("=" * 60)
    
    tilemaps = find_tilemaps(rom_data)
    
    print(f"\nFound {len(tilemaps)} potential tilemaps:\n")
    print(f"{'#':<4} {'Offset':<12} {'Size':<10} {'Non-zero':<10} {'Unique':<10}")
    print("-" * 60)
    
    for i, tm in enumerate(tilemaps):
        print(f"{i:<4} 0x{tm['offset']:06X}   0x800      {tm['nonzero']:<10} {tm['unique']:<10}")
    
    print("\nKnown locations:")
    for i, loc in enumerate(KNOWN_TILEMAPS):
        print(f"  {i}: {loc['name']} at 0x{loc['offset']:06X}")
    
    return tilemaps


def view_tilemap(rom_data, level_index):
    """View tilemap as ASCII art."""
    if level_index < 0 or level_index >= len(KNOWN_TILEMAPS):
        print(f"Error: Invalid level index {level_index}")
        return
    
    offset = KNOWN_TILEMAPS[level_index]['offset']
    name = KNOWN_TILEMAPS[level_index]['name']
    
    if offset + 0x800 > len(rom_data):
        print(f"Error: Tilemap extends beyond ROM size")
        return
    
    tilemap_data = rom_data[offset:offset + 0x800]
    tiles = parse_tilemap(tilemap_data)
    
    print("\n" + "=" * 60)
    print(f"Tilemap: {name} (0x{offset:06X})")
    print("=" * 60)
    
    # Display as 32x32 grid with ASCII characters
    print("\n32x32 Tile Grid (showing tile IDs mod 10):\n")
    
    for row in range(32):
        line = ""
        for col in range(32):
            idx = row * 32 + col
            if idx < len(tiles):
                tile_id = tiles[idx]['id'] % 10
                line += str(tile_id)
            else:
                line += "."
        print(line)
    
    # Show statistics
    unique_tiles = len(set(t['id'] for t in tiles))
    print(f"\nStatistics:")
    print(f"  Unique tiles: {unique_tiles}")
    print(f"  Max tile ID: {max(t['id'] for t in tiles)}")
    print(f"  Min tile ID: {min(t['id'] for t in tiles)}")


def export_tilemap(rom_data, level_index, output_path):
    """Export tilemap to JSON or binary."""
    if level_index < 0 or level_index >= len(KNOWN_TILEMAPS):
        print(f"Error: Invalid level index {level_index}")
        return False
    
    offset = KNOWN_TILEMAPS[level_index]['offset']
    name = KNOWN_TILEMAPS[level_index]['name']
    
    if offset + 0x800 > len(rom_data):
        print(f"Error: Tilemap extends beyond ROM size")
        return False
    
    tilemap_data = rom_data[offset:offset + 0x800]
    tiles = parse_tilemap(tilemap_data)
    
    output_path = Path(output_path)
    
    if output_path.suffix == '.json':
        # Export as JSON
        data = {
            'name': name,
            'offset': offset,
            'size': 0x800,
            'format': '16-bit SNES tilemap',
            'grid': '32x32',
            'tiles': tiles
        }
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Exported tilemap to {output_path} (JSON format)")
    else:
        # Export as binary
        output_path.write_bytes(tilemap_data)
        print(f"Exported tilemap to {output_path} (binary format)")
    
    return True


def import_tilemap(rom_data, level_index, input_path, output_path=None):
    """Import modified tilemap and inject into ROM."""
    if level_index < 0 or level_index >= len(KNOWN_TILEMAPS):
        print(f"Error: Invalid level index {level_index}")
        return False
    
    offset = KNOWN_TILEMAPS[level_index]['offset']
    name = KNOWN_TILEMAPS[level_index]['name']
    
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return False
    
    # Load tilemap data
    if input_path.suffix == '.json':
        with open(input_path) as f:
            data = json.load(f)
        # Reconstruct binary from tiles
        tilemap_data = bytearray(0x800)
        for i, tile in enumerate(data['tiles'][:1024]):
            val = tile['raw']
            tilemap_data[i * 2] = val & 0xFF
            tilemap_data[i * 2 + 1] = (val >> 8) & 0xFF
        tilemap_data = bytes(tilemap_data)
    else:
        tilemap_data = input_path.read_bytes()
    
    if len(tilemap_data) != 0x800:
        print(f"Warning: Tilemap is {len(tilemap_data)} bytes, expected 0x800")
    
    # Validate injection
    errors = validate_injection(rom_data, offset, tilemap_data)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # Inject
    if output_path:
        result = inject_tilemap(rom_data, input_path, offset, output_path, create_backup_file=True)
        if result:
            print(f"Injected tilemap to {output_path}")
            return True
    else:
        print("No output path specified. Use --output to save modified ROM.")
        return False
    
    return False


def interactive_mode(rom_data):
    """Interactive level editor mode."""
    print("\n" + "=" * 60)
    print("B.O.B. Level Editor - Interactive Mode")
    print("=" * 60)
    print("\nCommands:")
    print("  list              - List all tilemaps")
    print("  view <index>      - View tilemap as ASCII")
    print("  export <i> <path> - Export tilemap to file")
    print("  import <i> <path> - Import tilemap from file")
    print("  help              - Show this help")
    print("  quit              - Exit editor")
    print("=" * 60)
    
    while True:
        try:
            cmd = input("\n> ").strip().split()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break
        
        if not cmd:
            continue
        
        command = cmd[0].lower()
        
        if command == 'quit' or command == 'exit':
            print("Exiting...")
            break
        
        elif command == 'help':
            print("\nCommands:")
            print("  list              - List all tilemaps")
            print("  view <index>      - View tilemap as ASCII")
            print("  export <i> <path> - Export tilemap to file")
            print("  import <i> <path> - Import tilemap from file")
            print("  help              - Show this help")
            print("  quit              - Exit editor")
        
        elif command == 'list':
            list_levels(rom_data)
        
        elif command == 'view':
            if len(cmd) < 2:
                print("Usage: view <index>")
                continue
            try:
                index = int(cmd[1])
                view_tilemap(rom_data, index)
            except ValueError:
                print("Error: Invalid index")
        
        elif command == 'export':
            if len(cmd) < 3:
                print("Usage: export <index> <output_path>")
                continue
            try:
                index = int(cmd[1])
                output_path = cmd[2]
                export_tilemap(rom_data, index, output_path)
            except ValueError:
                print("Error: Invalid index")
        
        elif command == 'import':
            if len(cmd) < 3:
                print("Usage: import <index> <input_path>")
                continue
            try:
                index = int(cmd[1])
                input_path = cmd[2]
                output_path = cmd[3] if len(cmd) > 3 else None
                import_tilemap(rom_data, index, input_path, output_path)
            except ValueError:
                print("Error: Invalid index")
        
        else:
            print(f"Unknown command: {command}")
            print("Type 'help' for available commands")


def main():
    parser = argparse.ArgumentParser(
        description='B.O.B. Level Editor CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bob_level_editor.py --rom B.O.B..smc              # Interactive mode
  python bob_level_editor.py --rom B.O.B..smc list         # List levels
  python bob_level_editor.py --rom B.O.B..smc view 0       # View level 0
  python bob_level_editor.py --rom B.O.B..smc export 0 level_0.json
  python bob_level_editor.py --rom B.O.B..smc import 0 modified.json --output modified.sfc
        """
    )
    
    parser.add_argument('--rom', required=True, help='Path to ROM file')
    parser.add_argument('command', nargs='?', default='interactive',
                       choices=['list', 'view', 'export', 'import', 'interactive'],
                       help='Command to execute (default: interactive)')
    parser.add_argument('index', nargs='?', type=int, help='Level index')
    parser.add_argument('--input', '-i', help='Input file path')
    parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    
    # Load ROM
    rom_data = load_rom(args.rom)
    if not rom_data:
        return 1
    
    # Execute command
    if args.command == 'interactive':
        interactive_mode(rom_data)
    
    elif args.command == 'list':
        list_levels(rom_data)
    
    elif args.command == 'view':
        if args.index is None:
            print("Error: --index required for view command")
            return 1
        view_tilemap(rom_data, args.index)
    
    elif args.command == 'export':
        if args.index is None or not args.output:
            print("Error: --index and --output required for export command")
            return 1
        export_tilemap(rom_data, args.index, args.output)
    
    elif args.command == 'import':
        if args.index is None or not args.input:
            print("Error: --index and --input required for import command")
            return 1
        import_tilemap(rom_data, args.index, args.input, args.output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
