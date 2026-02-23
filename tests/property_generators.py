#!/usr/bin/env python3
"""
Property generators for B.O.B. ROM Toolkit

Random data generators for property-based testing.
"""

import random
from typing import List, Tuple


def random_bytes(size: int, seed: int = None) -> bytes:
    """Generate random bytes."""
    if seed is not None:
        random.seed(seed)
    return bytes([random.randint(0, 255) for _ in range(size)])


def random_rom_like_data(size_kb: int = 1024, seed: int = None) -> bytes:
    """
    Generate ROM-like data with valid header.
    
    Creates data that resembles a SNES ROM with:
    - Optional 512-byte copier header
    - Valid header at 0x7FC0
    - Mixed content (code, data, graphics-like regions)
    """
    if seed is not None:
        random.seed(seed)
    
    total_size = size_kb * 1024
    
    # Add 512-byte header (50% chance)
    has_copier_header = random.random() < 0.5
    if has_copier_header:
        header = bytes([random.randint(0, 255) for _ in range(512)])
    else:
        header = b''
    
    # Generate ROM body
    rom_body = bytearray(total_size - len(header))
    
    # Fill with mixed content
    pos = 0
    while pos < len(rom_body):
        region_type = random.random()
        region_size = min(random.randint(256, 4096), len(rom_body) - pos)
        
        if region_type < 0.3:
            # Code-like region (structured bytes)
            for i in range(region_size):
                rom_body[pos + i] = random.choice([
                    0x00, 0x01, 0x02, 0x20, 0x4C, 0x60,  # Common opcodes
                    0xA9, 0xA2, 0xA0, 0x8D, 0xAD, 0x85,  # LDA/STA variants
                    random.randint(0, 255)
                ])
        elif region_type < 0.6:
            # Graphics-like region (moderate entropy)
            for i in range(region_size):
                rom_body[pos + i] = random.randint(0, 15)  # 4bpp-like
        elif region_type < 0.9:
            # Data region (varied)
            for i in range(region_size):
                rom_body[pos + i] = random.randint(0, 255)
        else:
            # Compressed-like region (high entropy)
            for i in range(region_size):
                rom_body[pos + i] = random.randint(0, 255)
        
        pos += region_size
    
    return header + bytes(rom_body)


def random_compressed_stream(size: int = 100, seed: int = None) -> bytes:
    """
    Generate valid compressed stream.
    
    Creates a synthetic LZ77-like compressed stream with:
    - Mix of literals and backreferences
    - Valid chunk headers
    - Proper distance/length encoding
    """
    if seed is not None:
        random.seed(seed)
    
    output = bytearray()
    
    while len(output) < size:
        # Generate chunk header (8 operations)
        header = 0
        chunk_data = bytearray()
        
        for bit in range(8):
            if len(output) >= size:
                break
            
            op_type = random.random()
            
            if op_type < 0.6:
                # Literal (60%)
                header |= (1 << (7 - bit))
                chunk_data.append(random.randint(0, 255))
            else:
                # Backreference (40%)
                header |= (0 << (7 - bit))
                
                # Generate valid distance (1-2047)
                dist = random.randint(1, min(500, len(output) or 1))
                
                # Generate valid length (3-34)
                length = random.randint(3, min(34, size - len(output)))
                
                # Encode as 16-bit LE
                encoded = dist | ((length - 3) << 11)
                chunk_data.append(encoded & 0xFF)
                chunk_data.append((encoded >> 8) & 0xFF)
        
        if chunk_data:
            output.append(header)
            output.extend(chunk_data)
    
    return bytes(output)


