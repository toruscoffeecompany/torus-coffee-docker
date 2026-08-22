#!/usr/bin/env python3
"""
FIX: Force repair Docker Desktop using installer with correct syntax.
The installer help showed: install [--quiet] [--accept-license] [--backend=wsl-2|hyper-v|windows|docker-vmm]
Need to try --backend flag.
"""
import subprocess, time, os, json

print("=== DOCKER REPAIR: Force reinstall ===\n")

# ─── 1. Kill all Docker processes ─────────────────────────────────────────────────
print("1. Killing all Docker processes:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe",
             "Docker Desktop Service.exe", "Docker Desktop VM.exe", "installer.exe"]:
    r = subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
    if r.returncode == 0:
        print(f"   ✅ Killed {proc}")
print("   Done")
time.sleep(10)

# ─── 2. Clean up corrupted Docker install ─────────────────────────────────────___
print("\n2. Cleaning corrupted Docker install:")
# Remove settings.json to force first-run
settings_path = os.path.expanduser(r"~\AppData\Roaming\Docker\settings.json")
if os.path.exists(settings_path):
    os.remove(settings_path)
    print(f"   Removed settings.json (force fresh config)")

# Remove lock files
for lock in [r"~\AppData\Local\Docker\backend.lock",
             r"~\AppData\Local\Docker\frontend.lock",
             r"~\AppData\Local\Docker\launcher.lock"]:
    path = os.path.expanduser(lock)
    if os.path.exists(path):
        os.remove(path)
        print(f"   Removed {lock}")

# ─── 3. Run installer with --backend=wsl-2 ────────────────────────────────────────
print("\n3. Running Docker Desktop installer:")
installer = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop Installer.exe"

# Try with explicit backend flag
r = subprocess.run([installer, "install", "--quiet", "--accept-license", "--backend=wsl-2"],
    capture_output=True, text=True, timeout=180)
print(f"   Install wsl-2: exit={r.returncode}")
print(f"   stdout: {r.stdout[:300]}")
if r.stderr:
    print(f"   stderr: {r.stderr[:200]}")

# If that failed, try without backend flag (let it auto-detect)
if r.returncode != 0:
    print("\n   Retrying without --backend flag:")
    r = subprocess.run([installer, "install", "--quiet", "--accept-license"],
        capture_output=True, text=True, timeout=180)
    print(f"   Install: exit={r.returncode}")
    print(f"   stdout: {r.stdout[:300]}")

# ─── 4. Try launching Docker Desktop.exe directly ───────────────────────────────────
print("\n4. Launching Docker Desktop.exe:")
time.sleep(10)
docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
if os.path.exists(docker_exe):
    subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("   Launched — waiting 120s...")
    
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
        if i % 6 == 5:
            print(f"   Waiting... ({i+1}/24)")

# ─── 5. Check Docker Desktop UI log ─────────────────────────────────────────────___
print("\n5. Docker Desktop UI error log:")
time.sleep(5)
log_dir = os.path.expanduser(r"~\AppData\Local\Docker\log\host")
if os.path.exists(log_dir):
    logs = sorted([f for f in os.listdir(log_dir) if f.endswith(".log") and "installer" in f], 
        key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True)
    if logs:
        with open(os.path.join(log_dir, logs[0]), 'r', errors='ignore') as f:
            content = f.read()
        print(f"   {logs[0]}:")
        for line in content.split("\n")[-25:]:
            if line.strip():
                print(f"     {line.strip()[:150]}")

# ─── 6. Also check electron log ─────────────────────────────────────────────────___
time.sleep(2)
with open(os.path.join(log_dir, "electron-ui-console-*.log"), 'r', errors='ignore') as f:
    content = f.read()
print(f"\n   electron-ui-console:")
for line in content.split("\n")[-15:]:
    if line.strip():
        print(f"     {line.strip()[:150]}")

# ─── 7. Final status ─────────────────────────────────────────────────────────────___
print("\n6. Final status:")
time.sleep(10)
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {proc}", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    print(f"   {proc}: {'✅' if r.stdout.count(proc) > 1 else '❌'}")

# Docker
time.sleep(3)
r = subprocess.run(["docker", "version"], capture_output=True, text=True, timeout=8)
if r.returncode == 0:
    print(f"\n   ✅ docker version OK")
else:
    print(f"\n   ❌ docker version: {r.stderr[:150]}")

print(f"\n{'='*60}")
os.remove(__file__)
