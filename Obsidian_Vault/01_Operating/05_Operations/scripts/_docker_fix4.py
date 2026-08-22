#!/usr/bin/env python3
"""
FIX: Launch Docker Desktop.exe directly + accept license.
Docker Desktop.exe files found at:
- AppData/Local/Programs/DockerDesktop/Docker Desktop.exe
- AppData/Local/Programs/DockerDesktop/frontend/Docker Desktop.exe
- AppData/Local/Programs/DockerDesktop/resources/Docker desktop.exe
Installer needs --accept-license flag.
"""
import subprocess, time, os

installer = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop Installer.exe"
docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"

print("=== DOCKER DESKTOP REINSTALL (ATTEMPT 4) ===\n")

# ─── 1. Kill any zombie processes ─────────────────────────────────────────────────
print("1. Cleaning zombie processes:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "installer.exe"]:
    subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
    print(f"   Killed {proc}")

# ─── 2. Reinstall with --accept-license ──────────────────────────────────────────
print("\n2. Reinstalling with --accept-license:")
r = subprocess.run([installer, "install", "--quiet", "--accept-license"],
    capture_output=True, text=True, timeout=300)
print(f"   Exit: {r.returncode}")
if r.stdout:
    print(f"   stdout: {r.stdout[:400]}")
if r.stderr:
    print(f"   stderr: {r.stderr[:400]}")

# ─── 3. Launch Docker Desktop directly ──────────────────────────────────────────
print("\n3. Launching Docker Desktop.exe directly:")
if os.path.exists(docker_exe):
    print(f"   Found: {docker_exe}")
    try:
        # Launch without waiting (non-blocking)
        p = subprocess.Popen([docker_exe], 
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"   Launched PID: {p.pid}")
        print(f"   Waiting 90s for startup...")
    except Exception as e:
        print(f"   Launch failed: {e}")
        # Try GUI mode
        r = subprocess.run([docker_exe], capture_output=True, text=True, timeout=5)
        print(f"   GUI mode exit: {r.returncode}")

# ─── 4. Wait for Docker to initialize ────────────────────────────────────────────
print("\n4. Waiting for Docker initialization:")
for i in range(18):
    time.sleep(5)
    r = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"],
        capture_output=True, text=True, timeout=5)
    if r.returncode == 0 and r.stdout.strip():
        print(f"   ✅ Docker Server: {r.stdout.strip()}")
        break
    if i % 4 == 3:
        print(f"   ...waiting ({i+1}/18)")
else:
    print(f"   ❌ Docker did not start after 90s")

# ─── 5. Check all Docker processes ────────────────────────────────────────────────
print("\n5. Docker processes:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "docker-desktop-service.exe"]:
    time.sleep(2)
    r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {proc}"],
        capture_output=True, text=True, timeout=5)
    print(f"   {proc}: {'✅' if r.stdout.count(proc) > 1 else '❌'}")

# ─── 6. Check Docker daemon ──────────────────────────────────────────────────────
print("\n6. Docker daemon tests:")
time.sleep(3)
r = subprocess.run(["docker", "version"], capture_output=True, text=True, timeout=8)
if r.returncode == 0:
    print(f"   ✅ docker version OK")
else:
    print(f"   ❌ docker version: {r.stderr[:120]}")

time.sleep(3)
r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
if r.returncode == 0:
    print(f"   ✅ docker info OK")
    for line in r.stdout.split("\n"):
        if any(k in line for k in ["Server Version", "Storage Driver", "Operating System", "Docker Root Dir", "Cgroup"]):
            print(f"     {line.strip()}")
else:
    print(f"   ❌ docker info: {r.stderr[:150]}")

# ─── 7. Check containers ──────────────────────────────────────────────────────────
time.sleep(5)
r = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True, timeout=10)
if r.returncode == 0:
    lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
    print(f"\n   Containers ({len(lines)-1}):")
    for l in lines[:15]:
        print(f"     {l}")
else:
    print(f"\n   docker ps: ❌ {r.stderr[:100]}")

# ─── 8. Check Docker API ports ────────────────────────────────────────────────────
time.sleep(3)
for port in [2375, 2376]:
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", "3", f"http://localhost:{port}/_ping"],
        capture_output=True, text=True, timeout=5)
    print(f"   Port {port}: HTTP {r.stdout.strip()}")

print(f"\n{'='*60}")

os.remove(__file__)
