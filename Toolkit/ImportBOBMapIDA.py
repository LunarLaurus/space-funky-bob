"""
ImportBOBMapIDA.py - Import B.O.B. ROM map into IDA Pro (Enhanced)

Usage:
1. Open your B.O.B. ROM in IDA Pro
2. File -> Script file... (or press Alt+F7)
3. Select this script
4. Select your rom_map.json file when prompted

This script imports region annotations from the B.O.B. ROM Analysis Toolkit
into IDA Pro with full annotations including:
- Memory segments for each region
- Bookmarks at key locations
- Comments describing region purpose
- Data type definitions for tilemaps
- Compressed block markers
- Vector table analysis

Enhanced features (v1.0):
- Automatic segment creation
- Tilemap entry data type definition
- Compressed block annotations
- Region-specific comments
- Error handling and progress reporting

Requires: IDA Pro 7.0 or later with Python support
"""

import idaapi
import ida_segment
import ida_bytes
import ida_nalt
import ida_struct
import ida_name
import ida_kernwin
import json
import os


# =============================================================================
# Data Type Definitions
# =============================================================================

def create_tilemap_entry_type():
    """
    Define SNES tilemap entry structure (16-bit).
    
    Bit layout:
    - Bits 0-9:   Tile ID (0-1023)
    - Bits 10-11: CHR Bank (0-3)
    - Bits 12-13: Palette (0-3)
    - Bit 14:     X-Flip
    - Bit 15:     Y-Flip
    """
    sid = ida_struct.get_struc_id("TilemapEntry")
    
    # Check if type already exists
    if sid != ida_struct.BADADDR:
        print("  TilemapEntry type already exists")
        return sid
    
    # Create new structure
    sid = ida_struct.add_struc(-1, "TilemapEntry")
    sptr = ida_struct.get_struc(sid)
    
    # Add bitfields
    ida_struct.add_bitfield(sptr, "tile_id", 0, 10)      # Bits 0-9
    ida_struct.add_bitfield(sptr, "chr_bank", 10, 2)     # Bits 10-11
    ida_struct.add_bitfield(sptr, "palette", 12, 2)      # Bits 12-13
    ida_struct.add_bitfield(sptr, "x_flip", 14, 1)       # Bit 14
    ida_struct.add_bitfield(sptr, "y_flip", 15, 1)       # Bit 15
    
    print("  Created TilemapEntry data type")
    return sid


# =============================================================================
# Segment Creation
# =============================================================================

def create_segment(region, base_addr=0x800000):
    """
    Create segment for ROM region.
    
    Args:
        region: Region dict with start, size, type, name
        base_addr: Base address for ROM mapping
    """
    start_ea = base_addr + region['start']
    end_ea = start_ea + region['size']
    name = region.get('name', f"region_{region['start']:06X}")
    region_type = region.get('type', 'unknown')
    
    # Check if segment already exists
    existing_seg = ida_segment.get_segment_at(start_ea)
    if existing_seg:
        print(f"  Segment {name} already exists at 0x{start_ea:X}")
        return False
    
    # Create segment
    seg = ida_segment.segment_t()
    seg.start_ea = start_ea
    seg.end_ea = end_ea
    seg.bitness = 0  # 16-bit
    seg.sel = ida_segment.setup_selector(0)
    seg.orgbase = 0
    
    # Set permissions based on type
    perm = ida_segment.SEGPERM_READ
    if region_type != 'code':
        perm |= ida_segment.SEGPERM_WRITE
    if region_type == 'code':
        perm |= ida_segment.SEGPERM_EXEC
    
    # Add segment
    if ida_segment.add_segment_ex(seg, name, 0, perm, ida_segment.ADDSEG_OR_DIE):
        # Set segment type
        if region_type == 'code':
            ida_segment.set_segment_type(seg, ida_segment.SEG_CODE)
        else:
            ida_segment.set_segment_type(seg, ida_segment.SEG_DATA)
        
        print(f"  Created segment: {name} (0x{start_ea:X}, {region['size']} bytes)")
        return True
    else:
        print(f"  Failed to create segment: {name}")
        return False


# =============================================================================
# Bookmarks and Comments
# =============================================================================

def add_bookmark(region, base_addr=0x800000):
    """
    Add IDA bookmark for region.
    
    Args:
        region: Region dict
        base_addr: Base address for ROM mapping
    """
    ea = base_addr + region['start']
    region_type = region.get('type', 'unknown')
    start_offset = region['start']
    
    # Create bookmark name
    bookmark_name = f"{region_type}_{start_offset:06X}"
    
    # Add bookmark
    ida_nalt.set_bookmark(ea, 0, bookmark_name)
    print(f"  Added bookmark: {bookmark_name}")
    return True


