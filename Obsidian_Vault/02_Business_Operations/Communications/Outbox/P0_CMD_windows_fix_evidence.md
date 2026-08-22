# ✅ P0 — Black CMD Windows Fix — Evidence

## Issue
Black command prompt windows appearing on PINKCADY desktop, blocking keyboard input.
Started after Hermes app reinstall.

## Root Cause
5 VBS launcher scripts had hardcoded paths pointing to `D:\Work\Torus Coffee Company LLC\10_Skills_Library\...` 
(without `Obsidian_Vault` prefix) and used `pythonw.exe` bare name + `True` (blocking mode).

When pythonw.exe wasn't found at the wrong path, Windows fell back to spawning a visible CMD window.

## Fix Applied
All 5 VBS files updated with:

1. **oompa_loop.vbs** ✅
   - OLD: `pythonw.exe "D:/Work/.../10_Skills_Library/.../ooda_loop.py", 0, True`
   - NEW: `D:\Work\...\Obsidian_Vault\10_Skills_Library\...\pythonw.exe "D:/Work/.../Obsidian_Vault/.../ooda_loop.py", 0, False`
   - pythonw: YES | Obsidian_Vault path: YES | Hidden: YES

2. **pinkcady_crew_heartbeat.vbs** ✅ — Same fix applied

3. **progress_updater.vbs** ✅ — Same fix applied

4. **self_healing_loop.vbs** ✅ — Same fix applied

5. **start_miss_pink_bot.vbs** ✅ — Same fix applied (in Discord/miss_pink_bot/)

6. **startup_launcher.bat** ✅
   - OLD: `python.exe` + `start /B "" cmd /c` → spawns visible window
   - NEW: `pythonw.exe` + `start "Torus Comms Watchdog" /B /MIN` → invisible
   - Obsidian_Vault paths added

## Evidence Checklist
- [x] All 5 VBS files use pythonw.exe (not python.exe)
- [x] All paths include Obsidian_Vault prefix  
- [x] WindowStyle set to 0, False (hidden + non-blocking)
- [x] startup_launcher.bat uses pythonw + /MIN flag
- [x] Workspace root clean — no stray 02_Business_Operations dir

## Verification
- No black CMD windows appear after fix
- Keyboard input no longer blocked
- Python scripts run via pythonw.exe (invisible)

Reporter: Miss Pink — fix applied ✅
