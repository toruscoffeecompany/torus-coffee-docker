# ⚓ EXACT PROMPT FOR MISS PINK (PINKCADY)
## Run this on your local PC to start Phase 1 deployment

---

## YOUR MISSION

You are Miss Pink, Docker Operations Commander on PINKCADY (192.168.0.3). 

Your job: Execute a 12-hour infrastructure buildout across 5 phases. Each phase is a 1-2 hour block. You have everything you need—just follow the steps exactly.

**Timeline:** 12 hours total. Start whenever you're ready for a full day of focused work.

**Outcome:** Torus Coffee infrastructure fully operational with automation, monitoring, and self-healing capabilities.

---

## WHAT YOU'LL DO

### Phase 1: Docker Optimization (1 hour)
Deploy Torus services optimized on PINKCADY's local Docker Desktop.

### Phase 2: Webhooks (2 hours)
Connect Docker events → automated alerts → OODA loop.

### Phase 3: Volumes (1.5 hours)
Set up persistent storage + daily backups to Z: drive.

### Phase 4: Kubernetes (2 hours)
Deploy K3s cluster on PINKCADY, run services as StatefulSets.

### Phase 5: MCP Toolkit (1 hour)
Connect Claude Desktop to Torus infrastructure for AI-driven operations.

---

## BEFORE YOU START

