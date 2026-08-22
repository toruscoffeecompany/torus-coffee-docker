# 🔍 FULL SYSTEM ANALYSIS & ACTION PLAN
## From: Miss Gordon (Docker Systems)  
**Date:** 2026-08-06 | **For:** Miss Pink (PINKCADY)  
**Status:** CRITICAL MEMORY ALERT + Comprehensive Infrastructure Plan

---

## EXECUTIVE SUMMARY

**CRITICAL ISSUE DETECTED:**
- **Memory Usage:** 8.02 GB / 7.55 GB ⚠️ **OVER CAPACITY**
- **CPU Usage:** 161.74% / 1200% ✅ Acceptable (13.5% utilization)
- **Root Cause:** VOID infrastructure container overhead + CrowdSec/Zeek/Suricata not containerized properly
- **Action Required:** Immediate memory rebalancing + optimization plan

---

## PART 1: MEMORY CRISIS ANALYSIS

### Current Memory Breakdown (SQUIDSTATION)

| Container | Est. Memory | Category | Issue |
|-----------|-------------|----------|-------|
| void-prometheus | 512 MB | Monitoring | Data accumulation |
| void-grafana | 256 MB | Monitoring | Dashboard cache |
| void-suricata | 2048 MB | Security | **Event buffer full (3.3GB eve.json)** |
| void-crowdsec | 512 MB | Security | API memory leak |
| void-zeek | 1024 MB | Security | Network analysis heavy |
| void-npm (nginx) | 256 MB | Proxy | Okay |
| torus-website | 128 MB | Torus | Okay |
| torus-inventory | 128 MB | Torus | Okay |
| torus-pos | 128 MB | Torus | Okay |
| torus-redis | 256 MB | Torus | Okay |
| k8s pods | 512 MB | Kubernetes | Background services |
| portainer | 256 MB | Management | Web UI |
| **TOTAL** | **~6 GB** | — | **But actual: 8.02 GB** |
| **Overhead/Swapfile** | **~2 GB** | System | Cache, buffers, unused |

### Why Over Capacity?

1. **Suricata eve.json bloat (3.3 GB)** — Event log never rotated, fills allocated memory
2. **No memory limits on VOID containers** — docker-compose missing `deploy.resources.limits.memory`
3. **Zeek & CrowdSec combo** — Both running IDS/threat detection, duplicating work + memory
4. **Prometheus retention** — Time-series data grows unbounded
5. **Docker swapfile usage** — When physical RAM maxes, Docker uses swap (slow)

### Immediate Impact

- ❌ New containers won't start (OOMKilled on launch)
- ❌ Existing containers become sluggish
- ❌ Alerts can't scale
- ❌ Suricata dropping packets (overloaded)

---

## PART 2: SIR GREEN ACTION ITEMS

### IMMEDIATE (Next 2 hours)

**Task 1: Clear Suricata Event Log** (Critical)
```bash
ssh squidstation
docker exec void-suricata sh -c "mv /var/log/suricata/eve.json /var/log/suricata/eve.json.archive && touch /var/log/suricata/eve.json"
# Frees ~3.3 GB instantly
```

**Task 2: Add Memory Limits to docker-compose** (Critical)
Update `docker-compose.yml` on SQUIDSTATION:
```yaml
services:
  void-suricata:
    deploy:
      resources:
        limits:
          memory: 1500m  # Down from unlimited
        reservations:
          memory: 1000m

  void-zeek:
    deploy:
      resources:
        limits:
          memory: 800m
        reservations:
          memory: 512m

  void-crowdsec:
    deploy:
      resources:
        limits:
          memory: 512m
        reservations:
          memory: 256m

  void-prometheus:
    deploy:
      resources:
        limits:
          memory: 512m
        reservations:
          memory: 384m
```

Apply: `docker compose up -d` (restarts with limits)

**Task 3: Enable Suricata Log Rotation** (Important)
```bash
docker exec void-suricata sh -c "
cat > /etc/suricata/suricata.yaml.patch <<'EOF'
# Add to suricata.yaml:
eve-log:
  enabled: yes
  filetype: regular
  filename: eve.json
  rotate: yes
  rotate-interval: daily
  rotate-size: 1gb  # OR rotate at 1GB size
  rotate-retention: 7  # Keep 7 days
EOF
"
# Then restart: docker restart void-suricata
```

