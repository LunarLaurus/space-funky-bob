"""
Death Type Analyzer for Space Funky B.O.B.

Analyzes death types and sound effects.
Source: EQUATES.H death equates, BOB.A death handling
"""

# Death types from EQUATES.H
DEATH_TYPES = {
    0: {'name': 'crumbled', 'sound': 'SFXCRUMBLEDEATH', 'hex': '$95',
        'trigger': 'Walking/crouching death on solid ground'},
    1: {'name': 'drained', 'sound': 'None', 'hex': '-',
        'trigger': 'Energy drained (unused?)'},
    2: {'name': 'sidecrush', 'sound': 'None', 'hex': '-',
        'trigger': 'Squished from side'},
    3: {'name': 'topcrush', 'sound': 'SFXEXPLODE2', 'hex': '$9F',
        'trigger': 'Squished from above/blown up'},
    4: {'name': 'melted', 'sound': 'SFXMELTDEATH', 'hex': '$94',
        'trigger': 'Background drain/melt (mustmelt flag)'},
    5: {'name': 'burned', 'sound': 'Unused', 'hex': '-',
        'trigger': 'Fried by flames'},
}

# Death animation sequences
DEATH_SEQUENCES = {
    'crumbled': {'frames': 13, 'uses': 'shrapneldeath0-24'},
    'topcrush': {'frames': 'instant', 'uses': 'SFXEXPLODE2'},
    'melted': {'frames': 13, 'uses': 'same as crumble'},
}


def analyze_death_types():
    """Analyze death type system."""
    return {
        'total_types': len(DEATH_TYPES),
        'types': DEATH_TYPES,
        'sounds': {
            'SFXCRUMBLEDEATH': '$95',
            'SFXEXPLODE2': '$9F',
            'SFXMELTDEATH': '$94'
        },
        'sequences': DEATH_SEQUENCES
    }


def get_death_sound(death_type):
    """Get sound effect for death type."""
    return DEATH_TYPES.get(death_type, {}).get('sound', 'Unknown')


def get_death_trigger(death_type):
    """Get trigger condition for death type."""
    return DEATH_TYPES.get(death_type, {}).get('trigger', 'Unknown')


if __name__ == '__main__':
    analysis = analyze_death_types()
    print(f"Death Type Analysis:")
    print(f"  Total types: {analysis['total_types']}")
    print(f"\nDeath types:")
    for type_id, data in analysis['types'].items():
        print(f"  {type_id}: {data['name']} - {data['sound']} ({data['trigger']})")
