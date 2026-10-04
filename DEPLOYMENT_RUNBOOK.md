# ============================================================================
# TORUS COFFEE DOCKER — DEPLOYMENT RUNBOOK
# ============================================================================
# Step-by-step procedures for deploying and managing the Torus fleet
# Last updated: 2026-08-04
# ============================================================================

## PHASE 1: PRE-DEPLOYMENT CHECKS

### On PINKCADY (Developer)

1. **Verify Docker context is set to SQUIDSTATION:**
   ```powershell
   docker context ls
   # Expected: torus-squidstation marked as current (*)
   ```

2. **Verify network connection:**
   ```powershell
   ping 192.168.0.39
   # Expected: replies (< 5ms latency)
   ```

3. **Verify vault mount:**
   ```powershell
   Test-Path Z:/Developer_Brain/Shared_With_Pink
   # Expected: True
   ```

---

## PHASE 2: BUILD IMAGES

### Build torus-inventory

```powershell
cd \"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Docker\torus-inventory\"
docker --context torus-squidstation build -t torus-inventory:local .
# Expected: Successfully tagged torus-inventory:local
```

### Build torus-pos

```powershell
cd \"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Docker\torus-pos\"
docker --context torus-squidstation build -t torus-pos:local .
```

### Build torus-dashboard

```powershell
cd \"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Docker\torus-dashboard\"
docker --context torus-squidstation build -t torus-dashboard:local .
```

### Build torus-alert-router

```powershell
cd \"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Docker\torus-alert-router\"
docker --context torus-squidstation build -t torus-alert-router:local .
```

### Build torus-backup

```powershell
cd \"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Docker\torus-backup\"
docker --context torus-squidstation build -t torus-backup:local .
```

### Build torus-website

```powershell
cd \"D:\Work\Torus Coffee Company LLC\06_Website\next-storefront\"
.\\BUILD_AND_DEPLOY.ps1
# This script handles npm install, build, and Docker build automatically
```

---

## PHASE 3: DEPLOYMENT ON SQUIDSTATION

### SSH into SQUIDSTATION

```bash
# Option 1: Remote PowerShell
Enter-PSSession -ComputerName SQUIDSTATION

# Option 2: SSH
ssh user@192.168.0.39

# Option 3: Use Tailscale
ssh user@squidstation
```

### Fix torus-inventory (if stuck restarting)

```powershell
# From SQUIDSTATION (or PINKCADY with torus-squidstation context)
docker stop torus-inventory
docker rm torus-inventory
docker run -d `
  --name torus-inventory `
  --restart unless-stopped `
  -p 3200:3200 `
  -v \"D:/Work/Torus Coffee Company LLC:/vault:ro\" `
  --network torus-network `
  torus-inventory:local
```

### Deploy entire fleet

```powershell
# On SQUIDSTATION, in the Docker ops directory:
cd \"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\Docker\"

# Option 1: Use master deployment script
.\\DEPLOY_FLEET.ps1

# Option 2: Manual docker-compose
docker compose -f docker-compose.torus.fleet.yml up -d

# Option 3: Deploy single service
docker compose -f docker-compose.torus.fleet.yml up -d torus-pos
```

### Verify deployment

```bash
# List running containers
docker compose -f docker-compose.torus.fleet.yml ps

# Check individual service health
curl http://localhost:3200/health  # inventory
curl http://localhost:3100/health  # pos
curl http://localhost:4000/health  # alert-router

# View logs
docker compose -f docker-compose.torus.fleet.yml logs -f torus-inventory
```

---

## PHASE 4: POST-DEPLOYMENT VERIFICATION

### Health checks

```bash
# Redis
redis-cli -p 6379 PING
# Expected: PONG

# Inventory API
curl -s http://localhost:3200/health | jq
# Expected: {\"status\":\"ok\",\"service\":\"torus-inventory\"}

# POS API
curl -s http://localhost:3100/health | jq

# Alert Router
curl -s http://localhost:4000/health | jq

# Dashboard
docker exec torus-dashboard curl -s http://localhost:3000/health
```

### Container resource usage

```bash
docker stats --no-stream
# Verify memory/CPU not maxed out
```

### Network connectivity

```bash
# From within a container
docker exec torus-pos curl -s http://torus-redis:6379/health

# Between containers
docker exec torus-dashboard curl -s http://torus-inventory:3200/health
```

### Backup verification

```bash
# Check backup directory
ls -lah /var/lib/docker/volumes/torus-backup-data/_data/

# List backups
ls -lah /var/lib/docker/volumes/torus-backup-data/_data/torus_vault_*.tar.gz

# Verify backup integrity
tar -tzf /var/lib/docker/volumes/torus-backup-data/_data/torus_vault_LATEST.tar.gz | head -20
```

