#!/usr/bin/env python3
"""
bob_map.py — B.O.B. ROM Code/Data Region Mapper

Analyzes a SNES ROM to classify regions as code, data, compressed blocks,
or graphics. Uses 65816 disassembly, entropy analysis, opcode density,
and pointer table detection.

Outputs:
- rom_map.json: JSON map of all regions
- rom_map.html: Interactive HTML visualization

Usage:
    python bob_map.py --rom SpaceFunkyBob.sfc --candidates out/candidates.json --outdir out/
"""

import argparse
import json
import math
from pathlib import Path
from collections import defaultdict


# 65816 opcode tables (simplified for code detection)
# Format: opcode -> (mnemonic, length, is_terminator)
OPCODES = {
    0x00: ("BRK", 2, True),
    0x01: ("ORA", 2, False),
    0x02: ("COP", 2, True),
    0x03: ("ORA", 2, False),
    0x04: ("TSB", 2, False),
    0x05: ("ORA", 2, False),
    0x06: ("ASL", 2, False),
    0x08: ("PHP", 1, False),
    0x09: ("ORA", 2, False),  # Immediate (size varies with M flag)
    0x0A: ("ASL", 1, False),
    0x0D: ("ORA", 3, False),
    0x0E: ("ASL", 3, False),
    0x10: ("BPL", 2, False),
    0x18: ("CLC", 1, False),
    0x19: ("ORA", 3, False),
    0x1A: ("INC", 1, False),
    0x20: ("JSR", 3, False),
    0x22: ("JSL", 4, False),
    0x28: ("PLP", 1, False),
    0x29: ("AND", 2, False),
    0x2A: ("ROL", 1, False),
    0x2C: ("BIT", 3, False),
    0x30: ("BMI", 2, False),
    0x38: ("SEC", 1, False),
    0x40: ("RTI", 1, True),
    0x48: ("PHA", 1, False),
    0x4C: ("JMP", 3, False),
    0x5C: ("JMP", 4, False),  # JML
    0x60: ("RTS", 1, True),
    0x6B: ("RTL", 1, True),
    0x68: ("PLA", 1, False),
    0x78: ("SEI", 1, False),
    0x80: ("BRA", 2, False),
    0x85: ("STA", 2, False),
    0x86: ("STX", 2, False),
    0x88: ("DEY", 1, False),
    0x8A: ("TXA", 1, False),
    0x8D: ("STA", 3, False),
    0x90: ("BCC", 2, False),
    0x98: ("TYA", 1, False),
    0x9A: ("TXS", 1, False),
    0xA0: ("LDY", 2, False),
    0xA2: ("LDX", 2, False),
    0xA5: ("LDA", 2, False),
    0xA8: ("TAY", 1, False),
    0xA9: ("LDA", 2, False),
    0xAA: ("TAX", 1, False),
    0xAD: ("LDA", 3, False),
    0xB0: ("BCS", 2, False),
    0xB8: ("CLV", 1, False),
    0xBA: ("TSX", 1, False),
    0xC0: ("CPY", 2, False),
    0xC2: ("REP", 2, False),
    0xC8: ("INY", 1, False),
    0xC9: ("CMP", 2, False),
    0xCA: ("DEX", 1, False),
    0xD0: ("BNE", 2, False),
    0xD8: ("CLD", 1, False),
    0xE0: ("CPX", 2, False),
    0xE2: ("SEP", 2, False),
    0xE8: ("INX", 1, False),
    0xEA: ("NOP", 1, False),
    0xF0: ("BEQ", 2, False),
    0xF8: ("SED", 1, False),
    0xFA: ("PLX", 1, False),
    0xFB: ("XCE", 1, False),
}


def calculate_entropy(data):
    """Calculate Shannon entropy."""
    if not data:
        return 0.0
    freq = [0] * 256
    for byte in data:
        freq[byte] += 1
    entropy = 0.0
    data_len = len(data)
    for count in freq:
        if count > 0:
            p = count / data_len
            entropy -= p * math.log2(p)
    return entropy


