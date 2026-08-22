# Cmd Popup Elimination Audit

**Date:** 2026-08-08  
**Owner:** Miss Pink  

## Popup Sources Found

| File | Problem | Fix Applied |
|------|---------|-------------|
| `Startup\Torus_Dashboard_Launcher.vbs` | Used `C:\Python314\python.exe` (not `pythonw.exe`), hardcoded wrong Python path, broken path `\b_Skills` escape | Rewrote to use `venv\Scripts\pythonw.exe` with correct vault path |
| `scripts\run_vault_audit_hidden.vbs` | Wrapped `python.exe` in `cmd.exe /c "python.exe ... >> log 2>&1"` — cmd popup on Windows | Direct `pythonw.exe` invocation, no `cmd.exe /c` |
| `scripts\run_ooda_hidden.vbs` | Same `cmd.exe /c` wrapper pattern | Direct `pythonw.exe` invocation |
| `scripts\start_watchers.vbs` | Same `cmd.exe /c` wrapper pattern (2 lines) | Direct `pythonw.exe` invocation (both lines) |

## Verified Clean (no fix needed)

| File | Status |
|------|--------|
| `scripts\run_master_ooda_silent.vbs` | ✅ Already uses `pythonw.exe` directly |
| `scripts\run_master_ooda_hidden.vbs` | ✅ Already uses `pythonw.exe` directly |
| `scripts\run_continuous_ooda_hidden.vbs` | ✅ Already uses `pythonw.exe` directly |
| `scripts\run_smart_ticket_cycle_hidden.vbs` | ✅ Already uses `pythonw.exe` directly |
| `scripts\run_automated_verification_hidden.vbs` | ✅ Already uses `pythonw.exe` directly |
| `scripts\run_continuous_tasklist_hidden.vbs` | ✅ Already uses `pythonw.exe` directly |
| `scripts\run_silent_trigger_hidden.vbs` | ✅ Already uses `pythonw.exe` directly |
| `miss_pink_bot\start_miss_pink_bot.vbs` | ✅ Already uses `pythonw.exe` directly |
| `Startup\Torus_Comms_Watcher_Launcher.vbs` | ✅ Already uses `pythonw.exe` directly |

## Scheduled Tasks (all verified using `pythonw.exe` directly)

| Task Name | Command | Status |
|-----------|---------|--------|
| `Torus_Silent_Smart_System_Trigger` | `wscript.exe run_master_ooda_silent.vbs` | ✅ Clean |
| `Torus_Smart_Ticket_Cycle` | `wscript.exe run_smart_ticket_cycle_hidden.vbs` | ✅ Clean |
| `Torus_Automated_Verification` | `wscript.exe run_automated_verification_hidden.vbs` | ✅ Clean |
| `Torus_Continuous_OODA` | `wscript.exe run_continuous_ooda_hidden.vbs` | ✅ Disabled |
| `Torus_Daily_Ops_Check` | `pythonw.exe daily_ops_automation.py` | ✅ Clean |
| `Torus_Trello_Sync` | `pythonw.exe trello_sync.py` | ✅ Clean |
| `Torus_Inventory_Sync` | (scheduled) | ✅ Clean |
| `Torus_Inventory_Alert` | (scheduled) | ✅ Clean |
| `Torus_Marketing_Campaign_Check` | (scheduled) | ✅ Clean |
| `Torus_Social_Media_Check` | (scheduled) | ✅ Clean |
| `Torus_Social_Media_Calendar` | (scheduled) | ✅ Clean |
| `Torus_Daily_Obsidian_Note` | (scheduled) | ✅ Clean |
| `Torus_Weekly_Obsidian_Note` | (scheduled) | ✅ Clean |
| `Torus_Monthly_Obsidian_Note` | (scheduled) | ✅ Clean |
| `Torus_Monthly_Ops_Review` | (scheduled) | ✅ Clean |
| `Torus_Weekly_Ops_Review` | (scheduled) | ✅ Clean |
| `Torus_Order_Manager` | (scheduled) | ✅ Clean |
| `Torus_Miss_Pink_Self_Heal` | (scheduled) | ✅ Clean |
| `Torus_Vault_Audit` | (scheduled) | ✅ Clean |
| `Torus_Vault_Cleanup` | (scheduled) | ✅ Clean |
| `Torus_Vault_Sync_To_GitHub` | (scheduled) | ✅ Clean |
| `Torus_Asset_Validator` | (scheduled) | ✅ Clean |
| `Torus_Product_Photo_Tracker` | (scheduled) | ✅ Clean |
| `Torus_Monthly_Inventory_Count` | (scheduled) | ✅ Clean |
| `PINKCADY_SQUIDSTATION_Backup` | (scheduled) | ✅ Clean |
| `Torus Nightly Calendar Sync` | (scheduled) | ✅ Disabled |

## Critical Rule for Future VBS

**Never** use `cmd.exe /c` in VBS launchers — even with `0, False`, it creates a console window.  
**Always** call `pythonw.exe` directly with absolute paths:

```vbscript
WshShell.Run "D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\venv\Scripts\pythonw.exe D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\scripts\script.py", 0, False
```

## Root Cause

The 400+ stale `master_ooda_loop.py` processes from the crashed loop were launched by the old `run_master_ooda_silent.vbs` + `run_master_ooda_hidden.vbs`. The PID file check was failing due to `WinError 6` (invalid handle), causing the loop to error without properly checking for duplicates. The `silent_trigger_helper.py` then kept relaunching new instances every 5 minutes.

**Fix:** Kill all stale processes, clear PID file, reset state. The VBS wrappers that were already correct (`run_master_ooda_silent.vbs`) are fine for relaunching once the script bugs are fixed.
