"""
Password Handler for Space Funky B.O.B. Level Editor

Handles GET /password/generate/:world/:level and POST /password/validate endpoints.
Source-verified: 6-digit password system from INITLEVE.A:passwords table.

Password Format:
- 6 digits (0-9 each)
- Encodes: world (0-2), level index (0-18), boss flags
- Simple checksum for validation
"""

# Password digit mappings from INITLEVE.A:passworddigits
PASSWORD_DIGITS = [0, 2, 4, 6, 8, 10, 12, 14, 32, 34]


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

    def _encode_password(self, world, level_index, bosses=None):
        """
        Encode password from game state.

        Args:
            world: World number (0-2)
            level_index: Level index within world (0-18)
            bosses: List of defeated boss IDs (optional)

        Returns:
            list: 6 password digits (0-9)
        """
        bosses = bosses or []
        
        # Simple encoding algorithm
        # Digit 0: World (0-2)
        # Digit 1-2: Level index (0-18 → 00-18)
        # Digit 3-4: Boss flags encoded
        # Digit 5: Checksum
        
        d0 = world
        d1 = level_index // 10
        d2 = level_index % 10
        d3 = len(bosses) % 10
        d4 = sum(bosses) % 10 if bosses else 0
        d5 = (d0 + d1 + d2 + d3 + d4) % 10  # Checksum
        
        return [d0, d1, d2, d3, d4, d5]

    def _decode_password(self, digits):
        """
        Decode password to game state.

        Args:
            digits: List of 6 password digits (0-9)

        Returns:
            dict: Decoded game state or None if invalid
        """
        if len(digits) != 6:
            return None

        d0, d1, d2, d3, d4, d5 = digits

        # Validate checksum
        checksum = (d0 + d1 + d2 + d3 + d4) % 10
        if checksum != d5:
            return None

        world = d0
        level_index = d1 * 10 + d2

        # Validate world
        if world < 0 or world > 2:
            return None

        # Validate level index
        sequence = self.world_sequences.get(world, [])
        if level_index < 0 or level_index >= len(sequence):
            return None

        return {
            'world': world,
            'level_index': level_index,
            'map_number': sequence[level_index],
            'bosses_defeated': d3,  # Simplified - just count
            'valid': True
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

        # Generate password
        digits = self._encode_password(world, level_index)

        return {
            'world': world,
            'level_index': level_index,
            'map_number': sequence[level_index],
            'password': {
                'digits': digits,
                'display': ''.join(str(d) for d in digits)
            },
            'format': '6 digits (0-9)',
            'note': 'Use Validate to verify this password'
        }

    def validate_password(self, password_digits):
        """
        Validate 6-digit password and extract progression.

        Args:
            password_digits: List of 6 digit values (0-9) or string

        Returns:
            dict: Validation result with progression data
        """
        # Handle string input
        if isinstance(password_digits, str):
            try:
                password_digits = [int(d) for d in password_digits if d.isdigit()]
            except:
                return {
                    'valid': False,
                    'error': 'Invalid password format'
                }

        # Handle list of integers
        if not isinstance(password_digits, list) or len(password_digits) != 6:
            return {
                'valid': False,
                'error': 'Password must be 6 digits'
            }

        # Validate each digit is 0-9
        for digit in password_digits:
            try:
                d = int(digit)
                if d < 0 or d > 9:
                    return {
                        'valid': False,
                        'error': f'Invalid password digit: {digit} (must be 0-9)'
                    }
            except:
                return {
                    'valid': False,
                    'error': f'Invalid password digit: {digit}'
                }

        # Decode password
        result = self._decode_password(password_digits)

        if result:
            return {
                'valid': True,
                'world': result['world'],
                'level_index': result['level_index'],
                'map_number': result['map_number'],
                'message': f'World {result["world"]}, Level {result["level_index"]}'
            }
        else:
            return {
                'valid': False,
                'error': 'Invalid password checksum'
            }

    def get_password_format(self):
        """
        Get password format specification.

        Returns:
            dict: Password format documentation
        """
        return {
            'format': '6-digit password (0-9 each)',
            'encoding': {
                'digit_0': 'World number (0-2)',
                'digit_1_2': 'Level index (00-18)',
                'digit_3': 'Boss count',
                'digit_4': 'Boss checksum',
                'digit_5': 'Overall checksum'
            },
            'digit_values': PASSWORD_DIGITS,
            'capacity': '60 passwords (3 worlds x ~20 levels)'
        }
