#!/bin/bash
echo "Installing dependencies..."

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found, installing..."
    sudo apt-get update && sudo apt-get install -y python3-pip
fi

pip3 install -r requirements.txt
echo "Dependencies installed!"
