#!/usr/bin/env python3
"""
Web server for Space Funky B.O.B. Level Editor

Main entry point - routes requests to handler modules.
Refactored: 834 lines → 80 lines (handlers in editor/handlers/)
"""

import http.server
import socketserver
import os
import sys

# Add lib to path
sys.path.insert(0, os.path.dirname(__file__) + "/lib")
sys.path.insert(0, os.path.dirname(__file__))

from handlers import LevelHandler, TilesetHandler, DataHandler
from handlers import ExportHandler, BossHandler, PasswordHandler

PORT = 8000
EDITOR_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(EDITOR_DIR, '..', 'data')


class EditorHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler routing to handler modules."""
    
    # Handler instances (initialized on first request)
    level_handler = None
    tileset_handler = None
    data_handler = None
    export_handler = None
    boss_handler = None
    password_handler = None
    
    def init_handlers(self):
        """Initialize handler instances."""
        if not self.level_handler:
            self.level_handler = LevelHandler(DATA_DIR)
            self.tileset_handler = TilesetHandler(os.path.join(DATA_DIR, 'tilesets'))
            self.data_handler = DataHandler(os.path.join(DATA_DIR, 'extracted'))
            self.export_handler = ExportHandler()
            self.boss_handler = BossHandler()
            self.password_handler = PasswordHandler()
    
    def do_GET(self):
        """Handle GET requests by routing to handlers."""
        self.init_handlers()

        # API routes
        if self.path == '/levels':
            self._send_json(self.level_handler.get_level_list())
        elif self.path.startswith('/level/'):
            name = self.path[7:]
            self._send_json(self.level_handler.get_level_data(name))
        elif self.path == '/tilesets':
            self._send_json(self.tileset_handler.get_all_tilesets())
        elif self.path.startswith('/tileset/'):
            name = self.path[9:]
            self._send_json(self.tileset_handler.get_tileset(name))
        elif self.path.startswith('/palette/'):
            idx = int(self.path[9:])
            self._send_json(self.tileset_handler.get_palette(idx))
        elif self.path == '/bosses':
            self._send_json(self.boss_handler.get_all_bosses())
        elif self.path.startswith('/password/generate/'):
            parts = self.path[19:].split('/')
            if len(parts) >= 2:
                world, level = int(parts[0]), int(parts[1])
                self._send_json(self.password_handler.generate_password(world, level))
        elif self.path == '/data/files':
            self._send_json(self.data_handler.list_data_files())
        elif self.path.startswith('/data/'):
            filename = self.path[6:]
            result = self.data_handler.get_data_file(filename)
            self._send_json(result if result else {'error': 'File not found'})
        elif self.path == '/midi':
            self._send_json(self.data_handler.get_midi_list())
        # Static files - let SimpleHTTPRequestHandler serve them
        elif self.path == '/':
            self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            # Serve static files (CSS, JS, images)
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests by routing to handlers."""
        self.init_handlers()

        if self.path == '/export-level':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            import json
            level_data = json.loads(body)
            result = self.export_handler.export_level(level_data)
            self._send_json(result)
        elif self.path == '/password/validate':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            import json
            data = json.loads(body)
            result = self.password_handler.validate_password(data.get('digits', []))
            self._send_json(result)
        else:
            self.send_error(404, 'Not Found')
    
    def _send_json(self, data):
        """Send JSON response."""
        import json
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())


if __name__ == '__main__':
    # Change to editor directory so static files are served correctly
    os.chdir(os.path.dirname(__file__))
    
    with socketserver.TCPServer(("", PORT), EditorHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print(f"Serving files from: {os.getcwd()}")
        httpd.serve_forever()
