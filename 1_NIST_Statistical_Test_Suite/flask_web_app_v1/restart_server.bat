@echo off
title Restart NIST Server
color 0E
echo.
echo ================================================================================
echo                        Restarting NIST Server
echo ================================================================================
echo.

echo Step 1: Stopping existing server...
call stop_server.bat

echo.
echo Step 2: Starting server...
timeout /t 2 /nobreak >nul
call start_server.bat
