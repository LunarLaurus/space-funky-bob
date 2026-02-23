"""
Password Handler for Space Funky B.O.B. Level Editor

Handles GET /password/generate/:level and POST /password/validate endpoints.
Source-verified: 6-digit password system from INITLEVE.A:passwords table.
"""

# Password digit mappings from INITLEVE.A:passworddigits
PASSWORD_DIGITS = [0, 2, 4, 6, 8, 10, 12, 14, 32, 34]

# Password frame positions from INITLEVE.A:passwordframe
PASSWORD_FRAME = [
    (0xF0, 0xC0, 12),
    (0xE0, 0xC0, 14),
    (0xD0, 0xC0, 32),
    (0xC0, 0xC0, 34),
    (0x90, 0xC0, 36),
    (0xA0, 0xC0, 38)
]


class PasswordHandler:
    """Handle password generation and validation."""
    
    def __init__(self, world_sequences=None):
        """
        Initialize password handler.
        
        Args:
            world_sequences: Dict of world -> level sequences
        """
        self.world_sequences = world_sequences or {
            0: [0, 1, 2, 9, 4, 22, 6, 5, 14, 20, 21, 18, 13, 11],
            1: [23, 15, 7, 24, 16, 51, 19, 29, 32, 55, 25, 3, 27, 28, 33, 30, 26, 40, 34],
            2: [35, 48, 36, 38, 43, 53, 47, 44, 37, 49, 56, 52, 12, 50, 10, 54, 59]
        }
    
    def generate_password(self, world, level_index):
        """
        Generate 6-digit password for level progression.
        
        Args:
            world: World number (0-2)
            level_index: Level index within world (0-18)
        
        Returns:
            dict: Password data with 6 digits
        """
        if world < 0 or world > 2:
            return {'error': 'Invalid world number (0-2)'}
        
        sequence = self.world_sequences.get(world, [])
        if level_index < 0 or level_index >= len(sequence):
            return {'error': f'Invalid level index for world {world}'}
        
        # Generate password digits (simplified algorithm)
        # Actual algorithm would encode: world, level, boss defeats
        digits = []
        seed = (world * 100) + level_index
        
        for i in range(6):
            digit_index = (seed + i * 7) % len(PASSWORD_DIGITS)
            digits.append(PASSWORD_DIGITS[digit_index])
        
        return {
            'world': world,
            'level_index': level_index,
            'map_number': sequence[level_index],
            'password': {
                'digits': digits,
                'display': ''.join(str(d // 2) for d in digits)  # Simplified display
            },
            'format': '6 digits (0-9)'
        }
    
    def validate_password(self, password_digits):
        """
        Validate 6-digit password and extract progression.
        
        Args:
            password_digits: List of 6 digit values
        
        Returns:
            dict: Validation result with progression data
        """
        if not isinstance(password_digits, list) or len(password_digits) != 6:
            return {
                'valid': False,
                'error': 'Password must be 6 digits'
            }
        
        # Validate each digit is in valid range
        for digit in password_digits:
            if digit not in PASSWORD_DIGITS:
                return {
                    'valid': False,
                    'error': f'Invalid password digit: {digit}'
                }
        
        # Decode progression (simplified)
        # Actual algorithm would decode: world, level, boss defeats
        seed = sum(password_digits) % 300
        world = seed // 100
        level_index = seed % 100
        
        return {
            'valid': True,
            'progression': {
                'world': world,
                'level_index': level_index,
                'bosses_defeated': []  # Would be encoded in actual password
            }
        }
    
    def get_password_format(self):
        """
        Get password format specification.
        
        Returns:
            dict: Password format documentation
        """
        return {
            'format': '6-digit password',
            'digit_values': PASSWORD_DIGITS,
            'frame_positions': PASSWORD_FRAME,
            'storage': '8-byte entries in passwords table',
            'terminator': -1,
            'capacity': '60 passwords (3 worlds x ~20 levels)'
        }
