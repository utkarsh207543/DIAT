#!/bin/bash
echo "NIST 800-22 Statistical Test Suite - Web Interface"
echo "=================================================="
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting web server..."
echo "Access the application at: http://localhost:5000"
echo "To access from other computers, use: http://[YOUR_IP]:5000"
echo "Press Ctrl+C to stop the server"
echo "=================================================="

python run.py
