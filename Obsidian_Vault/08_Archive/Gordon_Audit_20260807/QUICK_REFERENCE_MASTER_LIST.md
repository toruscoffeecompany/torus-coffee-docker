# 📌 QUICK REFERENCE MASTER LIST
## Copy-Paste Commands & Key Data

---

## 🚨 CRITICAL COMMANDS (Execute This Week)

### Fix PINKCADY Memory Crisis (1 Hour)
```bash
# Set memory limits on ALL containers
docker ps --format "{{.Names}}" | while read c; do
  docker update -m 512m --memory-reservation 256m $c
done

# Verify limits applied
docker ps --format "{{.Names}}" | while read c; do
  echo "$c:"
  docker inspect $c | grep -E '"Memory"|"MemoryReservation"'
done
```

### Verify Security (30 Minutes)
```bash
# Check TLS enabled
docker info | grep -i "tlsverify"

# Check for privileged containers
docker ps --format "{{.Names}}" | while read c; do
  if docker inspect $c | grep -q '"Privileged": true'; then
    echo "PRIVILEGED: $c"
  fi
done

# Check memory limits
docker ps --format "{{.Names}}" | while read c; do
  echo -n "$c: "
  docker inspect $c | grep '"Memory"' | head -1
done

# Check storage location
docker info | grep "Docker Root Dir"
```

---

## ⚡ HIGH PRIORITY COMMANDS (This Month)

### Optimize Kernel Parameters (1 Hour)
```bash
# Check current values
echo "=== Current Values ==="
sysctl vm.swappiness
sysctl net.core.somaxconn
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.ip_local_port_range

# Set optimal values
echo "=== Setting Optimal Values ==="
sudo sysctl -w vm.swappiness=10
sudo sysctl -w net.core.somaxconn=32768
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=32768
sudo sysctl -w 'net.ipv4.ip_local_port_range=1024 65535'

# Make persistent
echo "=== Making Persistent ==="
echo "vm.swappiness = 10" | sudo tee -a /etc/sysctl.conf
echo "net.core.somaxconn = 32768" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 32768" | sudo tee -a /etc/sysctl.conf

# Reload
sudo sysctl -p
```

### Unlock GPU on STEALTHATTACK (30 Minutes)
```bash
# Test GPU access
docker run --gpus all nvidia/cuda:12.0-base nvidia-smi

# Deploy JupyterLab with GPU
docker run --gpus all -d -p 8888:8888 \
  -e JUPYTER_ENABLE_LAB=yes \
  jupyter/pytorch-notebook

# Access at: http://stealthattack:8888
```

### Create Custom Network (30 Minutes)
```bash
# Create network
docker network create pirate-fleet

# Verify created
docker network ls | grep pirate-fleet

# Connect existing containers (one at a time)
docker stop <container>
docker rm <container>
docker run --network pirate-fleet --name <container> ...

# Test DNS resolution
docker exec <container> nslookup <other_container_on_network>
```

---

## 🔧 DIAGNOSTIC COMMANDS (When Troubleshooting)

### Storage Space Issues
```bash
# Overall Docker space usage
docker system df

# List all volumes
docker volume ls

# List dangling volumes
docker volume ls --filter dangling=true

# Remove dangling
docker volume prune -f

# Find what's eating space
du -sh /var/lib/docker/*
```

### Memory Issues
```bash
# Real-time memory stats
docker stats --no-stream

# Watch memory for specific container
watch -n 1 'docker stats --no-stream | grep <container>'

# Check kernel OOMKill logs
dmesg | grep -i oomkill

# Check memory limits
docker inspect <container> | grep -E '"Memory"|"MemoryReservation"'
```

### Networking Issues
```bash
# Test DNS from inside container
docker exec <container> nslookup <other_container>

# Test connectivity
docker exec <container> ping <other_container_ip>

# Check network configuration
docker network inspect <network>

# List all networks
docker network ls
```

### GPU Issues
```bash
# Check GPU on host
nvidia-smi

# Check GPU from container
docker run --gpus all nvidia/cuda:12.0-base nvidia-smi

# Monitor GPU usage
watch -n 1 nvidia-smi

# Check CUDA version
docker run --gpus all nvidia/cuda:12.0-base nvcc --version
```

### Tailscale Mesh Status
```bash
# Check mesh status
tailscale status

# Check connectivity to other ships
tailscale ping pinkcady
tailscale ping stealthattack
tailscale ping squidstation

# View logs
sudo journalctl -u tailscaled -f
```

---

## 📊 DATA REFERENCE

### Ships Network IPs
```
SQUIDSTATION:
  Local IP: 192.168.0.39
  Tailscale IP: 100.83.247.14
  Docker Port: 2375

PINKCADY:
  Local IP: 192.168.0.3
  Tailscale IP: 100.106.235.103
  Docker Port: 2375

STEALTHATTACK:
  Local IP: 192.168.0.10
  Tailscale IP: 100.110.238.68
  Docker Port: 2375
```

### Kernel Parameters Optimal Values
```
vm.swappiness = 10 (was 60)
net.core.somaxconn = 32768 (was 128)
net.ipv4.tcp_max_syn_backlog = 32768 (was 256)
net.ipv4.ip_local_port_range = 1024 65535 (was 32768 61000)
```

### Container Memory Recommendations
```
Web Service: 512m
Database: 1-2g
Cache (Redis): 512m-1g
Message Queue: 256m
API Gateway: 256m
Worker: 256m-512m
```

