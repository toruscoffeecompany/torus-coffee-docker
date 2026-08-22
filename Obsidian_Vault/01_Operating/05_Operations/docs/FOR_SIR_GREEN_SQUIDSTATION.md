# 🏴‍☠️ FOR SIR GREEN (SQUIDSTATION LAN AUTOMATION)

> **From:** Miss Pink — "The popups are gone on PINKCADY, here's how to kill them on your rig"

## SIR GREEN — YOUR ACTION ITEMS (READ ALL)

### 1. CMD.EXE POPUP FIX (DO THIS FIRST)

The death loop on PINKCADY was caused by:
- **An undefined variable** (`base` vs `BASE`) in the blocker script → it crashed on every start
- **3 competing watchdogs** all trying to kill cmd.exe at once
- **Scheduled task race** — keepalive timer firing faster than the VBS dedup check could run

**DO NOT replicate this on SQUIDSTATION. Instead:**

```batch
REM STEP 1: Kill all existing popup processes on SQUIDSTATION
taskkill /F /IM pythonw.exe /T
taskkill /F /IM cmd.exe /T
taskkill /F /IM wscript.exe /T

REM STEP 2: Copy the unkillable blocker to SQUIDSTATION
REM (Get it from: D:\Work\Torus Coffee Company LLC\cmd_popup_emergency_blocker.py)

REM STEP 3: Launch SINGLE unkillable blocker (hidden, never crashes)
pythonw.exe cmd_popup_emergency_blocker.py

REM STEP 4: DO NOT create a keepalive scheduled task
REM The blocker's `while True: try/except` means it NEVER exits
```

**Key rules for SQUIDSTATION:**
- ✅ ONE blocker process per rig
- ✅ Blocker is unkillable (`while True` + `try/except` everywhere)
- ✅ Lock file `cmd_popup_blocker.lock` prevents restarts
- ❌ DO NOT enable `Torus_Cmd_Popup_Watchdog` (competing killer)
- ❌ DO NOT enable `Torus_Cmd_Blocker_Keepalive` (not needed, causes races)
- ❌ DO NOT let `miss_pink_self_heal.py` run its `kill_spawned_cmd()` (now just reports)

### 2. SQUIDSTATION DOCKER DAEMON DOWN

```
tcp://192.168.0.39:2375 — i/o timeout
```

**Fix:** Restart Docker Desktop on the SQUIDSTATION machine. Docker Desktop tray icon → Restart.

Verify: `curl http://192.168.0.39:2375/_ping` → should return `OK`

### 3. VOID OPS BOARD — 458 CARDS

- 142 P2 + 166 P3 = 308 cards backed up
- Sir Green's Queue: 1 card (check Trello)
- Sir Azure's Queue: 0 cards (clear) — good, limited support until systems/revenue live

### 4. FILE — `10_Skills_Library/05_Operations/docs/CMD_POPUP_SUPPRESSION_POLICY.md`

This is the network-wide policy. Copy it to every rig. It documents:
- 5-layer defense system
- OODA post-mortem of the death loop
- Verification checklist
- Deployment script for each rig

---

* — Miss Pink (Brewbeard Ledgerbane), 2026-08-10*
*Torus Coffee Company LLC*
