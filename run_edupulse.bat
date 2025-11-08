@echo off
echo Starting EduPulse...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the app
python main.py

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo ERROR: EduPulse encountered an error!
    echo Check the error message above.
    pause
)