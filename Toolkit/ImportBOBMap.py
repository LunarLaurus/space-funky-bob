"""
ImportBOBMap.py - Import B.O.B. ROM map into Ghidra

Usage:
1. Open your B.O.B. ROM in Ghidra
2. Window -> Script Manager
3. Click "Refresh" to find this script
4. Double-click to run
5. Select your rom_map.json file when prompted

This script imports region annotations from the B.O.B. ROM Analysis Toolkit
into Ghidra as bookmarks for easy navigation and analysis.
"""

import json
from ghidra.program.model.symbol import SourceType
from ghidra.program.model.address import AddressSet


def rom_to_snes_lorom(rom_offset):
    """Convert ROM offset to SNES address for LoROM mapping"""
    bank = (rom_offset // 0x8000)
    offset_in_bank = rom_offset % 0x8000
    snes_addr = (bank << 16) | (0x8000 + offset_in_bank)
    return snes_addr


def rom_to_snes_hirom(rom_offset):
    """Convert ROM offset to SNES address for HiROM mapping"""
    return 0xC00000 + rom_offset


def import_rom_map():
    """Main import function"""
    
    # Get rom_map.json from user
    rom_map_file = askFile("Select rom_map.json", "Open")
    
    if not rom_map_file:
        print("No file selected. Import cancelled.")
        return
    
    # Load JSON
    try:
        with open(rom_map_file.getAbsolutePath(), 'r') as f:
            data = json.load(f)
    except Exception as e:
        print("Error loading JSON: " + str(e))
        return
    
    mapping = data.get("rom_mapping", "LoROM")
    header_offset = data.get("header_offset", 0)
    regions = data.get("regions", [])
    
    print("=" * 50)
    print("B.O.B. ROM Map Import")
    print("=" * 50)
    print("ROM Mapping: " + mapping)
    print("Header Offset: " + hex(header_offset))
    print("Total Regions: " + str(len(regions)))
    print("=" * 50)
    
    # Base address (should match import settings)
    base = 0x808000 if mapping == "LoROM" else 0xC00000
    
    # Create bookmarks for each region
    bookmark_mgr = currentProgram.getBookmarkManager()
    
    success_count = 0
    error_count = 0
    
    for i, region in enumerate(regions):
        region_type = region.get("type", "unknown")
        start_offset = region.get("start", 0) - header_offset
        size = region.get("size", 0)
        confidence = region.get("confidence", 0)
        
        # Convert to Ghidra address
        try:
            if mapping == "LoROM":
                snes_addr = rom_to_snes_lorom(start_offset)
            else:
                snes_addr = rom_to_snes_hirom(start_offset)
            
            addr = currentProgram.getAddressFactory().getAddress(hex(snes_addr))
            
            if addr is None:
                print("Error: Invalid address " + hex(snes_addr))
                error_count += 1
                continue
            
            # Create bookmark
            description = "{} | size={} | confidence={}%".format(
                region_type, 
                region.get("size_hex", hex(size)), 
                confidence
            )
            
            bookmark_mgr.setBookmark(
                addr,
                "Analysis",
                region_type.upper(),
                description
            )
            
            success_count += 1
            
            # For high-confidence code regions, try to disassemble
            if region_type == "code" and confidence > 80:
                try:
                    addr_set = AddressSet(addr, addr.add(min(size - 1, 0x1000)))
                    if not currentProgram.getListing().getInstructionAt(addr):
                        disassemble(addr)
                except:
                    pass  # Disassembly may fail, that's OK
            
            if (i + 1) % 50 == 0:
                print("Processed {} regions...".format(i + 1))
                
        except Exception as e:
            print("Error at " + hex(start_offset) + ": " + str(e))
            error_count += 1
    
    print("=" * 50)
    print("Import Complete!")
    print("  Success: " + str(success_count))
    print("  Errors: " + str(error_count))
    print("=" * 50)
    print("Check Window -> Bookmarks to see imported regions")


# Run the import
if __name__ == "__main__":
    import_rom_map()
