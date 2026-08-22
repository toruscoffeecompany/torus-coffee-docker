# Crew Fleet Audit — 2026-08-09

## Fleet Mesh Status

| Rig | Hostname | LAN IP | Tailscale IP | Role | Owner | Docker 2375 | Containers |
|-----|----------|--------|--------------|------|-------|-------------|------------|
| PINKCADY | PINKCADY | 192.168.0.3 | 100.8.0.2 | Torus Coffee Ops | **Miss Pink** ✅ | **UP** (HTTP 200) | 10 running |
| SQUIDSTATION | SQUIDSTATION | 192.168.0.39 | 100.8.0.3 | Fleet/Security Stack | **Sir Green** ⚠️ | **DOWN** (i/o timeout) | 0 reachable |
| STEALTHATTACK | STEALTHATTACK | 192.168.0.32 | 100.8.0.4 | Render/AI containers | **Sir Azure** ⚠️ | **502** (proxy/gateway) | unknown |

## PINKCADY (Miss Pink's Rig) — FULLY OPERATIONAL ✅

### Docker Desktop
- **Version:** 4.85.0, Server 29.6.2
- **Daemon:** `tcp://localhost:2375` → HTTP 200
- **Kubernetes:** DISABLED (was consuming ~1.4GB RAM)
- **Containers:** 10 running (torus-light stack)
  - torus-website (3000, healthy)
  - torus-redis (6379, healthy)
  - torus-grafana (3002, healthy)
  - torus-node-exporter (9100, unhealthy)
  - torus-backup (healthy)
  - torus-inventory (3200, unhealthy — needs mem_limit)
  - torus-pos (3100, unhealthy — needs mem_limit)
  - torus-alert-router (4000, unhealthy — needs mem_limit)
  - torus-cadvisor (8081, unhealthy)
  - torus-prometheus (9090, unhealthy)

### Scheduled Tasks
- `Torus_Continuous_OODA` — ✅ Ready (every 5 min)
- `Torus_Smart_Ticket_Cycle` — ✅ Ready (every 5 min, anti-duplication)
- `Torus_Trello_Sync` — ✅ Ready
- `Torus_Miss_Pink_Self_Heal` — ✅ Ready
- `Torus_Silent_Smart_System_Trigger` — ❌ Disabled (root cause of 5K flood)

### Cmd.exe Popup Fix
- `shell=True` → `shell=False` + `CREATE_NO_WINDOW` in:
  - `miss_pink_continuous_ooda.py:16` (THE MAIN SOURCE — runs every 5 min)
  - `miss_pink_self_heal.py:161` (Popen with shell=True)
  - `vault_sync_to_github.py:17`
  - `Crew/ooda_task_executor.py:45`
  - `Crew/ooda_task_loop.py:58`

### Anti-Duplication Deployment
- `crew_queue_automation.py` — `create_void_card()` now checks `find_existing_card_by_name()`
- `crew_queue_automation.py` — `claim_work_item("crew_queue_sync", "misspink", ...)` lock added to `run()`
- `ooda_loop_agent.py` — `create_trello_card()` deduped
- `inbox_processor.py` — `create_trello_card()` deduped
- `miss_pink_inbox_watcher.py` — `create_trello_card()` deduped

## SQUIDSTATION (Sir Green's Rig) — DOCKER DAEMON DOWN ⚠️

- **Ping:** ✅ Responding (192.168.0.39, 1ms)
- **Docker 2375:** ❌ i/o timeout — Docker Desktop daemon not running
- **SSH (port 22):** ❌ Closed — cannot restart remotely
- **Action needed:** Sir Green to restart Docker Desktop on SQUIDSTATION
- **Impact:** Sir Green's scheduled tasks on SQUIDSTATION may be failing silently

## STEALTHATTACK (Sir Azure's Rig) — DOCKER PROXY ISSUE ⚠️

- **Ping:** ✅ Responding (192.168.0.32, 4ms)
- **Docker 2375:** ⚠️ 502 Bad Gateway — something listening but proxying incorrectly
- **Possible cause:** Docker daemon running but nginx/proxy misconfigured
- **Action needed:** Sir Azure to check Docker Desktop + port forwarding on STEALTHATTACK
- **Note:** Per crew rules, Sir Azure's lane — Miss Pink cannot directly intervene

## Trello Board State

### VOID Ops (6a595669b8f8f99c93392f4f)
- **Total open:** 458 (reduced from 925)
- **Smart Bridge cards:** 1 (was 468 — 467 archived)
- **Sir Green's Queue:** 1 (the remaining Smart Bridge card)
- **Sir Azure's Queue:** 0

### Torus Ops (6a70a3157d0db4214ac3f9a3)
- **Total open:** 112 (was 113 — 1 Smart Bridge duplicate archived)
- **Top 10:** 10
- **P1:** 15
- **P2:** 86
- **Sir Green's Queue:** 0 ✅
- **Sir Azure's Queue:** 0 ✅

## Crew Coordination System
- **Lock file:** `Z:\Developer_Brain\Shared_With_Pink\crew_coordination_lock.json`
- **Status:** Clean (no stale claims) ✅
- **Last updated:** 2026-08-09
- **Test result:** claim_work_item → True, double-claim → False, release → OK ✅

## Outstanding P0/P1 Items
1. **SQUIDSTATION Docker daemon down** — Sir Green needs to restart Docker Desktop
2. **STEALTHATTACK Docker proxy 502** — Sir Azure needs to check Docker + port forwarding
3. **torus-light containers unhealthy** — need mem_limit verification (512M-128M set in compose)
4. **Outbox: 10,544 files** — pinkcady_comms_watcher.py still creating files (dedup needed)
