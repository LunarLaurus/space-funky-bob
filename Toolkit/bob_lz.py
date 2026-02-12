#!/usr/bin/env python3
"""
bob_lz.py — B.O.B. LZ77 Decoder

Implementation of the B.O.B. (Space Funky B.O.B.) variant of LZ77 compression
used in the SNES game. This decoder handles the specific quirks of the format
including overlapping copies and reports decode anomalies.

Format specification (from original documentation by GuyPerfect):
- Chunks preceded by single status byte (8 bits processed MSB first)
- Bit 0: literal byte (copy next byte as-is)
- Bit 1: distance/length pair (16-bit little-endian value)
  * Low 11 bits: distance (1-2047)
  * High 5 bits: (length - 3), so length is 3-34
- Distance of 0 or distance > current output size = error
- Length may exceed distance (overlapping copy with sliding window semantics)

Known B.O.B. ROM details:
- Title: "B.O.B."
- Mapping: LoROM Fast
- ROM size: 8 Mbits (1 MB)
- Header location: 0x7FC0 (LoROM)
- Fixed byte: 0x69
- Checksum: 0x7379, Complement: 0x8C86

Original LZ decompression reverse engineered by GuyPerfect.
See: eludevisibility.org / superfamicom.org for source documentation.
"""

def bob_lz_decompress(src_bytes, dec_len):
    """
    Decompress a B.O.B.-variant LZ77 stream.
    
    Args:
        src_bytes: bytes-like compressed stream
        dec_len: expected decompressed size (int)
    
    Returns:
        tuple: (decompressed_bytes, consumed_input_bytes)
    
    Raises:
        ValueError: on unrecoverable decode error with descriptive message
    """
    s = 0  # source position
    d = 0  # destination position
    out = bytearray(dec_len)
    src = src_bytes
    
    while d < dec_len:
        if s >= len(src):
            raise ValueError(f"unexpected end of input at src offset {s}")
        
        cHdr = src[s]
        s += 1
        
        # Process 8 bits MSB first
        for bit in range(8):
            bitval = (cHdr >> (7 - bit)) & 1
            
            if bitval == 0:
                # Literal byte
                if s >= len(src):
                    raise ValueError(f"literal expects a byte but input ended at offset {s}")
                out[d] = src[s]
                s += 1
                d += 1
            else:
                # Distance/length pair
                if s + 1 >= len(src):
                    raise ValueError(f"distance/length expects two bytes but input ended at offset {s}")
                
                temp = src[s] | (src[s + 1] << 8)
                s += 2
                
                dist = temp & 0x7FF  # Low 11 bits
                length = (temp >> 11) + 3  # High 5 bits + 3
                
                # Validate distance
                if dist == 0:
                    raise ValueError(f"invalid distance 0 at output offset {d}")
                if dist > d:
                    raise ValueError(f"invalid distance {dist} > current output size {d} at output offset {d}")
                
                # Copy with overlapping support (sliding window)
                for _ in range(length):
                    if d >= dec_len:
                        break
                    out[d] = out[d - dist]
                    d += 1
            
            if d >= dec_len:
                break
    
    return bytes(out), s


def bob_lz_decompress_exploratory(src_bytes, max_dec_len=65536):
    """
    Exploratory decompression that doesn't require exact decompressed length.
    Useful for scanning unknown compressed blocks.
    
    Args:
        src_bytes: bytes-like compressed stream
        max_dec_len: maximum output size to prevent runaway (default 64KB)
    
    Returns:
        tuple: (decompressed_bytes, consumed_input_bytes, error_msg or None)
    """
    s = 0
    d = 0
    out = bytearray()
    src = src_bytes
    error_msg = None
    
    try:
        while d < max_dec_len and s < len(src):
            cHdr = src[s]
            s += 1
            
            for bit in range(8):
                bitval = (cHdr >> (7 - bit)) & 1
                
                if bitval == 0:
                    if s >= len(src):
                        error_msg = f"input ended expecting literal at offset {s}"
                        break
                    out.append(src[s])
                    s += 1
                    d += 1
                else:
                    if s + 1 >= len(src):
                        error_msg = f"input ended expecting dist/len at offset {s}"
                        break
                    
                    temp = src[s] | (src[s + 1] << 8)
                    s += 2
                    
                    dist = temp & 0x7FF
                    length = (temp >> 11) + 3
                    
                    if dist == 0 or dist > d:
                        error_msg = f"invalid distance {dist} at output offset {d}"
                        break
                    
                    for _ in range(length):
                        if d >= max_dec_len:
                            break
                        out.append(out[d - dist])
                        d += 1
                
                if error_msg or d >= max_dec_len:
                    break
            
            if error_msg:
                break
    except Exception as e:
        error_msg = str(e)
    
    return bytes(out), s, error_msg


