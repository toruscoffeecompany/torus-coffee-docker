# CMD.EXE Popup Fix — Root Cause & Resolution

## Problem
Quick-opening command prompt windows (cmd.exe popups) appearing every few seconds,
making typing difficult on PINKCADY.

## Root Cause
`Crew/ooda_auto_agent.py` line 61: `subprocess.run(cmd, shell=True, ...)`

On Windows, `shell=True` spawns `cmd.exe /c` for every command execution.
The continuous OODA auto-agent was running every 5 seconds, each time calling
`run()` for shell commands (git, docker, trello sync, etc.), spawning visible
cmd.exe windows.

## Fix Applied
### File: `Crew/ooda_auto_agent.py`
**Before:**
```python
def run(cmd, timeout=60, cwd=None):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)
```

**After:**
```python
import shlex

def run(cmd, timeout=60, cwd=None):
    """Run a command without spawning cmd.exe (fixes Windows popup windows).
    Accepts either a list (preferred) or a shell string (auto-split via shlex)."""
    try:
        args = cmd if isinstance(cmd, list) else shlex.split(cmd)
        r = subprocess.run(args, shell=False, capture_output=True, text=True,
                          timeout=timeout, cwd=cwd,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)
```

Key changes:
- `shell=True` → `shell=False` (prevents cmd.exe spawning)
- Added `shlex.split()` for shell string compatibility
- Added `creationflags=CREATE_NO_WINDOW` for defense-in-depth

Also fixed `run_raw()`:
```python
def run_raw(cmd, timeout=60):
    args = cmd if isinstance(cmd, list) else shlex.split(cmd)
    r = subprocess.run(args, shell=False, capture_output=True, text=True,
                      timeout=timeout,
                      creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return r.returncode, r.stdout, r.stderr
```

## Verification
All scheduled tasks now launch via `pythonw.exe` (hidden window) in VBS wrappers
with `WshShell.Run(..., 0, False)` — the `0` means hidden, `False` means don't wait.
No visible cmd.exe windows will appear.

## Related: Card Duplication Fix
While investigating, discovered that `continuous_ooda_worker.py` and
`smart_ticket_cycle.py` both had identical promotion logic running every 5 min
(continuous) vs continuously. This created 2,000+ duplicate Smart Bridge cards.

**Fix:** Disabled promotion in `continuous_ooda_worker.py` — only
`smart_ticket_cycle.py` handles Top 10 promotion now, with anti-duplication
tracking (`recently_promoted` state with 24h cooldown).
