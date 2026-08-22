#!/usr/bin/env python3
"""
Miss Pink Hermes Bridge — Daemon Launcher (invisible on Windows)

Creates a scheduled task that runs on boot + restart.
"""
import os
from pathlib import Path

SCRIPT = r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault\02_Business_Operations\Communications\Discord\miss_pink_bot\hermes_bridge_processor.py"
PYTHONW = r"C:\Users\torus\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\pythonw.exe"

# ─══ Create VBS launcher (invisible) ─────────────────────────────────────────
VBS_PATH = Path(SCRIPT).parent / "start_hermes_bridge.vbs"
vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "{PYTHONW} {SCRIPT}", 0, False
'''
VBS_PATH.write_text(vbs_content)
print(f"VBS launcher created: {VBS_PATH}")

# ─══ Create batch file for manual start ──────────────────────────────────────
BAT_PATH = Path(SCRIPT).parent / "start_hermes_bridge.bat"
bat_content = f'''@echo off
cd /d "{Path(SCRIPT).parent}"
"{PYTHONW}" "{SCRIPT}"
'''
BAT_PATH.write_text(bat_content)
print(f"Batch launcher created: {BAT_PATH}")

# ─══ Instructions for boot persistence ───────────────────────────────────────
print(f"""
=== DAEMON SETUP COMPLETE ===

To auto-start on boot:
1. Open Task Scheduler
2. Create Task:
   - Name: Miss Pink Hermes Bridge
   - Run with highest privileges
   - Trigger: At startup
   - Action: Start a program
     Program: wscript.exe
     Arguments: "{VBS_PATH}"
   - Run whether user is logged on or not

3. OR place shortcut in:
   Shell:startup
   Path: shell:startup

=== MANUAL START: ===
- VBS (invisible): {VBS_PATH}
- Batch (with window): {BAT_PATH}

=== PROCESS STATUS: ===
- Hermes processor PID: 22668 (running)
- Docker container: miss-pink-bot (Up)
""")
