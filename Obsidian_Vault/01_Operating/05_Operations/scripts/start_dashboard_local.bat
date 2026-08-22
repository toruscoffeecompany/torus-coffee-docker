@echo off
REM Start dashboard_server.py locally for Miss Pink OODA verification
REM Requires Python 3.11 at the venv path
set PYTHON=D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\pythonw.exe"
set SCRIPT=Z:\Developer_Brain\01_Projects\capta1n_orchestrat0r\dashboard\dashboard_server.py
echo Starting dashboard server on port 8080...
"%PYTHON%" "%SCRIPT%"
pause
