@echo off
echo Setting up NIST 800-22 Test Suite Environment...

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "temp" mkdir temp
if not exist "results" mkdir results

REM Initialize database
echo Initializing database...
python -c "from database import DatabaseManager; db = DatabaseManager(); print('Database initialized successfully')"

REM Check configuration
echo Checking configuration...
python -c "from config_loader import load_config; load_config()"

echo.
echo ✅ Environment setup complete!
echo.
echo Next steps:
echo 1. Ensure your .env file has the correct Google OAuth credentials
echo 2. Run: python app.py
echo 3. Open: http://localhost:5000
echo.
pause
