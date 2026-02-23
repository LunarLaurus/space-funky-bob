#!/usr/bin/env python3
"""
bob_render.py - B.O.B. ROM Data Visualization Tool

Analyzes extracted compressed blobs and generates an HTML visualization
showing contents, hex dumps, entropy analysis, and data type detection.

Usage:
    python toolkit/bob_render.py --data data/ --outdir data/

Output:
    blobs.html - Interactive visualization of all extracted blobs
"""

import argparse
import json
import math
import os
from pathlib import Path
from collections import Counter
from datetime import datetime


def calculate_entropy(data):
    """Calculate Shannon entropy of byte data."""
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


def analyze_blob(filepath):
    """Analyze a single blob file and return analysis data."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    size = len(data)
    entropy = calculate_entropy(data)
    
    # Byte frequency analysis
    freq = Counter(data)
    most_common = freq.most_common(10)
    
    # Null byte analysis
    null_count = data.count(0)
    null_percent = null_count / size * 100 if size > 0 else 0
    
    # ASCII analysis
    ascii_printable = sum(1 for b in data if 32 <= b <= 126)
    ascii_percent = ascii_printable / size * 100 if size > 0 else 0
    
    # High entropy detection
    is_high_entropy = entropy > 7.0
    is_low_entropy = entropy < 3.0
    
    # Detect potential data type
    data_type = "unknown"
    if null_percent > 50:
        data_type = "likely_empty_padding"
    elif ascii_percent > 80:
        data_type = "likely_text"
    elif is_high_entropy:
        data_type = "likely_compressed_encrypted"
    elif is_low_entropy:
        data_type = "likely_graphics"
    else:
        data_type = "likely_code_data"
    
    # Generate hex dump (first 256 bytes for preview)
    hex_lines = []
    preview_size = min(256, size)
    for i in range(0, preview_size, 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        addr = f'{i:04X}'
        hex_lines.append(f'{addr}  {hex_part:<48}  {ascii_part}')
    
    # Byte distribution (first 32 bytes for chart)
    byte_dist = freq.most_common(32)
    
    return {
        'filename': filepath.name,
        'size': size,
        'size_hex': f'0x{size:X}',
        'entropy': round(entropy, 2),
        'null_percent': round(null_percent, 1),
        'ascii_percent': round(ascii_percent, 1),
        'data_type': data_type,
        'most_common': [(f'0x{b:02X}', c) for b, c in most_common],
        'hex_dump': hex_lines,
        'byte_dist': [(f'0x{b:02X}', c) for b, c in byte_dist],
    }


def generate_html(analyses, rom_info, outdir):
    """Generate the HTML visualization."""
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>B.O.B. ROM - Extracted Blobs Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
            line-height: 1.5;
        }
        
        .header {
            background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%);
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid #30363d;
        }
        
        h1 {
            color: #58a6ff;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #8b949e;
            font-size: 14px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: #161b22;
            padding: 20px;
            border-radius: 6px;
            border: 1px solid #30363d;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #58a6ff;
        }
        
        .stat-label {
            font-size: 12px;
            color: #8b949e;
            text-transform: uppercase;
            margin-top: 5px;
        }
        
        .blob-card {
            background: #161b22;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #30363d;
            overflow: hidden;
        }
        
        .blob-header {
            background: #21262d;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
        }
        
        .blob-header:hover {
            background: #30363d;
        }
        
        .blob-title {
            font-size: 16px;
            font-weight: bold;
            color: #58a6ff;
        }
        
        .blob-meta {
            display: flex;
            gap: 20px;
            font-size: 12px;
            color: #8b949e;
        }
        
        .blob-tag {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }
        
        .tag-text { background: #238636; color: #fff; }
        .tag-graphics { background: #a371f7; color: #fff; }
        .tag-compressed { background: #f85149; color: #fff; }
        .tag-code { background: #f0883e; color: #fff; }
        .tag-unknown { background: #6e7681; color: #fff; }
        
        .blob-content {
            padding: 20px;
            display: none;
        }
        
        .blob-content.open {
            display: block;
        }
        
        .hex-dump {
            background: #0d1117;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
            white-space: pre;
            line-height: 1.8;
            border: 1px solid #30363d;
        }
        
        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .analysis-card {
            background: #0d1117;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #30363d;
        }
        
        .analysis-title {
            font-size: 12px;
            color: #8b949e;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        
        .bar-chart {
            display: flex;
            align-items: flex-end;
            height: 60px;
            gap: 2px;
            margin-top: 10px;
        }
        
        .bar {
            flex: 1;
            background: #58a6ff;
            min-width: 4px;
            transition: height 0.3s;
        }
        
        .bar:hover {
            background: #79c0ff;
        }
        
        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 30px;
            padding: 15px;
            background: #161b22;
            border-radius: 6px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
        }
        
        .legend-tag {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
        }
        
        .search-box {
            background: #161b22;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #30363d;
        }
        
        .search-input {
            width: 100%;
            padding: 10px 15px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 4px;
            color: #c9d1d9;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #58a6ff;
        }
        
        .filter-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 5px 12px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 4px;
            color: #c9d1d9;
            cursor: pointer;
            font-size: 12px;
        }
        
        .filter-btn:hover {
            background: #30363d;
        }
        
        .filter-btn.active {
            background: #58a6ff;
            color: #0d1117;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #6e7681;
            font-size: 12px;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>B.O.B. ROM - Extracted Blobs Analysis</h1>
        <div class="subtitle">'''
    
    html += f'''ROM: {rom_info.get('rom_file', 'Unknown')} | Size: {rom_info.get('rom_size', 0):,} bytes | Mapping: {rom_info.get('rom_mapping', 'Unknown')} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{len(analyses)}</div>
            <div class="stat-label">Total Blobs</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{sum(a['size'] for a in analyses):,}</div>
            <div class="stat-label">Total Bytes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{sum(1 for a in analyses if a['data_type'] == 'likely_text')}</div>
            <div class="stat-label">Text Blocks</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{sum(1 for a in analyses if a['data_type'] == 'likely_graphics')}</div>
            <div class="stat-label">Graphics Blocks</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{sum(1 for a in analyses if a['data_type'] == 'likely_compressed_encrypted')}</div>
            <div class="stat-label">High Entropy</div>
        </div>
    </div>
    
    <div class="search-box">
        <input type="text" class="search-input" id="searchInput" placeholder="Search blobs by name, type, or content..." onkeyup="filterBlobs()">
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="setFilter('all', this)">All</button>
            <button class="filter-btn" onclick="setFilter('text', this)">Text</button>
            <button class="filter-btn" onclick="setFilter('graphics', this)">Graphics</button>
            <button class="filter-btn" onclick="setFilter('compressed', this)">High Entropy</button>
            <button class="filter-btn" onclick="setFilter('code', this)">Code/Data</button>
        </div>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <span class="legend-tag tag-text">TEXT</span>
            >80% ASCII
        </div>
        <div class="legend-item">
            <span class="legend-tag tag-graphics">GRAPHICS</span>
            Low entropy
        </div>
        <div class="legend-item">
            <span class="legend-tag tag-compressed">COMPRESSED</span>
            High entropy (>7.0)
        </div>
        <div class="legend-item">
            <span class="legend-tag tag-code">CODE/DATA</span>
            Medium entropy
        </div>
        <div class="legend-item">
            <span class="legend-tag tag-unknown">UNKNOWN</span>
            Mixed/other
        </div>
    </div>
'''
    
    # Generate blob cards
    for i, analysis in enumerate(analyses):
        tag_class = {
            'likely_text': 'tag-text',
            'likely_graphics': 'tag-graphics',
            'likely_compressed_encrypted': 'tag-compressed',
            'likely_code_data': 'tag-code',
        }.get(analysis['data_type'], 'tag-unknown')
        
        tag_label = {
            'likely_text': 'TEXT',
            'likely_graphics': 'GRAPHICS',
            'likely_compressed_encrypted': 'HIGH ENTROPY',
            'likely_code_data': 'CODE/DATA',
            'likely_empty_padding': 'EMPTY',
        }.get(analysis['data_type'], 'UNKNOWN')
        
        hex_dump_html = '\\n'.join(analysis['hex_dump'])
        
        # Generate byte distribution bars
        bars_html = ''
        if analysis['byte_dist']:
            max_count = max(c for _, c in analysis['byte_dist'])
            for byte_val, count in analysis['byte_dist'][:16]:
                height = (count / max_count * 100) if max_count > 0 else 0
                bars_html += f'<div class="bar" style="height:{height}%" title="{byte_val}: {count}"></div>'
        
        html += f'''
    <div class="blob-card" data-type="{analysis['data_type']}" data-name="{analysis['filename']}">
        <div class="blob-header" onclick="toggleBlob(this)">
            <div class="blob-title">{analysis['filename']}</div>
            <div class="blob-meta">
                <span class="blob-tag {tag_class}">{tag_label}</span>
                <span>{analysis['size']:,} bytes ({analysis['size_hex']})</span>
                <span>Entropy: {analysis['entropy']}</span>
                <span>ASCII: {analysis['ascii_percent']}%</span>
            </div>
        </div>
        <div class="blob-content">
            <div class="analysis-grid">
                <div class="analysis-card">
                    <div class="analysis-title">Statistics</div>
                    <div>Size: {analysis['size']:,} bytes</div>
                    <div>Entropy: {analysis['entropy']} bits/byte</div>
                    <div>Null bytes: {analysis['null_percent']}%</div>
                    <div>ASCII: {analysis['ascii_percent']}%</div>
                    <div>Type: {analysis['data_type']}</div>
                </div>
                <div class="analysis-card">
                    <div class="analysis-title">Most Common Bytes</div>
                    <div>{', '.join(f'{b} ({c}x)' for b, c in analysis['most_common'][:5])}</div>
                </div>
                <div class="analysis-card">
                    <div class="analysis-title">Byte Distribution</div>
                    <div class="bar-chart">{bars_html}</div>
                </div>
            </div>
            <div class="analysis-title" style="margin-top:20px">Hex Dump (First 256 bytes)</div>
            <div class="hex-dump">{hex_dump_html}</div>
        </div>
    </div>
'''
    
    html += '''
    <div class="footer">
        Generated by B.O.B. ROM Analysis Toolkit | https://github.com/anomalyco/bob-rom-analysis
    </div>
    
    <script>
        function toggleBlob(header) {
            const content = header.nextElementSibling;
            content.classList.toggle('open');
        }
        
        let currentFilter = 'all';
        
        function setFilter(filter, btn) {
            currentFilter = filter;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterBlobs();
        }
        
        function filterBlobs() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.blob-card');
            
            cards.forEach(card => {
                const name = card.dataset.name.toLowerCase();
                const type = card.dataset.type;
                const matchesSearch = name.includes(search);
                const matchesFilter = currentFilter === 'all' || 
                    (currentFilter === 'text' && type === 'likely_text') ||
                    (currentFilter === 'graphics' && type === 'likely_graphics') ||
                    (currentFilter === 'compressed' && type === 'likely_compressed_encrypted') ||
                    (currentFilter === 'code' && type === 'likely_code_data');
                
                if (matchesSearch && matchesFilter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>'''
    
    # Write HTML file
    output_path = outdir / 'blobs.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='B.O.B. ROM Blob Visualization Tool'
    )
    parser.add_argument(
        '--data',
        default='data',
        help='Directory containing extracted blobs (default: data)'
    )
    parser.add_argument(
        '--outdir',
        default='data',
        help='Output directory (default: data)'
    )
    
    args = parser.parse_args()
    
    data_dir = Path(args.data)
    out_dir = Path(args.outdir)
    
    # Load candidates.json for ROM info
    candidates_file = data_dir / 'candidates.json'
    if candidates_file.exists():
        with open(candidates_file) as f:
            rom_info = json.load(f)
    else:
        rom_info = {'rom_file': 'Unknown', 'rom_size': 0, 'rom_mapping': 'Unknown'}
    
    # Find all decompressed blob files
    blob_files = sorted(data_dir.glob('decompressed_*.bin'))
    
    print(f'Found {len(blob_files)} blob files to analyze...')
    
    # Analyze each blob
    analyses = []
    for i, blob_file in enumerate(blob_files):
        if (i + 1) % 10 == 0:
            print(f'Analyzed {i + 1}/{len(blob_files)}...')
        
        analysis = analyze_blob(blob_file)
        analyses.append(analysis)
    
    # Sort by offset (extract from filename)
    analyses.sort(key=lambda x: int(x['filename'].replace('decompressed_', '').replace('.bin', ''), 16))
    
    # Generate HTML
    print('Generating HTML visualization...')
    output_path = generate_html(analyses, rom_info, out_dir)
    
    print(f'\\nDone! Generated: {output_path}')
    print(f'Total blobs analyzed: {len(analyses)}')


if __name__ == '__main__':
    main()
