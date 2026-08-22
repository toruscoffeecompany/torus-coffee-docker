#!/usr/bin/env python3
"""
FIX: Docker Desktop — use correct WSL2 --import --vhd syntax.
wsl --import docker-desktop-data <install_location> <path_to_vhdx> --version 2
Also need to start docker-desktop distro.
"""
import subprocess, time, os, json

print("=== DOCKER FIX: WSL2 --import --vhd ===\n")

# ─── 1. Kill Docker Desktop ─────────────────────────────────────────────────────__
print("1. Killing Docker Desktop:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
print("   Killed")
time.sleep(5)

# ─── 2. Register docker-desktop-data using --vhd ────────────────────────────────────
print("\n2. Registering docker-desktop-data with --vhd:")
data_vhdx = r"C:\Users\torus\AppData\Local\Docker\wsl\disk\docker_data.vhdx"
data_basepath = r"C:\Users\torus\AppData\Local\Docker\wsl\data"

# Create the directory if it doesn't exist
if not os.path.exists(data_basepath):
    os.makedirs(data_basepath)

# Use wsl --import with --vhd (Windows 10 2004+)
r = subprocess.run(["wsl", "--import", "docker-desktop-data", data_basepath, data_vhdx, "--vhd"],
    capture_output=True, text=True, timeout=60)
print(f"   Exit: {r.returncode}")
print(f"   stdout: {r.stdout[:200]}")
print(f"   stderr: {r.stderr[:200]}")

# ─── 3. Register docker-desktop too ────────────────────────────────────────────────
print("\n3. Registering docker-desktop with --vhd:")
main_vhdx = r"C:\Users\torus\AppData\Local\Docker\wsl\main\ext4.vhdx"
main_basepath = r"C:\Users\torus\AppData\Local\Docker\wsl\main"

r = subprocess.run(["wsl", "--import", "docker-desktop", main_basepath, main_vhdx, "--vhd"],
    capture_output=True, text=True, timeout=60)
print(f"   Exit: {r.returncode}")
print(f"   stdout: {r.stdout[:200]}")
print(f"   stderr: {r.stderr[:200]}")

# ─── 4. Set both to WSL2 ────────────────────────────────────────────────────────────
print("\n4. Setting WSL2 version:")
time.sleep(3)
r = subprocess.run(["wsl", "--set-version", "docker-desktop-data", "2"],
    capture_output=True, text=True, timeout=30)
print(f"   docker-desktop-data: exit={r.returncode}, {r.stdout[:100]}{r.stderr[:100]}")

time.sleep(3)
r = subprocess.run(["wsl", "--set-version", "docker-desktop", "2"],
    capture_output=True, text=True, timeout=30)
print(f"   docker-desktop: exit={r.returncode}, {r.stdout[:100]}{r.stderr[:100]}")

# ─── 5. List all WSL distros ────────────────────────────────────────────────────────
print("\n5. All WSL distros:")
time.sleep(5)
r = subprocess.run(["wsl", "-l", "--verbose"], capture_output=True, text=True, timeout=15)
print(f"   {r.stdout[:400] if r.stdout else r.stderr[:200]}")

# ─── 6. Start docker-desktop-data ────────────────────────────────────────────────────
print("\n6. Starting docker-desktop-data:")
time.sleep(3)
r = subprocess.run(["wsl", "-d", "docker-desktop-data", "-u", "root", "ls /"],
    capture_output=True, text=True, timeout=30)
print(f"   exit={r.returncode}")
print(f"   stdout: {r.stdout[:200]}")
print(f"   stderr: {r.stderr[:200]}")

# ─── 7. Launch Docker Desktop ────────────────────────────────────────────────────────
print("\n7. Launching Docker Desktop:")
time.sleep(5)
docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
if os.path.exists(docker_exe):
    subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"   Launched — waiting 120s...")

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

# ─── 8. Final check ────────────────────────────────────────────────────────────────
print("\n8. Final status:")
time.sleep(10)
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    time.sleep(2)
    r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {proc}", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    print(f"   {proc}: {'✅' if r.stdout.count(proc) > 1 else '❌'}")

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
    for l in lines[:15]:
        print(f"     {l}")
else:
    print(f"\n   ❌ docker info: {r.stderr[:150]}")

print(f"\n{'='*60}")
os.remove(__file__)