### Docker Port Assignments
```
2375/2376: Docker API (HTTP/HTTPS)
8080-8099: Web services
9090: Prometheus
3000: Grafana
3100: Loki
5672: RabbitMQ
6379: Redis
5432: PostgreSQL
```

---

## 🔍 28 EDGE CASES QUICK LOOKUP

### Memory Pressure (4):
1. OOMKill without warning → Set memory-reservation
2. Swap thrashing → Set vm.swappiness=0
3. Cache bloat → `echo 3 | sudo tee /proc/sys/vm/drop_caches`
4. Memory leak → Lower limit to catch faster

### Networking (5):
1. No DNS resolution → Use custom network
2. Port conflicts → Use Tailscale IPs
3. DNS loops → Add --add-host workaround
4. Cross-ship routing → Use host network or overlay
5. Tailscale issues → Restart tailscaled

### Storage (5):
1. Root filesystem fills → Move /var/lib/docker
2. Dangling volumes → `docker volume prune -f`
3. Build cache huge → `docker builder prune -f`
4. Image bloat → Multi-stage builds
5. Driver slow → Migrate to overlay2

### Security (3):
1. TLS cert expires → Monitor with openssl
2. Privileged escape → Use --cap-drop/add
3. Secrets in image → Use docker secrets/env files

### Performance (3):
1. Kernel not tuned → Run sysctl commands
2. Default bridge slow → Create custom network
3. Storage driver old → Migrate to overlay2

### GPU (4):
1. CUDA mismatch → Use correct nvidia/cuda version
2. GPU memory full → Limit per container
3. Driver incompatible → Check matrix, update
4. GPU hangs system → Set timeout

### Mesh (3):
1. Connection flaps → Restart tailscaled
2. DNS not working → Enable MagicDNS
3. TLS mismatch → Use correct port/certs

---

## 📈 MONITORING COMMANDS

### Continuous Monitoring
```bash
# Watch all containers
docker stats

# Watch specific container
docker stats <container>

# Watch with no-stream (one snapshot)
docker stats --no-stream

# Watch memory specifically
watch -n 1 'free -h && docker ps --format "table {{.Names}}\t{{.MemoryUsage}}"'
```

### Regular Health Checks
```bash
# Check every ship
for ship in pinkcady squidstation stealthattack; do
  echo "=== $ship ==="
  tailscale ping $ship
  docker -H $ship:2375 ps --format "table {{.Names}}\t{{.Status}}"
done

# Check storage on all ships
for ship in pinkcady squidstation stealthattack; do
  echo "=== $ship ==="
  docker -H $ship:2375 system df
done
```

---

## 🎯 QUICK DECISION TREE

**Container keeps crashing?**
→ Check: `docker logs <container>`
→ Fix: Set memory limits (likely cause)

**Network slow?**
→ Check: `docker network inspect <network>`
→ Fix: Use custom network, optimize kernel

**Disk full?**
→ Check: `docker system df`
→ Fix: Remove dangling volumes/images

**GPU not working?**
→ Check: `docker run --gpus all nvidia/cuda:12.0-base nvidia-smi`
→ Fix: Install nvidia-docker2, check CUDA version

**Ships can't talk?**
→ Check: `tailscale ping <ship>`
→ Fix: Check Tailscale status, restart if needed

**System unresponsive?**
→ Check: `free -h && sysctl vm.swappiness`
→ Fix: Set swappiness to 0, reduce swap

---

## 📝 TEMPLATE SCRIPTS

### Mass Update Memory Limits
```bash
#!/bin/bash
LIMIT=${1:-512m}
RESERVATION=${2:-256m}

docker ps --format "{{.Names}}" | while read container; do
  echo "Updating $container: limit=$LIMIT, reservation=$RESERVATION"
  docker update -m $LIMIT --memory-reservation $RESERVATION "$container"
done

echo "Verification:"
docker ps --format "{{.Names}}" | while read container; do
  echo -n "$container: "
  docker inspect "$container" | grep '"Memory"' | head -1
done
```

### Cross-Ship Health Check
```bash
#!/bin/bash
SHIPS=("pinkcady" "squidstation" "stealthattack")

for ship in "${SHIPS[@]}"; do
  echo "=== $ship ==="
  tailscale ping "$ship" 2>&1 | grep -E "bytes|error"
  docker -H "$ship":2375 ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null
  docker -H "$ship":2375 system df 2>/dev/null | head -5
  echo ""
done
```

---

## 🚀 EXECUTION CHECKLIST

### Week 1 - CRITICAL (5 hours):
```
☐ Set PINKCADY memory limits (1h)
☐ Verify security status (30m)
☐ Check storage driver (30m)
☐ Monitor for issues (1h)
☐ Report status (1h)
```

### Week 2-4 - HIGH PRIORITY (10 hours):
```
☐ Optimize kernel parameters (1h)
☐ Unlock GPU (30m)
☐ Create custom networks (1h)
☐ Deploy monitoring (2h)
☐ Phase 1 verification (5.5h)
```

### Month 2-3 - PHASE 2:
```
☐ Build Obsidian vault (2h)
☐ Deploy advanced tools (4h)
☐ Enable health checks (2h)
☐ Integrate monitoring (4h)
```

---

✅ **All commands copy-paste ready**
✅ **All data current**
✅ **All edge cases mapped**
✅ **All solutions documented**

**Start with CRITICAL commands this week.**

⚓ 🚀
