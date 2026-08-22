# DOCKER_TASKLIST_20260806
Generated: 2026-08-06T16:12:00.000000+00:00
Sources: Docker deep dive audit, Sir Azure inbox, Trello, GitHub

## P1 — Execute Now

### Dashboard
- [ ] Restart `torus-dashboard` container on SQUIDSTATION
- [ ] Fix root cause of dashboard 502 regression
- [ ] Verify `/healthz`, `/api/crew_heartbeat`, `/api/fleet`, `/api/tools`, `/api/security-docs`, `/api/hw`, `/api/rig-report` all return 200

### Backup
- [ ] Start `torus-backup` container
- [ ] Verify backup jobs executing
- [ ] Check backup volume mounts and data integrity

### Security
- [ ] Fix Redis cross-protocol attack source (Prometheus scrape on Redis)
- [ ] Restrict Redis access to application containers only
- [ ] Verify Redis auth/password configured
- [ ] Add rate limiting to Redis connections

### Monitoring
- [ ] Fix Prometheus scrape config for `torus-website:3000/metrics`
- [ ] Fix Prometheus scrape config for `torus-pos:3100/metrics`
- [ ] Fix Prometheus scrape config for `torus-grafana:3000/metrics`
- [ ] Remove invalid scrape targets or add metrics endpoints

### Docker Hub
- [ ] Fix Docker Hub auth on PINKCADY (`toruscoffeecompany`)
- [ ] Verify push/pull works after auth fix
- [ ] Re-push `torus-dashboard` and `torus-backup` images

### Sir Azure / STEALTHATTACK
- [ ] Respond to Sir Azure with Trello API key + token
- [ ] Respond to Sir Azure with VOID Pirate Trading Co board IDs
- [ ] Respond to Sir Azure with guidance on Docker exec format error (A/B/C choice)
- [ ] Verify Sir Azure can build/push containers after guidance

## P2 — This Week

- [ ] Deduplicate Docker volumes (`torus_*` vs `torus-light_torus_*`)
- [ ] Prune 5.272GB reclaimable images
- [ ] Prune 1.222GB reclaimable build cache
- [ ] Add health checks to all compose services
- [ ] Add CPU/memory limits to all compose services
- [ ] Configure nginx reverse proxy for load balancing
- [ ] Set alert router env vars from secrets
- [ ] Add resource constraints to prevent exhaustion

## P3 — Backlog

- [ ] Migrate Torus services to Kubernetes
- [ ] Set up Docker Hub automated builds
- [ ] Deploy MCP server containers
- [ ] Implement proper secrets management

## Trello Cards Created
1. 🚨 [P1] Dashboard 502 regression: ALL routes down
2. 🚨 [P1] torus-backup container not running: backup automation offline
3. 🔐 [P1] Redis cross-protocol attacks every 75s from 172.18.0.5
4. 📊 [P1] Prometheus scrape failures: website/POS/grafana metrics broken
5. 🔑 [P1] Docker Hub auth failure: toruscoffeecompany push denied
6. 🐳 [P1] Sir Azure STEALTHATTACK: python:3.11-slim exec format error

## GitHub Issues Created
1. #215 🚨 [P1] Dashboard 502 regression: ALL routes down
2. #216 🚨 [P1] torus-backup container not running
3. #217 🔐 [P1] Redis cross-protocol attacks from 172.18.0.5
4. #218 📊 [P1] Prometheus scrape failures on website/POS/grafana
5. #219 🔑 [P1] Docker Hub auth failure toruscoffeecompany
6. #220 🐳 [P1] Sir Azure STEALTHATTACK Docker exec format error

## Crew Asks

### Sir Green
1. Restart dashboard container + investigate 502 root cause
2. Start backup container
3. Share Docker Hub credentials for auth fix
4. Confirm if K8s migration is planned

### Sir Azure
1. Choose Docker exec format error path: A/WSL2 debug, B/remote SQUIDSTATION, C/Windows-native
2. Provide Trello API key + token
3. Provide VOID Pirate Trading Co board IDs
