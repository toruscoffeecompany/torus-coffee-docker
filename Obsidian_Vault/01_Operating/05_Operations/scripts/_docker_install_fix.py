#!/usr/bin/env python3
"""
FIX: Install Docker Desktop with correct installer flags.
The --accept-license flag is wrong. Docker Desktop installer uses:
  install [--quiet] [--accept-non-docker-desktop-tos] [--backend=wsl-2|hyper-v|windows|docker-vmm]
"""
import subprocess, time, os

print("=== DOCKER INSTALL FIX ===\n")

installer = r"C:\Users\torus\Downloads\DockerDesktop_Installer.exe"

# ─── 1. Check installer help ───────────────────────────────────────────────────────
print("1. Checking installer help:")
time.sleep(3)
r = subprocess.run([installer, "--help"], capture_output=True, text=True, timeout=10)
print(r.stdout[:400])
print(r.stderr[:200])

# ─── 2. Try install with correct flags ─────────────────────────────────────────────
print("\n2. Installing with --accept-non-docker-desktop-tos:")
r = subprocess.run([installer, "install", "--quiet", "--accept-non-docker-desktop-tos", "--backend=wsl-2"],
    capture_output=True, text=True, timeout=300)
print(f"   Exit: {r.returncode}")
print(f"   stdout: {r.stdout[:400]}")
print(f"   stderr: {r.stderr[:300]}")

# If that didn't work, try --install
if r.returncode != 0:
    print("\n3. Trying with --install flag:")
    r = subprocess.run([installer, "install", "--quiet", "--accept-non-docker-desktop-tos"],
        capture_output=True, text=True, timeout=300)
    print(f"   Exit: {r.returncode}")
    print(f"   stdout: {r.stdout[:400]}")

# ─── 3. Launch Docker Desktop ──────────────────────────────────────────────────────
print("\n4. Launching Docker Desktop:")
time.sleep(15)
docker_paths = [
    r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
    r"C:\Program Files\Docker\Docker\resources\Docker Desktop.exe",
    r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe",
]
for p in docker_paths:
    if os.path.exists(p):
        print(f"   Found: {p}")
        subprocess.Popen([p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("   Launched")
        break
else:
    print("   ❌ Docker Desktop.exe not found — checking install location")
    # Search
    for root, dirs, files in os.walk(r"C:\Program Files\Docker"):
        for f in files:
            if f.lower() == "docker desktop.exe":
                full = os.path.join(root, f)
                print(f"   Found: {full}")
                subprocess.Popen([full], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("   Launched")
                break

# ─── 4. Wait + verify ──────────────────────────────────────────────────────────────
print("\n5. Waiting 120s for Docker startup:")
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

# ─── 5. Final ──────────────────────────────────────────────────────────────────────
print("\n6. Final status:")
time.sleep(10)
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    time.sleep(1)
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
else:
    print(f"\n   ❌ docker info: {r.stderr[:150]}")

print(f"\n{'='*60}")
os.remove(__file__)