def add_comment(region, base_addr=0x800000):
    """
    Add comment describing region.
    
    Args:
        region: Region dict
        base_addr: Base address for ROM mapping
    """
    ea = base_addr + region['start']
    region_type = region.get('type', 'unknown')
    size = region.get('size', 0)
    confidence = region.get('confidence', 0)
    
    # Create comment
    comment = f"B.O.B. ROM Region\nType: {region_type}\nSize: {size} bytes\nConfidence: {confidence:.0%}"
    
    if region_type == 'compressed':
        comment += "\n\nThis is a compressed block.\nDecompress to view actual data."
    elif region_type == 'tilemap':
        comment += "\n\nSNES tilemap format (16-bit entries).\nSee TilemapEntry data type."
    elif region_type == 'code':
        comment += "\n\n65816 code region.\nRun analysis to find functions."
    
    # Set repeatable comment
    ida_bytes.set_cmt(ea, comment, True)
    print(f"  Added comment at 0x{ea:X}")
    return True


# =============================================================================
# Naming
# =============================================================================

def add_region_name(region, base_addr=0x800000):
    """
    Add symbolic name for region.
    
    Args:
        region: Region dict
        base_addr: Base address for ROM mapping
    """
    ea = base_addr + region['start']
    region_type = region.get('type', 'unknown')
    start_offset = region['start']
    
    # Create name
    name = f"{region_type}_{start_offset:06X}"
    
    # Force name creation
    ida_name.set_name(ea, name, ida_name.SN_FORCE)
    print(f"  Created name: {name}")
    return True


# =============================================================================
# Vector Table Analysis
# =============================================================================

def analyze_vector_table(base_addr=0x800000):
    """
    Analyze SNES vector table at 0x7FE0-0x7FFF.
    
    Args:
        base_addr: Base address for ROM mapping
    """
    print("\nAnalyzing vector table...")
    
    # SNES vectors are at 0x7FE0-0x7FFF (LoROM)
    vector_base = base_addr + 0x7FE0
    
    vectors = [
        (0x7FE0, "COP_vector"),    # COP vector
        (0x7FE2, "BRK_vector"),    # BRK vector
        (0x7FE4, "ABORT_vector"),  # ABORT vector
        (0x7FE6, "NMI_vector"),    # NMI vector
        (0x7FE8, "RESET_vector"),  # RESET vector
        (0x7FEA, "IRQ_vector"),    # IRQ vector
    ]
    
    for offset, name in vectors:
        ea = base_addr + offset
        ida_name.set_name(ea, name, ida_name.SN_FORCE)
        ida_bytes.set_cmt(ea, f"SNES {name.replace('_vector', '')} vector", True)
        print(f"  Marked {name} at 0x{ea:X}")


# =============================================================================
# Main Import Function
# =============================================================================

def import_rom_map():
    """Main import function - Enhanced v1.0"""
    
    print("=" * 60)
    print("B.O.B. ROM Map Import for IDA Pro (Enhanced v1.0)")
    print("=" * 60)
    
    # Get rom_map.json from user
    json_path = ida_kernwin.ask_file(False, "*.json", "Select rom_map.json")
    
    if not json_path:
        print("No file selected. Import cancelled.")
        return False
    
    # Load JSON
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return False
    
    mapping = data.get("rom_mapping", "LoROM")
    header_offset = data.get("header_offset", 0)
    regions = data.get("regions", [])
    
    print(f"ROM Mapping: {mapping}")
    print(f"Header Offset: {hex(header_offset)}")
    print(f"Total Regions: {len(regions)}")
    print("=" * 60)
    
    # Base address for IDA (typical SNES ROM load address)
    base_addr = 0x800000
    
    # Create tilemap data type
    print("\nCreating data types...")
    create_tilemap_entry_type()
    
    # Counters
    segment_count = 0
    bookmark_count = 0
    comment_count = 0
    name_count = 0
    error_count = 0
    
    # Process regions
    print("\nProcessing regions...")
    for i, region in enumerate(regions):
        region_type = region.get("type", "unknown")
        start_offset = region.get("start", 0) - header_offset
        
        try:
            # Create segment
            if create_segment(region, base_addr):
                segment_count += 1
            
            # Add bookmark
            if add_bookmark(region, base_addr):
                bookmark_count += 1
            
            # Add comment
            if add_comment(region, base_addr):
                comment_count += 1
            
            # Add name
            if add_region_name(region, base_addr):
                name_count += 1
            
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1} regions...")
        
        except Exception as e:
            print(f"  Error at 0x{start_offset:X}: {e}")
            error_count += 1
    
    # Analyze vector table
    analyze_vector_table(base_addr)
    
    # Summary
    print("\n" + "=" * 60)
    print("Import Complete!")
    print(f"  Segments created: {segment_count}")
    print(f"  Bookmarks added: {bookmark_count}")
    print(f"  Comments added: {comment_count}")
    print(f"  Names created: {name_count}")
    print(f"  Errors: {error_count}")
    print("=" * 60)
    print("\nCheck View -> Open subviews -> Bookmarks to see imported regions")
    print("Check Local Types -> TilemapEntry for tilemap structure")
    print("Check vector table at 0x807FE0-0x807FFF")
    
    return True


# =============================================================================
# Script Entry Point
# =============================================================================

if __name__ == "__main__":
    import_rom_map()
else:
    # Run when loaded as IDA script
    import_rom_map()
