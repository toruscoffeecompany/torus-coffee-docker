# DASHBOARD FIX PLAN — 2026-08-06
Generated: 2026-08-06T07:30:00.000000+00:00
Status: BLOCKED — needs Sir Green action

## Current state
- localhost:8080 = no listener
- localhost:8089 = no listener
- localhost:2375 = connection refused
- localhost:9999 = connection refused
- PINKCADY docker context: 9 containers up, 8081→307, 3000→200, 3100→200, 3200→200, 4000→200
- K8s namespace `torus` running on Docker Desktop

## Root cause candidates
1. `dashboard_server.py` not started on any ship
2. Hard-coded `VAULT_PATH = C:\Users\kidsm\Documents\My docs\VOID Pirate Trading Co\Obsidian_Vault\Developer_Brain` causes early failure if run from wrong user/context
3. Docker API on 2375/2376 not exposed on PINKCADY
4. SQUIDSTATION health-check endpoint 9999 not responding

## Verified fixes I can do without editing Sir Green’s code
- Confirmed `dashboard_server.py` expects port 8080
- Confirmed routes: `/`, `/api/status`, `/api/whale`, `/api/crew_heartbeat`, `/api/kuma`, `/healthz`
- Confirmed K8s demo workload live in `torus` namespace
- Confirmed Docker stack health on PINKCADY

## Actions needed from Sir Green
- Start `dashboard_server.py` on PINKCADY at `Z:\Developer_Brain\01_Projects\capta1n_orchestrat0r\dashboard\`
- Confirm vault path mapping for `kidsm` vs `torus` user
- Confirm whether Squidstation should expose 9999 health-check or if we use 8081 cadvisor instead
- Do NOT edit `dashboard_server.py` unless confirmed safe

## Actions needed from Captain/Miss Gordon
- Confirm Docker API exposure policy on 2375/2376
- Confirm whether dashboard should bind to 0.0.0.0 or 127.0.0.1
