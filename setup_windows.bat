@echo off
echo ================================================
echo    EduPulse - Automated Setup for Windows
echo ================================================
echo.

echo [1/4] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo Python found!
echo.

echo [2/4] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created!
echo.

echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [4/4] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo ================================================
echo    Setup Complete! 
echo ================================================
echo.
echo To run EduPulse:
echo 1. Open Command Prompt in this folder
echo 2. Type: venv\Scripts\activate
echo 3. Type: python main.py
echo.
echo Or simply double-click run_edupulse.bat
echo.
pause