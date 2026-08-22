# Next-Gen Smart Ticketing Design — Miss Pink / Torus Coffee
**Last updated:** 2026-08-08  
**Owner:** Miss Pink  
**Status:** implemented locally; pending crew confirmations for Discord/dashboard

## Goal
Turn Torus_Ops into a self-advancing hive-mind board:
- One primary automation path, not three competing loops
- Every Trello card/GitHub issue gets exactly one status comment per advance
- Top 10 stays full; P0/P1/P2 get worked before backlog
- Stuck cards auto-route to P5/P6 with follow-up timestamps
- Done cards are verified before closing; unverified ones are requeued

## Primary Processing Order
1. `Top 10 — Focus Fleet` (hard cap 10)
2. `P0 - Alert / Critical / Do Now`
3. `P1 - High / Doing Now`
4. `P2 - Med High / This Week`
5. `P3 - Medium / Follow Up`

## Smart Ticket Cycle (`smart_ticket_cycle.py`)
- Runs as single hidden scheduled task every 5 minutes
- Promotes best P1/P2 into Top 10 when slots are open
- Downgrades stuck cards:
  - Explicit blockers/Waiting → P6 after 48h
  - Other stale high-priority cards → P5 after 96h
- Sets follow-up due dates on downgraded cards
- Done-list audit:
  - `VERIFIED_DONE` → close permanently
  - No verification → requeue to P2/P3 with audit comment

## Master OODA Loop (`master_ooda_loop.py`)
- Single source of truth for Trello + GitHub
- Refreshes `MASTER_OODA_TASKLIST.json` from live sources every cycle
- Selects next item from tasklist first, then live board as fallback
- Tracks recent work history with 4-hour cooldown
- Creates review notes for non-executable cards
- Moves completed work to Done; incomplete to P5
- Self-skips if duplicate instance is already running

## Silent Windows Automation
- All launchers use `pythonw.exe` directly via hidden VBS
- No `cmd.exe /c` wrappers; no console popups
- Silent trigger helper ensures master loop stays running
- Self-heal watchdog restarts loops only when unhealthy

## Discord Crew Plan
- Miss Pink: local bot token verified; webhook notifications active
- Crew apps await Sir Green/Sir Azure confirmation:
  - Sir Green: `Sir Green Bot` + dashboard/API/Docker
  - Sir Azure: `Sir Azure Discord Bot` + ComfyUI/GPU
  - Miss Pink: `Miss Pink` + `Crew Alert Bot`
  - TBD: `Ticket Alert Bot`, `White Whale Defense Bot`, `Inventory Bot`, `Rig Monitor Bot`

## Crew Actions Needed
1. Sir Green: SQUIDSTATION dashboard auth endpoint + preferred update method
2. Sir Azure: PINKCADY browser route to `localhost:8080` + Discord channel IDs
3. Sir Green/Sir Azure: approve creation of 5 pending Discord apps for guild `1527500149365018774`

## Anti-Spam Rules
- One timestamped status comment per card per advance
- 10-minute comment cooldown on Trello cards
- 4-hour recent-work cooldown before repeating the same card
- Discord connect confirmation sent once only
- No duplicate scheduled tasks for the same loop
