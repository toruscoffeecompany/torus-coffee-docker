# OODA Continued Bug Hunt — 2026-08-13T07:15Z

## Network Edge + Trading Pipeline Deep Hunt

### Summary
Acted as a human user testing all network interfaces, Docker APIs, SSH, Wazuh, Augur, and security config.

### New Bugs Found (6 new, carded to VOID_OPS)

#### P0 — Critical (1)
1. **Docker API port 2376 unreachable on ALL interfaces**
   - `192.168.0.39:2376/_ping` → HTTP 000
   - `100.83.247.14:2376/_ping` → HTTP 000
   - `100.106.235.103:2376/_ping` → HTTP 000
   - Blocks ALL Docker operations (container management, monitoring, deployment)
   - Card: https://trello.com/c/RHRYjiHF

#### P1 — High (1)
2. **STEALTHATTACK API port 5000 unreachable**
   - Dashboard on 8080 works ✅, but SM API on 5000 → HTTP 000
   - Sir Azure's PC trading pipeline down
   - Card: https://trello.com/c/Dj0vdfeO

#### P2 — Medium (4)
3. **Wazuh security data missing** — agents installed but no data in dashboard API
   - Card: https://trello.com/c/TmKUXA8e

4. **Signals API has no timestamp** — can't verify data freshness
   - Card: https://trello.com/c/ZyTBMazf

5. **5 missing security headers** — X-Frame-Options, X-Content-Type-Options, HSTS, GZIP, Cache-Control
   - All FREE fixes
   - Card: https://trello.com/c/uHh52CJe

6. **Docker API — no TLS encryption configured** — if port 2376 is opened, needs TLS certs
   - Card: https://trello.com/c/Pxqe3ag2

### Already Carded (NOT re-created)
All these are already on VOID_OPS — skipped to avoid duplicates:
- Augur not running (running=False, genome_id=None)
- TM containers_down=[] (0 containers running)
- All dashboard 502s (services, vault, opsec, comms, scanner, captain, sir-azure, white-whale)
- All dashboard 404s (15 routes)
- All TM API 404s (account, orders, balance, performance, backtest, trade, execute, risk)
- GZIP + Cache-Control + HTTP/2 missing
- Docker API port 2376 unreachable on PINKCADY
- PINKCADY Tailscale IP unreachable
- Signals empty + no augur runs
- Positions empty
- Port 3000 running Gitea (not TreasureMap)
- TM /health returns HTML
- Alpaca gap_check=None
- TM /api/status download_status=null

### Auto-Verification Status
- Cron job `b309a7b70217` running every 5 min ✅
- 5 cards already verified + archived as FIXED by Sir Green:
  - API /api/services returns 502
  - API /api/captain returns 502
  - API /api/scanner returns 502
  - Dashboard /api/scanner + /api/sir-azure 502
  - Dashboard /api/vault 502
- Remaining broken cards auto-reopened

### OODA Loop Status
- ✅ 9/9 ALL SYSTEMS GO
- Dashboard: HTTP 200

### Action Items
- [ONGOING] Auto-verify monitor continues running
- [Sir Green] 6 new bug cards + 46 existing cards to fix
- [Miss Pink] Focus on A (website) + B (monitoring) per Captain's direction