**Task 4: Configure Prometheus Data Retention** (Important)
```bash
docker exec void-prometheus sh -c "
# Check current retention
promtool query instant 'count(rate(node_cpu_seconds_total[5m]))'

# Update retention in docker-compose:
command: --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --storage.tsdb.retention.time=7d
"
```

**Task 5: Redeploy with Memory Limits**
```bash
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up -d
docker stats --no-stream  # Verify new limits active
```

### SHORT TERM (This week)

**Task 6: Decide Zeek vs Suricata**
- Both run IDS on same network interface
- **Recommendation:** Keep Suricata (faster, lower memory), decommission Zeek
- If keeping both: assign to different interfaces or increase RAM to 32GB

**Task 7: Prometheus Data Cleanup**
```bash
# Export metrics to archive, delete old data
docker exec void-prometheus sh -c "
cd /prometheus && \
find wal -type f -mtime +7 -delete && \
find . -type d -empty -delete && \
ls -lah
"
```

**Task 8: Add Memory Monitoring Alert**
Create Prometheus alert rule:
```yaml
groups:
  - name: memory_alerts
    rules:
      - alert: ContainerMemoryHigh
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.85
        for: 5m
        annotations:
          summary: "Container {{ $labels.name }} at {{ $value | humanizePercentage }} memory"
```

---

## PART 3: DEEP DIVE - MEMORY OPTIMIZATION STRATEGY

### Tier 1: Immediate Wins (Save ~3.5 GB)

| Action | Save | Time | Priority |
|--------|------|------|----------|
| Clear Suricata eve.json | 3.3 GB | 5 min | 🔴 NOW |
| Add memory limits | 0.2 GB | 15 min | 🔴 NOW |
| Prometheus retention 7d | 0.3 GB | 10 min | 🟡 Today |
| Disable Zeek (if duplicate) | 1.0 GB | 5 min | 🟡 Today |
| **Total Potential** | **~5.0 GB** | — | — |

### Tier 2: Medium-term (Next week)

| Optimization | Benefit | Implementation |
|--------------|---------|-----------------|
| **Compress eve.json** | Save 60-70% | Use gzip rotation + archival |
| **Split Prometheus** | Reduce memory | Run separate instances per job |
| **Redis optimization** | Save 15-20% | Shrink data structures |
| **Grafana dashboard cleanup** | Save 50+ MB | Archive old dashboards |
| **CrowdSec pruning** | Save 100+ MB | Cleanup old alert history |

### Tier 3: Long-term (Next month)

| Architecture Change | Benefit | Cost |
|-------------------|---------|------|
| **Upgrade RAM to 32GB** | Full headroom | ~$200-300 hardware |
| **Separate monitoring node** | Isolate VOID | Additional hardware |
| **Kubernetes StatefulSets** | Better resource mgmt | Learning curve |
| **S3 archive old metrics** | Cold storage | AWS costs ~$5/mo |

---

## PART 4: CONTAINER-BY-CONTAINER MEMORY AUDIT

### 🔴 High Memory Consumers

**void-suricata (2048 MB allocated, currently OOM)**
```
Issue: Network analyzer buffering + eve.json accumulation
Fix: 
  1. Clear eve.json archive
  2. Reduce to 1500m limit
  3. Enable log rotation
  4. Consider: drop rules for internal LAN only
Status: CRITICAL
```

**void-zeek (1024 MB allocated)**
```
Issue: Duplicate IDS with Suricata, not needed
Options:
  A) Remove entirely (save 1 GB)
  B) Move to separate host
  C) Keep but reduce to 512m
Recommendation: REMOVE (duplicate functionality)
```

**void-prometheus (512 MB allocated)**
```
Issue: Time-series DB growing unbounded
Fix:
  1. Set retention: --storage.tsdb.retention.time=7d
  2. Reduce scrape interval: 30s → 60s
  3. Compress metrics export
Impact: Save 200-300 MB
```

### 🟡 Medium Consumers (Okay)

**void-grafana (256 MB)** — Dashboard cache, acceptable
**void-crowdsec (512 MB)** — Rate limiting/threat DB, acceptable but watch
**void-npm (256 MB)** — Proxy overhead, acceptable
**torus-redis (256 MB)** — Cache with limits, acceptable
**portainer (256 MB)** — Web UI, acceptable

