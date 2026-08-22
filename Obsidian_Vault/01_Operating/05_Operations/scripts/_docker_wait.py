#!/usr/bin/env python3
"""Wait for Docker Desktop to fully initialize + verify."""
import subprocess, time, os

print("=== DOCKER INITIALIZATION WAIT ===\n")

# Poll for dockerd + com.docker.proxy
for i in range(20):  # 100 seconds
    time.sleep(5)
    
    # Check dockerd
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq dockerd.exe", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    dockerd_running = r.stdout.count("dockerd") > 1
    
    # Check com.docker.proxy
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq com.docker.proxy.exe", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    proxy_running = r.stdout.count("com.docker.proxy") > 1
    
    # Check docker info (shorter timeout)
    r = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"],
        capture_output=True, text=True, timeout=5)
    docker_ok = r.returncode == 0 and r.stdout.strip()
    
    status = []
    status.append(f"dockerd: {'✅' if dockerd_running else '❌'}")
    status.append(f"proxy: {'✅' if proxy_running else '❌'}")
    status.append(f"api: {'✅' if docker_ok else '❌'}")
    
    print(f"  [{i+1}/20] {' | '.join(status)}", flush=True)
    
    if docker_ok:
        print(f"\n  ✅ Docker Server: {r.stdout.strip()}")
        break
    
    # Also check if Docker Desktop is still running
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Docker Desktop.exe", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    if r.stdout.count("Docker Desktop") <= 1:
        print(f"\n  ❌ Docker Desktop.exe crashed/stopped!")
        break

# ─── Final verification ───────────────────────────────────────────────────────────
print("\n=== FINAL DOCKER STATUS ===")
time.sleep(3)

# Docker info
r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
if r.returncode == 0:
    print("✅ docker info: OK")
    for line in r.stdout.split("\n"):
        if any(k in line for k in ["Server Version", "Storage Driver", "Operating System", "Docker Root Dir", "Cgroup", "Name", "Live Restore"]):
            print(f"  {line.strip()}")
    
    # Containers
    time.sleep(3)
    r = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}\\t{{.Status}}"],
        capture_output=True, text=True, timeout=10)
    lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
    print(f"\n📦 Containers ({len(lines)}):")
    for l in lines[:20]:
        print(f"  {l}")
else:
    print(f"❌ docker info: {r.stderr[:150]}")

# Docker API ports
time.sleep(3)
for port in [2375, 2376]:
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", "3", f"http://localhost:{port}/_ping"],
        capture_output=True, text=True, timeout=5)
    print(f"\nPort {port}: HTTP {r.stdout.strip()}")

print(f"\n{'='*60}")
os.remove(__file__)
