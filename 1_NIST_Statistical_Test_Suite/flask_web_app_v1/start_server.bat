@echo off
title NIST 800-22 Statistical Test Suite Server
color 0A
echo.
echo ================================================================================
echo                    NIST 800-22 Statistical Test Suite Server
echo ================================================================================
echo.
echo Starting server...
echo.
echo Server will be available at:
echo   - Local access:    http://localhost:5000
echo   - Network access:  http://[YOUR_IP]:5000
echo.
echo Press Ctrl+C to stop the server
echo To stop server properly, run stop_server.bat or close this window
echo.
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    echo.
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "app.py" (
    echo ERROR: app.py not found in current directory
    echo Please make sure you're running this from the correct folder
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Quick dependency check
echo Checking dependencies...
python -c "import flask, numpy, scipy" 2>nul
if errorlevel 1 (
    echo.
    echo WARNING: Some dependencies are missing or not working
    echo Please run install_dependencies.bat first
    echo.
    echo Attempting to install missing dependencies...
    python -m pip install flask numpy scipy --user --quiet
    echo.
)

REM Set Python path to include user site-packages (for Microsoft Store Python)
set PYTHONPATH=%APPDATA%\Python\Python313\site-packages;%PYTHONPATH%

REM Start the Flask application
echo Starting Flask server...
echo.
python app.py

REM If we get here, the server has stopped
echo.
echo ================================================================================
echo Server has stopped.
echo ================================================================================
pause
