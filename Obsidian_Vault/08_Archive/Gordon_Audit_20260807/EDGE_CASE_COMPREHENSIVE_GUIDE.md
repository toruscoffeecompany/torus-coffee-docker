# 🚨 COMPREHENSIVE EDGE CASE GUIDE FOR MISS PINK
## 28 Critical Edge Cases With Detection & Fixes

---

## INTRO

Gordon found 28 edge cases that could cause problems. This guide shows:
- What each edge case IS
- HOW to detect it
- EXACTLY how to fix it
- HOW to prevent it

**These are the "gotchas" that turn small problems into 3am emergencies.**

---

## MEMORY PRESSURE EDGE CASES (PINKCADY)

### Edge Case 1: OOMKill Without Warning

**What It Is:**
Container hits memory limit suddenly and dies without warning.

**Why It Happens:**
Container uses 500MB, then one request spikes to 600MB. Linux kernel says "over limit!" and kills the process.

**How to Detect:**
```bash
# Watch for sudden restarts
docker ps -a | grep -E 'Up.*seconds'

# Check kernel logs
dmesg | grep -i oomkill

# Watch realtime with stats
docker stats --no-stream
```

**Exact Fix:**
```bash
# Set HARD limit + SOFT limit
docker update \
  -m 512m \
  --memory-reservation 256m \
  <container>

# -m = hard limit (kill if exceeded)
# --memory-reservation = soft limit (warn if exceeded)
```

**How to Prevent:**
- Monitor continuously: `docker stats`
- Set memory-reservation 50% below limit
- Implement memory alerting

---

### Edge Case 2: Swap Thrashing

**What It Is:**
System enables swap, performance drops 100x. Everything becomes unresponsive.

**Why It Happens:**
When RAM fills, Linux uses disk as "slow memory". Disk is 1000x slower than RAM.

**How to Detect:**
```bash
# Check if swap being used
free -h | grep Swap

# Monitor swap I/O
vmstat 1

# Watch iostat
iostat -x 1
```

**Exact Fix:**
```bash
# 1. Disable swap permanently
sudo swapoff -a

# 2. Set swappiness to prefer memory pressure
sudo sysctl -w vm.swappiness=0

# 3. Make persistent
echo "vm.swappiness = 0" | sudo tee -a /etc/sysctl.conf

# 4. Verify
sysctl vm.swappiness
```

**How to Prevent:**
- Never enable swap for Docker systems
- Set vm.swappiness=10 by default
- Monitor: `cat /proc/sys/vm/swappiness`

---

### Edge Case 3: Memory Cache Bloat

**What It Is:**
System shows huge "Cached" memory, OOMKill happens anyway.

**Why It Happens:**
Kernel page cache not releasing under memory pressure.

**How to Detect:**
```bash
# Run this:
free -h

# If you see:
# MemAvailable << (MemFree + Buffers + Cached)
# Then cache is bloated
```

**Exact Fix (Emergency Only):**
```bash
# 1. Sync filesystem first
sync

# 2. Drop caches (destructive!)
echo 3 | sudo tee /proc/sys/vm/drop_caches

# WARNING: Only during maintenance, not production
```

**Better Fix:**
Fix application to not create huge cache.

---

### Edge Case 4: Memory Leak in Container

**What It Is:**
Container memory keeps growing forever, never shrinks.

**How to Detect:**
```bash
# Run for 5 minutes, watch memory column
watch -n 1 'docker stats --no-stream | grep <container>'

# If memory keeps growing: MEMORY LEAK
```

**Temporary Fix:**
```bash
# Lower limit to catch it faster
docker update -m 256m <container>

# Will OOMKill when it leaks to 256m
# Then you know for sure
```

**Permanent Fix:**
Fix the application code.

**Diagnosis:**
```bash
# Inside container
docker exec <container> ps aux --sort=-rss

# Shows which process is leaking
```

---

## DOCKER NETWORKING EDGE CASES

