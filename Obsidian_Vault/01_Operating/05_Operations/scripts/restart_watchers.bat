@echo off
taskkill /F /FI "WINDOWTITLE eq *pinkcady_comms_watcher*" 2>nul
taskkill /F /FI "WINDOWTITLE eq *ooda_self_prompt_loop*" 2>nul
timeout /t 2 /nobreak >nul
start "pinkcady_comms_watcher" /B  "10_Skills_Library\05_Operations\venv\Scripts\"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\pythonw.exe" 10_Skills_Library\05_Operations\Crew\pinkcady_comms_watcher.py"
start "ooda_self_prompt_loop" /B  "10_Skills_Library\05_Operations\venv\Scripts\"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\pythonw.exe" 10_Skills_Library\05_Operations\Crew\ooda_self_prompt_loop.py"