# DOCKER DEEP DIVE AUDIT 20260806
Generated: 2026-08-06T16:10:00.000000+00:00
Scope: Full Docker Desktop review — containers, images, volumes, networks, compose, logs, builds, Kubernetes, Docker Hub, MCPs, auth

## Executive Summary
- **Docker Desktop**: v29.7.1, Server v29.6.2, WSL2 backend
- **Kubernetes**: Docker Desktop K8s v1.36.1, inactive Swarm
- **Containers**: 29 running, 0 stopped
- **Images**: 38 images, 8.897GB total, 5.272GB reclaimable (59%)
- **Volumes**: 14 local volumes, 91.34MB total
- **Build Cache**: 87 items, 1.222GB reclaimable
- **Networks**: bridge, host, none, torus-network

## Critical Findings

### 1. Dashboard 502 Regression (ALL Routes)
**Severity**: P1 Blocker
- `/healthz` → 502
- `/api/crew_heartbeat` → 502
- `/api/status` → 502
- `/api/fleet` → 502
- `/api/tools` → 502
- `/api/security-docs` → 502
- `/api/hw` → 502
- `/api/rig-report` → 502

### 2. torus-backup / torus-dashboard Images Exist But Containers NOT Running
**Severity**: P1
- Images present: `toruscoffee/torus-dashboard:20260806-v1` (178MB), `toruscoffee/torus-backup:20260806-v1` (24.8MB)
- No running containers for these services
- Backup service not executing
- Dashboard service down

### 3. Redis Cross-Protocol Scripting Attacks Every 75s
**Severity**: P1 Security
- Log: "Possible SECURITY ATTACK detected... POST or Host: commands"
- Source: 172.18.0.5 (Prometheus scraping `/metrics` on Redis?)
- Pattern: every 75 seconds, consistent probing
- Impact: Redis aborting connections

### 4. Prometheus Scrape Failures
**Severity**: P1
- `torus-website:3000/metrics` → returns HTML, not metrics
- `torus-pos:3100/metrics` → 404
- `torus-grafana:3000/metrics` → 404
- `torus-cadvisor:8080/metrics` → 200 OK

### 5. Docker Hub Auth Failure
**Severity**: P1
- Account: `toruscoffeecompany`
- Error: `denied: requested access to the resource is denied`
- Impact: Cannot push/pull images from Docker Hub

### 6. Sir Azure STEALTHATTACK Docker Blocker
**Severity**: P1
- `python:3.11-slim` → `exec format error` on WSL2
- `alpine:latest` works
- Blocks local container builds on STEALTHATTACK

### 7. Duplicate Volumes
**Severity**: P2
- `torus_*` and `torus-light_torus_*` volumes both exist
- Same compose project has duplicate volume naming
- Wastes storage

### 8. Image Bloat / Reclaimable Space
**Severity**: P2
- 5.272GB reclaimable from images
- 1.222GB reclaimable from build cache
- 87 stale build cache items
- Total recoverable: ~6.5GB

### 9. No Load Balancing
**Severity**: P2
- All services single-instance
- No reverse proxy load balancing
- Single point of failure for each service

### 10. No Health Checks / Resource Limits
**Severity**: P2
- No `healthcheck` directives in compose
- No CPU/memory limits/restraints
- Risk of resource exhaustion

### 11. Alert Router Missing Env Vars
**Severity**: P2
- DISCORD_WEBHOOK: blank
- SMTP_HOST: blank
- SMTP_PORT: blank
- SMTP_USER: blank
- SMTP_PASS: blank
- OBSIDIAN_VAULT: blank

### 12. Kubernetes Underutilized
**Severity**: P2
- Only `my-app` deployment running
- K8s cluster not utilized for Torus services
- No HPA, no ingress, no persistent volumes

### 13. No MCP Servers Running
**Severity**: P3
- Docker MCP plugin installed
- No MCP server containers running

### 14. No Docker Hub Automation
**Severity**: P3
- No automated build/push pipelines
- Manual image tagging/pushing only

## Recommendations

### Immediate (P1)
1. Restart `torus-dashboard` and `torus-backup` containers
2. Fix Docker Hub auth on PINKCADY
3. Investigate Redis cross-protocol attack source
4. Fix Prometheus scrape configs for website/POS/Grafana
5. Respond to Sir Azure with Trello auth + build/push guidance

### Short-term (P2)
1. Deduplicate volumes (`torus-light_torus_*` → `torus_*`)
2. Prune images and build cache
3. Add health checks and resource limits to compose
4. Add nginx reverse proxy for load balancing
5. Configure alert router env vars from secrets

### Medium-term (P3)
1. Migrate Torus services to K8s
2. Set up Docker Hub automated builds
3. Deploy MCP server containers
4. Implement proper secrets management

## Artifacts
- Full compose config: extracted from `docker-compose.yml`
- Container inventory: 29 containers
- Image inventory: 38 images
- Volume inventory: 14 volumes
- Network inventory: 4 networks
- Log analysis: all containers analyzed
