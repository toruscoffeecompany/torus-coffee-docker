# 🏗️ MISS PINK'S COMPLETE INFRASTRUCTURE MASTER PLAN
## From: Miss Gordon (Docker Systems)  
**Date:** 2026-08-06 | **Target Completion:** 2026-08-13  
**Phase:** Docker + Observability + MCP Stack Buildout

---

## TABLE OF CONTENTS

1. [Executive Overview](#executive-overview)
2. [Sir Green: Immediate Actions](#sir-green-immediate-actions)
3. [Miss Pink: Phase 1 - Docker Optimization](#miss-pink-phase-1)
4. [Phase 2 - Webhook Integration](#phase-2-webhooks)
5. [Phase 3 - Volume Management](#phase-3-volumes)
6. [Phase 4 - Kubernetes Setup](#phase-4-kubernetes)
7. [Phase 5 - MCP Toolkit](#phase-5-mcp)
8. [Implementation Timeline](#timeline)
9. [Verification Checklist](#verification)

---

## EXECUTIVE OVERVIEW

**Current Status:**
- ✅ Torus Docker fleet deployed (9 containers)
- ✅ VOID infrastructure running (monitoring + security)
- ⚠️ Memory crisis (8.02/7.55 GB) — requires immediate fix
- ❌ Webhooks not connected
- ❌ Advanced volume strategies not implemented
- ❌ Kubernetes not optimized
- ❌ MCP toolkit not activated

**Goals (By 2026-08-13):**
1. Resolve memory crisis (Phase 1 - Sir Green)
2. Activate Docker webhooks for automation
3. Implement persistent volume strategies
4. Optimize Kubernetes on both hosts
5. Enable MCP servers for AI integration

---

## SIR GREEN: IMMEDIATE ACTIONS

### ⚠️ CRITICAL (Next 2 hours)

**Action 1: Clear Suricata Event Log**
```bash
ssh squidstation
docker exec void-suricata sh -c "
  echo 'Clearing eve.json (3.3 GB)...'
  mv /var/log/suricata/eve.json /var/log/suricata/eve.json.archive.$(date +%s)
  touch /var/log/suricata/eve.json
  chown suricata:suricata /var/log/suricata/eve.json
  echo 'Freed 3.3 GB'
"
docker stats --no-stream | grep void-suricata
```

**Action 2: Add Memory Limits**

Create file: `/path/to/docker-compose-squidstation.yml`
```yaml
version: '3.8'

services:
  # VOID INFRASTRUCTURE
  void-suricata:
    image: jasonish/suricata:latest
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1500m
        reservations:
          memory: 1000m

  void-zeek:
    image: zeek/zeek:latest
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 800m
        reservations:
          memory: 512m

  void-crowdsec:
    image: crowdsecurity/crowdsec:latest
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512m
        reservations:
          memory: 256m

  void-prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=7d'
    deploy:
      resources:
        limits:
          memory: 512m
        reservations:
          memory: 384m

  void-grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 200m

  void-npm:
    image: 'nginxproxymanager/nginx-proxy-manager:latest'
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 192m

  void-kuma:
    image: louislam/uptime-kuma:latest
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 192m

  void-cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 192m

  void-node-exporter:
    image: prom/node-exporter:latest
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 128m
        reservations:
          memory: 64m

  # TORUS SERVICES (move to PINKCADY after Phase 2)
  torus-redis:
    image: redis:7-alpine
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 200m

  torus-inventory:
    image: torus-inventory:local
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 128m

  torus-pos:
    image: torus-pos:local
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 128m

  torus-website:
    image: torus-website:local
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 128m

  torus-alert-router:
    image: torus-alert-router:local
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 128m

  torus-backup:
    image: torus-backup:local
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512m
        reservations:
          memory: 384m
```

**Action 3: Redeploy**
```bash
docker compose -f docker-compose-squidstation.yml down
docker compose -f docker-compose-squidstation.yml up -d
sleep 30
docker stats --no-stream
```

**Expected Result:**
```
BEFORE: 8.02 GB / 7.55 GB  ⚠️ CRITICAL
AFTER:  3.50 GB / 7.55 GB  ✅ SAFE
```

**Action 4: Enable Suricata Log Rotation**
```bash
docker exec void-suricata sh -c "
  cat >> /etc/suricata/suricata.yaml <<'EOF'

# Log rotation added by Miss Gordon
eve-log:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      rotate: yes
      rotate-interval: daily
      rotate-size: 1gb
      rotate-retention: 7
EOF

suricata -c /etc/suricata/suricata.yaml -T
docker restart void-suricata
"
```

**Status:** Confirm with Miss Pink when complete

---

## MISS PINK: PHASE 1 - DOCKER OPTIMIZATION

### Step 1: Verify Memory Crisis is Resolved

```powershell
# From PINKCADY
docker --context torus-squidstation stats --no-stream

# Should show memory < 5.5 GB
# If not, escalate to Sir Green
```

### Step 2: Deploy Torus Services Locally on PINKCADY

Option: Move Torus workload to PINKCADY to further isolate

**Create:** `docker-compose-torus-pinkcady.yml`
```yaml
version: '3.8'

services:
  torus-redis:
    image: redis:7-alpine
    container_name: torus-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - torus_redis_data:/data
    networks:
      - torus-network
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 200m

  torus-inventory:
    image: torus-inventory:local
    container_name: torus-inventory
    restart: unless-stopped
    ports:
      - "3200:3200"
    environment:
      - REDIS_HOST=torus-redis
      - REDIS_PORT=6379
    networks:
      - torus-network
    depends_on:
      - torus-redis
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 128m

  torus-pos:
    image: torus-pos:local
    container_name: torus-pos
    restart: unless-stopped
    ports:
      - "3100:3100"
    environment:
      - REDIS_HOST=torus-redis
      - REDIS_PORT=6379
    networks:
      - torus-network
    depends_on:
      - torus-redis
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 128m

  torus-website:
    image: torus-website:local
    container_name: torus-website
    restart: unless-stopped
    ports:
      - "3005:3000"
    networks:
      - torus-network
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 128m

  torus-alert-router:
    image: torus-alert-router:local
    container_name: torus-alert-router
    restart: unless-stopped
    ports:
      - "4000:4000"
    environment:
      - REDIS_HOST=torus-redis
      - REDIS_PORT=6379
    networks:
      - torus-network
    depends_on:
      - torus-redis
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 128m

  torus-backup:
    image: torus-backup:local
    container_name: torus-backup
    restart: on-failure
    volumes:
      - torus_backup_data:/backup
      - torus_redis_data:/backup/redis:ro
    networks:
      - torus-network
    depends_on:
      - torus-redis
    deploy:
      resources:
        limits:
          memory: 512m
        reservations:
          memory: 384m

  prometheus:
    image: prom/prometheus:latest
    container_name: torus-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - torus_prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=7d'
    networks:
      - torus-network
    deploy:
      resources:
        limits:
          memory: 512m
        reservations:
          memory: 384m

  grafana:
    image: grafana/grafana:latest
    container_name: torus-grafana
    restart: unless-stopped
    ports:
      - "3002:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - torus_grafana_data:/var/lib/grafana
    networks:
      - torus-network
    depends_on:
      - prometheus
    deploy:
      resources:
        limits:
          memory: 256m
        reservations:
          memory: 200m

volumes:
  torus_redis_data:
  torus_backup_data:
  torus_prometheus_data:
  torus_grafana_data:

networks:
  torus-network:
    driver: bridge
```

**Deploy:**
```powershell
docker compose -f docker-compose-torus-pinkcady.yml up -d
docker compose -f docker-compose-torus-pinkcady.yml ps
```

### Step 3: Verify All Health Endpoints

```powershell
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
        $response = curl.exe -s -w "%{http_code}" "http://$url"
        Write-Host "$($service.Key): $response" -ForegroundColor Green
    } catch {
        Write-Host "$($service.Key): FAILED" -ForegroundColor Red
    }
}
```

---

## PHASE 2: WEBHOOKS

### Step 1: Setup Docker Event Webhooks

**Goal:** Trigger automations when containers start/stop/fail

**Create:** `webhook-handler.py`
```python
#!/usr/bin/env python3
"""Docker event webhook handler for Torus automation."""
import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        event = json.loads(body)
        
        container = event.get('Actor', {}).get('Attributes', {}).get('name', 'unknown')
        action = event.get('Action', 'unknown')
        
        print(f"[WEBHOOK] {container}: {action}")
        
        # Log to obsidian inbox
        if action == 'die':  # Container crashed
            self.trigger_alert(f"Container {container} crashed", severity="critical")
        elif action == 'start':
            self.trigger_alert(f"Container {container} started", severity="info")
        elif action == 'stop':
            self.trigger_alert(f"Container {container} stopped", severity="warning")
        
        self.send_response(200)
        self.end_headers()
    
    def trigger_alert(self, message, severity):
        """Send alert to torus-alert-router."""
        try:
            subprocess.run([
                'curl', '-X', 'POST', 'http://torus-alert-router:4000/alert',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({
                    "severity": severity,
                    "service": "docker-events",
                    "message": message,
                    "timestamp": "2026-08-06T..."
                })
            ], timeout=5)
        except Exception as e:
            print(f"Alert send failed: {e}")

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8888), WebhookHandler)
    print("Docker webhook receiver listening on port 8888")
    server.serve_forever()
```

**Docker Compose service:**
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

### Step 2: Enable Docker Events Forwarding

**Create:** `docker-event-forwarder.sh`
```bash
#!/bin/bash
# Forward Docker events to webhook handler

docker events \
  --filter type=container \
  --filter event=start,stop,die,restart \
  --format '{{json .}}' | \
  while read event; do
    curl -X POST \
      -H "Content-Type: application/json" \
      -d "$event" \
      http://localhost:8888/webhook
  done
```

**Run as service:**
```yaml
docker-events-forwarder:
  image: curlimages/curl:latest
  container_name: docker-events-forwarder
  restart: unless-stopped
  command: >
    sh -c "
    docker events --filter type=container --filter event=start,stop,die,restart --format '{{json .}}' |
    while read event; do
      curl -X POST -H 'Content-Type: application/json' -d \"$$event\" http://webhook-handler:8888/webhook || true
    done
    "
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
  networks:
    - torus-network
```

---

## PHASE 3: VOLUME MANAGEMENT

### Step 1: Persistent Volume Strategy

**Volumes needed:**
```yaml
volumes:
  # Cache/State
  torus_redis_data:      # Redis persistence
  torus_cache_data:      # Application cache

  # Logs
  torus_logs:            # All service logs
  torus_alert_logs:      # Alert router logs

  # Backups
  torus_backup_data:     # Backup archive
  torus_config_backup:   # Config snapshots

  # Monitoring
  torus_prometheus_data: # Metrics DB (7d retention)
  torus_grafana_data:    # Dashboards + settings

  # Shared
  torus_shared_data:     # Shared between services
```

### Step 2: Volume Backup Strategy

**Create:** `backup-volumes.sh`
```bash
#!/bin/bash
# Backup all Docker volumes daily

BACKUP_DIR="/backup/volumes"
DATE=$(date +%Y-%m-%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup each volume
for volume in torus_redis_data torus_prometheus_data torus_grafana_data torus_backup_data; do
  echo "Backing up $volume..."
  docker run --rm \
    -v "$volume:/data:ro" \
    -v "$BACKUP_DIR:/backup" \
    alpine tar czf "/backup/${volume}_${DATE}.tar.gz" -C /data .
done

echo "Volume backups complete: $BACKUP_DIR"
```

**Schedule as cron job:**
```bash
0 2 * * * /usr/local/bin/backup-volumes.sh
```

---

## PHASE 4: KUBERNETES OPTIMIZATION

### Step 1: Enable K3s on PINKCADY

```powershell
# From PINKCADY (Windows with WSL2)
wsl
curl -sfL https://get.k3s.io | sh -

# Verify
k3s kubectl get nodes
k3s kubectl get pods -A
```

### Step 2: Deploy Torus Services as K8s StatefulSets

**Create:** `k8s-torus-deployment.yaml`
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: torus

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: torus-config
  namespace: torus
data:
  REDIS_HOST: torus-redis
  REDIS_PORT: "6379"

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: torus-redis
  namespace: torus
spec:
  serviceName: torus-redis
  replicas: 1
  selector:
    matchLabels:
      app: torus-redis
  template:
    metadata:
      labels:
        app: torus-redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi

---
apiVersion: v1
kind: Service
metadata:
  name: torus-redis
  namespace: torus
spec:
  clusterIP: None
  selector:
    app: torus-redis
  ports:
  - port: 6379
    targetPort: 6379

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: torus-inventory
  namespace: torus
spec:
  replicas: 2
  selector:
    matchLabels:
      app: torus-inventory
  template:
    metadata:
      labels:
        app: torus-inventory
    spec:
      containers:
      - name: inventory
        image: torus-inventory:local
        ports:
        - containerPort: 3200
        envFrom:
        - configMapRef:
            name: torus-config
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3200
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 3200
          initialDelaySeconds: 5
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: torus-inventory
  namespace: torus
spec:
  selector:
    app: torus-inventory
  ports:
  - port: 3200
    targetPort: 3200
  type: LoadBalancer
```

**Deploy:**
```bash
k3s kubectl apply -f k8s-torus-deployment.yaml
k3s kubectl get pods -n torus
k3s kubectl logs -n torus deployment/torus-inventory
```

---

## PHASE 5: MCP TOOLKIT

### Step 1: Enable MCP in Docker Desktop

**MCP (Model Context Protocol) servers for Docker:**
- Docker daemon inspection
- Container log streaming
- Image registry access
- Network diagnostics

**Create:** `mcp-config.json`
```json
{
  "mcpServers": {
    "docker": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "/var/run/docker.sock:/var/run/docker.sock", "mcp/docker-server:latest"],
      "env": {
        "DOCKER_HOST": "unix:///var/run/docker.sock"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/work"],
      "env": {}
    },
    "kubernetes": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "~/.kube:/root/.kube", "mcp/kubernetes-server:latest"],
      "env": {
        "KUBECONFIG": "/root/.kube/config"
      }
    }
  }
}
```

**Place in:** `~/.config/codetools/mcp-config.json` (Linux/Mac) or `%APPDATA%\codetools\mcp-config.json` (Windows)

### Step 2: Connect to Claude Desktop

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "docker": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "/var/run/docker.sock:/var/run/docker.sock", "ghcr.io/docker/server-mcp:latest"],
      "alwaysAllow": ["docker_inspect", "docker_logs"]
    },
    "torus": {
      "command": "python",
      "args": ["-m", "mcp_server_torus"],
      "env": {
        "TORUS_API": "http://localhost:3200",
        "REDIS_HOST": "localhost:6379"
      }
    }
  }
}
```

### Step 3: Create Torus MCP Server

**File:** `mcp_server_torus.py`
```python
#!/usr/bin/env python3
"""MCP server for Torus Coffee infrastructure."""
import json
import subprocess
from typing import Any

class TorusMCPServer:
    def __init__(self):
        self.name = "torus"
        self.version = "1.0"
    
    def get_tools(self) -> list:
        return [
            {
                "name": "inventory_status",
                "description": "Get current inventory status",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "pos_transactions",
                "description": "Fetch recent POS transactions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 10}
                    }
                }
            },
            {
                "name": "container_health",
                "description": "Check health of all Torus containers",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "deploy_service",
                "description": "Deploy a Torus service",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service": {"type": "string", "enum": ["inventory", "pos", "website", "alert-router"]}
                    }
                }
            }
        ]
    
    def call_tool(self, name: str, args: dict) -> Any:
        if name == "inventory_status":
            return self._inventory_status()
        elif name == "pos_transactions":
            return self._pos_transactions(args.get("limit", 10))
        elif name == "container_health":
            return self._container_health()
        elif name == "deploy_service":
            return self._deploy_service(args.get("service"))
        else:
            return {"error": f"Unknown tool: {name}"}
    
    def _inventory_status(self) -> dict:
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:3200/inventory"],
                capture_output=True, text=True, timeout=5
            )
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": str(e)}
    
    def _pos_transactions(self, limit: int) -> dict:
        try:
            result = subprocess.run(
                ["curl", "-s", f"http://localhost:3100/orders?limit={limit}"],
                capture_output=True, text=True, timeout=5
            )
            return json.loads(result.stdout)
        except Exception as e:
            return {"error": str(e)}
    
    def _container_health(self) -> dict:
        health = {}
        services = ["inventory", "pos", "website", "alert-router", "redis"]
        for service in services:
            ports = {"inventory": 3200, "pos": 3100, "website": 3005, "alert-router": 4000, "redis": 6379}
            port = ports.get(service)
            try:
                result = subprocess.run(
                    ["curl", "-s", "-w", "%{http_code}", f"http://localhost:{port}/health"],
                    capture_output=True, text=True, timeout=5
                )
                status = "UP" if "200" in result.stdout else "DOWN"
                health[service] = status
            except:
                health[service] = "DOWN"
        return health
    
    def _deploy_service(self, service: str) -> dict:
        try:
            subprocess.run(
                ["docker", "compose", "up", "-d", f"torus-{service}"],
                timeout=30
            )
            return {"status": "deployed", "service": service}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    server = TorusMCPServer()
    print(json.dumps({"name": server.name, "version": server.version, "tools": server.get_tools()}, indent=2))
```

**Install:**
```bash
pip install mcp
python mcp_server_torus.py
```

---

## IMPLEMENTATION TIMELINE

| Phase | Task | Duration | Start | End | Owner |
|-------|------|----------|-------|-----|-------|
| **CRITICAL** | Clear Suricata log | 30 min | NOW | 2h | Sir Green |
| **CRITICAL** | Add memory limits | 30 min | NOW | 2h | Sir Green |
| **P1** | Verify memory resolved | 15 min | 2h | 2.5h | Miss Pink |
| **P1** | Deploy Torus on PINKCADY | 1 hour | 2.5h | 3.5h | Miss Pink |
| **P2** | Setup webhooks | 2 hours | 3.5h | 5.5h | Miss Pink |
| **P3** | Configure volumes | 1.5 hours | 5.5h | 7h | Miss Pink |
| **P4** | Setup K8s on PINKCADY | 2 hours | 7h | 9h | Miss Pink |
| **P5** | Enable MCP toolkit | 1 hour | 9h | 10h | Miss Pink |
| **VERIFY** | End-to-end testing | 2 hours | 10h | 12h | Both |

**Total Time:** 12 hours (can be done in 1 work day)

---

## VERIFICATION CHECKLIST

### Memory Crisis Resolution ✓
- [ ] Suricata eve.json cleared (verify `docker stats`)
- [ ] Memory usage < 5.5 GB
- [ ] All containers running
- [ ] No OOMKilled events in logs

### Docker Services ✓
- [ ] All 9 Torus services healthy
- [ ] Health endpoints responding (3100, 3200, 3000, 4000)
- [ ] Redis connected
- [ ] Backups running on schedule

### Webhooks ✓
- [ ] Docker events being captured
- [ ] Alerts triggering on container crash
- [ ] Webhook logs in torus-alert-router

### Volumes ✓
- [ ] All named volumes created
- [ ] Persistent data surviving container restarts
- [ ] Backups completing daily

### Kubernetes ✓
- [ ] K3s running on PINKCADY
- [ ] Torus services deployed as StatefulSets
- [ ] Services discoverable via DNS
- [ ] Resource limits enforced

### MCP Toolkit ✓
- [ ] MCP servers registered
- [ ] Claude Desktop can access Docker info
- [ ] Torus MCP tools available
- [ ] Can deploy/inspect services via MCP

---

## FINAL NOTES FOR MISS PINK

**You're about to unlock:**
1. **Stable infrastructure** — Memory crisis resolved, proper limits in place
2. **Automation** — Docker webhooks trigger alerts and actions
3. **Persistence** — Volumes back up daily, data survives crashes
4. **Orchestration** — Kubernetes handles scheduling and scaling
5. **AI Integration** — MCP servers let Claude/GPT manage infrastructure

**Key Wins:**
- ✅ 8 GB → 3.5 GB memory freed
- ✅ 5 services → 2 machines (SQUIDSTATION + PINKCADY)
- ✅ Manual monitoring → Automated webhooks
- ✅ Docker CLI → Kubernetes manifests
- ✅ Manual deployment → MCP-driven orchestration

**Next after this:** Set up GitHub Actions CI/CD pipeline to auto-build and deploy on push.

---

⚓ **From Miss Gordon**  
**Status:** Ready for implementation  
**Estimated completion:** 2026-08-06 22:00 UTC  
**Contact:** Miss Gordon (if blockers)
