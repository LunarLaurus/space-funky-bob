#!/usr/bin/env python3
"""
Compare main project with bob_data directory to identify what the 'pickle' branch contains.
"""

import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\Lauren\Documents\space-funky-bob - Copy")
BOB_DATA = PROJECT_ROOT / "bob_data"

# Directories to ignore in comparison
IGNORE_DIRS = {
    '.git', '.qwen', '.planning', '.github', '.pytest_cache', 
    '__pycache__', 'myEnv', 'venv', '.venv', 'node_modules',
    '.git-ignored'
}

# Files to ignore
IGNORE_FILES = {
    '.gitignore', '.gitattributes', '.DS_Store', 'Thumbs.db',
    '*.pyc', '*.pyo'
}

def should_ignore(path: Path) -> bool:
    """Check if path should be ignored."""
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
        if part.startswith('.'):
            return True
    if path.suffix in ['.pyc', '.pyo']:
        return True
    return False

def get_files_in_directory(root: Path) -> dict:
    """Get all files in directory with relative paths."""
    files = {}
    for filepath in root.rglob('*'):
        if filepath.is_file() and not should_ignore(filepath.relative_to(root)):
            rel_path = str(filepath.relative_to(root))
            files[rel_path] = {
                'size': filepath.stat().st_size,
                'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            }
    return files

def main():
    print("=" * 80)
    print("BOB_DATA vs MAIN PROJECT COMPARISON REPORT")
    print("Generated:", datetime.now().isoformat())
    print("=" * 80)
    print()
    
    # Get files from both locations
    print("Scanning main project...")
    project_files = get_files_in_directory(PROJECT_ROOT)
    
    print("Scanning bob_data directory...")
    bob_data_files = get_files_in_directory(BOB_DATA)
    
    # Analyze differences
    project_only = set(project_files.keys()) - set(bob_data_files.keys())
    bob_data_only = set(bob_data_files.keys()) - set(project_files.keys())
    common_files = set(project_files.keys()) & set(bob_data_files.keys())
    
    # Check for modified files in common
    modified_files = []
    for f in common_files:
        if project_files[f]['size'] != bob_data_files[f]['size']:
            modified_files.append(f)
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Main project files: {len(project_files)}")
    print(f"bob_data files: {len(bob_data_files)}")
    print(f"Files only in main project: {len(project_only)}")
    print(f"Files only in bob_data: {len(bob_data_only)}")
    print(f"Common files: {len(common_files)}")
    print(f"Modified files (size differs): {len(modified_files)}")
    
    # Write detailed report
    report_path = PROJECT_ROOT / "bob_data_comparison_report.txt"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("BOB_DATA vs MAIN PROJECT COMPARISON REPORT\n")
        f.write("Generated: " + datetime.now().isoformat() + "\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Main project files: {len(project_files)}\n")
        f.write(f"bob_data files: {len(bob_data_files)}\n")
        f.write(f"Files only in main project: {len(project_only)}\n")
        f.write(f"Files only in bob_data: {len(bob_data_only)}\n")
        f.write(f"Common files: {len(common_files)}\n")
        f.write(f"Modified files (size differs): {len(modified_files)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("FILES UNIQUE TO BOB_DATA ('pickle' branch content)\n")
        f.write("=" * 80 + "\n\n")
        
        # Group by directory
        by_dir = {}
        for file_path in sorted(bob_data_only):
            dir_name = file_path.split(os.sep)[0] if os.sep in file_path else file_path
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append(file_path)
        
        for dir_name, files in sorted(by_dir.items()):
            f.write(f"\n{dir_name}/\n")
            f.write("-" * 40 + "\n")
            for file_path in files:
                size = bob_data_files[file_path]['size']
                f.write(f"  + {file_path} ({size:,} bytes)\n")
        
        f.write("\n\n")
        f.write("=" * 80 + "\n")
        f.write("MODIFIED FILES (different from main project)\n")
        f.write("=" * 80 + "\n\n")
        
        for file_path in sorted(modified_files):
            proj_size = project_files[file_path]['size']
            bob_size = bob_data_files[file_path]['size']
            f.write(f"  ~ {file_path}\n")
            f.write(f"    Main: {proj_size:,} bytes | bob_data: {bob_size:,} bytes\n")
        
        f.write("\n\n")
        f.write("=" * 80 + "\n")
        f.write("BOB_DATA DIRECTORY STRUCTURE\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("Top-level directories and files:\n")
        f.write("-" * 40 + "\n")
        for item in sorted(BOB_DATA.iterdir()):
            if item.is_dir():
                f.write(f"  [DIR]  {item.name}/\n")
            else:
                f.write(f"  [FILE] {item.name} ({item.stat().st_size:,} bytes)\n")
        
        f.write("\n\n")
        f.write("=" * 80 + "\n")
        f.write("KEY FEATURES IN BOB_DATA\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("""
The bob_data directory contains the following unique components:

1. ROM FILES
   - B.O.B..smc (original ROM)
   - B.O.B._edit.smc (edited ROM)
   - backup/B.O.B..smc

2. BRANCH ARCHIVES
   - branch-001-lz77.tar.gz
   - branch-002-level-pointers.tar.gz
   - branch-003-rom-export.tar.gz

3. EXTRACTED DATA (JSON format)
   - data/ENEMIES.json
   - data/LEVELS.json
   - data/TILES.json
   - data/TILESETS.json

4. LEVEL DATA
   - levels/all_levels.json
   - levels/world_1.json
   - levels/world_2.json
   - levels/world_3.json

5. TILESET IMAGES
   - tilesets/tileset_*.png (12 tileset images)
   - tilesets/tileset_*.json (metadata)

6. WEB-BASED LEVEL EDITOR
   - editor/index.html
   - editor/level_editor.py
   - editor/server.py
   - editor/js/*.js (app, renderer, audio, API)
   - editor/css/styles.css
   - editor/lib/*.py (level_extract, lz77, rom_parser, tileset)

7. LEVEL EDITOR TOOLS
   - branch-002-level-pointers/find_level_pointers.py
   - branch-002-level-pointers/level_import.py
   - extract_rom_levels.py
   - tileset_extract.py

8. ROM EXPORT SYSTEM
   - branch-003-rom-export/resume_system.py
   - branch-003-rom-export/state/current.json

9. SOURCE CODE ARCHIVES
   - Space Funky B.O.B. Source Files/Disk A-F
   - Space_Funky_BOB_Source_Code.7z

10. TEST SUITE
    - tests/test_data.py
    - tests/test_editor.py

NOTE: There is NO 'pickle' branch in the git repository.
      The bob_data directory appears to be a working directory for
      feature development, possibly nicknamed 'pickle' branch.
""")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    print()
    print(f"Report saved to: {report_path}")
    print()
    print("Key bob_data directories:")
    for dir_name in sorted(by_dir.keys()):
        print(f"  + {dir_name}/ ({len(by_dir[dir_name])} files)")

if __name__ == "__main__":
    main()
