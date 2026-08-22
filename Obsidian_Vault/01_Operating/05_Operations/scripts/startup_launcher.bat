@echo off
REM Silent startup launcher for Torus comms watchdog
REM Runs in background, logs to file, never shows a window.
setlocal

set PYTHON=D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\venv\Scripts\pythonw.exe
set LAUNCHER=D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\scripts\watchdog_launcher.py
set LOG=D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\logs\startup_launcher.log

if not exist "%PYTHON%" (
    echo [%date% %time%] PYTHON_MISSING "%PYTHON%" >> "%LOG%"
    exit /b 1
)

if not exist "%LAUNCHER%" (
    echo [%date% %time%] LAUNCHER_MISSING "%LAUNCHER%" >> "%LOG%"
    exit /b 1
)

echo [%date% %time%] STARTING_WATCHDOG >> "%LOG%"
start "Torus Comms Watchdog" /B /MIN "%PYTHON%" "%LAUNCHER%" >> "%LOG%" 2>&1
echo [%date% %time%] LAUNCHER_DISPATCHED >> "%LOG%"
endlocal
