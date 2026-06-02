@echo off
echo "Stopping NIST STS Server..."
taskkill /F /IM python.exe /T
del server_pid.txt
echo "Server hopefully stopped."
pause