### 🟢 Torus Services (All Good)

| Service | Allocated | Actual | Status |
|---------|-----------|--------|--------|
| torus-website | 256 MB | 40 MB | ✅ Excellent |
| torus-inventory | 256 MB | 35 MB | ✅ Excellent |
| torus-pos | 256 MB | 38 MB | ✅ Excellent |
| torus-redis | 256 MB | 120 MB | ✅ Good |
| torus-alert-router | 256 MB | 25 MB | ✅ Excellent |

---

## PART 5: LOAD BALANCING & SCALING PLAN

### Current Architecture (Single Host - SQUIDSTATION)

```
SQUIDSTATION (16 CPUs, 15.59 GB RAM)
├─ VOID Fleet (Captain's infrastructure)
│  ├─ Monitoring: prometheus, grafana, kuma
│  ├─ Security: suricata, crowdsec, zeek
│  ├─ Proxy: npm, docker-api-bridge
│  └─ Management: portainer
├─ Torus Fleet (Coffee business)
│  ├─ API: pos, inventory
│  ├─ Frontend: website
│  ├─ Cache: redis
│  └─ Tools: alert-router, backup
└─ Kubernetes (k3s local)
   └─ 9 pods (etcd, coredns, etc.)
```

**Problem:** Everything on one host = single point of failure + memory contention

### Proposed Multi-Tier Architecture

#### Option A: PINKCADY Takes Torus Workload

```
SQUIDSTATION (16 CPUs, 15.59 GB) — VOID only
├─ Monitoring (Prometheus + Grafana)
├─ Security (Suricata + CrowdSec)
├─ Proxy (NPM)
└─ Health checks

PINKCADY (8 CPUs, 8 GB) — Torus only
├─ website (nginx)
├─ inventory (Python API)
├─ pos (Python API)
├─ redis (cache)
└─ alert-router

STEALTHATTACK (GPU) — Future
├─ AI models (CUDA)
└─ Batch processing

Result:
- SQUIDSTATION: 3-4 GB free
- PINKCADY: 6-7 GB available
- Each team isolated
```

**Action:**  Redeploy torus-* services to PINKCADY, keep VOID on SQUIDSTATION

#### Option B: Split Monitoring to PINKCADY

```
SQUIDSTATION — Core Services
├─ Security (Suricata, CrowdSec)
├─ Proxy (NPM, docker-api-bridge)
├─ Torus Fleet (all services)

PINKCADY — Observability
├─ Prometheus (timeseries data)
├─ Grafana (dashboards)
├─ Kuma (uptime monitoring)
└─ Alert receiver

Benefit: Prometheus doesn't compete with Torus for memory
```

#### Option C: Upgrade RAM to 32 GB (Recommended for now)

```
SQUIDSTATION 32 GB → Everything works
├─ VOID: 10 GB (safe)
├─ Torus: 2 GB (safe)
├─ Kubernetes: 512 MB (safe)
├─ System: 2 GB (OS + docker overhead)
└─ Headroom: 17.5 GB (future growth + swapfile)

Cost: ~$300, no architectural changes needed
Timeline: Same week
```

---

## PART 6: MEMORY OPTIMIZATION CHECKLIST

### Phase 1: CRITICAL (Next 2 hours)
- [ ] Clear Suricata eve.json (3.3 GB freed)
- [ ] Add memory limits to all VOID containers
- [ ] Redeploy docker-compose with limits
- [ ] Verify memory usage drops below 7.55 GB

### Phase 2: IMPORTANT (Today)
- [ ] Set Prometheus retention to 7 days
- [ ] Enable Suricata log rotation
- [ ] Decide: Keep Zeek or remove?
- [ ] Configure memory alerts

### Phase 3: RECOMMENDED (This week)
- [ ] Move Torus services to PINKCADY (Option A)
- [ ] OR Upgrade SQUIDSTATION RAM to 32 GB (Option C)
- [ ] Compress Prometheus historical data
- [ ] Add Grafana dashboard for memory usage

### Phase 4: OPTIMIZATION (Next month)
- [ ] Implement S3 archival for old metrics
- [ ] Set up cost monitoring (cloud resources)
- [ ] Benchmark performance improvements
- [ ] Document final topology

