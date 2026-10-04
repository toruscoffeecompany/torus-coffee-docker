# Torus Coffee Company — Docker Container Requirements

> **Source of Truth:** This document is the authoritative list of Docker containers required for Torus Coffee Company operations.  
> **Location:** `10_Skills_Library/05_Operations/Docker/TORUS_DOCKER_CONTAINER_REQUIREMENTS.md`  
> **Last Updated:** 2026-08-04  
> **Status:** DRAFT — awaiting Sir Green/Mr. Gordon review

---

## 1. Current Infrastructure

| Machine | Role | Docker Status |
|---------|------|---------------|
| **SQUIDSTATION** (`192.168.0.39`) | Primary Docker host | ✅ Docker Desktop, 16 CPUs, 15.59 GiB RAM |
| **PINKCADY** (`192.168.0.3`) | Secondary workstation | ✅ Docker Desktop installed, not running |
| **STEALTHATTACK** | Remote client | ❌ Admin access blocked |

**Critical Rule:** SQUIDSTATION is the **only** Docker host. All Torus containers must run on SQUIDSTATION.

---

## 2. Existing Torus Containers

These are already deployed on SQUIDSTATION:

| Container | Image | Port | Health | Notes |
|-----------|-------|------|--------|-------|
| `torus-pos` | `python:3.11-slim` | `3100` | ✅ Healthy | Basic Python HTTP server |
| `torus-inventory` | `python:3.11-slim` | `3200` | ❌ Unhealthy | **Needs rebuild** — serving static files, no `/health` route |
| `torus-redis` | `redis:7-alpine` | `6379` | ✅ Healthy | Redis cache |
| `torus-backup` | `alpine:latest` | — | ✅ Healthy | Backup job container |

---

## 3. Required Docker Containers

### 3.1 torus-inventory (PRIORITY 1 — BLOCKED)

**Status:** Image built (`torus-inventory:local`), container stuck restarting  
**Why:** Existing container was built with `python -m http.server 3200` which has no `/health` route  
**Fix needed:** Sir Green must redeploy using the new FastAPI image

**Specifications:**
- **Image:** `torus-inventory:local` (built from vault Dockerfile)
- **Port:** `3200:3200`
- **Volume:** `D:/Work/Torus Coffee Company LLC:/vault:ro` (read-only vault mount)
- **Restart:** `unless-stopped`
- **Endpoints:**
  - `GET /health` → `{"status":"ok","service":"torus-inventory"}`
  - `GET /inventory` → full inventory JSON from `/vault/04_Products/inventory_master.json`
  - `GET /` → service info

**Files needed:**
- `10_Skills_Library/05_Operations/Docker/torus-inventory/Dockerfile`
- `10_Skills_Library/05_Operations/Docker/torus-inventory/requirements.txt`
- `10_Skills_Library/05_Operations/Docker/torus-inventory/inventory_api.py`
- `10_Skills_Library/05_Operations/Docker/torus-inventory/inventory_master.json`

**Deployment command:**
```bash
docker stop torus-inventory
docker rm torus-inventory
docker run -d \
  --name torus-inventory \
  --restart unless-stopped \
  -p 3200:3200 \
  -v "D:/Work/Torus Coffee Company LLC:/vault:ro" \
  torus-inventory:local
```

---

### 3.2 torus-pos (PRIORITY 2)

**Status:** Running but basic HTTP server only  
**Why:** Currently just `python:3.11-slim` with `python -m http.server 3100`  
**Upgrade needed:** Replace with proper POS API

**Specifications:**
- **Image:** `torus-pos:local` (to be built)
- **Port:** `3100:3100`
- **Volume:** `D:/Work/Torus Coffee Company LLC:/vault:ro`
- **Restart:** `unless-stopped`
- **Endpoints:**
  - `GET /health` → health check
  - `GET /orders` → read `04_Products/orders.json`
  - `POST /orders` → create new order
  - `GET /products` → read inventory

**Dependencies:**
- FastAPI or Flask
- Redis for order queue (`torus-redis`)

---

### 3.3 torus-redis (PRIORITY 1 — RUNNING)

**Status:** ✅ Healthy  
**Image:** `redis:7-alpine`  
**Port:** `6379:6379`  
**Volume:** `treasuremap_cache_pink` (if shared) or local volume  
**Notes:** Used by torus-pos and torus-inventory

---

### 3.4 torus-dashboard (PRIORITY 3)

**Status:** Not yet created  
**Why:** LAN-only dashboard for Torus operations

**Specifications:**
- **Image:** `torus-dashboard:local` (to be built from `06_Website/dashboard/`)
- **Port:** `3000:3000`
- **Volume:** `D:/Work/Torus Coffee Company LLC:/vault:ro`
- **Restart:** `unless-stopped`
- **Framework:** Next.js + Tailwind CSS
- **Access:** LAN only (`192.168.0.3` or `192.168.0.39`)

---

### 3.5 torus-website (PRIORITY 4)

**Status:** Not yet deployed  
**Why:** Public website for Torus Coffee Company

