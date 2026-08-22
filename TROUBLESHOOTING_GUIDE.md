# ============================================================================
# TORUS DOCKER — TROUBLESHOOTING GUIDE
# ============================================================================
# Diagnostic procedures and solutions for common problems
# ============================================================================

## QUICK DIAGNOSTICS (Start here!)

```bash
# Check if Docker is running
docker info

# Check if torus-network exists
docker network ls | grep torus-network

# List all Torus containers
docker ps -a --filter \"name=torus\"

# Check disk space
docker system df

# Check container stats
docker stats --no-stream
```

---

## SERVICE-SPECIFIC TROUBLESHOOTING

### torus-inventory (3200)

**Problem: \"Connection refused\" or \"Cannot GET /inventory\"**

1. Check if running:
   ```bash
   docker ps | grep torus-inventory
   ```

2. If not running, check why:
   ```bash
   docker logs torus-inventory
   # Look for: Python errors, port already in use, missing dependencies
   ```

3. If errors about missing inventory_master.json:
   ```bash
   # Check vault is mounted
   docker exec torus-inventory ls /vault/04_Products/inventory_master.json
   
   # If missing, rebuild image:
   docker stop torus-inventory && docker rm torus-inventory
   INVENTORY_DEPLOYMENT_FIX.ps1
   ```

4. If still failing:
   ```bash
   # Rebuild from source
   cd 10_Skills_Library/05_Operations/Docker/torus-inventory
   docker build -t torus-inventory:local .
   docker run -d --name torus-inventory -p 3200:3200 torus-inventory:local
   ```

**Problem: \"Health check failing\"**

1. Manually test:
   ```bash
   curl -v http://localhost:3200/health
   ```

2. If \"Connection refused\":
   - Container crashed: `docker logs torus-inventory`
   - Port not exposed: `docker port torus-inventory`
   - Firewall blocking: check Windows Defender firewall

3. If returns error:
   - Check app logs: `docker logs torus-inventory`
   - Invalid JSON? `curl http://localhost:3200/health | jq`

---

### torus-pos (3100)

**Problem: \"Redis connection failed\"**

1. Check Redis is running:
   ```bash
   docker ps | grep torus-redis
   curl http://localhost:6379/ping  # Should fail (Redis protocol)
   ```

2. Check POS can reach Redis:
   ```bash
   docker exec torus-pos curl -v http://torus-redis:6379
   # Should timeout or show Redis response
   ```

3. Fix Redis:
   ```bash
   docker logs torus-redis
   docker restart torus-redis
   ```

**Problem: \"Orders endpoint empty\" or \"Not getting product data\"**

1. Check vault mount:
   ```bash
   docker exec torus-pos ls /vault/04_Products/
   # Should list: orders.json, inventory_master.json, etc.
   ```

2. If nothing listed:
   - Vault mount failed
   - Check SQUIDSTATION has Docker mounted properly
   - Remount: `docker restart torus-pos`

3. If files exist but not reading:
   ```bash
   docker logs torus-pos
   # Look for: JSON decode errors, file permission errors
   ```

---

### torus-dashboard (3000)

**Problem: \"Dashboard endpoints return 500\"**

1. Check Flask dependencies:
   ```bash
   docker logs torus-dashboard
   # Look for: missing imports, Python errors
   ```

2. Check service connectivity:
   ```bash
   docker exec torus-dashboard curl -v http://torus-inventory:3200/health
   docker exec torus-dashboard curl -v http://torus-pos:3100/health
   # Both should return 200 with JSON
   ```

3. If service unreachable:
   - Check network: `docker network inspect torus-network`
   - Verify services in network: `docker inspect torus-pos | grep NetworkID`
   - Restart service: `docker restart torus-pos`

**Problem: \"No metrics displayed in UI\"**

- No UI is built yet (Flask-only, no HTML/CSS)
- Use API endpoints only for now: `/health`, `/status`
- Full UI coming in next phase

---

### torus-alert-router (4000)

**Problem: \"Alerts not being sent\"**

