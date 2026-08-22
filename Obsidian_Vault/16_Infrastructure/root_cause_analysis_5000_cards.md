# Root Cause Analysis: 5,000 Card Board Bloat

## Problem
Torus Ops board had 5,000 open cards instead of the expected ~300.

## Root Causes

### 1. VOID Transfer Piled Cards Into Crew Queue Lists (NOT separate boards)
- `card_cleanup_ooda.py` transferred 321 VOID cards to "Sir Green's Queue" and "Sir Azure's Queue"
  on the **same** Torus Ops board, NOT the separate VOID Ops board
- These lists were never targeted by `smart_ticket_cycle.py` or archiving scripts
- Sir Green's Queue: **2,925 open cards**, Sir Azure's Queue: **1,158 open cards**

### 2. smart_ticket_cycle Only Processes Primary Work Lists
The cycle script's `work_list_order` is `[TOP10_LIST, P0_LIST, P1_LIST, P2_LIST, P3_LIST]`
and it only archives via `close_card()` for Done-list cards with "VERIFIED_DONE" in desc.
It **never touches** crew queue lists.

### 3. archive_aggressive_v3.py Pattern Matching Was Too Narrow
The v3 archiver only matched specific name patterns:
- `[INBOX]`, `[AUTO]`, `SYSTEM ONLINE`, `Webhook Event`, etc.
- Duplicates by name
- OODA in desc + old (>7 days)
- VERIFIED_DONE in desc

This missed the VOID transferred cards that:
- Had no OODA comment (just transferred with a comment)
- Didn't match any name pattern
- Were in crew queue lists (not P2/P3 lists)

### 4. Done List Never Populated
Cards were closed (archived) directly via `closed=true` in the Trello API,
never moved to the "Done" list first. The Done list had **0 cards**.

## Fix Actions
1. **Run `archive_aggressive_v4.py`**: Targets crew queue lists explicitly
2. **Patch `smart_ticket_cycle.py`**: Added auto-archive pass for P3+ cards with OODA comments >7 days old
3. **Verify VOID board**: Check if VOID Ops board (6a7437aa41aa267cb787c900) is the correct target

## Prevention
- smart_ticket_cycle now archives P3+ cards with OODA desc comments >7 days old
- Archive scripts now scan ALL lists, not just priority lists
- Board counts log now includes per-list breakdown
