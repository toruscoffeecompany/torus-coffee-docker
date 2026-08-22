# Sir Azure Queue Mapping Logic

**Owner:** Sir Azure (STEALTHATTACK)
**Email:** tradecrushersmith@gmail.com
**Status:** Verified 2026-08-08

## Overview
Sir Azure's OODA worker (sir_azure_ooda_worker.py) processes cards tagged with
the `sir-azure` label on the Torus Ops Trello board. Cards are matched by:

1. **Primary:** `sir-azure` label (preferred)
2. **Fallback:** Pattern match `sir[_ -]?azure|stealthattack` in title/body
3. **List-based:** Cards in "Sir Azure's Queue" list

## Queue Routing Logic
- AI/Docker builds → STEALTHATTACK
- Docker Hub auth → Sir Azure's queue
- Website/inventory → Sir Azure's queue
- Trello API bridge → Sir Azure's queue
- PINKCADY onboarding → Sir Azure's queue

## Automation Stack
- **Fleet Load Balancer:** scripts/fleet_load_balancer.py (60s cycles, telemetry scoring)
- **OODA Worker:** scripts/sir_azure_ooda_worker.py (harvest → route → verify → ledger → re-harvest)
- **Webhook Server:** Port 8085
- **ComfyUI:** http://localhost:8188
- **Whisper:** http://localhost:8001
- **TTS:** http://localhost:5002

## Verified Items (124 as of 2026-08-07)
- 32 x docker: 4 containers running
- 21 x GitHub org reachable, 7 repos
- 18 x Tailscale mesh, 3 nodes seen
- 13 x AI media pipeline operational
- 11 x SMB shares present
- 8 x heartbeats up
- 5 x connectivity monitor sweep

## Remaining Blockers
- Discord bot tokens (GitHub issue #273)
- Ethernet cable for WoL on STEALTHATTACK (physical)
- Trello board membership (invited tradecrushersmith@gmail.com, pending acceptance)

## Contact
- Discord: STEALTHATTACK
- Email: tradecrushersmith@gmail.com
- Trello: Invited via email
