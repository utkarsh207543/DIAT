#!/usr/bin/env python3
"""
NIST 800-22 Statistical Test Suite - Web Interface
Run this script to start the web server.
"""

import os
import sys
import webbrowser
from threading import Timer

def open_browser():
    """Open the web browser after a short delay"""
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("="*60)
    print("NIST 800-22 Statistical Test Suite - Web Interface")
    print("="*60)
    print("Starting web server...")
    print("Access the application at: http://localhost:5000")
    print("To access from other computers, use: http://[YOUR_IP]:5000")
    print("Press Ctrl+C to stop the server")
    print("="*60)
    
    # Open browser after 2 seconds
    Timer(2.0, open_browser).start()
    
    # Import and run the Flask app
    from app import app
    app.run(host='0.0.0.0', port=5000, debug=False)
