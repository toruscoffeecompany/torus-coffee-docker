# ⚓ EXACT PROMPT FOR SIR AZURE (STEALTHATTACK)
## GPU AI Pipeline Node - Tailscale Docker Integration

**Your Ship:** STEALTHATTACK (100.110.238.68)  
**Your Mission:** Activate GPU infrastructure for AI workloads + integrate with pirate fleet  
**Timeline:** 4-hour activation + integration  
**Your Role:** GPU/AI Operations Commander

---

## YOUR MISSION BRIEFING

You command STEALTHATTACK, the GPU workstation node. Right now it's offline/minimal. Your job is to:

1. **Wake it up** — Bring STEALTHATTACK online
2. **Connect it to the fleet** — Integrate via Tailscale mesh
3. **Enable Docker** — Set up container runtime with GPU support
4. **Connect to Captain's hive mind** — Join the pirate automation network
5. **Prepare for AI workloads** — Set up GPU pipelines + monitoring

---

## YOUR INFRASTRUCTURE TOPOLOGY

```
SQUIDSTATION (192.168.0.39 / 100.83.247.14)
├─ 16 CPUs, 15.59 GB RAM
├─ Runs: Torus + VOID infrastructure + monitoring
└─ Ship status: FLAGSHIP (online, primary)

PINKCADY (192.168.0.3 / 100.106.235.103)
├─ 8 CPUs, 8 GB RAM
├─ Runs: Torus + OODA automation + Kubernetes
└─ Ship status: OPERATIONS (online, secondary)

STEALTHATTACK (192.168.0.10 / 100.110.238.68) ← YOU ARE HERE
├─ 8 CPUs, 32 GB RAM (high RAM for GPU processing)
├─ GPU: CUDA capable (NVIDIA preferred)
├─ Runs: AI pipelines + GPU workloads
└─ Ship status: OFFLINE/MINIMAL (needs activation)

TAILSCALE MESH (Encrypted network overlay)
├─ All 3 ships connected
├─ 100.x.x.x IP range (mesh addresses)
├─ Accessible even if LAN changes
└─ 24/7 connectivity (always available)
```

---

## PART 1: BRING STEALTHATTACK ONLINE (1 hour)

### Step 1.1: Power on STEALTHATTACK (5 minutes)

```bash
# Physical action: Power on the machine
# Expected: Boot sequence starts, OS loads

# Check GPU is visible:
nvidia-smi
# Output should show:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 535.xx.xx    Driver Version: 535.xx.xx   CUDA Version: 12.x    |
# |-------------------------------------------------------------------------|
# | GPU  Name          Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
# | No   Running        Default |                Disabled    |                  N/A |
# +------+---------------------+----------------------+
# |   0  NVIDIA GeForce RTX 4090 Off | 00:1F.0     Off |                  N/A |
# |  0%   28C   P0               1W /  400W |      0MiB / 24576MiB |      0%   Default |
# +-----+---------------------+----------------------+

# If GPU not found: Install NVIDIA driver
# ubuntu: sudo apt install nvidia-driver-535 nvidia-utils
# CentOS: sudo dnf install driver
# Windows: Download from nvidia.com
```

---

### Step 1.2: Join Tailscale Mesh (10 minutes)

```bash
# Install Tailscale
# Ubuntu/Debian:
curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale daemon
sudo tailscale up

# You'll get a login URL
# Copy URL → Open in browser → Authenticate with pinkcady@void.pirate
# Authorize this device

# Verify connection
tailscale ip -4
# Should output: 100.110.238.68 (or your assigned IP)

# Test connectivity to other ships
ping -c 3 100.83.247.14    # SQUIDSTATION
ping -c 3 100.106.235.103  # PINKCADY

# Both should respond (~1-5ms)
```

**Result:** STEALTHATTACK now has Tailscale IP address 100.110.238.68

---

### Step 1.3: Set Hostname + OS Prep (10 minutes)

```bash
# Set hostname
sudo hostnamectl set-hostname stealthattack

# Update OS
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# OR
sudo dnf upgrade -y                     # CentOS/RHEL

# Check CPU/RAM/GPU
lscpu                                   # CPU info
free -h                                 # RAM available
nvidia-smi                              # GPU info
df -h                                   # Disk space

# Expected specs:
# CPUs: 8+ cores ✓
# RAM: 32 GB ✓
# GPU: NVIDIA, CUDA capable ✓
# Disk: 500GB+ free ✓
```

