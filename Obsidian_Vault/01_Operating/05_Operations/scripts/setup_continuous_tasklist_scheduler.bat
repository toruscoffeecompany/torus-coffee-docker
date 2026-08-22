@echo off
REM Setup Windows Task Scheduler for continuous tasklist generation
REM Runs every 15 minutes

SCHTASKS /CREATE /TN "Torus_Continuous_Tasklist" /TR "\"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\pythonw.exe"\" \"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\scripts\continuous_tasklist.py\"" /SC MINUTE /MO 15 /F

SCHTASKS /CREATE /TN "Torus_OODA_Loop" /TR "\"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\pythonw.exe"\" \"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Crew\ooda_loop.py\" --once" /SC MINUTE /MO 1 /F

SCHTASKS /CREATE /TN "Torus_Vault_Audit" /TR "\"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\pythonw.exe"\" \"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\scripts\vault_audit.py\"" /SC DAILY /ST 02:00 /F

echo.
echo Scheduled tasks created:
echo - Torus_Continuous_Tasklist: every 15 minutes
echo - Torus_OODA_Loop: every 1 minute
echo - Torus_Vault_Audit: daily at 2:00 AM
