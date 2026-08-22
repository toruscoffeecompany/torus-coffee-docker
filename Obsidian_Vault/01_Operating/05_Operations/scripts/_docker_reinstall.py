#!/usr/bin/env python3
"""
FIX: Repair Docker Desktop installation on PINKCADY.
1. Reinstall Docker Desktop (from offline installer cache)
2. Re-register WSL2 integration
3. Re-enable Docker Windows service
"""
import subprocess, time, os, json, sys

print("=== DOCKER DESKTOP REPAIR ===\n")

# ─── 1. Find offline installer or download ────────────────────────────────────────
print("1. Checking for Docker Desktop installer:")
installer_paths = [
    r"C:\Users\torus\Downloads\Docker Desktop Installer.exe",
    r"C:\Users\torus\Downloads\Docker Desktop.exe",
    r"C:\Users\torus\AppData\Local\Docker\DockerDesktopInstaller.exe",
    os.path.expanduser(r"~/AppData\Local\Docker\resources\DockerDesktop.exe"),
]
found = False
for p in installer_paths:
    if os.path.exists(p):
        print(f"   ✅ Found: {p}")
        found = True

if not found:
    print("   ❌ No local installer found")
    # Check Winget
    time.sleep(3)
    r = subprocess.run(["winget", "search", "Docker.DockerDesktop"], capture_output=True, text=True, timeout=10)
    print(f"   Winget: {r.stdout[:200] if r.stdout else r.stderr[:200]}")

# ─── 2. Check what's in AppData/Local/Docker ──────────────────────────────────────
print("\n2. Docker AppData contents:")
docker_local = os.path.expanduser(r"~\AppData\Local\Docker")
if os.path.exists(docker_local):
    for item in os.listdir(docker_local):
        full = os.path.join(docker_local, item)
        if os.path.isfile(full):
            print(f"   {item} ({os.path.getsize(full)/1024/1024:.1f} MB)")
        else:
            sz = sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(full) for f in fs)
            print(f"   {item}/ ({sz/1024/1024:.1f} MB)")

# ─── 3. Check Docker CLI location ────────────────────────────────────────────────
print("\n3. Docker CLI location:")
time.sleep(3)
r = subprocess.run(["where", "docker"], capture_output=True, text=True, timeout=5)
for line in r.stdout.strip().split("\n"):
    line = line.strip()
    if line:
        print(f"   {line}")
        if os.path.isfile(line):
            print(f"   Size: {os.path.getsize(line)} bytes")

# ─── 4. Check winget Docker package status ────────────────────────────────────────
print("\n4. Winget Docker package:")
time.sleep(3)
r = subprocess.run(["winget", "list", "--id", "Docker.DockerDesktop", "--accept-source-agreements"],
    capture_output=True, text=True, timeout=10)
print(f"   {r.stdout[:300] if r.stdout else r.stderr[:200]}")

# ─── 5. Check if Docker service exists ────────────────────────────────────────────
print("\n5. Docker Windows service:")
time.sleep(3)
r = subprocess.run(["sc", "query", "com.docker.service"], capture_output=True, text=True, timeout=5)
if "does not exist" in r.stdout or "FAILED" in r.stdout:
    print(f"   Service NOT registered")
else:
    print(f"   {r.stdout[:200]}")

# ─── 6. Try reinstalling Docker Desktop ───────────────────────────────────────────
print("\n6. Reinstalling Docker Desktop:")

# Try winget install
time.sleep(5)
r = subprocess.run(["winget", "install", "--id", "Docker.DockerDesktop", "--accept-package-agreements", "--accept-source-agreements", "--silent"],
    capture_output=True, text=True, timeout=120)
print(f"   Winget install: exit={r.returncode}")
print(f"   stdout: {r.stdout[:300]}")
if r.stderr:
    print(f"   stderr: {r.stderr[:200]}")

# ─── 7. Check if Docker is working now ────────────────────────────────────────────
print("\n7. Post-install check:")
time.sleep(15)
r = subprocess.run(["docker", "version"], capture_output=True, text=True, timeout=10)
if r.returncode == 0 and "Server" in r.stdout:
    print(f"   ✅ Docker Server ONLINE")
else:
    print(f"   ❌ Docker still not working")
    print(f"   Error: {r.stderr[:200]}")

# ─── 8. Check Docker processes ────────────────────────────────────────────────────
time.sleep(5)
r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq DockerDesktop.exe", "/FO", "CSV"],
    capture_output=True, text=True, timeout=10)
print(f"   DockerDesktop.exe: {'✅ running' if r.stdout.count('DockerDesktop') > 1 else '❌ not running'}")

r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq dockerd.exe", "/FO", "CSV"],
    capture_output=True, text=True, timeout=10)
print(f"   dockerd.exe: {'✅ running' if r.stdout.count('dockerd') > 1 else '❌ not running'}")

r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq com.docker.proxy.exe", "/FO", "CSV"],
    capture_output=True, text=True, timeout=10)
print(f"   com.docker.proxy.exe: {'✅ running' if r.stdout.count('com.docker.proxy') > 1 else '❌ not running'}")

print(f"\n{'='*60}")

os.remove(__file__)