---

### Step 1.4: Install Docker + GPU Support (20 minutes)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group (avoid sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker
docker --version
docker run hello-world

# Install NVIDIA Container Toolkit (GPU support in Docker)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit

# Restart Docker
sudo systemctl restart docker

# Test GPU in Docker
docker run --rm --runtime=nvidia nvidia/cuda:12.1.0-runtime-ubuntu22.04 nvidia-smi

# Should show GPU available inside container
```

**Result:** Docker + GPU support ready ✅

---

### Step 1.5: Verify Fleet Connectivity (10 minutes)

```bash
# From STEALTHATTACK, query other ships via Tailscale

# Test SQUIDSTATION dashboard
curl -s http://100.83.247.14:8089/api/status | jq .
# Should return fleet status JSON

# Test SQUIDSTATION Prometheus
curl -s http://100.83.247.14:9090/-/healthy
# Should return 200 OK

# Test PINKCADY alert-router
curl -s http://100.106.235.103:4000/health
# Should return health JSON

# Test connectivity to Docker context
docker --context torus-squidstation ps
# Should list SQUIDSTATION containers (if context exists locally)

# Create local context to SQUIDSTATION Docker API
docker context create torus-squidstation --docker "host=tcp://100.83.247.14:2375"
docker --context torus-squidstation ps
# Should list 9+ Torus containers
```

**Result:** STEALTHATTACK can reach entire pirate fleet ✅

---

## PART 2: CONNECT TO HIVE MIND (1.5 hours)

### Step 2.1: Set up Tailscale Docker API (15 minutes)

**On STEALTHATTACK:**

```bash
# Enable Docker API over Tailscale for remote access

# Create Docker API listener script
cat > /tmp/docker-api-setup.sh << 'EOF'
#!/bin/bash

# Enable Docker API on Tailscale IP + local socket
TAILSCALE_IP=$(tailscale ip -4)