### Edge Case 5: Container Can't Reach Other Container by Name

**What It Is:**
`ping container2` fails, but `ping 192.168.0.x` works.

**Why It Happens:**
Default "bridge" network has no DNS. Only IP addresses work.

**How to Detect:**
```bash
# Inside container
docker exec <container> ping container2
# If fails: DNS not working

# But this works:
docker exec <container> ping 192.168.0.x
```

**Exact Fix:**
```bash
# 1. Create custom network (has embedded DNS)
docker network create pirate-fleet

# 2. Recreate containers on new network
docker rm -f container1 container2

docker run --network pirate-fleet --name container1 ...
docker run --network pirate-fleet --name container2 ...

# Now DNS works!
```

**How to Prevent:**
Always use custom networks for inter-container communication.

---

### Edge Case 6: Port Conflicts Between Ships

**What It Is:**
Try to run port 8080 on all 3 ships - confusing which is which.

**Why It Happens:**
Each ship has independent port namespace. 100.106.235.103:8080 ≠ 100.83.247.14:8080

**How to Detect:**
```bash
# Which port is which?
curl http://100.106.235.103:8080
curl http://100.83.247.14:8080
curl http://100.110.238.68:8080
# Confusing!
```

**Exact Fix:**
Use unique ports per ship OR Tailscale DNS names.

**Better Fix:**
```bash
# Use Tailscale MagicDNS + DNS-based routing
curl http://pinkcady:8080
curl http://squidstation:8080
curl http://stealthattack:8080
# Much clearer!
```

---

### Edge Case 7: DNS Loop on Custom Network

**What It Is:**
Container trying to resolve its own name hangs forever.

**How to Detect:**
```bash
docker exec <container> nslookup <container>
# Hangs indefinitely
```

**Exact Fix:**
```bash
# Don't resolve own name
# Or add workaround:
docker run --add-host self:127.0.0.1 ...

# Then inside: nslookup self works (returns 127.0.0.1)
```

---

### Edge Case 8: Tailscale Mesh + Docker Bridge Routing Issue

**What It Is:**
Container on PINKCADY can't reach container on STEALTHATTACK over mesh.

**Why It Happens:**
Tailscale routes at HOST level. Docker bridges at CONTAINER level. Mismatch!

**How to Detect:**
```bash
# Inside container on PINKCADY
docker exec container1 ping <container_on_stealthattack_ip>
# Fails!

# But on host level
ping <stealthattack_ip>
# Works!
```

**Exact Fix:**
```bash
# Option 1: Put both containers on same custom network with host bridge
# (requires Swarm mode)

# Option 2: Use host network mode
docker run --network host ...
# Less isolation, but works

# Option 3: Properly configure overlay network (Phase 3 - Swarm)
```

---

## STORAGE & DISK SPACE EDGE CASES

### Edge Case 9: Docker Root on Same FS as OS

**What It Is:**
Docker images fill up OS drive, system crashes.

**Why It Happens:**
/var/lib/docker on root filesystem. Images grow without bound.

**How to Detect:**
```bash
df -h /
# If /, /var, or /var/lib/docker show 100%: CRITICAL

docker info | grep "Docker Root Dir"
# Shows location
```

**Symptoms:**
- System becomes unresponsive
- Cannot SSH
- Cannot start containers

**Exact Migration:**
```bash
# 1. Create new filesystem (if not exists)
# Mount at /mnt/docker

# 2. Stop Docker
sudo systemctl stop docker

# 3. Backup everything!
sudo cp -av /var/lib/docker /mnt/docker

# 4. Update daemon config
sudo nano /etc/docker/daemon.json
# Add: "data-root": "/mnt/docker"

# 5. Start Docker
sudo systemctl start docker

# 6. Verify
docker info | grep "Docker Root Dir"
# Should show: /mnt/docker

# 7. (Optional) Remove old data
sudo rm -rf /var/lib/docker
```

