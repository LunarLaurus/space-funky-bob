"""
Extract Music Themes from B.O.B. ROM

Extracts music theme assignments from EQUATES.H.
Output: data/music_themes.json
"""

import json
from pathlib import Path

# Music theme equates from EQUATES.H
MUSIC_THEMES = {
    'borgtheme': {'id': 3, 'levels': ['borg', 'borg2', 'borg3', 'borg4', 'world', 'space']},
    'bugtheme': {'id': 4, 'levels': ['bug', 'bubble']},  # Shared
    'anctheme': {'id': 5, 'levels': ['ancient', 'lava']},  # Shared
    'ultratheme': {'id': 6, 'levels': ['ultra']},
}

# MIDI files from Disk A
MIDI_FILES = [
    'BORGBG0.MID', 'BORGMTK.MID',  # Borg theme
    'BUGTRK0.MID', 'BUGMTK.MID',   # Bug theme
    'TEMPCOL0.MID', 'TEMPMTK.MID', # Ancient theme
    'TITMTK.MID', 'TITSTD.MID',    # Title theme
]


def extract_music(output_dir):
    """Extract music theme data."""
    print("Extracting music theme data...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    music_data = {
        'metadata': {
            'source': 'EQUATES.H',
            'total_themes': 4,
            'theme_sharing': True
        },
        'themes': MUSIC_THEMES,
        'sharing': {
            'bug_bubble': {
                'theme': 'bugtheme',
                'id': 4,
                'note': 'Bug and Bubble levels share the same music theme'
            },
            'ancient_lava': {
                'theme': 'anctheme',
                'id': 5,
                'note': 'Ancient and Lava levels share the same music theme'
            }
        },
        'midi_files': {
            'source': 'Disk A/bob music files/',
            'files': MIDI_FILES
        }
    }
    
    # Save music data
    output_file = output_dir / 'music_themes.json'
    with open(output_file, 'w') as f:
        json.dump(music_data, f, indent=2)
    
    print(f"Extracted music themes to {output_file}")
    return music_data


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract music themes from B.O.B.')
    parser.add_argument('--output', default='../data', help='Output directory')
    
    args = parser.parse_args()
    extract_music(args.output)
