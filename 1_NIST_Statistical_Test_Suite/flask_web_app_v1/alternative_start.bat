@echo off
title NIST Server (Alternative Start Method)
color 0A
echo.
echo ================================================================================
echo                    NIST Server - Alternative Start Method
echo ================================================================================
echo.

REM This alternative method works better with Microsoft Store Python

REM Set environment variables for Microsoft Store Python
set PYTHONPATH=%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages;%PYTHONPATH%
set PATH=%LOCALAPPDATA%\Microsoft\WindowsApps;%PATH%

echo Checking Python installation...
python --version
echo.

echo Checking if packages are available...
python -c "import sys; print('Python executable:', sys.executable)"
python -c "import sys; print('Python path:', sys.path)"
echo.

REM Try to import required packages
python -c "import flask; print('Flask found:', flask.__version__)" 2>nul || echo Flask not found
python -c "import numpy; print('NumPy found:', numpy.__version__)" 2>nul || echo NumPy not found  
python -c "import scipy; print('SciPy found:', scipy.__version__)" 2>nul || echo SciPy not found
echo.

echo Starting server with alternative method...
echo Server will be available at: http://localhost:5000
echo.

REM Start with explicit Python path
python "%~dp0app.py"

echo.
echo Server stopped.
pause
