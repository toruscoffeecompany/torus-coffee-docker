@echo off
REM Admin script: register Miss Pink Auto-Prompt Generator as a Windows Scheduled Task
REM Usage: Run this ONCE as the admin user to create the scheduled job.
REM OPSEC: No secrets are stored in this file.

setlocal

REM --- Config ---
set TASK_NAME=Miss_Pink_Auto_Prompt
set PYTHON="D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\pythonw.exe""
set SCRIPT="D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\scripts\misspink_auto_prompt.py"
set LOG_DIR="D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\logs"
set RUN_AS=torus

REM --- Preflight ---
if not exist %PYTHON% (
    echo [ERROR] Python venv not found: %PYTHON%
    pause
    exit /b 1
)

if not exist %SCRIPT% (
    echo [ERROR] Script not found: %SCRIPT%
    pause
    exit /b 1
)

REM --- Create log dir ---
if not exist %LOG_DIR% mkdir %LOG_DIR%

REM --- Register task (every 15 minutes, run whether user is logged on or not) ---
echo [INFO] Registering scheduled task: %TASK_NAME%
schtasks /create ^
  /tn "%TASK_NAME%" ^
  /tr "%PYTHON% %SCRIPT%" ^
  /sc minute ^
  /mo 15 ^
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
echo [INFO] View it in Task Scheduler under 'Miss_Pink_Auto_Prompt'
echo [INFO] To run now: schtasks /run /tn "%TASK_NAME%"
echo [INFO] To remove:  schtasks /delete /tn "%TASK_NAME%" /f

endlocal
pause
