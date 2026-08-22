#!/usr/bin/env python3
"""Check Docker Desktop status after launch."""
import subprocess, time, os

print("=== DOCKER STATUS CHECK ===\n")

# Check if Docker Desktop.exe is still running
time.sleep(3)
r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Docker Desktop.exe", "/V", "/FO", "CSV"],
    capture_output=True, text=True, timeout=10)
print(f"Docker Desktop.exe: {'✅ running' if r.stdout.count('Docker Desktop') > 1 else '❌'}")

# Check dockerd
time.sleep(3)
r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq dockerd.exe", "/FO", "CSV"],
    capture_output=True, text=True, timeout=10)
print(f"dockerd.exe: {'✅ running' if r.stdout.count('dockerd') > 1 else '❌'}")

# Check com.docker.proxy
time.sleep(3)
r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq com.docker.proxy.exe", "/FO", "CSV"],
    capture_output=True, text=True, timeout=10)
print(f"com.docker.proxy.exe: {'✅ running' if r.stdout.count('com.docker.proxy') > 1 else '❌'}")

# Check if Docker API responds
time.sleep(5)
r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=15)
if r.returncode == 0:
    print(f"\n✅ Docker API responding!")
    for line in r.stdout.split("\n"):
        if any(k in line for k in ["Server Version", "Storage Driver", "Operating System", "Docker Root Dir", "Cgroup", "Runtimes"]):
            print(f"  {line.strip()}")
    
    # Check containers
    time.sleep(3)
    r = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}\\t{{.Status}}"],
        capture_output=True, text=True, timeout=10)
    lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
    print(f"\n   Containers ({len(lines)}):")
    for l in lines[:20]:
        print(f"     {l}")
else:
    print(f"\n❌ Docker API not responding: {r.stderr[:150]}")
    print("   Docker Desktop.exe is still initializing...")

# Check Docker API ports
time.sleep(3)
for port in [2375, 2376]:
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", "3", f"http://localhost:{port}/_ping"],
        capture_output=True, text=True, timeout=5)
    print(f"   Port {port}: HTTP {r.stdout.strip()}")

print(f"\n{'='*60}")
os.remove(__file__)
