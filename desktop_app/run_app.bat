@echo off
echo Starting Husqvarna Svartpilen 401 OBD2 Monitor...

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Running setup...
    call setup.bat
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
python obd2_monitor.py

pause