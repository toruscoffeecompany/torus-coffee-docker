@echo off
REM Admin script: register Torus comms watcher launcher as Windows Scheduled Task
REM Run ONCE as Administrator.
setlocal

set TASK_NAME=Torus_Comms_Watcher_Launcher
set PYTHON=D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\pythonw.exe"
set LAUNCHER=D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\scripts\start_watcher_safe.py
set RUN_AS=torus

if not exist %PYTHON% (
    echo [ERROR] Python venv not found: %PYTHON%
    pause
    exit /b 1
)
if not exist %LAUNCHER% (
    echo [ERROR] Launcher not found: %LAUNCHER%
    pause
    exit /b 1

echo [INFO] Registering scheduled task: %TASK_NAME%
schtasks /create ^
  /tn "%TASK_NAME%" ^
  /tr "\"%PYTHON%\" \"%LAUNCHER%\"" ^
  /sc minute ^
  /mo 10 ^
  /ru "%RUN_AS%" ^
  /rl HIGHEST ^
  /f ^
  /np ^
  >nul 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create task. Try running this batch file as Administrator.
    pause
    exit /b 1
)

echo [OK] Task registered: %TASK_NAME%
echo [INFO] View it in Task Scheduler under '%TASK_NAME%'
echo [INFO] To run now: schtasks /run /tn "%TASK_NAME%"
echo [INFO] To remove:  schtasks /delete /tn "%TASK_NAME%" /f
pause
endlocal
