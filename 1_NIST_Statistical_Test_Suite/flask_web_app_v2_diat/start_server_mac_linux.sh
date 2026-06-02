#!/bin/bash

# Start the server (using Python)
echo "Starting NIST STS Server..."
# Use absolute path to ensure execution
python3 nist_gui/app.py &
# Store PID
echo $! > server_pid.txt
echo "Server started with PID: $(cat server_pid.txt)"
