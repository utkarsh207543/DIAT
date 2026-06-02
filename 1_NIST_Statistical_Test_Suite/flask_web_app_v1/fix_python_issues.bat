@echo off
title Fix Python Installation Issues
color 0D
echo.
echo ================================================================================
echo                    Python Installation Issue Fixer
echo ================================================================================
echo.

echo Detected Python 3.13 from Microsoft Store
echo This can sometimes cause package installation issues.
echo.
echo Recommended solutions:
echo.

echo 1. RECOMMENDED: Install Python from python.org
echo    - Go to https://python.org/downloads
echo    - Download Python 3.11 or 3.12 (more stable)
echo    - During installation, check "Add Python to PATH"
echo    - This will give you a more reliable Python installation
echo.

echo 2. ALTERNATIVE: Fix current installation
echo    - We'll try to fix your current Microsoft Store Python
echo    - This may work but is less reliable
echo.

set /p choice="Choose option (1 for python.org install, 2 to fix current): "

if "%choice%"=="1" (
    echo.
    echo Opening python.org downloads page...
    start https://python.org/downloads
    echo.
    echo After installing Python from python.org:
    echo 1. Restart your computer
    echo 2. Run install_dependencies.bat again
    echo 3. Run start_server.bat
    echo.
    pause
    exit /b 0
)

if "%choice%"=="2" (
    echo.
    echo Attempting to fix current Python installation...
    echo.
    
    REM Try to install setuptools and wheel first
    echo Installing build tools...
    python -m pip install --upgrade pip setuptools wheel --user --no-warn-script-location
    
    echo.
    echo Installing dependencies with compatibility flags...
    python -m pip install Flask==2.3.3 --user --no-warn-script-location --no-build-isolation
    python -m pip install numpy --user --no-warn-script-location --no-build-isolation
    python -m pip install scipy --user --no-warn-script-location --no-build-isolation
    
    echo.
    echo Testing installation...
    python -c "import flask, numpy, scipy; print('All packages imported successfully!')"
    
    if errorlevel 1 (
        echo.
        echo Fix attempt failed. Please consider installing Python from python.org
        echo.
    ) else (
        echo.
        echo Fix successful! You can now run start_server.bat
        echo.
    )
)

echo.
pause
