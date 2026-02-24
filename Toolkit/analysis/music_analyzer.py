"""
Music Theme Analyzer for Space Funky B.O.B.

Analyzes music theme assignments and sharing.
Source: EQUATES.H music equates, INITLEVE.A:whichthememusic
"""

# Music themes from EQUATES.H
MUSIC_THEMES = {
    'borgtheme': {'id': 3, 'usage': 'Borg Factory, World Maps, Space'},
    'bugtheme': {'id': 4, 'usage': 'Bug Planet, Bubble Forest (shared)'},
    'anctheme': {'id': 5, 'usage': 'Ancient Ruins, Lava World (shared)'},
    'ultratheme': {'id': 6, 'usage': 'Ultra Force'},
}

# Level type to music mapping
LEVEL_MUSIC = {
    'borglevel': 'borgtheme', 'borglevel2': 'borgtheme',
    'borglevel3': 'borgtheme', 'borglevel4': 'borgtheme',
    'buglevel': 'bugtheme', 'bubblelevel': 'bugtheme',  # Shared
    'ancientlevel': 'anctheme', 'lavalevel': 'anctheme',  # Shared
    'ultralevel': 'ultratheme', 'worldlevel': 'borgtheme',
    'worldlevel2': 'borgtheme', 'worldlevel3': 'borgtheme',
    'spacelevel': 'borgtheme',
}

# MIDI files from Disk A
MIDI_FILES = {
    'borgtheme': ['BORGBG0.MID', 'BORGMTK.MID'],
    'bugtheme': ['BUGTRK0.MID', 'BUGMTK.MID'],
    'anctheme': ['TEMPCOL0.MID', 'TEMPMTK.MID'],
    'title': ['TITMTK.MID', 'TITSTD.MID'],
}


def analyze_music():
    """Analyze music theme assignments."""
    return {
        'total_themes': len(MUSIC_THEMES),
        'themes': MUSIC_THEMES,
        'sharing': {
            'bug_bubble': {'theme': 'bugtheme', 'id': 4},
            'ancient_lava': {'theme': 'anctheme', 'id': 5}
        },
        'level_mapping': LEVEL_MUSIC,
        'midi_files': MIDI_FILES
    }


def get_theme_for_level(level_type):
    """Get music theme for level type."""
    return LEVEL_MUSIC.get(level_type, 'borgtheme')


def get_sharing_info():
    """Get theme sharing information."""
    return {
        'bug_bubble': 'Bug and Bubble levels share theme 4 (bugtheme)',
        'ancient_lava': 'Ancient and Lava levels share theme 5 (anctheme)'
    }


if __name__ == '__main__':
    analysis = analyze_music()
    print(f"Music Theme Analysis:")
    print(f"  Total themes: {analysis['total_themes']}")
    print(f"  Theme sharing: {list(analysis['sharing'].keys())}")
    print(f"\nLevel type mapping:")
    for level_type, theme in analysis['level_mapping'].items():
        print(f"  {level_type}: {theme}")
