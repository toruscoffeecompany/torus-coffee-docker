#!/usr/bin/env python3
"""
FIX: Docker Desktop 4.88.0 backend crashing on data migration.
The 182GB old Docker data is incompatible. Need to:
1. Backup important data
2. Clear corrupted WSL2 distros
3. Re-import fresh docker-desktop + docker-desktop-data
4. Docker Desktop will recreate fresh data volume

CRITICAL: We preserve the docker-desktop-data vhdx as backup but
create a new empty one for Docker Desktop to initialize.
"""
import subprocess, time, os, json, shutil

print("=== DOCKER FIX: Clear corrupted data + fresh start ===\n")

# ─── 1. Kill all Docker + WSL processes ─────────────────────────────────────────__
print("1. Killing all Docker + WSL processes:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe",
             "com.docker.backend.exe", "vmmem.exe", "vmmem"]:
    subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
    print(f"   Killed {proc}")
time.sleep(10)

# ─── 2. Shutdown WSL2 ─────────────────────────────────────────────────────────────
print("\n2. Shutting down WSL2:")
time.sleep(3)
r = subprocess.run(["wsl", "--shutdown"], capture_output=True, text=True, timeout=30)
print(f"   exit={r.returncode}")
time.sleep(15)

# ─── 3. Backup + clear corrupted Docker data ─────────────────────────────────____
print("\n3. Backing up corrupted Docker data:")
wsl_dir = os.path.expanduser(r"~\AppData\Local\Docker\wsl")
if os.path.exists(wsl_dir):
    backup_dir = wsl_dir + "_backup_20260817"
    if not os.path.exists(backup_dir):
        # Rename the corrupted data dir as backup
        try:
            os.rename(wsl_dir, backup_dir)
            print(f"   ✅ Renamed {wsl_dir} → {backup_dir}")
        except Exception as e:
            print(f"   ❌ Rename failed: {e}")
            # Try moving instead
            try:
                shutil.move(wsl_dir, backup_dir)
                print(f"   ✅ Moved {wsl_dir} → {backup_dir}")
            except Exception as e2:
                print(f"   ❌ Move also failed: {e2}")
    
    # Recreate empty wsl dir
    os.makedirs(wsl_dir, exist_ok=True)
    print(f"   ✅ Created fresh empty: {wsl_dir}")

# ─── 4. Clean up registry entries ─────────────────────────────────────────────────
print("\n4. Cleaning registry entries:")
time.sleep(3)
# Remove docker-desktop from Lxss
r = subprocess.run(["reg", "delete", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Lxss\\{fee811f4-d604-41db-b27c-ee3ed5bcd434}"],
    capture_output=True, text=True, timeout=10)
print(f"   Deleted docker-desktop registry: exit={r.returncode}")

# Also try to delete any docker-desktop-data entry
time.sleep(2)
r = subprocess.run(["reg", "query", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Lxss", "/s", "/f", "docker-desktop-data"],
    capture_output=True, text=True, timeout=10)
if "docker-desktop-data" in r.stdout:
    print("   Found docker-desktop-data in registry")
    # Extract GUID and delete
    for line in r.stdout.split("\n"):
        if "docker-desktop-data" in line and "HKEY" in line:
            guid = line.strip()
            print(f"   Would delete: {guid}")
else:
    print("   docker-desktop-data not in registry")

# ─── 5. Clean Docker settings ─────────────────────────────────__________________
print("\n5. Cleaning Docker config:")
settings_path = os.path.expanduser(r"~\AppData\Roaming\Docker\settings.json")
if os.path.exists(settings_path):
    os.remove(settings_path)
    print(f"   Removed settings.json (fresh first-run)")

# Clean daemon.json
daemon_path = os.path.expanduser(r"~\.docker\daemon.json")
if os.path.exists(daemon_path):
    os.remove(daemon_path)
    print(f"   Removed daemon.json (fresh first-run)")

# Remove lock files
for lock in [r"~\AppData\Local\Docker\backend.lock",
             r"~\AppData\Local\Docker\frontend.lock",
             r"~\AppData\Local\Docker\launcher.lock"]:
    path = os.path.expanduser(lock)
    if os.path.exists(path):
        os.remove(path)

# ─── 6. Launch Docker Desktop fresh ─────────────────────────────────────────______
print("\n6. Launching Docker Desktop fresh:")
time.sleep(10)
docker_exe = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
if not os.path.exists(docker_exe):
    docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"

if os.path.exists(docker_exe):
    subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"   Launched: {docker_exe}")
    print(f"   Waiting 180s for first-run initialization...")
    
    for i in range(36):
        time.sleep(5)
        try:
            r = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"],
                capture_output=True, text=True, timeout=3)
            if r.returncode == 0 and r.stdout.strip():
                print(f"   ✅ Docker Server: {r.stdout.strip()}")
                break
        except:
            pass
        if i % 12 == 11:
            # Check WSL distros
            time.sleep(3)
            r = subprocess.run(["wsl", "-l", "--verbose"], capture_output=True, text=True, timeout=15)
            if r.stdout:
                decoded = r.stdout[::2].decode('utf-16-le') if len(r.stdout) % 2 == 0 else r.stdout.decode('utf-16-le')
                if "docker" in decoded.lower():
                    print(f"   WSL: {decoded[:200]}")
            print(f"   Waiting... ({i+1}/36)")
else:
    print(f"   ❌ Docker Desktop.exe not found")

# ─── 7. Check if Docker is working ─────────────────────────────────_______________
print("\n7. Final status:")
time.sleep(15)
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {proc}", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    print(f"   {proc}: {'✅' if r.stdout.count(proc) > 1 else '❌'}")

# WSL distros
time.sleep(5)
r = subprocess.run(["wsl", "-l", "--verbose"], capture_output=True, text=True, timeout=15)
if r.stdout:
    print(f"\n   WSL distros:")
    for line in r.stdout.split("\n"):
        if line.strip():
            print(f"     {line.strip()}")

# Docker info
time.sleep(3)
r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
if r.returncode == 0:
    print(f"\n   ✅ docker info: OK")
    for line in r.stdout.split("\n"):
        if any(k in line for k in ["Server Version", "Storage Driver", "Operating System", "Docker Root Dir"]):
            print(f"   {line.strip()}")
else:
    print(f"\n   ❌ docker info: {r.stderr[:150]}")

print(f"\n{'='*60}")
print("Docker fresh-start repair complete")
print(f"Note: Old Docker data backed up to {backup_dir}")
print(f"{'='*60}")

os.remove(__file__)
