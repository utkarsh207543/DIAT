@echo off
echo "Restarting NIST STS Server..."
taskkill /F /IM python.exe /T
timeout /t 2 /nobreak >nul
start /B python nist_gui\app.py
echo "Server restarted. Check console."
pause
