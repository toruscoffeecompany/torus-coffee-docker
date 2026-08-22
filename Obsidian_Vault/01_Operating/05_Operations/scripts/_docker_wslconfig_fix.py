#!/usr/bin/env python3
"""
FIX: Docker Desktop WSL2 resource error 0x800705aa.
1. Set WSL2 memory limits in .wslconfig
2. Shutdown WSL2 service to apply changes
3. Restart Docker Desktop
"""
import subprocess, time, os, json

print("=== DOCKER FIX: WSL2 RESOURCE LIMITS ===\n")

# ─── 1. Write .wslconfig ────────────────────────────────────────────────────────────
print("1. Writing .wslconfig with WSL2 resource limits:")
wslconfig = """[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true
"""
wslconfig_path = r"C:\Users\torus\.wslconfig"
with open(wslconfig_path, 'w') as f:
    f.write(wslconfig)
print(f"   ✅ Written: {wslconfig_path}")
print(f"   Content: {wslconfig.strip()}")

# Also write to Docker data dir
docker_wslconfig = r"C:\Users\torus\AppData\Local\Docker\wsl\config\.wslconfig"
docker_wslconfig_dir = os.path.dirname(docker_wslconfig)
if not os.path.exists(docker_wslconfig_dir):
    os.makedirs(docker_wslconfig_dir)
with open(docker_wslconfig, 'w') as f:
    f.write(wslconfig)
print(f"   ✅ Written: {docker_wslconfig}")

# ─── 2. Shutdown WSL2 ───────────────────────────────────────────────────────────────
print("\n2. Shutting down WSL2 service:")
time.sleep(3)
r = subprocess.run(["wsl", "--shutdown"], capture_output=True, text=True, timeout=30)
print(f"   wsl --shutdown: exit={r.returncode}")
time.sleep(15)

# ─── 3. Kill Docker processes ─────────────────────────────────────────────────────___
print("\n3. Killing Docker processes:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
    print(f"   Killed {proc}")
time.sleep(5)

# ─── 4. Launch Docker Desktop ─────────────────────────────────────────────────______
print("\n4. Launching Docker Desktop:")
docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
if os.path.exists(docker_exe):
    subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"   Launched — waiting 120s for WSL2 backend...")
    
    for i in range(24):
        time.sleep(5)
        try:
            r = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"],
                capture_output=True, text=True, timeout=3)
            if r.returncode == 0 and r.stdout.strip():
                print(f"   ✅ Docker Server: {r.stdout.strip()}")
                break
        except:
            pass
        if i % 4 == 3:
            # Check WSL2 status
            time.sleep(2)
            r = subprocess.run(["wsl", "-l", "--verbose"], capture_output=True, text=True, timeout=10)
            wsl_status = "running" if "Running" in (r.stdout or "") else "checking"
            print(f"   Waiting... ({i+1}/24) [WSL: {wsl_status}]")
else:
    print(f"   ❌ Docker Desktop.exe not found")

# ─── 5. Final status ────────────────────────────────────────────────────────────────
print("\n5. Final status:")
time.sleep(10)

# Processes
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    time.sleep(1)
    r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {proc}", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    print(f"   {proc}: {'✅' if r.stdout.count(proc) > 1 else '❌'}")

# WSL distros
time.sleep(3)
r = subprocess.run(["wsl", "-l", "--verbose"], capture_output=True, text=True, timeout=10)
print(f"\n   WSL distros:")
if r.stdout:
    for line in r.stdout.split("\n"):
        if "docker" in line.lower() or "NAME" in line:
            print(f"     {line.strip()}")

# Docker info
time.sleep(3)
r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=8)
if r.returncode == 0:
    print(f"\n   ✅ docker info: OK")
    for line in r.stdout.split("\n"):
        if any(k in line for k in ["Server Version", "Storage Driver", "Operating System", "Docker Root Dir"]):
            print(f"   {line.strip()}")
    
    # Containers
    time.sleep(3)
    r = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}\\t{{.Status}}"],
        capture_output=True, text=True, timeout=8)
    lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
    print(f"\n   Containers ({len(lines)}):")
    for l in lines[:10]:
        print(f"     {l}")
else:
    print(f"\n   ❌ docker info: {r.stderr[:150]}")

# Port check
time.sleep(2)
for port in [2375, 2376]:
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", "3", f"http://localhost:{port}/_ping"],
            capture_output=True, text=True, timeout=5)
        print(f"   Port {port}: HTTP {r.stdout.strip()}")
    except:
        print(f"   Port {port}: ERR")

print(f"\n{'='*60}")
os.remove(__file__)
