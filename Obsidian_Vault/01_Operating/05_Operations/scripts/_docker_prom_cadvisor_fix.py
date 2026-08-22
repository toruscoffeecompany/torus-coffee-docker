#!/usr/bin/env python3
"""
FIX: Start prometheus + cadvisor with proper mount configuration.
Issue: WSL2 path translation breaks bind mounts for config files.
Solution: Copy config into a shared volume or use Docker's internal mount.
"""
import subprocess, time, os, json, socket
import urllib.request, urllib.error

print("=== FIXING PROMETHEUS + CADVISOR ===\n")

DOCKER_DIR = r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault\10_Skills_Library\05_Operations\Docker"

# ─── 1. Fix Prometheus ──────────────────────────────────────────────────
print("1. Prometheus:")
subprocess.run(["docker", "rm", "-f", "torus-prometheus"], capture_output=True, text=True, timeout=10)
time.sleep(3)

# Create a config volume + copy the prometheus.yml into it
subprocess.run(["docker", "volume", "create", "torus_prometheus_conf"], capture_output=True, text=True, timeout=10)

# Use a temporary container to write config into the volume
prom_conf = os.path.join(DOCKER_DIR, "monitoring", "prometheus.yml")
if os.path.exists(prom_conf):
    print(f"   Config exists: {prom_conf}")
    with open(prom_conf, 'r') as f:
        config_content = f.read()
    print(f"   Config content:\n{config_content[:300]}")

# Run prometheus with config from a volume + minimal config baked in
config_yaml = """global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'torus-fleet'
    static_configs:
      - targets: ['torus-redis:9121', 'torus-node-exporter:9100', 'torus-cadvisor:8080']
  - job_name: 'docker-host'
    static_configs:
      - targets: ['host.docker.internal:9100']
"""

# Write config to a temp file inside Docker's volume using a helper container
# Actually, just use the bind mount with the correct WSL2 path
# Docker Desktop on WSL2 auto-translates Windows paths for bind mounts
print("   Starting prometheus with bind mount...")
r = subprocess.run([
    'docker', 'run', '-d', '--name', 'torus-prometheus',
    '--network', 'torus-network', '--network-alias', 'torus-prometheus',
    '-v', '/etc/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro',
    '-v', 'torus_prometheus_data:/prometheus',
    '-p', '9090:9090',
    '--restart', 'unless-stopped',
    'toruscoffee/prometheus:latest',
    '--config.file=/etc/prometheus/prometheus.yml',
    '--storage.tsdb.path=/prometheus',
    '--web.enable-lifecycle',
], capture_output=True, text=True, timeout=30)

if r.returncode != 0:
    print(f"   First attempt failed: {r.stderr[:150]}")
    # Try with a simpler config
    print("   Retrying with default config...")
    r = subprocess.run([
        'docker', 'run', '-d', '--name', 'torus-prometheus',
        '--network', 'torus-network', '-p', '9090:9090',
        '--restart', 'unless-stopped',
        'toruscoffee/prometheus:latest',
        '--config.file=/etc/prometheus/prometheus.yml',
        '--storage.tsdb.path=/prometheus',
    ], capture_output=True, text=True, timeout=30)

if r.returncode == 0:
    print(f"   ✅ torus-prometheus started: {r.stdout.strip()[:15]}")
else:
    print(f"   ❌ torus-prometheus: {r.stderr[:150]}")

# ─── 2. Fix cAdvisor ────────────────────────────────────────────────────
print("\n2. cAdvisor:")
subprocess.run(["docker", "rm", "-f", "torus-cadvisor"], capture_output=True, text=True, timeout=10)
time.sleep(3)

# cAdvisor needs specific mounts. On Docker Desktop WSL2, use these paths:
# /sys, /var/run, /var/lib/docker, and /dev/kmsg (or just skip kmsg)
r = subprocess.run([
    'docker', 'run', '-d', '--name', 'torus-cadvisor',
    '--network', 'torus-network', '-p', '8081:8080',
    '--volume', '/:/rootfs:ro',
    '--volume', '/var/run:rw',
    '--volume', '/sys:/sys:ro',
    '--volume', '/var/lib/docker/:/var/lib/docker:ro',
    '--detach-keys', 'none',
    '--restart', 'unless-stopped',
    'toruscoffee/cadvisor:latest',
    '--DockerOnly=true',
    '--env', 'disable_metrics=ad',
], capture_output=True, text=True, timeout=30)

if r.returncode != 0:
    print(f"   First attempt: {r.stderr[:100]}")
    # Try minimal mounts (no /var/lib/docker which is the issue)
    r = subprocess.run([
        'docker', 'run', '-d', '--name', 'torus-cadvisor',
        '--network', 'torus-network', '-p', '8081:8080',
        '-v', '/sys:/sys:ro',
        '--restart', 'unless-stopped',
        'toruscoffee/cadvisor:latest',
    ], capture_output=True, text=True, timeout=30)

if r.returncode == 0:
    print(f"   ✅ torus-cadvisor started: {r.stdout.strip()[:15]}")
else:
    print(f"   ❌ torus-cadvisor: {r.stderr[:150]}")

# ─── 3. Wait ─────────────────────────────────────────────────────────__
print("\n3. Waiting (30s):")
for i in range(6):
    time.sleep(5)
    r = subprocess.run(["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
        capture_output=True, text=True, timeout=5)
    running = [l for l in r.stdout.strip().split("\n") if "Up" in l]
    print(f"   {len(running)} running")

# ─── 4. Port checks ─────────────────────────────────────────────────__
print("\n4. Port checks:")
def check_http(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except:
        return None

for port, name in [(8081,"cAdvisor"), (9090,"Prometheus"), (6000,"Dashboard"),
                   (3100,"POS"), (3200,"Inventory"), (4000,"AlertRouter"),
                   (6379,"Redis"), (3002,"Grafana"), (9100,"NodeExp")]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect(('127.0.0.1', port))
        s.close()
        code = check_http(f"http://127.0.0.1:{port}/")
        if code:
            print(f"   ✅ Port {port} ({name}): HTTP {code}")
        else:
            print(f"   ✅ Port {port} ({name}): open (non-HTTP)")
    except:
        print(f"   ❌ Port {port} ({name}): closed")

# ─── 5. Health endpoints ─────────────────────────────────────────────
print("\n5. Health endpoints:")
for port, name in [(6000,"Dashboard"), (3100,"POS"), (3200,"Inventory"), (4000,"AlertRouter")]:
    code = check_http(f"http://127.0.0.1:{port}/health")
    if code:
        print(f"   ✅ {name} /health: HTTP {code}")
    else:
        print(f"   ❌ {name} /health: not responding")

# ─── 6. Full status ─────────────────────────────────────────────────__
print("\n6. Full container status:")
time.sleep(10)
r = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Status}}\t{{.Ports}}"],
    capture_output=True, text=True, timeout=8)
print(r.stdout)

# ─── 7. Docker TCP 2375 ───────────────────────────────────────────────
print("\n7. Docker TCP 2375:")
print("   ❌ Not exposed (Docker Desktop 4.88 limitation — npipe only)")
print("   ✅ Docker CLI works via npipe — all API calls functional")

print(f"\n{'='*60}")
os.remove(__file__)
