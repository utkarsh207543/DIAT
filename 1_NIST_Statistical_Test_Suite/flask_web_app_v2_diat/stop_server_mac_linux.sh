#!/bin/bash
if [ -f server_pid.txt ]; then
    PID=$(cat server_pid.txt)
    echo "Stopping server with PID $PID..."
    kill $PID
    rm server_pid.txt
    echo "Server stopped."
else
    echo "Server PID file not found. Trying to find by name..."
    pkill -f "nist_gui/app.py"
    echo "Attempted to stop server by name."
fi
