#!/usr/bin/env python3
"""
bob_lz_encode.py — B.O.B. LZ77 Encoder

Encodes data using the B.O.B. variant of LZ77 compression.
This is required for a level editor to re-compress modified level data.

Format (matching bob_lz.py decoder):
- 8-bit header per chunk, processed MSB first
- Bit 0: literal byte (copy next byte as-is)
- Bit 1: distance/length pair (16-bit little-endian)
  * Low 11 bits: distance (1-2047)
  * High 5 bits: (length - 3), effective length 3-34
- Max match length: 34 bytes
- Max distance: 2047 bytes
"""

from typing import Tuple, List, Optional


def find_best_match(data: bytes, pos: int, window_start: int) -> Optional[Tuple[int, int]]:
    """
    Find the best backreference match in the sliding window.
    
    Args:
        data: source data to encode
        pos: current position in data
        window_start: earliest position allowed for backreference
    
    Returns:
        Tuple of (distance, length) if match found, None otherwise
    """
    if pos <= window_start:
        return None
    
    max_length = min(34, len(data) - pos)  # Max 34 byte matches
    if max_length < 3:
        return None
    
    best_match = None
    best_length = 0
    best_distance = 0
    
    # Search backwards from current position
    for dist in range(1, pos - window_start + 1):
        match_start = pos - dist
        
        # Count matching bytes
        length = 0
        while length < max_length and data[match_start + length] == data[pos + length]:
            length += 1
        
        # Prefer longer matches, then shorter distances
        if length >= 3:
            if best_match is None or length > best_length or (length == best_length and dist < best_distance):
                best_match = (dist, length)
                best_length = length
                best_distance = dist
    
    return best_match


def bob_lz_encode(data: bytes, lazy: bool = True) -> bytes:
    """
    Encode data using B.O.B. LZ77 compression.
    
    Args:
        data: raw data to compress
        lazy: if True, use lazy matching (try skipping to find longer match)
    
    Returns:
        compressed byte stream
    """
    if not data:
        return bytes()
    
    pos = 0
    output = bytearray()
    
    while pos < len(data):
        chunk_bits = []
        chunk_data = bytearray()
        
        # Process up to 8 operations per chunk
        ops_in_chunk = 0
        
        while ops_in_chunk < 8 and pos < len(data):
            window_start = max(0, pos - 2047)
            
            # Try lazy matching: check if current literal followed by better match
            match = find_best_match(data, pos, window_start)
            
            if match:
                dist, length = match
                
                # Lazy evaluation: check if skipping this literal gives better result
                if lazy and pos + 1 < len(data):
                    next_match = find_best_match(data, pos + 1, window_start)
                    if next_match and next_match[1] > length:
                        # Emit literal first, then match
                        chunk_bits.append(0)  # literal
                        chunk_data.append(data[pos])
                        pos += 1
                        ops_in_chunk += 1
                        
                        if ops_in_chunk < 8:
                            dist, length = next_match
                            chunk_bits.append(1)  # backref
                            chunk_data.append(dist & 0xFF)
                            chunk_data.append((dist >> 8) | ((length - 3) << 3))
                            pos += length
                            ops_in_chunk += 1
                        continue
                
                # Emit backreference
                chunk_bits.append(1)
                chunk_data.append(dist & 0xFF)
                chunk_data.append((dist >> 8) | ((length - 3) << 3))
                pos += length
            else:
                # Emit literal
                chunk_bits.append(0)
                chunk_data.append(data[pos])
                pos += 1
            
            ops_in_chunk += 1
        
        # Build chunk header (bits MSB first)
        header = 0
        for i, bit in enumerate(chunk_bits):
            if bit:
                header |= (1 << (7 - i))
        
        output.append(header)
        output.extend(chunk_data)
    
    return bytes(output)


