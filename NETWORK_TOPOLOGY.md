# Torus Coffee Company — Docker Network Topology

> **Source of Truth:** `10_Skills_Library/05_Operations/Docker/NETWORK_TOPOLOGY.md`  
> **Last Updated:** 2026-08-04  
> **Status:** VERIFIED — matches SQUIDSTATION Obsidian vault

---

## Actual Network Topology

### SQUIDSTATION (`192.168.0.39`) — Primary Docker Host

| Network | Driver | Scope | Purpose |
|---------|--------|-------|---------|
| `bridge` | bridge | local | Default Docker network |
| `docker-network` | bridge | local | VOID fleet services |
| `host` | host | local | Host networking |
| `none` | null | local | Isolated containers |
| `torus-network` | bridge | local | **Torus Coffee containers** |

**Note:** `void-fleet` does NOT exist on SQUIDSTATION. It was planned but never created.

### PINKCADY (`192.168.0.3`) — Secondary Workstation

| Network | Driver | Scope | Purpose |
|---------|--------|-------|---------|
| `torus-network` | bridge | local | **Torus Coffee containers** |

### Current Misalignment

| Expected | Actual | Status |
|----------|--------|--------|
| `void-fleet` network | **Does not exist** | ❌ Missing |
| Torus containers on `void-fleet` | Torus containers on `torus-network` | ⚠️ Different network |
| VOID containers on `docker-network` | VOID containers on `docker-network` | ✅ Correct |
| PINKCADY joins `void-fleet` | PINKCADY has `torus-network` | ❌ Different network |

### Legal Separation: Torus vs VOID

**TORUS COFFEE COMPANY (Miss Pink):**
- Network: `torus-network`
- Containers: `torus-pos`, `torus-inventory`, `torus-dashboard`, `torus-website`, `torus-alert-router`, `torus-redis`, `torus-backup`
- Vault: `D:\Work\Torus Coffee Company LLC`
- Hermes Agent: Separate profile

**VOID PIRATE TRADING CO (Captain/Sir Green):**
- Network: `docker-network`
- Containers: `void-npm`, `void-vaultwarden`, `void-nextcloud`, `void-gitea`, `void-kuma`, `void-grafana`, `void-prometheus`, etc.
- Vault: `Z:\Developer_Brain\` (SQUIDSTATION Obsidian vault)
- Hermes Agent: Main profile

**SHARED RESOURCES:**
- Docker Engine: SQUIDSTATION only
- Z: drive: Read-only vault bridge (`\192.168.0.39\Vault`)
- Shared folder: `Z:\Developer_Brain\Shared_With_Pink\`

### Network Communication Paths

**Within Torus network:**
- torus-pos ↔ torus-inventory ✅
- torus-pos ↔ torus-redis ✅
- torus-dashboard ↔ torus-pos ✅
- torus-dashboard ↔ torus-inventory ✅
- torus-website ↔ torus-dashboard ✅
- torus-alert-router ↔ all Torus services ✅

**Between Torus and VOID networks:**
- ❌ No direct container-to-container communication
- ⚠️ Can communicate via host ports if exposed
- ✅ Can communicate via shared Z: drive

---

## Recommended Actions

1. **Create `void-fleet` network** on SQUIDSTATION if cross-business communication is needed
2. **Keep Torus on `torus-network`** for legal separation
3. **Use host ports** for any required cross-network access
4. **Document all port allocations** to avoid conflicts

---

## Port Allocation Matrix

| Port | Service | Owner | Status |
|------|---------|-------|--------|
| 80 | void-npm HTTP | VOID | ✅ Allocated |
| 81 | void-npm Admin | VOID | ✅ Allocated |
| 443 | void-npm HTTPS | VOID | ✅ Allocated |
| 3000 | void-gitea / torus-dashboard | VOID/Torus | ⚠️ Conflict |
| 3001 | void-kuma | VOID | ✅ Allocated |
| 3002 | void-grafana | VOID | ✅ Allocated |
| 3100 | torus-pos | Torus | ✅ Allocated |
| 3200 | torus-inventory | Torus | ✅ Allocated |
| 4000 | torus-alert-router | Torus | ✅ Allocated |
| 6379 | torus-redis | Torus | ✅ Allocated |
| 8080 | void-npm HTTP alt | VOID | ✅ Allocated |
| 8081 | void-cadvisor | VOID | ✅ Allocated |
| 9090 | void-prometheus | VOID | ✅ Allocated |
| 9100 | void-node-exporter | VOID | ✅ Allocated |

**Note:** Port 3000 is shared between `void-gitea` and `torus-dashboard`. On SQUIDSTATION, `torus-dashboard` has no external port binding.

---

⚓ **Document maintained by:** Miss Pink  
⚓ **Verified against:** SQUIDSTATION Obsidian vault, `docker network ls`, `docker ps`
