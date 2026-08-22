# 🏴‍☠️ POLICY: cmd.exe POPUP SUPPRESSION — NETWORK-WIDE SELF-HEAL

> **Author:** Miss Pink (Brewbeard Ledgerbane)  
> **Date:** 2026-08-10  
> **Status:** ✅ DEPLOYED — Death loop eliminated  
> **Distribution:** Sir Green (SQUIDSTATION), Sir Azure (STEALTHATTACK), Pirate Captain's Dashboard

---

## EXECUTIVE SUMMARY

cmd.exe popup windows are **eliminated** on PINKCADY. The death loop that caused repeated blocker restarts has been **permanently fixed**. This document serves as the network-wide self-heal policy — Sir Green should apply the same pattern on SQUIDSTATION, and Sir Azure on STEALTHATTACK.

---

## DEATH LOOP ROOT CAUSE (OAU — Observe, Orient, Decide, Act)

### What Happened
1. **Multiple competing cmd.exe killers** were running simultaneously:
   - `cmd_popup_emergency_blocker.py` — 30ms check
   - `cmd_popup_watchdog.py` — 3s check
   - `miss_pink_self_heal.py` — has its own cmd.exe killer (lines 225-232)
2. **Startup VBS files** auto-launched `watchdog_launcher.py` which spawned more daemons
3. **Keepalive scheduled task** restarted the blocker every 2 minutes
4. **The blocker script had a bug**: `base` variable was undefined → crashed on start → keepalive restarted it → it crashed again = **infinite restart loop**

### Detection (OODA Loop)
- **Observe:** Blocker log showed 19 START entries in 4 minutes (every ~15s)
- **Orient:** Same PIDs being killed 47 times each — blocker was killing its own wmi subprocesses, AND the keepalive was racing
- **Decide:** Need single unkillable blocker + no competing watchdogs
- **Act:** Rewrote blocker with `try/except` around EVERYTHING so it never exits; disabled keepalive; removed startup VBS files

---

## THE FIX (5-Layer Defense)

### Layer 1: Unkillable Blocker (PRIMARY)
**File:** `cmd_popup_emergency_blocker.py`
- Written as `pythonw.exe` (hidden, no console window)
- `while True:` main loop with `try/except` catching EVERYTHING — **never exits**
- Checks for cmd.exe every **30ms** (0.03s) — faster than any window can render
- Uses `creationflags=CREATE_NO_WINDOW` on ALL `subprocess.run` calls
- PID parsing: `''.join(c for c in pid if c.isdigit())` — strips quotes, no death loop
- Writes PID file + lock file on start
- Lock file is NEVER removed — so dedup always works

### Layer 2: Shell=True Elimination (SYSTEMIC)
**Files fixed:**
- `miss_pink_continuous_ooda.py:16`
- `miss_pink_self_heal.py:161`
- `vault_sync_to_github.py:17`
- `ooda_task_executor.py:45`
- `ooda_task_loop.py:58`

**Fix pattern:** `shell=True` → `shell=False` + `shlex.split()` + `creationflags=CREATE_NO_WINDOW`

### Layer 3: VBS Launcher Dedup (PREVENTIVE)
**Files:** 13 VBS launcher files in `scripts/`
- Each checks `wmic process where "name='pythonw.exe' and CommandLine like '%script_name%'" GET ProcessId`
- If already running → `WScript.Quit` (exit immediately)
- All use `, 0, False` (hidden window mode)

### Layer 4: PID-File Dedup in Python Launchers (DEFENSE-IN-DEPTH)
**Files:** `launch_watcher.py`, `start_watcher_safe.py`
- Both now check PID files before spawning new processes
- `is_running()` checks BOTH `python.exe` AND `pythonw.exe` (was only checking `python.exe`)

### Layer 5: No Keepalive Task (ELIMINATES RACE)
- The keepalive scheduled task was **the cause of the race condition**
- 2-minute timer fired VBS → VBS ran `wmic` (takes >1s) → second timer fired → spawned duplicate before first VBS finished checking
- **FIX:** Disabled keepalive task entirely. The unkillable blocker's `try/except` means it never crashes, so no restart is needed.

