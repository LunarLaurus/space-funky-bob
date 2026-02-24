"""
Password Generator for Space Funky B.O.B.

Generates and validates 6-digit passwords.
Source: INITLEVE.A:passwords table
"""

# Password digit values from INITLEVE.A:passworddigits
PASSWORD_DIGITS = [0, 2, 4, 6, 8, 10, 12, 14, 32, 34]

# World sequences
WORLD_SEQUENCES = {
    0: [0, 1, 2, 9, 4, 22, 6, 5, 14, 20, 21, 18, 13, 11],
    1: [23, 15, 7, 24, 16, 51, 19, 29, 32, 55, 25, 3, 27, 28, 33, 30, 26, 40, 34],
    2: [35, 48, 36, 38, 43, 53, 47, 44, 37, 49, 56, 52, 12, 50, 10, 54, 59],
}


def generate_password(world, level_index):
    """
    Generate 6-digit password for level progression.
    
    Args:
        world: World number (0-2)
        level_index: Level index within world
    
    Returns:
        dict: Password with digits
    """
    if world < 0 or world > 2:
        return {'error': 'Invalid world (0-2)'}
    
    sequence = WORLD_SEQUENCES.get(world, [])
    if level_index < 0 or level_index >= len(sequence):
        return {'error': f'Invalid level index for world {world}'}
    
    # Generate password digits (simplified algorithm)
    seed = (world * 100) + level_index
    digits = []
    for i in range(6):
        digit_index = (seed + i * 7) % len(PASSWORD_DIGITS)
        digits.append(PASSWORD_DIGITS[digit_index])
    
    return {
        'world': world,
        'level_index': level_index,
        'map_number': sequence[level_index],
        'password': {
            'digits': digits,
            'display': ''.join(str(d // 2) for d in digits)
        }
    }


def validate_password(digits):
    """
    Validate 6-digit password.
    
    Args:
        digits: List of 6 digit values
    
    Returns:
        dict: Validation result
    """
    if len(digits) != 6:
        return {'valid': False, 'error': 'Password must be 6 digits'}
    
    for digit in digits:
        if digit not in PASSWORD_DIGITS:
            return {'valid': False, 'error': f'Invalid digit: {digit}'}
    
    # Decode progression (simplified)
    seed = sum(digits) % 300
    world = seed // 100
    level_index = seed % 100
    
    return {
        'valid': True,
        'progression': {'world': world, 'level_index': level_index}
    }


def get_password_format():
    """Get password format specification."""
    return {
        'format': '6-digit password',
        'digit_values': PASSWORD_DIGITS,
        'storage': '8-byte entries in passwords table',
        'terminator': -1,
        'capacity': '60 passwords (3 worlds x ~20 levels)'
    }


if __name__ == '__main__':
    # Test password generation
    for world in range(3):
        for level in range(min(3, len(WORLD_SEQUENCES[world]))):
            result = generate_password(world, level)
            print(f"World {world}, Level {level}: {result['password']['display']}")
