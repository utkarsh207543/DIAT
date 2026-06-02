@echo off
title Stop NIST Server
color 0C
echo.
echo ================================================================================
echo                         Stopping NIST Server
echo ================================================================================
echo.

REM Kill Python processes running Flask
echo Stopping Flask server processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq NIST 800-22 Statistical Test Suite Server*" >nul 2>&1
taskkill /f /im python.exe /fi "COMMANDLINE eq *app.py*" >nul 2>&1

REM More aggressive approach - kill all Python processes (use with caution)
REM Uncomment the line below if the above doesn't work
REM taskkill /f /im python.exe >nul 2>&1

echo.
echo Server processes stopped.
echo.
echo ================================================================================
echo NIST 800-22 Server has been stopped successfully.
echo ================================================================================
echo.
pause