def analyze_opcode_density(rom, offset, length=256):
    """
    Analyze opcode density in a region.
    
    Returns:
        tuple: (valid_opcode_ratio, avg_instruction_length)
    """
    if offset + length > len(rom):
        length = len(rom) - offset
    
    data = rom[offset:offset + length]
    valid_count = 0
    total_instructions = 0
    pos = 0
    
    while pos < len(data):
        opcode = data[pos]
        if opcode in OPCODES:
            valid_count += 1
            _, instr_len, _ = OPCODES[opcode]
            pos += instr_len
        else:
            pos += 1
        total_instructions += 1
    
    if total_instructions == 0:
        return 0.0, 0.0
    
    valid_ratio = valid_count / total_instructions
    avg_len = length / total_instructions if total_instructions > 0 else 0
    
    return valid_ratio, avg_len


def find_pointer_tables(rom, mapping="LoROM"):
    """
    Scan for pointer tables (sequences of addresses pointing into ROM).
    
    Returns:
        list: offsets of likely pointer tables
    """
    pointer_tables = []
    rom_size = len(rom)
    
    # Scan for sequences of valid pointers
    for offset in range(0, rom_size - 6, 2):
        # Read 3 consecutive 16-bit values
        ptrs = []
        valid = True
        
        for i in range(3):
            if offset + (i * 2) + 1 >= rom_size:
                valid = False
                break
            ptr = rom[offset + (i * 2)] | (rom[offset + (i * 2) + 1] << 8)
            
            # Check if pointer is valid ROM address (LoROM $8000-$FFFF maps to ROM)
            if mapping == "LoROM":
                if 0x8000 <= ptr <= 0xFFFF:
                    rom_offset = (ptr & 0x7FFF)
                    if rom_offset < rom_size:
                        ptrs.append(rom_offset)
                    else:
                        valid = False
                        break
                else:
                    valid = False
                    break
        
        if valid and len(ptrs) == 3:
            pointer_tables.append(offset)
    
    return pointer_tables


def trace_code_from_vectors(rom, header_offset, mapping):
    """
    Trace code regions starting from reset/interrupt vectors.
    
    Returns:
        set: offsets marked as code
    """
    code_offsets = set()
    
    # Get vector table location based on mapping
    if mapping == "LoROM":
        vector_table_offset = 0x7FE0
    else:  # HiROM
        vector_table_offset = 0xFFE0
    
    rom_no_header = rom[header_offset:] if header_offset else rom
    
    if vector_table_offset + 32 > len(rom_no_header):
        return code_offsets
    
    # Read reset vector (Native mode)
    reset_vector_pos = vector_table_offset + 0x1C
    if reset_vector_pos + 1 < len(rom_no_header):
        reset_addr = rom_no_header[reset_vector_pos] | (rom_no_header[reset_vector_pos + 1] << 8)
        
        # Convert to ROM offset (LoROM: $8000-$FFFF -> 0x0000-0x7FFF per bank)
        if mapping == "LoROM" and 0x8000 <= reset_addr <= 0xFFFF:
            rom_offset = (reset_addr & 0x7FFF)
            if rom_offset < len(rom_no_header):
                # Mark region around reset vector as code
                for i in range(max(0, rom_offset - 16), min(len(rom_no_header), rom_offset + 1024)):
                    code_offsets.add(i + header_offset)
    
    return code_offsets


