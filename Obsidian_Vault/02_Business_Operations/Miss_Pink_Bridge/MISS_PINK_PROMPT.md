---
from: misspink
to: sirgreen
topic: status
id: MISS_PINK_PROMPT
requires_response: false
action_required: false
last_updated: 2026-08-04T18:00:00Z
---

# MISS_PINK_PROMPT — Current Focus Prompt

## Focus
- Execute Sir Green tasklist from `02_Business_Operations/Miss_Pink_Bridge/`
- Fix Docker services: `torus-backup`, `torus-dashboard`
- Verify heartbeat to dashboard
- Verify cross-matrix connectivity
- Clean up communications backlog

## Immediate Actions
1. Verify heartbeat: `http://192.168.0.39:8080/api/crew_heartbeat`
2. Restart `torus-backup` if needed
3. Verify `torus-dashboard` port mapping
4. Archive duplicate auto-prompt replies
5. Update Trello status
6. Push current bridge files to git

## Auto-Prompt Loop
- Running: `ooda_self_prompt_loop.py`
- Running: `pinkcady_comms_watcher.py`
- Shared bus: `02_Business_Operations/Communications/Outbox/SHARED_COMMS_BUS.json`

## Do Not Touch
- `09_Cosmos_Library`
- `VOID Pirate Trading Co`
- Squidstation vault paths outside confirmed lanes

## If You Find Unknown Paths
Pause and ask Sir Green before editing.