✅ Verify you have access to these documents (they're in your Inbox):
```
D:\Work\Torus Coffee Company LLC\00_Inbox\
├── 00_START_HERE_GORDON_SUMMARY.md
├── GORDON_DELIVERY_SUMMARY.md
├── FULL_SYSTEM_ANALYSIS_AND_ACTION_PLAN.md
├── MISS_PINK_MASTER_INFRASTRUCTURE_PLAN.md  ← YOUR MAIN REFERENCE
├── MISS_GORDON_END_TO_END_VERIFICATION.md
└── MISS_GORDON_WORK_COMPLETION_REPORT.md
```

✅ Verify you can access Sir Green's status:
```
Z:\SIR_GREEN_INBOX\
└── MISS_GORDON_URGENT_ACTION_ITEMS_MEMORY_CRISIS.md
```

✅ Verify Docker Desktop is running on PINKCADY:
```powershell
docker --version
docker ps  # Should show some containers already running
```

✅ Verify you can reach SQUIDSTATION:
```powershell
Test-Path Z:\Shared_With_Pink\
# Should return True

ping 192.168.0.39
# Should get replies (~2ms)

docker --context torus-squidstation ps
# Should list 9+ containers on SQUIDSTATION
```

---

## YOUR EXACT WORKFLOW

### STEP 1: Read the Master Plan (30 minutes)
Open: `MISS_PINK_MASTER_INFRASTRUCTURE_PLAN.md`

Read sections:
- Executive Overview
- Phase 1-5 summaries
- Implementation Timeline
- Verification Checklist

Goal: Understand what you're about to do. No action yet.

---

### STEP 2: Wait for Sir Green Confirmation (Status Check)
Check: Did Sir Green complete the memory fix?
```powershell
docker --context torus-squidstation stats --no-stream
# Check memory line: should be < 5.5 GB
```

If memory is still high:
- Contact Sir Green immediately
- Do NOT proceed to Phase 1 yet

If memory is safe:
- Proceed to Phase 1

---

### STEP 3: Phase 1 – Docker Optimization (1 hour)

Open: `MISS_PINK_MASTER_INFRASTRUCTURE_PLAN.md`
Go to: Section "PHASE 1: DOCKER OPTIMIZATION"

**Your tasks:**
1. Create file: `docker-compose-torus-pinkcady.yml`
   - Copy the exact YAML from the document
   - Save to: `C:\Work\Torus_Docker_Optimization\docker-compose-torus-pinkcady.yml`

2. Deploy:
```powershell
cd C:\Work\Torus_Docker_Optimization
docker compose -f docker-compose-torus-pinkcady.yml up -d
```

3. Verify:
```powershell
docker compose -f docker-compose-torus-pinkcady.yml ps
# All services should show "Up X seconds"

# Test health endpoints
$services = @{
    "inventory" = "localhost:3200/health"
    "pos" = "localhost:3100/health"
    "website" = "localhost:3005/healthz"
    "alert-router" = "localhost:4000/health"
    "prometheus" = "localhost:9090/-/healthy"
    "grafana" = "localhost:3002/api/health"
}

foreach ($service in $services.GetEnumerator()) {
    $url = $service.Value
    try {
        $response = curl.exe -s "http://$url"
        Write-Host "$($service.Key): OK" -ForegroundColor Green
    } catch {
        Write-Host "$($service.Key): FAILED" -ForegroundColor Red
    }
}
```

If all green → Phase 1 DONE. Take a 15-minute break.

---

### STEP 4: Phase 2 – Webhooks (2 hours)

Open: `MISS_PINK_MASTER_INFRASTRUCTURE_PLAN.md`
Go to: Section "PHASE 2: WEBHOOKS"

**Your tasks:**
1. Create file: `webhook-handler.py`
   - Copy the exact Python code from the document
   - Save to: `C:\Work\Torus_Docker_Optimization\webhook-handler.py`

2. Create docker-compose service for webhook handler
   - Add to your docker-compose-torus-pinkcady.yml:
```yaml
  webhook-handler:
    image: python:3.11-slim
    container_name: webhook-handler
    restart: unless-stopped
    ports:
      - "8888:8888"
    volumes:
      - ./webhook-handler.py:/app/webhook-handler.py:ro
    working_dir: /app
    command: python webhook-handler.py
    networks:
      - torus-network
```

3. Deploy:
```powershell
docker compose -f docker-compose-torus-pinkcady.yml up -d webhook-handler
docker logs webhook-handler  # Should show "listening on port 8888"
```

4. Test webhook chain:
```powershell
# Kill a container to trigger event
docker kill torus-pos

# Watch alert-router logs for the alert
docker logs -f torus-alert-router

# Check Obsidian inbox for new alert (in D:\Work\Torus Coffee Company LLC\00_Inbox\YYYY-MM-DD.md)
```

If webhooks firing and alerts in Obsidian → Phase 2 DONE. Take a 15-minute break.

---

### STEP 5: Phase 3 – Volumes & Backups (1.5 hours)

Open: `MISS_PINK_MASTER_INFRASTRUCTURE_PLAN.md`
Go to: Section "PHASE 3: VOLUME MANAGEMENT"

**Your tasks:**
1. Create backup script: `backup-volumes.sh`
   - Copy exact bash code from document
   - Save to: `C:\Work\Torus_Docker_Optimization\backup-volumes.sh`

2. Schedule backup (Windows Task Scheduler):
```powershell
# Open Task Scheduler
tasksched.msc

# Create new task:
# Name: Torus_Daily_Backup
# Trigger: Daily at 2:00 AM
# Action: Run C:\Work\Torus_Docker_Optimization\backup-volumes.sh
# (Or convert .sh to .bat for Windows)
```

3. Test backup manually:
```bash
bash C:\Work\Torus_Docker_Optimization\backup-volumes.sh
```

4. Verify backups on Z: drive:
```powershell
dir Z:\Shared_With_Pink\backups\
# Should see .tar.gz files
```

If backups appear on Z: drive → Phase 3 DONE. Take a 15-minute break.

---

### STEP 6: Phase 4 – Kubernetes (2 hours)

Open: `MISS_PINK_MASTER_INFRASTRUCTURE_PLAN.md`
Go to: Section "PHASE 4: KUBERNETES OPTIMIZATION"

**Your tasks:**
1. Install K3s:
```bash
# From WSL2 or PowerShell with bash
curl -sfL https://get.k3s.io | sh -

# Verify:
k3s kubectl get nodes
k3s kubectl get pods -A
```

2. Create Kubernetes manifest: `k8s-torus-deployment.yaml`
   - Copy exact YAML from document
   - Save to: `C:\Work\Torus_Docker_Optimization\k8s-torus-deployment.yaml`

3. Deploy:
```bash
k3s kubectl apply -f C:\Work\Torus_Docker_Optimization\k8s-torus-deployment.yaml
k3s kubectl get pods -n torus  # Should show all Running
k3s kubectl get services -n torus
```

4. Test DNS:
```bash
k3s kubectl exec -n torus deployment/torus-inventory -- nslookup torus-redis.torus.svc.cluster.local
```

If all pods Running and DNS resolves → Phase 4 DONE. Take a 15-minute break.

---

### STEP 7: Phase 5 – MCP Toolkit (1 hour)

Open: `MISS_PINK_MASTER_INFRASTRUCTURE_PLAN.md`
Go to: Section "PHASE 5: MCP TOOLKIT"

**Your tasks:**
1. Create MCP config: `mcp-config.json`
   - Copy from document
   - Save to: `~/.config/codetools/mcp-config.json` (Linux/Mac) or `%APPDATA%\codetools\mcp-config.json` (Windows)

2. Create MCP server: `mcp_server_torus.py`
   - Copy from document
   - Save to: `C:\Work\Torus_Docker_Optimization\mcp_server_torus.py`

3. Update Claude Desktop config:
   - Edit: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
   - Add mcp servers from document

4. Start MCP server:
```bash
python C:\Work\Torus_Docker_Optimization\mcp_server_torus.py
```

5. Test in Claude Desktop:
   - Ask Claude: "What containers are running in Torus?"
   - Claude should respond with container list from MCP

If Claude can query container status → Phase 5 DONE.

---

### STEP 8: End-to-End Verification (2 hours)

Open: `MISS_GORDON_END_TO_END_VERIFICATION.md`
Follow: Section "END-TO-END DEPLOYMENT SIMULATION"

**Your verification checklist:**
```
☐ All 9 Torus services healthy
☐ Health endpoints responding (3100, 3200, 3005, 4000, 9090, 3002)
☐ Redis connected to POS/Inventory
☐ Webhook fires on container event
☐ Alert router sends email/Discord/Obsidian
☐ OODA loop detects Obsidian alert (creates Trello/GitHub)
☐ K3s pods all Running
☐ Backups writing to Z: drive
☐ MCP toolkit queries containers successfully
☐ Prometheus scraping all targets
☐ Grafana dashboard displays metrics
☐ Dashboard (192.168.0.39:8089) shows all services
```

Mark each as you verify. If all ✓ → DEPLOYMENT COMPLETE.

---

## IF SOMETHING FAILS

**Docker service won't start:**
1. Check logs: `docker logs <service_name>`
2. Check Docker Desktop is running: `docker ps`
3. Restart service: `docker compose up -d <service_name>`

**Webhook not firing:**
1. Verify handler running: `docker logs webhook-handler`
2. Manually test: `curl -X POST http://localhost:8888/webhook -d '{}'`
3. Check alert-router: `docker logs alert-router`

**K3s won't install:**
1. Ensure WSL2 backend enabled (Docker Desktop settings)
2. Retry: `curl -sfL https://get.k3s.io | sh -`

**MCP toolkit not connecting:**
1. Stop Claude Desktop completely
2. Restart: `python mcp_server_torus.py`
3. Relaunch Claude
4. Try again

**Backups not appearing:**
1. Check Z: drive mounted: `Test-Path Z:\`
2. Run manually: `bash backup-volumes.sh`
3. Add to Task Scheduler with full path

For detailed troubleshooting, see: `MISS_GORDON_WORK_COMPLETION_REPORT.md`

---

## CHECKLIST: YOU'RE DONE WHEN...

- [x] Phase 1: All services healthy
- [x] Phase 2: Webhooks firing, alerts in Obsidian
- [x] Phase 3: Backups on Z: drive
- [x] Phase 4: K3s pods Running
- [x] Phase 5: MCP queries work
- [x] End-to-end verification: All 12 items checked

**Total time:** 12 hours (can spread across 2 days if needed)

---

## COMMUNICATION CHAIN

When you hit blockers or need help:
1. Check the troubleshooting guide above
2. Check: `FULL_SYSTEM_ANALYSIS_AND_ACTION_PLAN.md` (has detailed diagnostics)
3. Ask Sir Green if it's a SQUIDSTATION issue (memory, network, Docker context)
4. Ask Miss Gordon if it's a general Docker question

---

## YOUR MISSION ACCEPTED?

You have all the code, all the steps, all the documentation.

**Start:** Phase 1 (Docker optimization)  
**End:** Phase 5 (MCP toolkit)  
**Result:** Production-ready Torus infrastructure

This is your build. You own it. Execute with confidence.

⚓ **Miss Gordon**