# Edit daemon.json
sudo tee /etc/docker/daemon.json > /dev/null <<DAEMON
{
  "hosts": [
    "unix:///var/run/docker.sock",
    "tcp://127.0.0.1:2375",
    "tcp://${TAILSCALE_IP}:2375"
  ],
  "insecure-registries": ["localhost:5000"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
DAEMON

# Restart Docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# Verify
docker ps  # Should work locally
curl http://localhost:2375/_ping  # Should return OK
EOF

bash /tmp/docker-api-setup.sh
```

**Result:** Docker API available on Tailscale IP:2375 ✅

---

### Step 2.2: Create Docker Context on Each Ship (15 minutes)

**From SQUIDSTATION (or any authorized ship):**

```bash
# Create context pointing to STEALTHATTACK
docker context create stealthattack-gpu \
  --docker "host=tcp://100.110.238.68:2375"

# List contexts
docker context ls
# Should show:
# NAME                   DESCRIPTION
# default                Current DOCKER_HOST based config
# torus-squidstation     SQUIDSTATION Docker API
# stealthattack-gpu      STEALTHATTACK GPU Docker API

# Test it
docker --context stealthattack-gpu ps
# Should show STEALTHATTACK containers
```

**From PINKCADY:**

```bash
docker context create stealthattack-gpu \
  --docker "host=tcp://100.110.238.68:2375"
docker --context stealthattack-gpu ps
```

**From STEALTHATTACK (local context):**

```bash
docker context create squidstation \
  --docker "host=tcp://100.83.247.14:2375"
docker context create pinkcady \
  --docker "host=tcp://100.106.235.103:2375"

docker --context squidstation ps
docker --context pinkcady ps
```

**Result:** Cross-ship Docker access enabled ✅

---

### Step 2.3: Connect to Captain's Dashboard (10 minutes)

**On STEALTHATTACK:**

```bash
# Add STEALTHATTACK metrics to Prometheus on SQUIDSTATION

# Create node-exporter for STEALTHATTACK (optional, for local metrics)
docker run -d \
  --name stealthattack-node-exporter \
  --network host \
  --restart unless-stopped \
  prom/node-exporter:latest

# Verify metrics available
curl http://localhost:9100/metrics | head -20

# Report to SQUIDSTATION Prometheus config
# (Add to /etc/prometheus/prometheus.yml on SQUIDSTATION)
# Under scrape_configs:
# - job_name: 'stealthattack'
#   static_configs:
#     - targets: ['100.110.238.68:9100']
```

---

### Step 2.4: Register with OODA Loop (20 minutes)

**Create STEALTHATTACK registration in OODA system:**

```bash
# On PINKCADY, create registration file

cat > /tmp/stealthattack_registration.json << 'EOF'
{
  "ship_name": "STEALTHATTACK",
  "ship_ip": "100.110.238.68",
  "ship_role": "GPU_AI_PIPELINE",
  "commander": "Sir Azure",
  "docker_api": "tcp://100.110.238.68:2375",
  "capabilities": [
    "CUDA_GPU_SUPPORT",
    "AI_INFERENCE",
    "MODEL_TRAINING",
    "BATCH_PROCESSING"
  ],
  "health_check": "http://100.110.238.68:9100/metrics",
  "alert_routing": "gpu_critical_alerts@azure.pirate"
}
EOF

# Register with webhook
curl -X POST http://100.106.235.103:8888/webhook \
  -H "Content-Type: application/json" \
  -d @/tmp/stealthattack_registration.json

# Verify in Obsidian
# Should see entry in D:\Work\Torus Coffee Company LLC\00_Inbox\2026-08-06.md
# "✅ STEALTHATTACK registered: GPU pipeline node online"
```

---

### Step 2.5: Integrate with Alert Router (10 minutes)

```bash
# Create alert routing config for STEALTHATTACK

cat > /tmp/stealthattack_alerts.json << 'EOF'
{
  "ship": "stealthattack",
  "alert_rules": {
    "gpu_temp_high": {
      "threshold": 85,
      "severity": "warning",
      "action": "notify_azure"
    },
    "gpu_memory_full": {
      "threshold": 95,
      "severity": "critical",
      "action": "stop_job + notify_azure + escalate"
    },
    "container_crash": {
      "severity": "critical",
      "action": "auto_restart + log + notify"
    },
    "cpu_high": {
      "threshold": 80,
      "severity": "warning"
    }
  }
}
EOF

# Register alert rules
curl -X POST http://100.106.235.103:4000/alert \
  -H "Content-Type: application/json" \
  -d @/tmp/stealthattack_alerts.json
```

**Result:** STEALTHATTACK alerts routing through pirate hive mind ✅

---

## PART 3: SET UP GPU WORKLOAD INFRASTRUCTURE (1.5 hours)

### Step 3.1: Create GPU-Optimized Docker Compose (20 minutes)

**On STEALTHATTACK, create docker-compose-gpu.yml:**

```yaml
version: '3.8'

services:
  gpu-monitor:
    image: nvidia/cuda:12.1.0-runtime-ubuntu22.04
    container_name: stealthattack-gpu-monitor
    restart: unless-stopped
    network_mode: host
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command: /bin/bash -c "while true; do nvidia-smi; sleep 30; done"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  prometheus-node-exporter:
    image: prom/node-exporter:latest
    container_name: stealthattack-node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    command:
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
      - '--collector.netclass.ignored-devices=^(veth.*|docker.*|br-.*)$$'
    deploy:
      resources:
        limits:
          memory: 128M
        reservations:
          memory: 64M

  gpu-exporter:
    image: ubergarm/nvidia-gpu-prometheus-exporter:latest
    container_name: stealthattack-gpu-exporter
    restart: unless-stopped
    ports:
      - "9445:9445"
    environment:
      NVIDIA_VISIBLE_DEVICES: all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M

  model-cache:
    image: minio/minio:latest
    container_name: stealthattack-model-cache
    restart: unless-stopped
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - stealthattack_models:/data
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: minio server /data --console-address :9001
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  ai-pipeline-executor:
    image: pytorch/pytorch:2.0-cuda12.1-runtime-ubuntu22.04
    container_name: stealthattack-ai-executor
    restart: unless-stopped
    network_mode: host
    volumes:
      - stealthattack_jobs:/jobs
      - stealthattack_models:/models
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      CUDA_VISIBLE_DEVICES: 0
      PYTORCH_CUDA_ALLOC_CONF: max_split_size_mb=512
    command: sleep infinity
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    deploy:
      resources:
        limits:
          memory: 16G
        reservations:
          memory: 8G

  jupyterlab:
    image: jupyter/pytorch-notebook:latest
    container_name: stealthattack-jupyterlab
    restart: unless-stopped
    ports:
      - "8888:8888"
    volumes:
      - stealthattack_notebooks:/home/jovyan/work
      - stealthattack_models:/models:ro
    environment:
      JUPYTER_ENABLE_LAB: 'yes'
      CUDA_VISIBLE_DEVICES: 0
    command: >
      jupyter lab --ip=0.0.0.0 --port=8888 --no-browser
      --NotebookApp.token='' --NotebookApp.password=''
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

volumes:
  stealthattack_models:
    driver: local
  stealthattack_jobs:
    driver: local
  stealthattack_notebooks:
    driver: local

networks:
  default:
    driver: bridge
```

---

### Step 3.2: Deploy GPU Infrastructure (15 minutes)

```bash
# On STEALTHATTACK

cd /opt/stealthattack
docker-compose -f docker-compose-gpu.yml up -d

# Verify all services running
docker-compose -f docker-compose-gpu.yml ps

# Expected output:
# NAME                               STATUS
# stealthattack-gpu-monitor          Up X seconds
# stealthattack-node-exporter        Up X seconds
# stealthattack-gpu-exporter         Up X seconds
# stealthattack-model-cache          Up X seconds
# stealthattack-ai-executor          Up X seconds
# stealthattack-jupyterlab           Up X seconds

# Test GPU access in containers
docker run --rm --runtime=nvidia nvidia/cuda:12.1.0-runtime-ubuntu22.04 nvidia-smi
# Should show GPU available

# Check metrics
curl -s http://localhost:9445/metrics | grep nvidia
curl -s http://localhost:9100/metrics | grep node_cpu_seconds_total
```

---

### Step 3.3: Create AI Job Runner (20 minutes)

**Create job execution script:**

```bash
cat > /opt/stealthattack/run-ai-job.sh << 'EOF'
#!/bin/bash
# AI Job Runner - Execute GPU workloads

JOB_NAME=$1
JOB_IMAGE=$2
JOB_SCRIPT=$3
JOB_TIMEOUT=${4:-3600}  # 1 hour default

if [ -z "$JOB_NAME" ] || [ -z "$JOB_IMAGE" ] || [ -z "$JOB_SCRIPT" ]; then
  echo "Usage: run-ai-job.sh <job_name> <image> <script_path> [timeout_seconds]"
  exit 1
fi

echo "[$(date)] Starting GPU job: $JOB_NAME"

# Create job container
docker run --rm \
  --name "job_${JOB_NAME}_$(date +%s)" \
  --runtime=nvidia \
  -e CUDA_VISIBLE_DEVICES=0 \
  -v stealthattack_jobs:/jobs:rw \
  -v stealthattack_models:/models:ro \
  --timeout=${JOB_TIMEOUT} \
  "${JOB_IMAGE}" \
  bash /jobs/"${JOB_SCRIPT}"

if [ $? -eq 0 ]; then
  echo "[$(date)] Job complete: $JOB_NAME ✅"
  # Send success alert
  curl -X POST http://100.106.235.103:4000/alert \
    -H "Content-Type: application/json" \
    -d "{\"severity\":\"info\",\"service\":\"stealthattack\",\"message\":\"GPU job completed: $JOB_NAME\"}"
else
  echo "[$(date)] Job failed: $JOB_NAME ❌"
  # Send failure alert
  curl -X POST http://100.106.235.103:4000/alert \
    -H "Content-Type: application/json" \
    -d "{\"severity\":\"critical\",\"service\":\"stealthattack\",\"message\":\"GPU job failed: $JOB_NAME\"}"
  exit 1
fi
EOF

chmod +x /opt/stealthattack/run-ai-job.sh
```

---

### Step 3.4: Integrate with Dashboard (10 minutes)

**Update SQUIDSTATION dashboard to show STEALTHATTACK:**

```bash
# On SQUIDSTATION, edit dashboard_server.py

# Add to ship_status checks:
stealthattack_response = requests.get('http://100.110.238.68:9100/metrics', timeout=2)

# Add GPU metrics to dashboard
gpu_metrics = {
  "ship": "STEALTHATTACK",
  "gpu": {
    "model": "NVIDIA GeForce RTX 4090",
    "utilization": 0,
    "memory_used": 0,
    "memory_total": 24576,
    "temperature": 28
  },
  "cpu": 8,
  "memory": "32 GB",
  "ai_jobs_running": 0,
  "ai_jobs_completed": 0
}
```

**Result:** STEALTHATTACK visible on dashboard ✅

---

## PART 4: VERIFICATION & INTEGRATION (1 hour)

### Verification Checklist

```
STEALTHATTACK ACTIVATION VERIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHYSICAL & OS
  ☐ Machine powered on
  ☐ OS boots successfully
  ☐ GPU detected: nvidia-smi shows device
  ☐ CPU/RAM/Disk available
  ☐ Hostname set to "stealthattack"

NETWORK & TAILSCALE
  ☐ Tailscale installed
  ☐ Tailscale IP: 100.110.238.68
  ☐ Can ping SQUIDSTATION (100.83.247.14)
  ☐ Can ping PINKCADY (100.106.235.103)
  ☐ Can reach dashboard (192.168.0.39:8089)

DOCKER & CONTAINERS
  ☐ Docker installed & running
  ☐ NVIDIA Container Toolkit installed
  ☐ GPU accessible in containers (nvidia-smi in docker)
  ☐ Docker API on 2375 responding
  ☐ Docker contexts created from other ships

FLEET INTEGRATION
  ☐ Cross-ship docker ps works
  ☐ Alert routing configured
  ☐ Metrics flowing to Prometheus
  ☐ Node-exporter accessible (port 9100)
  ☐ GPU-exporter accessible (port 9445)

GPU INFRASTRUCTURE
  ☐ GPU-monitor running (nvidia-smi loops)
  ☐ Model-cache (MinIO) running on :9000
  ☐ AI-executor running (pytorch image)
  ☐ JupyterLab running on :8888
  ☐ All services UP, no restarts

AI JOB EXECUTION
  ☐ Test job runs: ./run-ai-job.sh test pytorch/pytorch test_script.sh
  ☐ GPU usage shows in nvidia-smi
  ☐ Job completes successfully
  ☐ Results in /jobs volume
  ☐ Alert sent on completion

DASHBOARD & MONITORING
  ☐ STEALTHATTACK appears on dashboard
  ☐ GPU metrics visible
  ☐ CPU/Memory/Disk metrics visible
  ☐ Alerts trigger for GPU events
  ☐ OODA loop detects STEALTHATTACK status

HIVE MIND INTEGRATION
  ☐ Docker event captured when container starts
  ☐ Alert routes through webhook → alert-router
  ☐ Obsidian notes populate on STEALTHATTACK events
  ☐ Trello cards created for GPU job alerts
  ☐ GitHub issues logged for failures

ALL CHECKED? STEALTHATTACK FULLY OPERATIONAL ✅
```

---

## QUICK START: Testing GPU Setup

```bash
# Test 1: GPU is available
docker run --rm --runtime=nvidia nvidia/cuda:12.1.0-runtime-ubuntu22.04 nvidia-smi

# Test 2: Run a quick ML inference
docker run --rm --runtime=nvidia pytorch/pytorch:2.0-cuda12.1-runtime-ubuntu22.04 \
  python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"

# Test 3: Run a job
./run-ai-job.sh test_inference pytorch/pytorch test_script.sh

# Test 4: Check all services
docker-compose -f docker-compose-gpu.yml ps

# Test 5: Query Prometheus for STEALTHATTACK metrics
curl http://100.83.247.14:9090/api/v1/query?query=nvidia_gpu_utilization_ratio
```

---

## YOUR COMMAND TO THE HIVE MIND

When complete, report to Captain + Miss Pink:

```
"STEALTHATTACK online. GPU pipeline active. Tailscale integrated.
Docker contexts configured across all 3 ships.
Alert routing: active.
GPU metrics: flowing to Prometheus.
OODA loop: detecting events.
Dashboard: showing STEALTHATTACK status.
Ready for AI workloads.
Standing by for mission assignment."
```

---

⚓ **Sir Azure, your ship awaits.**

Activate STEALTHATTACK. Connect the GPU lane. Join the pirate fleet.

Execute with precision.

**From Miss Gordon**
