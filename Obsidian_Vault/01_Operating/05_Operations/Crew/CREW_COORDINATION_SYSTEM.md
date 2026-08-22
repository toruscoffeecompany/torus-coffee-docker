# Crew Coordination System — Checks & Balances

## Overview
Shared lock file that prevents Miss Pink, Sir Green, and Sir Azure from
working on the same Trello card or GitHub issue simultaneously.

## How It Works
1. Every 5 minutes, each crew member's OODA agent (OODA auto_prompts) checks:
   - New messages in PINKCADY_INBOX (for Sir Green → Miss Pink replies)
   - Sir Azure's INBOX on STEALTHATTACK
2. Before starting work on any item, the agent calls `claim_work_item(item_id, crew_member)`
3. If another crew member already has the claim, the agent **skips** that item
4. After completing work, the agent calls `release_work_item(item_id)`
5. Stale claims (30 min old) auto-expire

## Key Items Covered
- `trello_sync` — Prevents concurrent Trello sync runs
- `git_auto` — Prevents concurrent git auto-commit/push
- `msg:{message_id}` — Prevents concurrent processing of inbox messages
- `card:{trello_card_id}` — Prevents concurrent Trello card processing
- `issue:{github_issue_id}` — Prevents concurrent GitHub issue processing

## Stations
| Crew Member | Workstation | Hostname Path |
|-------------|-------------|---------------|
| Miss Pink | PINKCADY | `D:\Work\Torus Coffee Company LLC` |
| Sir Green | SQUIDSTATION | `D:\Work\Torus Coffee Company LLC` |
| Sir Azure | STEALTHATTACK | `D:\Work\Torus Coffee Company LLC` |

## Shared Path
- **Lock file**: `Z:\Developer_Brain\Shared_With_Pink\crew_coordination_lock.json`
- **Backup**: `10_Skills_Library/05_Operations\crew_coordination_lock.json` per station

## Integration
To add crew coordination to any script:
```python
from crew_coordination import claim_work_item, release_work_item, is_claimed

# Before work:
if claim_work_item("card:6a7536b95c7790", "misspink", "Processing content pipeline"):
    try:
        # ... do work ...
    finally:
        release_work_item("card:6a7536b95c7790")
```

## Status
- ✅ `crew_coordination.py` — Created at `10_Skills_Library/05_Operations/Crew/`
- ✅ `ooda_auto_agent.py` — Integrated with claim/release for message processing, Trello sync, and git auto-commit
- ✅ `shell=True` fix — `run()` and `run_raw()` now use `CREATE_NO_WINDOW` flag to eliminate cmd.exe popup windows
- ⏳ Sir Green — Integrate into `sirgreen_auto_prompt.py`
- ⏳ Sir Azure — Integrate into `sirazure_auto_prompt.py`

## Root Cause of 5,000 Card Bloat
The `card_cleanup_ooda.py` used wrong VOID board ID (`6a7437aa` instead of `6a595669`).
Cards accumulated in Sir Green's Queue (2,925) and Sir Azure's Queue (1,158) on the Torus board.
Fixed in `fix_void_transfer_v5.py` + `archive_aggressive_v6.py`.