---

## PHASE 5: MONITORING AND OBSERVABILITY

### Access Grafana dashboard

1. Open browser: http://192.168.0.39:3002
2. Login (default: admin / admin)
3. Change admin password immediately
4. Go to Dashboards → Torus Fleet
5. Monitor metrics:
   - Container CPU usage
   - Container memory usage
   - Network I/O
   - Container restart count

### View Prometheus targets

1. Open: http://192.168.0.39:9090/targets
2. Verify all targets show green (UP)
3. If any are red (DOWN):
   - Check container is running: `docker ps`
   - Check port is exposed: `docker inspect <container>`

### Collect logs

```bash
# All containers
docker compose -f docker-compose.torus.fleet.yml logs

# Single service
docker compose -f docker-compose.torus.fleet.yml logs torus-inventory

# Follow logs live
docker compose -f docker-compose.torus.fleet.yml logs -f torus-alert-router

# Last 100 lines
docker compose -f docker-compose.torus.fleet.yml logs --tail=100
```

---

## EMERGENCY PROCEDURES

### Container crashed

```bash
# Check why it crashed
docker logs <container_name>

# If disk is full
docker system df
docker system prune  # WARNING: removes dangling images

# If OOM (Out of Memory)
docker inspect <container> | grep -A 5 MemorySwap
docker update --memory 512m <container>
```

### Vault mount unavailable

```bash
# Check if mount is still present
ls /vault

# If missing, remount
sudo mount -t cifs \\\\192.168.0.39\\vault /vault -o username=user,password=pass

# Restart affected containers
docker restart torus-pos torus-inventory torus-backup
```

### Network connectivity lost

```bash
# Check Docker networks
docker network ls

# Inspect torus-network
docker network inspect torus-network

# If corrupted, recreate (WARNING: containers will reconnect automatically)
docker network disconnect torus-network <container>
docker network connect torus-network <container>
```

### Complete rollback

```bash
# Stop all containers
docker compose -f docker-compose.torus.fleet.yml down

# Remove volumes (WARNING: data loss!)
docker compose -f docker-compose.torus.fleet.yml down -v

# Redeploy from scratch
docker compose -f docker-compose.torus.fleet.yml up -d
```

---

## MAINTENANCE TASKS

### Daily

- [ ] Check Grafana dashboard for anomalies
- [ ] Verify backup completed at 2 AM
- [ ] Spot-check logs for errors

### Weekly

- [ ] Review resource usage trends
- [ ] Check disk space: `docker system df`
- [ ] Update container images if patches available

### Monthly

- [ ] Review and rotate API tokens
- [ ] Update SMTP credentials if needed
- [ ] Backup configuration files to Z: drive
- [ ] Test disaster recovery (restore from backup)

### Quarterly

- [ ] Full security audit
- [ ] Update base OS and Docker runtime
- [ ] Review and optimize resource limits
- [ ] Capacity planning (add nodes if needed)

---

## COMMON ISSUES & FIXES

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Container restart loop** | Healthy container shows \"Restarting\" | Check logs: `docker logs <container>` |
| **Port conflict** | Error: \"port already in use\" | `docker ps` to find what's using it |
| **Out of memory** | Container killed with exit 137 | Increase memory limit in compose |
| **Slow response** | API timing out | Check `docker stats` for CPU/memory |
| **Network unreachable** | Can't access other container | Verify both in same network: `docker network inspect torus-network` |
| **Vault unavailable** | No data accessible | Remount vault, restart containers |
| **Backup missing** | No tar.gz files in backup volume | Check cron job: `sudo crontab -l` |
| **Alert not routing** | Alerts not sent to Discord/email | Check integrations enabled in config |

---

## SUCCESS CRITERIA

✅ All 7 containers running and healthy  
✅ Health endpoints return 200 OK  
✅ Redis connected and persisting  
✅ Backup job ran successfully  
✅ Prometheus scraping all targets  
✅ Grafana dashboard shows metrics  
✅ DNS/network connectivity working  
✅ No errors in container logs

---

**Contact for issues:**
- Primary: Sir Green (SQUIDSTATION systems)
- Secondary: Miss Pink (PINKCADY operations)
- Escalation: Mr. Gordon (AI Quartermaster)

**Documentation location:**
- Z:\\Developer_Brain\\Shared_With_Pink\\
- D:\\Work\\Torus Coffee Company LLC\\10_Skills_Library\\05_Operations\\Docker\\
