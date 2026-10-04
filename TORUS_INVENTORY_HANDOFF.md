# Torus-Inventory Fix — Handoff for Sir Green/Gordon

**Date:** 2026-08-04  
**Status:** Image built, container deployment blocked from PINKCADY

## What Was Built

### Local Files (Source of Truth)
- `10_Skills_Library/05_Operations/Docker/torus-inventory/Dockerfile`
- `10_Skills_Library/05_Operations/Docker/torus-inventory/requirements.txt`
- `10_Skills_Library/05_Operations/Docker/torus-inventory/inventory_api.py`
- `10_Skills_Library/05_Operations/Docker/torus-inventory/inventory_master.json`

### Docker Image
- **Tag:** `torus-inventory:local`
- **Built via:** `docker --context torus-squidstation build`
- **Status:** ✅ Image exists on SQUIDSTATION

### Container Deployment Issue
From PINKCADY, `docker run` fails with:
```
docker: Error response from daemon: Conflict. 
The container name "/torus-inventory" is already in use
```

The existing `torus-inventory` container is stuck restarting because it was built with a plain `python:3.11-slim` + `python -m http.server 3200` image that has no `/health` route.

## What Sir Green/Gordon Need to Do on SQUIDSTATION

### Option 1: SSH into SQUIDSTATION and run directly
```bash
# Stop and remove broken container
docker stop torus-inventory
docker rm torus-inventory

# Deploy fixed image
docker run -d \
  --name torus-inventory \
  --restart unless-stopped \
  -p 3200:3200 \
  torus-inventory:local
```

### Option 2: Use docker-compose
Add to existing `docker-compose.miss-pink.UPDATED.yml`:
```yaml
torus-inventory:
  image: torus-inventory:local
  container_name: torus-inventory
  restart: unless-stopped
  ports:
    - "192.168.0.39:3200:3200"
  networks:
    - void-fleet
```

## Expected Result
- Health: `http://192.168.0.39:3200/health` → `{"status":"ok","service":"torus-inventory"}`
- Inventory: `http://192.168.0.39:3200/inventory` → full inventory JSON

## SIR_PINK PowerShell Script
Location: `10_Skills_Library/05_Operations/Docker/SIR_PINK_Setup.ps1`
- Creates Docker context `torus-squidstation`
- Sets default context to SQUIDSTATION
- Verifies connection

## Current Docker Context (PINKCADY)
- `default` — local Docker Desktop (not running)
- `desktop-linux` — Docker Desktop Linux engine
- `torus-squidstation` — **active**, pointing to `tcp://192.168.0.39:2375`

## Connection Status
- Ping: ✅ 2ms
- Docker API 2375: ✅ OK
- Z: drive: ✅ Read-only
- Backup job: ✅ Scheduled
- Container list: ✅ 24+ containers visible
