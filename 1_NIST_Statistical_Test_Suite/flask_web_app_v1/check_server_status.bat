@echo off
title Check NIST Server Status
color 0F
echo.
echo ================================================================================
echo                      NIST Server Status Check
echo ================================================================================
echo.

REM Check if Python processes are running
echo Checking for running Python processes...
tasklist /fi "imagename eq python.exe" /fo table 2>nul | find /i "python.exe" >nul
if errorlevel 1 (
    echo Status: NO Python processes found
    echo The NIST server is likely NOT running
) else (
    echo Status: Python processes found
    echo.
    echo Running Python processes:
    tasklist /fi "imagename eq python.exe" /fo table 2>nul
)

echo.
echo ================================================================================
echo Checking network connectivity to localhost:5000...
echo ================================================================================

REM Try to connect to the server
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000' -TimeoutSec 5 -UseBasicParsing; Write-Host 'SUCCESS: Server is responding on http://localhost:5000'; Write-Host 'Status Code:' $response.StatusCode } catch { Write-Host 'FAILED: Cannot connect to server on http://localhost:5000'; Write-Host 'Error:' $_.Exception.Message }"

echo.
echo ================================================================================
echo Status check complete.
echo.
echo If server is running, access it at: http://localhost:5000
echo ================================================================================
echo.
pause
