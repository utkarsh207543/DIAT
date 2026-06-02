@echo off
title Installing NIST Dependencies
color 0B
echo.
echo ================================================================================
echo                    Installing NIST 800-22 Dependencies
echo ================================================================================
echo.

echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing core dependencies...
pip install Flask==2.3.3
pip install numpy==1.24.3
pip install scipy==1.11.2

echo.
echo Installing Google authentication libraries...
pip install google-auth==2.23.3
pip install google-auth-oauthlib==1.1.0
pip install google-auth-httplib2==0.1.1
pip install flask-session==0.5.0
pip install requests==2.31.0

echo.
echo Installing from requirements file...
pip install -r requirements.txt

echo.
echo Verifying installations...
python -c "import Flask; print('Flask: OK')"
python -c "import numpy; print('NumPy: OK')"
python -c "import scipy; print('SciPy: OK')"
python -c "import google.auth; print('Google Auth: OK')"
python -c "import google_auth_oauthlib; print('Google OAuth: OK')"

echo.
echo ================================================================================
echo Installation complete!
echo ================================================================================
pause