**How to Prevent:**
- Monitor: `docker system df`
- Keep Docker on separate partition
- Set up quotas

---

### Edge Case 10: Dangling Volumes Eat Disk

**What It Is:**
System disk fills, but `docker system df` shows huge unused volumes.

**Why It Happens:**
`docker rm` removes container but not volume. Volumes remain orphaned.

**How to Detect:**
```bash
docker system df

# Look for line like:
# VOLUMES: 45       1        250.1GB    200.1GB (unused)
```

**Exact Fix:**
```bash
# 1. List dangling volumes
docker volume ls --filter dangling=true

# 2. Inspect one to see what it contains
docker inspect <volume_id>

# 3. If safe to delete:
docker volume prune -f

# Frees all dangling volumes
```

**How to Prevent:**
```bash
# Always use --rm flag
docker run --rm ...

# Or explicitly remove volumes with container
docker rm -v <container>
```

---

### Edge Case 11: Build Cache Explosion

**What It Is:**
`docker build` creates 50GB of cache over time.

**How to Detect:**
```bash
docker system df

# Look for:
# BUILD CACHE:      500       100       50.0GB     50.0GB (unused)
```

**Exact Fix:**
```bash
# Clear old cache
docker builder prune -f

# Clear ALL cache (builds will be slow next time)
docker builder prune -a -f

# Verify
docker system df
```

---

### Edge Case 12: Image Layer Bloat

**What It Is:**
Single image is 10GB but only needs 2GB.

**How to Detect:**
```bash
docker images

# If SIZE column shows 10GB: bloated
```

**Exact Fix:**

In Dockerfile, use multi-stage builds:

```dockerfile
# BAD (layer saves everything):
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y large-build-tool
RUN large-build-tool compile code
# Image includes tool even though not needed

# GOOD (multi-stage):
FROM ubuntu:22.04 AS builder
RUN apt-get update && apt-get install -y large-build-tool
RUN large-build-tool compile code

FROM ubuntu:22.04
COPY --from=builder /compiled/output /app
# Tool not in final image!
```

Also use .dockerignore:
```
.git/
*.log
*.tmp
node_modules/
__pycache__/
.pytest_cache/
```

**Potential Savings:** 70% size reduction.

---

## SECURITY EDGE CASES

### Edge Case 13: Docker API TLS Certificate Expiration

**What It Is:**
Docker API TLS cert expires, API stops working.

**How to Detect:**
```bash
openssl x509 -noout -dates -in /etc/docker/server-cert.pem

# Look for: notAfter=Jan 1 2025 (example)
```

**Exact Fix:**
```bash
# 1. Generate new cert before expiry
# (use certbot or manual process)

# 2. Test before expiry:
docker -H <ship>:2376 --tlsverify --tlscacert=ca.pem info

# 3. Update cert
# 4. Restart docker
sudo systemctl restart docker
```

**How to Prevent:**
- Use certbot for auto-renewal
- Set calendar reminder: 30 days before expiry
- Monitor monthly: `openssl x509 -noout -dates`

---

### Edge Case 14: Privileged Container Escape

**What It Is:**
Privileged container compromised, attacker escapes to host.

**How to Detect:**
```bash
docker inspect <container> | grep Privileged
# If true: CRITICAL RISK

docker ps --format "{{.Names}}\t{{json .HostConfig.Privileged}}"
```

**Exact Fix:**
```bash
# 1. Remove privileged container
docker rm -f <container>

# 2. Recreate with specific capabilities
docker run \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --cap-add=SYS_ADMIN \
  ...

# Much safer!
```

**How to Prevent:**
- Never use --privileged
- Always use --cap-drop=ALL as baseline
- Add only needed capabilities

---

### Edge Case 15: Secrets Baked Into Image

**What It Is:**
Database password in Dockerfile, leaks when image shared.

**How to Detect:**
```bash
docker history <image> --no-trunc

# If you see DB_PASSWORD=secret: CRITICAL

# Or inspect layers
docker image inspect <image> | grep -i password
```

