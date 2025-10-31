@echo off
echo === Husqvarna Svartpilen 401 OBD2 Monitor Test Setup ===
echo.
echo This script will help you test the desktop application
echo.

:menu
echo Select an option:
echo 1. Run Simple Data Generator (File-based)
echo 2. Run Simple Desktop GUI
echo 3. Run both (Generator + GUI) - RECOMMENDED
echo 4. Exit
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" goto generator
if "%choice%"=="2" goto gui
if "%choice%"=="3" goto both
if "%choice%"=="4" goto exit
goto menu

:generator
echo.
echo Starting Simple Data Generator...
echo This will create obd2_data.json file with simulated data
echo.
python simple_data_generator.py
goto menu

:gui
echo.
echo Starting Simple Desktop GUI...
echo This will read data from obd2_data.json file
echo.
python simple_monitor.py
goto menu

:both
echo.
echo Starting both Generator and GUI...
echo The generator will run in background, then GUI will open
echo.
start "Data Generator" cmd /c "python simple_data_generator.py"
timeout /t 2
python simple_monitor.py
goto menu

:exit
echo.
echo Goodbye!
pause