# Unit tests
def test_bob_lz():
    """Run unit tests for the B.O.B. LZ decoder."""
    print("Running B.O.B. LZ decoder unit tests...")
    
    # Test 1: Simple literal bytes
    # Status byte 0x00 = all literals
    compressed = bytes([0x00, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48])
    expected = b"ABCDEFGH"
    result, consumed = bob_lz_decompress(compressed, 8)
    assert result == expected, f"Test 1 failed: {result} != {expected}"
    assert consumed == 9, f"Test 1 consumed {consumed}, expected 9"
    print("[PASS] Test 1: Literal bytes")
    
    # Test 2: Overlapping copy with backreference  
    # Create "ABC" then copy dist=3, len=8 to get "ABCABCAB"
    # Chunk 0x08 = 0b00001000 = first 4 bits are literal (0), bit 4 is backref (1), rest literal
    # Actually easier: 0xE0 = 0b11100000 = 3 backref bits first, then 5 literals
    # WRONG - bits processed MSB first, so 0x08 = literal,literal,literal,backref,literal,literal,literal,literal
    # Let me use: 0x10 = 0b00010000 = 3 literals, 1 backref, 4 literals (but we'll stop at 8 bytes)
    # Chunk 0x10: bits MSB first = 0,0,0,1,0,0,0,0
    # So: literal, literal, literal, BACKREF, then 4 more literals
    compressed = bytes([
        0x10,  # chunk header
        0x41, 0x42, 0x43,  # 3 literals: "ABC"
        0x03, 0x28  # backref: dist=3, len=8
    ])
    expected = b"ABCABCAB"
    result, consumed = bob_lz_decompress(compressed, 8)
    assert result == expected, f"Test 2 failed: got {result!r}, expected {expected!r}"
    print("[PASS] Test 2: Overlapping copy")
    
    # Test 3: Invalid distance (zero)
    compressed = bytes([0x80, 0x00, 0x00])
    try:
        bob_lz_decompress(compressed, 8)
        assert False, "Test 3 should have raised ValueError"
    except ValueError as e:
        assert "invalid distance 0" in str(e)
        print("[PASS] Test 3: Zero distance error")
    
    # Test 4: Invalid distance (too large)
    # After one literal "A", try to copy from distance 2047 (which is > current output size of 1)
    # Chunk 0x40 = 0b01000000: literal, backref, then 6 literals
    compressed = bytes([0x40, 0x41, 0xFF, 0x07])  # "A" + backref(dist=2047, len=3)
    try:
        bob_lz_decompress(compressed, 8)
        assert False, "Test 4 should have raised ValueError"
    except ValueError as e:
        assert "invalid distance" in str(e) or "distance" in str(e).lower()
        print("[PASS] Test 4: Distance too large error")
    
    # Test 5: Exploratory mode
    compressed = bytes([0x00, 0x48, 0x45, 0x4C, 0x4C, 0x4F, 0x20, 0x42, 0x4F])
    result, consumed, error = bob_lz_decompress_exploratory(compressed)
    assert error is None
    assert result == b"HELLO BO"
    print("[PASS] Test 5: Exploratory decompression")
    
    print("\nAll tests passed! [SUCCESS]")


if __name__ == "__main__":
    test_bob_lz()