def bob_lz_encode_exhaustive(data: bytes) -> bytes:
    """
    Encode with exhaustive search (finds optimal matches, slower).
    Use this for verification or small data.
    """
    if not data:
        return bytes()
    
    pos = 0
    output = bytearray()
    
    while pos < len(data):
        chunk_bits = []
        chunk_data = bytearray()
        ops_in_chunk = 0
        
        while ops_in_chunk < 8 and pos < len(data):
            window_start = max(0, pos - 2047)
            
            # Find all matches, pick the longest
            best_dist = 0
            best_length = 0
            
            for dist in range(1, pos - window_start + 1):
                match_start = pos - dist
                length = 0
                while (pos + length < len(data) and 
                       length < 34 and 
                       data[match_start + length] == data[pos + length]):
                    length += 1
                
                if length >= 3 and length > best_length:
                    best_dist = dist
                    best_length = length
            
            if best_length >= 3:
                chunk_bits.append(1)
                chunk_data.append(best_dist & 0xFF)
                chunk_data.append((best_dist >> 8) | ((best_length - 3) << 3))
                pos += best_length
            else:
                chunk_bits.append(0)
                chunk_data.append(data[pos])
                pos += 1
            
            ops_in_chunk += 1
        
        header = 0
        for i, bit in enumerate(chunk_bits):
            if bit:
                header |= (1 << (7 - i))
        
        output.append(header)
        output.extend(chunk_data)
    
    return bytes(output)


def test_encoder():
    """Test the encoder by round-tripping."""
    from bob_lz import bob_lz_decompress
    
    print("Testing LZ77 encoder...")
    
    # Test 1: Simple literal data
    test_data = b"Hello, World! This is a test of the B.O.B. LZ77 encoder."
    compressed = bob_lz_encode(test_data)
    decompressed, consumed = bob_lz_decompress(compressed, len(test_data))
    assert decompressed == test_data, f"Test 1 failed: {decompressed!r} != {test_data!r}"
    print(f"[PASS] Test 1: Literal data ({len(test_data)} bytes -> {len(compressed)} bytes)")
    
    # Test 2: Data with repeated patterns
    test_data = b"A" * 100 + b"B" * 50 + b"ABABABAB" * 10
    compressed = bob_lz_encode(test_data)
    decompressed, consumed = bob_lz_decompress(compressed, len(test_data))
    assert decompressed == test_data, f"Test 2 failed"
    print(f"[PASS] Test 2: Repeated patterns ({len(test_data)} bytes -> {len(compressed)} bytes)")
    
    # Test 3: Known block from ROM (0x1AD34)
    # First decompress to get the original
    rom_path = "rom/B.O.B. (U) [!].smc"
    try:
        from pathlib import Path
        rom_data = Path(rom_path).read_bytes()
        header_offset = 512 if len(rom_data) % 1024 == 512 else 0
        compressed_known = rom_data[header_offset + 0x1AD34:header_offset + 0x1AD34 + 0x1000]
        decompressed_known, consumed = bob_lz_decompress(compressed_known, 0x822)
        
        # Re-encode and decompress again
        re_encoded = bob_lz_encode(decompressed_known)
        re_decoded, _ = bob_lz_decompress(re_encoded, 0x822)
        
        assert re_decoded == decompressed_known, "Known block round-trip failed"
        print(f"[PASS] Test 3: Known ROM block ({len(decompressed_known)} bytes -> {len(re_encoded)} bytes)")
    except FileNotFoundError:
        print("[SKIP] Test 3: ROM file not found")
    
    # Test 4: Empty data
    compressed = bob_lz_encode(b"")
    assert compressed == b"", "Test 4 failed"
    print("[PASS] Test 4: Empty data")
    
    # Test 5: Single byte
    compressed = bob_lz_encode(b"X")
    decompressed, consumed = bob_lz_decompress(compressed, 1)
    assert decompressed == b"X", "Test 5 failed"
    print("[PASS] Test 5: Single byte")
    
    # Test 6: Binary data
    import os
    test_data = bytes(range(256)) * 4  # 1KB of all byte values
    compressed = bob_lz_encode(test_data)
    decompressed, consumed = bob_lz_decompress(compressed, len(test_data))
    assert decompressed == test_data, "Test 6 failed"
    print(f"[PASS] Test 6: Binary data ({len(test_data)} bytes -> {len(compressed)} bytes)")
    
    print("\nAll encoder tests passed!")


if __name__ == "__main__":
    test_encoder()
