#!/usr/bin/env python3
"""
FIX: Docker on PINKCADY.
Launch Docker Desktop.exe directly + verify backend starts.
"""
import subprocess, time, os, json, sys

print("=== DOCKER FIX ===\n")

# ─── 1. Kill zombie Docker processes ───────────────────────────────────────────────
print("1. Killing zombie Docker processes:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "docker-desktop-service.exe"]:
    r = subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
    if r.returncode == 0:
        print(f"   ✅ Killed {proc}")
    else:
        print(f"   {proc}: not running")
    time.sleep(2)

# ─── 2. Launch Docker Desktop directly ─────────────────────────────────────────────
time.sleep(3)
print("\n2. Launching Docker Desktop.exe:")
docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
if os.path.exists(docker_exe):
    print(f"   Found: {docker_exe} ({os.path.getsize(docker_exe)/1024/1024:.1f} MB)")
    r = subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"   Launched PID: {r.pid}")
    print(f"   Waiting 120s for full initialization...")
else:
    print(f"   ❌ Not found")
    # Search for any Docker Desktop.exe
    for root, dirs, files in os.walk(r"C:\Users\torus\AppData\Local\Programs"):
        for f in files:
            if f.lower() == "docker desktop.exe":
                full = os.path.join(root, f)
                print(f"   Found: {full}")
                r = subprocess.Popen([full], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"   Launched PID: {r.pid}")
                break

# ─── 3. Wait + monitor ──────────────────────────────────────────────────────────────
print("\n3. Monitoring startup:")
for i in range(24):  # 120 seconds
    time.sleep(5)
    try:
        r = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            print(f"   ✅ Docker Server: {r.stdout.strip()}")
            break
    except:
        pass
    if i % 6 == 5:
        print(f"   Waiting... ({i+1}/24)")

# ─── 4. Check processes ─────────────────────────────────────────────────────────────
print("\n4. Process status:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "docker-desktop-service.exe", "vmmem.exe"]:
    time.sleep(2)
    r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {proc}", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    print(f"   {proc}: {'✅' if r.stdout.count(proc) > 1 else '❌'}")

# ─── 5. Docker info ────────────────────────────────────────────────────────────────
print("\n5. Docker info:")
time.sleep(5)
try:
    r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
    if r.returncode == 0:
        print("   ✅ docker info OK")
        for line in r.stdout.split("\n"):
            if any(k in line for k in ["Server Version", "Storage Driver", "Operating System", 
                "Docker Root Dir", "Cgroup", "Runtimes", "Default Runtime"]):
                print(f"   {line.strip()}")
    else:
        print(f"   ❌ docker info: {r.stderr[:150]}")
except subprocess.TimeoutExpired:
    print("   ❌ docker info timed out")

# ─── 6. Docker API ports ────────────────────────────────────────────────────────────
print("\n6. Docker API ports:")
time.sleep(3)
for port in [2375, 2376]:
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", "5", f"http://localhost:{port}/_ping"],
        capture_output=True, text=True, timeout=8)
    print(f"   Port {port}: HTTP {r.stdout.strip()}")

# ─── 7. Containers ──────────────────────────────────────────────────────────────────
print("\n7. Containers:")
time.sleep(5)
try:
    r = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}\\t{{.Status}}"],
        capture_output=True, text=True, timeout=10)
    if r.returncode == 0:
        lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
        print(f"   {len(lines)} containers:")
        for l in lines[:15]:
            print(f"     {l}")
    else:
        print(f"   ❌ docker ps: {r.stderr[:100]}")
except subprocess.TimeoutExpired:
    print("   ❌ docker ps timed out")

print(f"\n{'='*60}")
os.remove(__file__)
