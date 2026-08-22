#!/usr/bin/env python3
"""
FIX: Check truncated BasePath + try to fix Docker Desktop WSL distro.
The registry shows docker-desktop BasePath is truncated.
"""
import subprocess, time, os

print("=== DOCKER WSL2 REPAIR ===\n")

# ─── 1. Get full BasePath from registry ─────────────────────────────────────────────
print("1. Full Lxss registry check:")
time.sleep(2)
r = subprocess.run(["reg", "query", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Lxss\\{fee811f4-d604-41db-b27c-ee3ed5bcd434}", "/s"],
    capture_output=True, text=True, timeout=10)
print(r.stdout)

# ─── 2. Check all Lxss distributions ────────────────────────────────────────────────
print("\n2. All Lxss distributions:")
time.sleep(2)
r = subprocess.run(["reg", "query", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Lxss", "/s"],
    capture_output=True, text=True, timeout=10)
for line in r.stdout.split("\n"):
    if "DistributionName" in line or "BasePath" in line or "HKEY" in line:
        print(f"   {line.strip()}")

# ─── 3. Check if docker-desktop-data exists too ─────────────────────────────────────
time.sleep(2)
r = subprocess.run(["reg", "query", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Lxss", "/s", "/f", "docker-desktop-data"],
    capture_output=True, text=True, timeout=10)
print(f"\n3. docker-desktop-data in Lxss:")
print(f"   {r.stdout[:300] if r.stdout else 'not found'}")

# ─── 4. Check Docker filesystem location ────────────────────────────────────────────
print("\n4. Docker filesystem:")
wsl_dir = os.path.expanduser(r"~\AppData\Local\Docker\wsl")
if os.path.exists(wsl_dir):
    print(f"   WSL dir: {wsl_dir}")
    
    # Check for docker-desktop data
    for item in os.listdir(wsl_dir):
        full = os.path.join(wsl_dir, item)
        if os.path.isdir(full):
            files = os.listdir(full)
            print(f"   {item}/: {len(files)} items")
    
    # Check the "data" subdir
    data_dir = os.path.join(wsl_dir, "data")
    if os.path.exists(data_dir):
        print(f"   data/ contents:")
        for item in os.listdir(data_dir):
            full = os.path.join(data_dir, item)
            if os.path.isfile(full):
                print(f"     {item} ({os.path.getsize(full)} bytes)")
            else:
                print(f"     {item}/")
    else:
        print(f"   data/ NOT found")
    
    # Check for ext4 files
    for root, dirs, files in os.walk(wsl_dir):
        for f in files:
            if f.endswith(".ext4") or f == "fsutil":
                full = os.path.join(root, f)
                print(f"   Found: {full} ({os.path.getsize(full)/1024/1024:.1f} MB)")

# ─── 5. Check if WSL2 can access docker-desktop ─────────────────────────────────────
print("\n5. WSL docker-desktop access:")
time.sleep(3)
r = subprocess.run(["wsl", "-d", "docker-desktop", "-u", "root", "ls /"],
    capture_output=True, text=True, timeout=15)
print(f"   stdout: {r.stdout[:300] if r.stdout else 'empty'}")
print(f"   stderr: {r.stderr[:200] if r.stderr else 'empty'}")

# ─── 6. Try wsl --shutdown + relaunch ─────────────────────────────────────────────
print("\n6. WSL2 shutdown + Docker relaunch:")
time.sleep(3)
r = subprocess.run(["wsl", "--shutdown"], capture_output=True, text=True, timeout=30)
print(f"   WSL shutdown: exit={r.returncode}")
time.sleep(15)

# Relaunch Docker Desktop
docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
if os.path.exists(docker_exe):
    subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"   Relaunched Docker Desktop")
    print(f"   Waiting 60s...")
    
    for i in range(12):
        time.sleep(5)
        r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=8)
        if r.returncode == 0:
            print(f"   ✅ Docker info OK!")
            for line in r.stdout.split("\n"):
                if any(k in line for k in ["Server Version", "Storage Driver", "Operating System"]):
                    print(f"   {line.strip()}")
            break
        else:
            print(f"   Waiting... ({i+1}/12)")

# ─── 7. Check processes ─────────────────────────────────────────────────────────────
print("\n7. Final process check:")
time.sleep(5)
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {proc}", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    print(f"   {proc}: {'✅' if r.stdout.count(proc) > 1 else '❌'}")

print(f"\n{'='*60}")
os.remove(__file__)