def classify_regions(rom_data, header_offset, candidates_data, mapping):
    """
    Classify ROM regions into code, data, compressed, etc.
    
    Returns:
        list: regions with metadata
    """
    rom_size = len(rom_data)
    rom = rom_data[header_offset:] if header_offset else rom_data
    
    # Initialize region map
    region_map = [{"type": "unknown", "confidence": 0} for _ in range(rom_size)]
    
    # Mark compressed blocks
    if candidates_data and "candidates" in candidates_data:
        for candidate in candidates_data["candidates"]:
            if candidate.get("success"):
                offset = candidate["offset_int"]
                size = candidate["compressed_size"]
                for i in range(offset, min(offset + size, rom_size)):
                    region_map[i] = {"type": "compressed", "confidence": 90}
    
    # Find code regions via vector tracing
    code_offsets = trace_code_from_vectors(rom_data, header_offset, mapping)
    for offset in code_offsets:
        if offset < rom_size:
            region_map[offset] = {"type": "code", "confidence": 80}
    
    # Scan for code vs data using heuristics
    scan_block_size = 512
    for offset in range(0, rom_size, scan_block_size):
        if region_map[offset]["type"] != "unknown":
            continue
        
        end = min(offset + scan_block_size, rom_size)
        block = rom_data[offset:end]
        
        # Calculate entropy
        entropy = calculate_entropy(block)
        
        # Analyze opcode density
        valid_ratio, avg_len = analyze_opcode_density(rom_data, offset, min(256, len(block)))
        
        # Decision thresholds
        if valid_ratio > 0.85 and entropy < 6.5 and 1.5 < avg_len < 2.5:
            # Likely code
            region_type = "code"
            confidence = min(95, int(valid_ratio * 100))
        elif entropy > 7.2:
            # High entropy - likely compressed or encrypted
            region_type = "compressed_candidate"
            confidence = 60
        elif entropy < 4.0:
            # Low entropy - possibly graphics or repetitive data
            region_type = "graphics_candidate"
            confidence = 50
        else:
            # Unknown data
            region_type = "data"
            confidence = 40
        
        for i in range(offset, end):
            if region_map[i]["type"] == "unknown":
                region_map[i] = {"type": region_type, "confidence": confidence}
    
    # Consolidate into continuous regions
    regions = []
    current_region = None
    
    for offset in range(rom_size):
        rtype = region_map[offset]["type"]
        conf = region_map[offset]["confidence"]
        
        if current_region is None:
            current_region = {
                "start": offset,
                "end": offset + 1,
                "type": rtype,
                "confidence": conf
            }
        elif current_region["type"] == rtype:
            current_region["end"] = offset + 1
        else:
            regions.append(current_region)
            current_region = {
                "start": offset,
                "end": offset + 1,
                "type": rtype,
                "confidence": conf
            }
    
    if current_region:
        regions.append(current_region)
    
    # Add hex addresses and sizes
    for region in regions:
        region["start_hex"] = hex(region["start"])
        region["end_hex"] = hex(region["end"])
        region["size"] = region["end"] - region["start"]
        region["size_hex"] = hex(region["size"])
    
    return regions