1. Check if alerts are being logged:
   ```bash
   curl -X POST http://localhost:4000/alert \
     -H \"Content-Type: application/json\" \
     -d '{\"severity\":\"info\",\"service\":\"test\",\"message\":\"test alert\"}'
   ```

2. Check integrations are enabled:
   ```bash
   curl http://localhost:4000/config
   # Returns which integrations are enabled
   ```

3. Check Discord webhook (if enabled):
   ```bash
   # Verify webhook URL is valid
   # Test manually: curl -X POST <WEBHOOK_URL> -d '{\"content\":\"test\"}'
   
   # Check env var is set
   docker exec torus-alert-router env | grep DISCORD_WEBHOOK
   ```

4. Check SMTP (if enabled):
   ```bash
   # Verify credentials work
   docker logs torus-alert-router | grep -i smtp
   # Should show successful connections if emails sent
   ```

5. Check Obsidian (if enabled):
   ```bash
   # Verify vault path is accessible
   docker exec torus-alert-router ls /vault/00_Inbox/
   # Should list daily note files
   ```

**Problem: \"Alert cooldown preventing delivery\"**

- By design: only 1 alert per service per 5 minutes
- To test: send different severity level
- To disable: modify `COOLDOWN_MINUTES = 0` in alert_router.py

---

### torus-website (3005)

**Problem: \"Website not loading\"**

1. Check if container running:
   ```bash
   docker ps | grep torus-website
   ```

2. If not running, check why:
   ```bash
   docker logs torus-website
   # Look for: nginx errors, permission denied, 404
   ```

3. Check port is correct:
   ```bash
   docker port torus-website
   # Should show: 3000/tcp -> 0.0.0.0:3005
   ```

4. Test manually:
   ```bash
   curl -v http://localhost:3005
   curl -v http://192.168.0.39:3005
   ```

5. If 404 on index.html:
   - Next.js build may have failed
   - Check `out/` directory exists: `docker exec torus-website ls /usr/share/nginx/html/`
   - If empty, rebuild: `npm run build && docker build -f Dockerfile.prod ...`

**Problem: \"CSS/Images not loading\"**

1. Check nginx cache headers:
   ```bash
   curl -I http://localhost:3005/styles/...
   # Should show Cache-Control headers
   ```

2. Check files exist:
   ```bash
   docker exec torus-website ls /usr/share/nginx/html/_next/static/
   ```

3. Clear browser cache (Ctrl+Shift+Delete) and reload

---

### torus-redis (6379)

**Problem: \"Can't connect to Redis\"**

1. Check if running:
   ```bash
   docker ps | grep torus-redis
   ```

2. Test connection:
   ```bash
   docker exec torus-redis redis-cli PING
   # Expected: PONG
   ```

3. If \"Connection refused\":
   ```bash
   docker logs torus-redis
   # Look for: binding errors, permission issues
   ```

4. Force restart:
   ```bash
   docker stop torus-redis
   docker rm torus-redis
   docker run -d --name torus-redis -p 6379:6379 redis:7-alpine
   ```

**Problem: \"Data not persisting\"**

1. Check persistence is enabled:
   ```bash
   docker exec torus-redis redis-cli CONFIG GET appendonly
   # Expected: 1 (yes) or \"yes\"
   ```

2. Check data file exists:
   ```bash
   docker exec torus-redis ls -la /data/
   # Should show: appendonly.aof
   ```

3. If missing, enable persistence:
   ```bash
   docker exec torus-redis redis-cli CONFIG SET appendonly yes
   ```

---

### torus-backup

**Problem: \"Backups not being created\"**

1. Check if container running:
   ```bash
   docker ps | grep torus-backup
   ```

2. Check backup log:
   ```bash
   docker logs torus-backup
   # Should show: \"Archive created:\" every hour
   ```

3. Check backup directory:
   ```bash
   docker exec torus-backup ls -la /backup/
   # Should list tar.gz files
   ```

4. If no backups:
   - Check vault is mounted: `docker exec torus-backup ls /vault/`
   - Check disk space: `docker stats --no-stream`
   - Manually test backup: `docker exec torus-backup /usr/local/bin/backup.sh`

