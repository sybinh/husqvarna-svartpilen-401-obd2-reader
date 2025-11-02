@echo off
echo =========================================
echo Testing GUI with Simulated OBD2 Data
echo =========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Starting GUI application...
echo.
python src\main.py

pause
