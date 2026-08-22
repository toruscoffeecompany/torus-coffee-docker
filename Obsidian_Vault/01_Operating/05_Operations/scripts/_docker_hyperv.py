#!/usr/bin/env python3
"""
FIX: Docker Desktop — try Hyper-V backend instead of WSL2.
If WSL2 memory error persists, switch to Hyper-V backend.
"""
import subprocess, time, os, json

print("=== DOCKER FIX: Try Hyper-V backend ===\n")

# ─── 1. Check system memory ────────────────────────────────────────────────────────
print("1. System memory:")
time.sleep(2)
r = subprocess.run(["wmic", "computersystem", "get", "TotalPhysicalMemory"],
    capture_output=True, text=True, timeout=10)
mem_mb = 0
for line in r.stdout.split("\n"):
    line = line.strip()
    if line and line.isdigit():
        mem_mb = int(int(line) / 1024 / 1024)
        break
print(f"   Total RAM: {mem_mb} MB ({mem_mb/1024:.1f} GB)")

# Check free memory
time.sleep(2)
r = subprocess.run(["wmic", "OS", "get", "FreePhysicalMemory"],
    capture_output=True, text=True, timeout=10)
free_mb = 0
for line in r.stdout.split("\n"):
    line = line.strip()
    if line and line.isdigit():
        free_mb = int(int(line) / 1024)
        break
print(f"   Free RAM: {free_mb} MB")

# ─── 2. Check if Hyper-V is available ───────────────────────────────────────────────
print("\n2. Hyper-V availability:")
time.sleep(2)
r = subprocess.run(["powershell", "-Command", 
    "Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All"],
    capture_output=True, text=True, timeout=10)
print(f"   {r.stdout[:300] if r.stdout else r.stderr[:200]}")

# ─── 3. Try switching Docker Desktop to Hyper-V ─────────────────────────────────────
print("\n3. Switching to Hyper-V backend:")
settings_path = os.path.expanduser(r"~\AppData\Roaming\Docker\settings.json")
if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    # Switch to Hyper-V
    settings["wsl2BasedEngine"] = False
    settings["useWsl2"] = False
    settings["backend"] = "hyper-v"
    settings["windowsFeatures"] = {
        "Wsl2": False,
        "HyperV": True,
        "ContainerD": False,
        "DockerVsShim": False,
        "ClientGuarded": False
    }
    
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    print(f"   ✅ Updated settings.json to Hyper-V backend")
else:
    # Create settings
    settings = {
        "wsl2BasedEngine": False,
        "useWsl2": False,
        "backend": "hyper-v",
        "windowsFeatures": {
            "Wsl2": False,
            "HyperV": True
        }
    }
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    print(f"   ✅ Created settings.json with Hyper-V backend")

# Also update daemon.json for Hyper-V
daemon = {
    "builder": {
        "gc": {
            "defaultKeepStorage": "20GB",
            "enabled": True
        }
    },
    "experimental": False,
    "features": {
        "buildkit": True
    },
    "host": "npipe://",
    "hosts": [
        "npipe://",
        "tcp://0.0.0.0:2375"
    ]
}
daemon_path = os.path.expanduser(r"~\.docker\daemon.json")
with open(daemon_path, 'w') as f:
    json.dump(daemon, f, indent=2)
print(f"   ✅ Updated daemon.json")

# ─── 4. Kill + restart ─────────────────────────────────────────────────────────────
print("\n4. Restarting with Hyper-V backend:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
    print(f"   Killed {proc}")
time.sleep(5)

# Shutdown WSL2
subprocess.run(["wsl", "--shutdown"], capture_output=True, text=True, timeout=30)
print("   WSL2 shutdown")
time.sleep(10)

# Launch Docker Desktop
docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
if os.path.exists(docker_exe):
    subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"   Launched Docker Desktop")
    print(f"   Waiting 120s for Hyper-V backend...")
    
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

# ─── 5. Final status ────────────────────────────────────────────────────────────────
print("\n5. Final status:")
time.sleep(10)
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmcompute.exe"]:
    time.sleep(1)
    r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {proc}", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    print(f"   {proc}: {'✅' if r.stdout.count(proc) > 1 else '❌'}")

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
os.remove(__file__)
