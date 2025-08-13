#!/usr/bin/env python3
"""
WPlace Bot - Main Entry Point
Có thể chạy như web server hoặc CGI script
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app  # noqa: F401

# CGI mode cho shared hosting
if __name__ == "__main__":
    # Kiểm tra nếu chạy như CGI
    if 'REQUEST_METHOD' in os.environ:
        # CGI mode
        from wsgiref.handlers import CGIHandler
        CGIHandler().run(app)
    else:
        # Development mode
        app.run(host='0.0.0.0', port=5000, debug=True)
