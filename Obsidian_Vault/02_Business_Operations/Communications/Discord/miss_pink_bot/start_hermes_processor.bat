@echo off
REM ─|◊| Launch the Hermes Bridge Processor with the CORRECT Python environment
REM ─
REM FIX: Must use Hermes venv pythonw (has requests) — NOT uv python.exe (missing requests)
REM REF: trello-ops skill — TOOL NAME DISCIPLINE PITFALL
REM REF: windows-automation-audit — subprocess-creationflags pitfall

set BOT_DIR=D:\Work\Torus Coffee Company LLC\Obsidian_Vault\02_Business_Operations\Communications\Discord\miss_pink_bot
set PYTHONW=C:\Users\torus\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe

cd /d "%BOT_DIR%"
start /min "%PYTHONW%" "%BOT_DIR%\hermes_bridge_processor.py" > "%BOT_DIR%\hermes_runtime.log" 2>&1

echo Hermes bridge processor launched with correct venv Python