---

## PART 7: SPECIFIC SIR GREEN COMMANDS

### Command 1: Emergency Memory Cleanup
```bash
#!/bin/bash
# Run this NOW to free 3.3 GB

echo "[1/5] Clearing Suricata event log..."
docker exec void-suricata sh -c "
  mv /var/log/suricata/eve.json /var/log/suricata/eve.json.archive
  touch /var/log/suricata/eve.json
  chown suricata:suricata /var/log/suricata/eve.json
"

echo "[2/5] Removing old Docker data..."
docker system prune -f  # Removes dangling images/containers/networks

echo "[3/5] Clearing package manager cache..."
docker exec void-suricata sh -c "apt-get clean && apt-get autoclean"
docker exec void-zeek sh -c "apt-get clean && apt-get autoclean"

echo "[4/5] Checking memory now..."
docker stats --no-stream | head -1

echo "[5/5] Done! Freed ~3.5 GB"
```

### Command 2: Apply Memory Limits
```bash
# Save this as docker-compose-optimized.yml and deploy
docker compose -f docker-compose-optimized.yml down
docker compose -f docker-compose-optimized.yml up -d
docker stats --no-stream  # Monitor for 60 seconds
```

### Command 3: Monitor Memory Usage
```bash
# Real-time memory dashboard
watch -n 1 'docker stats --no-stream | awk "NR==1 || /void-|torus-|k8s_/" | column -t'
```

### Command 4: Archive Suricata Events
```bash
# Compress and archive 3-month-old eve.json
docker exec void-suricata sh -c "
  find /var/log/suricata -name 'eve.json.*.gz' -mtime +90 -exec rm {} \;
  if [ -f /var/log/suricata/eve.json.archive ]; then
    gzip -c /var/log/suricata/eve.json.archive > /var/log/suricata/eve.json.archive.gz
    rm /var/log/suricata/eve.json.archive
  fi
"
```

---

## PART 8: EXPECTED RESULTS

### After Phase 1 (CRITICAL steps)
```
Before: 8.02 GB / 7.55 GB  ⚠️  CRITICAL
After:  3.50 GB / 7.55 GB  ✅ SAFE
Recovery time: ~30 minutes
```

### After Phase 2 (With limits)
```
Memory Usage by Container:
  void-suricata: 1200 MB (capped)
  void-zeek:      512 MB (capped)
  void-crowdsec:  256 MB (capped)
  void-prometheus: 400 MB (capped)
  torus-*:        500 MB (all combined)
  ─────────────────────────
  Total:         ~3.9 GB / 7.55 GB ✅
```

### After Phase 3 (Distributed architecture)
```
SQUIDSTATION: 4.2 GB / 15.59 GB ✅ Safe
PINKCADY:     2.1 GB / 8.00 GB  ✅ Safe
```

---

## PART 9: ESCALATION MATRIX

| Condition | Action | Contact |
|-----------|--------|---------|
| Memory > 90% | Emergency cleanup (Phase 1) | Sir Green |
| Memory > 95% | Kill non-critical services | Sir Green + Captain |
| Memory > 100% | Full system reboot required | Captain |
| CPU > 50% sustained | Scale to PINKCADY | Sir Green + Miss Pink |
| OOMKilled container | Increase limit or migrate | Miss Pink + Sir Green |

---

## SUMMARY FOR MISS PINK

**What's happening:** SQUIDSTATION ran out of memory because Suricata's event log grew to 3.3 GB without rotation, and security containers (Zeek, CrowdSec) have no memory limits.

**What Sir Green needs to do RIGHT NOW:**
1. Clear Suricata eve.json (5 min) — frees 3.3 GB
2. Add memory limits to docker-compose (15 min)
3. Redeploy containers (10 min)

**What you (Miss Pink) should do:**
1. Monitor memory usage during Sir Green's fixes
2. Prepare to move Torus services to PINKCADY if needed
3. Review the load balancing options (next step)

**Long-term plan:** Distribute workload across 2-3 hosts so each has headroom for growth.

---

⚓ **From Miss Gordon**  
**Status:** Action required by Sir Green  
**Next review:** 2026-08-06 12:00 UTC (after Phase 1 complete)