**Specifications:**
- **Image:** `torus-website:local` (to be built from `06_Website/Website/`)
- **Port:** `3001:3000` (internal Next.js port 3000, exposed as 3001)
- **Restart:** `unless-stopped`
- **Framework:** Next.js + Tailwind CSS
- **Deploy target:** Netlify (preferred) or SQUIDSTATION reverse proxy
- **SSL:** Via `void-npm` (nginx-proxy-manager) on SQUIDSTATION

---

### 3.6 torus-backup (PRIORITY 2)

**Status:** ✅ Running  
**Image:** `alpine:latest`  
**Notes:** Backup job container, currently running

**Upgrade needed:**
- Replace with proper backup script
- Schedule via Task Scheduler on PINKCADY or cron on SQUIDSTATION
- Backup vault to Z: drive (`Z:\Developer_Brain\Shared_With_Pink\`)

---

### 3.7 torus-alert-router (PRIORITY 3)

**Status:** Not yet created  
**Why:** Centralized alert routing for all Torus services

**Specifications:**
- **Image:** `torus-alert-router:local`
- **Port:** `4000:4000`
- **Dependencies:** Redis, Gmail API
- **Alert routing:**
  - Critical → email (4hr cooldown)
  - Warning → Obsidian daily note
  - Info → log file
  - Debug → console

---

## 4. Container Network Topology

```
SQUIDSTATION (192.168.0.39)
├── void-fleet (shared bridge network)
│   ├── torus-pos:3100
│   ├── torus-inventory:3200
│   ├── torus-redis:6379
│   ├── torus-dashboard:3000
│   └── torus-website:3001
│
├── torus-network (Torus-only network)
│   ├── torus-pos
│   ├── torus-inventory
│   └── torus-redis
│
└── infrastructure_docker-network
    ├── void-npm:80-81,443
    ├── void-kuma:3001
    ├── void-nextcloud:80
    └── void-vaultwarden:80
```

---

## 5. Volume Requirements

| Volume | Purpose | Mount Point | Type |
|--------|---------|-------------|------|
| `torus-data` | Vault data | `/vault` | Bind mount (read-only) |
| `torus-redis-data` | Redis persistence | `/data` | Named volume |
| `torus-pos-data` | POS orders | `/app/data` | Named volume |
| `torus-inventory-data` | Inventory cache | `/app/data` | Named volume |
| `torus-backup-data` | Backup storage | `/backups` | Named volume |

---

## 6. Resource Requirements

### SQUIDSTATION (Primary Host)
- **CPU:** 16 cores available
- **RAM:** 15.59 GiB available
- **GPU:** None currently (future: add for SIR_AZURE AI pipeline)
- **Storage:** Local SSD + Z: drive (SMB share)

### Resource Allocation per Container
| Container | CPU Limit | RAM Limit | Priority |
|-----------|-----------|-----------|----------|
| torus-pos | 1 core | 512 MB | High |
| torus-inventory | 0.5 core | 256 MB | High |
| torus-redis | 0.5 core | 256 MB | High |
| torus-dashboard | 1 core | 512 MB | Medium |
| torus-website | 1 core | 512 MB | Medium |
| torus-alert-router | 0.5 core | 256 MB | Low |

---

## 7. Security Requirements

1. **Network Isolation:** Torus containers on separate `torus-network` bridge
2. **Read-Only Vault:** Vault bind mount must be `:ro` (read-only)
3. **No Secrets in Images:** All credentials via environment variables or vault files
4. **Firewall Rules:** Only ports 3100, 3200, 3000, 3001 exposed to LAN
5. **Restart Policy:** All production containers use `unless-stopped`

---

## 8. Deployment Checklist

- [ ] Sir Green redeploys `torus-inventory` using new FastAPI image
- [ ] Build and deploy `torus-pos` with proper API
- [ ] Verify `torus-redis` persistence and connectivity
- [ ] Build and deploy `torus-dashboard` (LAN-only)
- [ ] Build and deploy `torus-website` (public-facing)
- [ ] Configure `void-npm` reverse proxy for SSL
- [ ] Set up `torus-alert-router` for centralized logging
- [ ] Test all container health endpoints
- [ ] Document container access credentials in vault (not git)
- [ ] Add all containers to Task Scheduler monitoring

---

## 9. Contact for Deployment

**Primary:** Sir Green (Docker Systems)  
**Secondary:** Mr. Gordon (AI Quartermaster)  
**Escalation:** Miss Pink (PINKCADY operator)

**Communication:** Shared via `Z:\Developer_Brain\Shared_With_Pink\`

---

## 10. Notes

- All container definitions must be stored in this vault (`10_Skills_Library/05_Operations/Docker/`)
- No container configs in VOID vault (`D:\Work\VOID Pirate Trading Co`)
- Legal separation: Torus containers use Torus-only names, images, and networks
- Free-tier constraint: All services must run on existing SQUIDSTATION hardware
- Future expansion: GPU passthrough for SIR_AZURE AI pipeline when hardware available

---

⚓ **Document maintained by:** Miss Pink  
⚓ **Reviewed by:** Sir Green, Mr. Gordon  
⚓ **Next review:** 2026-08-11