def random_tilemap_data(seed: int = None) -> bytes:
    """
    Generate valid SNES tilemap data.
    
    Creates 32x32 tilemap (1024 entries × 2 bytes = 2048 bytes) with:
    - Valid tile IDs (0-1023)
    - Valid CHR banks (0-3)
    - Valid palettes (0-3)
    - Random flip flags
    """
    if seed is not None:
        random.seed(seed)
    
    tilemap = bytearray()
    
    for _ in range(1024):
        tile_id = random.randint(0, 1023)
        chr_bank = random.randint(0, 3)
        palette = random.randint(0, 3)
        x_flip = random.randint(0, 1)
        y_flip = random.randint(0, 1)
        
        entry = tile_id | (chr_bank << 10) | (palette << 12) | (x_flip << 14) | (y_flip << 15)
        
        tilemap.append(entry & 0xFF)
        tilemap.append((entry >> 8) & 0xFF)
    
    return bytes(tilemap)


def random_tile_data(format: str = '2bpp', seed: int = None) -> bytes:
    """
    Generate valid tile data.
    
    Args:
        format: '2bpp' (16 bytes), '4bpp' (32 bytes), or '8bpp' (64 bytes)
        seed: Random seed
    """
    if seed is not None:
        random.seed(seed)
    
    if format == '2bpp':
        size = 16
        max_val = 3
    elif format == '4bpp':
        size = 32
        max_val = 15
    elif format == '8bpp':
        size = 64
        max_val = 255
    else:
        raise ValueError(f"Unknown format: {format}")
    
    return bytes([random.randint(0, max_val) for _ in range(size)])


def shrink_data(data: bytes, strategy: str = 'halving') -> bytes:
    """
    Shrink data for failure minimization.
    
    Args:
        data: Original data
        strategy: 'halving', 'byte_removal', or 'value_reduction'
    """
    if strategy == 'halving':
        # Remove half the data
        return data[:len(data) // 2]
    
    elif strategy == 'byte_removal':
        # Remove every other byte
        return bytes([b for i, b in enumerate(data) if i % 2 == 0])
    
    elif strategy == 'value_reduction':
        # Reduce byte values
        return bytes([max(0, b - 1) for b in data])
    
    return data


# =============================================================================
# Property Invariants
# =============================================================================

def invariant_decompression_deterministic(decompress_func, test_data: bytes, size: int) -> bool:
    """Same input should always produce same output."""
    result1 = decompress_func(test_data, size)
    result2 = decompress_func(test_data, size)
    return result1[0] == result2[0]


def invariant_output_bounded(decompress_func, test_data: bytes, max_size: int) -> bool:
    """Output should never exceed requested size."""
    result = decompress_func(test_data, max_size)
    return len(result[0]) <= max_size


def invariant_empty_input_handling(decompress_func) -> bool:
    """Empty input should be handled gracefully."""
    try:
        result = decompress_func(b'', 0)
        return len(result[0]) == 0
    except:
        return True  # Exception is also acceptable


def invariant_roundtrip_encode_decode(encode_func, decode_func, original: bytes) -> bool:
    """Encode then decode should return original."""
    compressed = encode_func(original)
    decompressed = decode_func(compressed, len(original))
    return decompressed[0] == original


def invariant_entropy_increases_with_randomness(calculate_entropy, iterations: int = 10) -> bool:
    """More random data should have higher entropy."""
    uniform = bytes([0x00] * 256)
    random_data = random_bytes(256)
    
    entropy_uniform = calculate_entropy(uniform)
    entropy_random = calculate_entropy(random_data)
    
    return entropy_random > entropy_uniform


if __name__ == '__main__':
    # Quick test of generators
    print("Testing random generators...")
    
    print(f"  random_bytes(10): {random_bytes(10)[:10]}")
    print(f"  random_rom_like_data(10)[:20]: {random_rom_like_data(10)[:20]}")
    print(f"  random_compressed_stream(50)[:20]: {random_compressed_stream(50)[:20]}")
    print(f"  random_tilemap_data()[:20]: {random_tilemap_data()[:20]}")
    print(f"  random_tile_data('2bpp'): {random_tile_data('2bpp')}")
    
    print("\nAll generators working!")