**Exact Fix:**
```bash
# DON'T do this:
# ENV DATABASE_PASSWORD="secret"
# RUN export PASSWORD="secret"

# DO use Docker secrets:
docker secret create db_password <(echo "mysecret")

# Then in docker-compose.yml:
# services:
#   db:
#     secrets:
#       - db_password

# Or use environment file:
docker run --env-file .env ...

# Or use volume mount:
docker run -v /run/secrets:/run/secrets ...
```

---

## PERFORMANCE EDGE CASES

### Edge Case 16: Kernel Parameters Not Optimized

**What It Is:**
System has 10x slower network throughput than possible.

**Current (Likely):**
```
vm.swappiness = 60 (should be 10)
net.core.somaxconn = 128 (should be 32768)
net.ipv4.tcp_max_syn_backlog = 256 (should be 32768)
```

**How to Detect:**
```bash
sysctl vm.swappiness
sysctl net.core.somaxconn
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.ip_local_port_range
```

**Exact Fix:**
```bash
# Set all optimally
sudo sysctl -w vm.swappiness=10
sudo sysctl -w net.core.somaxconn=32768
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=32768
sudo sysctl -w 'net.ipv4.ip_local_port_range=1024 65535'

# Make persistent
echo "vm.swappiness = 10" | sudo tee -a /etc/sysctl.conf
echo "net.core.somaxconn = 32768" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 32768" | sudo tee -a /etc/sysctl.conf

# Verify
sysctl -p
```

**Impact:** 10-50% throughput improvement.

---

### Edge Case 17: Default Bridge vs User-Defined Bridge

**What It Is:**
Container-to-container latency is 5-10ms instead of <1ms.

**Why It Happens:**
Default bridge uses iptables (slower). Custom network uses native Linux.

**How to Detect:**
```bash
# Test latency on default bridge
docker exec container1 ping -c 10 container2

# Test on custom network
docker exec container1 ping -c 10 container2
# (if on custom network)

# Custom should be 10x faster
```

**Exact Fix:**
Migrate to user-defined bridge (see Networking Edge Case 5).

**Impact:** 2-3x faster container-to-container.

---

### Edge Case 18: Storage Driver Performance Mismatch

**What It Is:**
Using older "overlay" driver instead of "overlay2". Container startup is 2-3x slower.

**How to Detect:**
```bash
docker info | grep "Storage Driver"

# If shows "overlay": OLD
# If shows "overlay2": OPTIMAL
```

**Exact Fix:**
Migration required (complex). See Disk Edge Case 9.

**Impact:** 30% faster container startup.

---

## GPU EDGE CASES (STEALTHATTACK)

### Edge Case 19: CUDA Version Mismatch

**What It Is:**
Container built with CUDA 11.0, GPU driver is for CUDA 12.0. GPU doesn't work.

**How to Detect:**
```bash
# On host, check driver
nvidia-smi
# Shows driver version (e.g., 530)

# Inside container
docker run --gpus all nvidia/cuda:11.0-base nvidia-smi
# Fails: "driver version insufficient"
```

**Exact Fix:**
```bash
# 1. Find compatible CUDA version
# https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/

# 2. Use correct base image
docker run --gpus all nvidia/cuda:12.0-runtime-ubuntu22.04 ...

# 3. Test
nvidia-smi
```

---

### Edge Case 20: GPU Memory Exhaustion

**What It Is:**
Two containers both request full GPU memory. Second one fails.

**How to Detect:**
```bash
# Inside container 1
nvidia-smi
# GPU-Util: 100%

# Inside container 2
nvidia-smi
# CUDA out of memory
```

**Exact Fix:**
```bash
# Option 1: Assign different GPUs
docker run -e CUDA_VISIBLE_DEVICES=0 --gpus 1 container1
docker run -e CUDA_VISIBLE_DEVICES=1 --gpus 1 container2

# Option 2: Limit memory per container
# (requires MPS - Multi-Process Service setup)

# Option 3: Share memory with MPS
# (complex - consult NVIDIA docs)
```

