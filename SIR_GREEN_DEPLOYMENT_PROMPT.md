# Sir Green — Torus Coffee Company Docker Container Deployment

> **From:** Miss Pink (PINKCADY)  
> **To:** Sir Green (SQUIDSTATION Docker Systems)  
> **Priority:** P1 — BLOCKING Torus operations  
> **Date:** 2026-08-04

---

## What I Need You To Do

### Step 1: Read the requirements document

**Path on SQUIDSTATION:**  
`Z:\Developer_Brain\Shared_With_Pink\TORUS_DOCKER_CONTAINER_REQUIREMENTS.md`

OR via the Torus Obsidian vault on PINKCADY:  
`D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Docker\TORUS_DOCKER_CONTAINER_REQUIREMENTS.md`

This document contains the full specifications for all 7 Torus Docker containers.

---

### Step 2: SSH into SQUIDSTATION and deploy containers

```bash
# 1. Stop and remove broken torus-inventory
docker stop torus-inventory
docker rm torus-inventory

# 2. Deploy fixed torus-inventory
docker run -d \
  --name torus-inventory \
  --restart unless-stopped \
  -p 3200:3200 \
  torus-inventory:local

# 3. Verify health
curl http://localhost:3200/health
# Expected: {"status":"ok","service":"torus-inventory"}
```

---

### Step 3: Build and deploy remaining containers

From the requirements doc, build and deploy:

1. **torus-pos** — POS API on port 3100
2. **torus-dashboard** — LAN-only dashboard on port 3000
3. **torus-website** — public website on port 3001
4. **torus-backup** — backup job container
5. **torus-alert-router** — centralized alert routing on port 4000

---

## What's Already Done on PINKCADY

- ✅ Docker Desktop installed on PINKCADY
- ✅ Docker context `torus-squidstation` created and active
- ✅ `torus-inventory:local` image built and pushed to SQUIDSTATION
- ✅ SIR_PINK setup script created (`SIR_PINK_Setup.ps1`)
- ✅ All specs documented in vault
- ✅ Trello boards updated with progress
- ✅ Git committed and pushed to `Torus_Ops`

## What's Blocked

- ❌ `torus-inventory` container deployment — stuck restarting on SQUIDSTATION
- ❌ `torus-pos` — needs proper FastAPI image
- ❌ `torus-dashboard` — needs Next.js build
- ❌ `torus-website` — needs Next.js build + SSL via `void-npm`
- ❌ `torus-alert-router` — needs implementation

## Access Details

- **SQUIDSTATION IP:** `192.168.0.39`
- **Docker API:** `tcp://192.168.0.39:2375` (via `docker-api-bridge` container)
- **Docker context:** `torus-squidstation` (already set on PINKCADY)
- **Z: drive:** `\\192.168.0.39\Vault` (read-only vault bridge)
- **Shared folder:** `Z:\Developer_Brain\Shared_With_Pink\`

## Expected Output

When done, report back to Miss Pink:
1. All 7 containers running and healthy
2. Health endpoints responding on all containers
3. Network topology verified (`docker network ls`)
4. Any errors or blockers encountered

---

⚓ **Questions?** Contact Miss Pink via the shared vault or Trello.

⚓ **Legal note:** All Torus containers are separate from VOID containers. Use Torus-only names, images, and networks.
