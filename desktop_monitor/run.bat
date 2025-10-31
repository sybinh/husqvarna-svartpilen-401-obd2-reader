@echo off
echo ===================================================
echo Husqvarna Svartpilen 401 OBD2 Monitor Launcher
echo ===================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Select an option:
echo 1. Run Desktop Monitor
echo 2. Run Test Simulator
echo 3. Run Both (Simulator + Monitor)
echo 4. Exit
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" goto monitor
if "%choice%"=="2" goto simulator
if "%choice%"=="3" goto both
if "%choice%"=="4" goto exit
echo Invalid choice. Please enter 1-4.
goto :eof

:monitor
echo.
echo Starting Desktop Monitor...
python main.py
goto :eof

:simulator
echo.
echo Starting Test Simulator...
cd tests
python simulator.py
goto :eof

:both
echo.
echo Starting Test Simulator in background...
start "OBD2 Simulator" cmd /c "cd tests && python simulator.py"
timeout /t 2 >nul
echo Starting Desktop Monitor...
python main.py
goto :eof

:exit
echo Goodbye!
pause