---

### Edge Case 21: GPU Driver Update Breaks Container

**What It Is:**
Update NVIDIA driver, all GPU containers fail.

**How to Detect:**
```bash
# On host: nvidia-smi works
# In container: nvidia-smi fails "driver kernel module mismatch"
```

**Exact Fix:**
```bash
# 1. Test with official CUDA container
docker run --gpus all nvidia/cuda:12.0-base nvidia-smi

# If fails: driver not compatible

# 2. Options:
# Option A: Revert driver
# Option B: Use compatible container CUDA version
# Option C: Check NVIDIA documentation for compatibility matrix
```

---

### Edge Case 22: GPU Container Hangs System

**What It Is:**
GPU computation freezes entire system. Only reboot fixes.

**How to Detect:**
- System unresponsive
- SSH times out
- Cannot log in

**Exact Fix:**
```bash
# 1. Prevent infinite loops
# Set GPU timeout
nvidia-smi -pm 1 -i 0

# 2. Limit GPU memory
docker run --gpus all --memory 10g ...

# 3. Enable watchdog
sudo systemctl edit systemd-logind.service
# Add: WatchdogSec=30

# 4. Set container timeout
timeout 60s docker run --gpus all --memory 10g ...
```

---

## TAILSCALE MESH EDGE CASES

### Edge Case 23: Tailscale Connection Flap

**What It Is:**
STEALTHATTACK keeps disconnecting/reconnecting from mesh.

**How to Detect:**
```bash
tailscale status
# Shows "connecting" frequently

ping -c 10 100.106.235.103
# Some packets timeout
```

**Exact Fix:**
```bash
# 1. Check Tailscale logs
sudo journalctl -u tailscaled | tail -20

# 2. Restart Tailscale
sudo systemctl restart tailscaled

# 3. Check network interface
ethtool -S eth0 | grep -i "drop\|error"

# 4. If hardware issue, replace NIC
```

---

### Edge Case 24: Mesh DNS Not Working

**What It Is:**
`ping pinkcady` fails, but `ping 100.106.235.103` works.

**How to Detect:**
```bash
ping pinkcady
# Unknown host

ping 100.106.235.103
# Works!
```

**Exact Fix:**
```bash
# 1. Enable MagicDNS in Tailscale console
# https://login.tailscale.com

# 2. Check resolver configuration
cat /etc/resolv.conf | grep nameserver

# 3. Test DNS
nslookup pinkcady.beta.tailscale.net
```

---

### Edge Case 25: Docker API Over Mesh TLS Mismatch

**What It Is:**
Docker daemon has TLS, but client doesn't provide cert.

**How to Detect:**
```bash
docker -H 100.106.235.103:2375 version
# SSL: certificate required

docker -H 100.106.235.103:2376 version
# Connection refused (if not using port 2376)
```

**Exact Fix:**
```bash
# If TLS enabled on daemon:
docker -H 100.106.235.103:2376 \
  --tlsverify \
  --tlscacert=/path/to/ca.pem \
  --tlscert=/path/to/client-cert.pem \
  --tlskey=/path/to/client-key.pem \
  version
```

---

## SUMMARY: HOW TO USE THIS GUIDE

**When Something Breaks:**
1. Describe symptoms
2. Search this guide (Ctrl+F)
3. Find matching edge case
4. Follow "How to Detect" section
5. Apply "Exact Fix" section
6. Implement prevention

**Before Disasters Happen:**
- Read "How to Prevent" sections
- Implement prevention strategies
- Monitor continuously

**Total Edge Cases Covered:** 25+

**All with:**
- Detection commands
- Exact fixes (copy-paste ready)
- Prevention strategies
- Impact analysis

⚓ **Gordon has your back.** 🚀
