@echo off
title NIST Cleanup Utility
color 0E
echo.
echo ================================================================================
echo                    NIST Application Cleanup Utility
echo ================================================================================
echo.

echo Current storage usage:
python cleanup_utility.py --stats

echo.
echo Cleanup options:
echo 1. Clean files older than 30 days
echo 2. Clean files older than 7 days  
echo 3. Clean files older than 1 day
echo 4. Custom cleanup
echo 5. Show what would be cleaned (dry run)
echo 6. Exit
echo.

set /p choice="Choose option (1-6): "

if "%choice%"=="1" (
    echo Cleaning files older than 30 days...
    python cleanup_utility.py --files 30 --database 90
)

if "%choice%"=="2" (
    echo Cleaning files older than 7 days...
    python cleanup_utility.py --files 7 --database 30
)

if "%choice%"=="3" (
    echo Cleaning files older than 1 day...
    python cleanup_utility.py --files 1 --database 7
)

if "%choice%"=="4" (
    set /p file_days="Enter days for file cleanup: "
    set /p db_days="Enter days for database cleanup: "
    echo Cleaning with custom settings...
    python cleanup_utility.py --files %file_days% --database %db_days%
)

if "%choice%"=="5" (
    echo Showing what would be cleaned (dry run)...
    python cleanup_utility.py --files 30 --database 90 --dry-run
)

if "%choice%"=="6" (
    exit /b 0
)

echo.
echo Cleanup completed!
echo.
pause