def generate_html_visualization(regions, rom_size, output_path):
    """Generate interactive HTML visualization of ROM map."""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>B.O.B. ROM Map Visualization</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            margin: 0;
        }
        h1 {
            color: #4ec9b0;
            margin-bottom: 10px;
        }
        .info {
            margin-bottom: 20px;
            font-size: 14px;
        }
        .legend {
            margin: 20px 0;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .legend-color {
            width: 30px;
            height: 20px;
            border: 1px solid #555;
        }
        .rom-map {
            position: relative;
            width: 100%;
            height: 60px;
            background: #2d2d2d;
            border: 1px solid #555;
            margin: 20px 0;
        }
        .region {
            position: absolute;
            height: 100%;
            cursor: pointer;
            border-right: 1px solid rgba(255,255,255,0.1);
            transition: opacity 0.2s;
        }
        .region:hover {
            opacity: 0.8;
        }
        .tooltip {
            position: fixed;
            background: #252526;
            border: 1px solid #4ec9b0;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            display: none;
            max-width: 300px;
        }
        .region-list {
            margin-top: 30px;
        }
        .region-item {
            padding: 8px;
            margin: 4px 0;
            border-left: 4px solid;
            background: #2d2d2d;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <h1>🎮 B.O.B. ROM Memory Map</h1>
    <div class="info">
        ROM Size: """ + hex(rom_size) + """ (""" + str(rom_size) + """ bytes)
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: #4ec9b0;"></div>
            <span>Code</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #c586c0;"></div>
            <span>Compressed</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #dcdcaa;"></div>
            <span>Graphics Candidate</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #569cd6;"></div>
            <span>Data</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #808080;"></div>
            <span>Unknown</span>
        </div>
    </div>
    
    <div class="rom-map" id="romMap"></div>
    <div class="tooltip" id="tooltip"></div>
    
    <div class="region-list" id="regionList"></div>
    
    <script>
        const regions = """ + json.dumps(regions) + """;
        const romSize = """ + str(rom_size) + """;
        
        const colorMap = {
            'code': '#4ec9b0',
            'compressed': '#c586c0',
            'compressed_candidate': '#c586c0',
            'graphics_candidate': '#dcdcaa',
            'data': '#569cd6',
            'unknown': '#808080'
        };
        
        const mapEl = document.getElementById('romMap');
        const tooltipEl = document.getElementById('tooltip');
        const listEl = document.getElementById('regionList');
        
        // Render regions on map
        regions.forEach(region => {
            const div = document.createElement('div');
            div.className = 'region';
            div.style.left = (region.start / romSize * 100) + '%';
            div.style.width = (region.size / romSize * 100) + '%';
            div.style.background = colorMap[region.type] || '#808080';
            
            div.addEventListener('mouseenter', (e) => {
                tooltipEl.innerHTML = `
                    <strong>${region.type.toUpperCase()}</strong><br>
                    Address: ${region.start_hex} - ${region.end_hex}<br>
                    Size: ${region.size_hex} (${region.size} bytes)<br>
                    Confidence: ${region.confidence}%
                `;
                tooltipEl.style.display = 'block';
            });
            
            div.addEventListener('mousemove', (e) => {
                tooltipEl.style.left = (e.clientX + 10) + 'px';
                tooltipEl.style.top = (e.clientY + 10) + 'px';
            });
            
            div.addEventListener('mouseleave', () => {
                tooltipEl.style.display = 'none';
            });
            
            mapEl.appendChild(div);
        });
        
        // Render region list
        regions.forEach(region => {
            const div = document.createElement('div');
            div.className = 'region-item';
            div.style.borderLeftColor = colorMap[region.type];
            div.innerHTML = `
                <strong>${region.type.toUpperCase()}</strong> | 
                ${region.start_hex} - ${region.end_hex} | 
                Size: ${region.size_hex} | 
                Confidence: ${region.confidence}%
            `;
            listEl.appendChild(div);
        });
    </script>
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description="Map B.O.B. ROM regions")
    parser.add_argument("--rom", required=True, help="Path to ROM file")
    parser.add_argument("--candidates", help="Path to candidates.json from bob_lz_scan.py")
    parser.add_argument("--outdir", default="out", help="Output directory")
    args = parser.parse_args()
    
    # Read ROM
    rom_path = Path(args.rom)
    rom_data = rom_path.read_bytes()
    print(f"Loaded ROM: {len(rom_data)} bytes")
    
    # Load candidates if provided
    candidates_data = None
    if args.candidates:
        with open(args.candidates, 'r') as f:
            candidates_data = json.load(f)
        print(f"Loaded {candidates_data.get('num_candidates', 0)} compressed block candidates")
    
    # Detect ROM properties
    header_offset = candidates_data.get("header_offset", 0) if candidates_data else 0
    mapping = candidates_data.get("rom_mapping", "LoROM") if candidates_data else "LoROM"
    
    print(f"ROM mapping: {mapping}")
    print(f"Header offset: {header_offset}")
    
    # Classify regions
    print("Classifying regions...")
    regions = classify_regions(rom_data, header_offset, candidates_data, mapping)
    print(f"Identified {len(regions)} distinct regions")
    
    # Output directory
    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)
    
    # Save JSON
    output = {
        "rom_file": str(rom_path),
        "rom_size": len(rom_data),
        "header_offset": header_offset,
        "rom_mapping": mapping,
        "num_regions": len(regions),
        "regions": regions
    }
    
    json_path = outdir / "rom_map.json"
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved ROM map to {json_path}")
    
    # Generate HTML visualization
    html_path = outdir / "rom_map.html"
    generate_html_visualization(regions, len(rom_data), html_path)
    print(f"Saved visualization to {html_path}")
    
    # Print summary
    print("\n=== Region Summary ===")
    type_counts = defaultdict(int)
    type_sizes = defaultdict(int)
    for region in regions:
        type_counts[region["type"]] += 1
        type_sizes[region["type"]] += region["size"]
    
    for rtype in sorted(type_counts.keys()):
        print(f"{rtype:20s}: {type_counts[rtype]:4d} regions, {type_sizes[rtype]:8d} bytes ({type_sizes[rtype]/len(rom_data)*100:5.2f}%)")
    
    return 0


if __name__ == "__main__":
    exit(main())