**Problem: \"Backups taking too long\"**

1. Check file size:
   ```bash
   du -sh /var/lib/docker/volumes/torus-backup-data/_data/torus_vault_*.tar.gz
   ```

2. If > 1 GB:
   - Increase backup script timeout
   - Or reduce retention: `BACKUP_RETENTION_DAYS=3`

---

## NETWORK TROUBLESHOOTING

### Container can't reach another container

1. Verify both in torus-network:
   ```bash
   docker inspect torus-pos | grep -A 10 NetworkID
   docker inspect torus-inventory | grep -A 10 NetworkID
   # NetworkID should match
   ```

2. Test connectivity:
   ```bash
   docker exec torus-pos curl -v http://torus-inventory:3200/health
   ```

3. If unreachable:
   ```bash
   # Manually reconnect to network
   docker network disconnect torus-network torus-pos
   docker network connect torus-network torus-pos
   ```

### Container can't reach external network

1. Check Docker daemon logging:
   ```bash
   # Windows: %LOCALAPPDATA%\\Docker\\log\\vm\\dockerd.log
   # Linux: journalctl -u docker.service
   ```

2. Test DNS resolution:
   ```bash
   docker exec torus-alert-router nslookup google.com
   ```

3. Check firewall:
   - Windows Defender Firewall blocking Docker?
   - Allow Docker in firewall settings

---

## PERFORMANCE TROUBLESHOOTING

### High CPU usage

1. Identify container:
   ```bash
   docker stats --no-stream
   # Sort by CPU% column
   ```

2. Check what's consuming CPU:
   ```bash
   docker top <container_name>
   # Shows processes inside container
   ```

3. Optimize:
   - Reduce request rate
   - Check for infinite loops in code
   - Add resource limits

### High memory usage

1. Identify container:
   ```bash
   docker stats --no-stream
   # Sort by MEM USAGE
   ```

2. Check memory limit:
   ```bash
   docker inspect <container> | grep Memory
   ```

3. Increase limit:
   ```yaml
   # In docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 512m  # Increase from 256m
   ```

4. Restart: `docker compose up -d`

### Disk space filling up

1. Check usage:
   ```bash
   docker system df
   ```

2. Clean up:
   ```bash
   docker system prune  # Remove unused images, containers, networks
   docker system prune -a --volumes  # Also remove unused volumes (careful!)
   ```

3. Check backup size:
   ```bash
   du -sh /var/lib/docker/volumes/torus-backup-data/_data/
   # If > 50 GB, reduce retention or compress older backups
   ```

---

## LOGGING & DEBUGGING

### Increase log verbosity

1. Check current logging:
   ```bash
   docker compose -f docker-compose.torus.fleet.yml ps --format \"table {{.Names}}\\t{{.Status}}\"
   ```

2. View full logs with timestamps:
   ```bash
   docker compose logs --timestamps --tail=500 torus-inventory
   ```

3. Export logs to file:
   ```bash
   docker logs torus-inventory > torus-inventory.log 2>&1
   ```

### Debug container

1. Open shell in running container:
   ```bash
   docker exec -it torus-inventory sh
   # Inside container: ls, cat, curl, etc.
   ```

2. Run temporary debug container:
   ```bash
   docker run -it --rm --network torus-network alpine sh
   # Test network connectivity from clean container
   ```

---

## WHEN TO CONTACT SUPPORT

🟢 **Handle locally:**
- Container restarted automatically (restart policy working)
- Single service down but others healthy
- Slow response (check resource usage first)
- 404 on new endpoint (probably not built yet)

🟡 **Escalate to Miss Pink:**
- Multiple containers crashing
- Entire fleet down
- Vault mount permanently unavailable
- Backup not running for > 24 hours

🔴 **Emergency (Contact Sir Green):**
- SQUIDSTATION completely unresponsive
- Data loss or corruption suspected
- Security incident
- Need immediate rollback

---

**Last updated:** 2026-08-04  
**Maintained by:** Miss Gordon  
**Next review:** 2026-08-11