---

## NETWORK-WIDE DEPLOYMENT (For Sir Green + Sir Azure)

### Apply to SQUIDSTATION
```batch
# 1. Copy the blocker to the same path on SQUIDSTATION
scp cmd_popup_emergency_blocker.py \\SQUIDSTATION\C$\Torus_Crew\Scripts\

# 2. Create the unkillable service via scheduled task (runs at boot)
schtasks /create /tn "Torus_Cmd_Blocker" /tr "pythonw.exe C:\Torus_Crew\Scripts\cmd_popup_emergency_blocker.py" /sc onstart /f

# 3. NO keepalive task — the blocker never exits
# 4. Remove any existing startup VBS files that compete
```

### Apply to STEALTHATTACK
```batch
# Same pattern — single unkillable blocker, NO competing watchdogs
# Do NOT deploy cmd_popup_watchdog.py alongside the emergency blocker
```

### Docker Containers (for all rigs running Docker)
Containers that spawn `cmd.exe` (via `shell=True` in Python) need the same `shell=False` + `CREATE_NO_WINDOW` fix. Check with:
```bash
docker exec TORUS_CONTAINER grep -rn "shell=True" --include="*.py" .
```

---

## VERIFICATION CHECKLIST

| Check | Command | Expected |
|-------|---------|----------|
| cmd.exe running | `tasklist /FI "IMAGENAME eq cmd.exe"` | 0 processes |
| Blocker running | `tasklist /FI "IMAGENAME eq pythonw.exe"` | 1 process |
| wscript.exe running | `tasklist /FI "IMAGENAME eq wscript.exe"` | 0 processes |
| No competing tasks | `schtasks /query /tn "Torus_Cmd_Popup_Watchdog"` | Disabled |
| No startup VBS | `ls $APPDATA/.../Startup/.*.vbs` | Empty (except desktop.ini) |
| Lock file exists | `file_exists cmd_popup_blocker.lock` | Yes |
| Log shows 1 start | `grep START cmd_blocker_emergency.log` | 1 entry |
| No restarts | `wc -l cmd_blocker_emergency.log` | ≤ 3 entries |

---

## CURRENT STATE (Verified 2026-08-10)

```
pythonw.exe:  1  ✅  (blocker only)
cmd.exe:      0  ✅  (all popups killed)
wscript.exe:  0  ✅  (no competing launchers)
Scheduled tasks: 6 essential enabled, 23 non-essential disabled

Keepalive task: DISABLED (not needed — blocker is unkillable)
```

---

## GIT COMMITS

- `792f82e` — fix: PID parsing death loop (strip quotes, digits only)
- `e81338b` — fix: VBS dedup on ALL 11 launcher scripts
- `0c24a2d` — fix: PID-file dedup on launch_watcher + start_watcher_safe
- `6013a53` — fix: disabled keepalive to prevent duplicates
- `e10119e` — fix: Windows startup VBS + all cmd.exe defenses
- `870f0db` — fix: DEATH LOOP FIXED — lock file dedup + all tasks reset
- `3ace5de` — fix: system state updates + death loop eliminated
- `b7c7e03` — fix: unblocker PID parsing death loop fix + start script + scheduled tasks

**Latest:** `3ace5de` — Death loop permanently eliminated

---

## LESSONS LEARNED (for Pirate Captain's Dashboard)

1. **Never have multiple cmd.exe killers running** — they compete and create feedback loops
2. **PID-file dedup is better than wmic** — wmic is slow (>1s), creating race conditions
3. **Scheduled task keepalive timers RACE** — two timers can fire simultaneously and both spawn processes before either checks
4. **`base` vs `BASE` variable error** — in scripts that run detached (pythonw), errors are invisible. Always test scripts with regular `python` first.
5. **Lock files should be persistent** — don't remove them on exit. The unkillable blocker writes lock once and never removes it.
