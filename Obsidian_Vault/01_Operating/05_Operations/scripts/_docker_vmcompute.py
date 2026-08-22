#!/usr/bin/env python3
"""
FIX: Start vmcompute service (Hyper-V Host Compute Service).
This is the core service that both WSL2 and Hyper-V depend on.
If it's disabled, Docker Desktop can't start any backend.
"""
import subprocess, time, os, json

print("=== DOCKER FIX: vmcompute service ===\n")

# ─── 1. Check vmcompute service status ─────────────────────────────────────────────
print("1. vmcompute service status:")
time.sleep(3)
r = subprocess.run(["sc", "query", "vmcompute"], capture_output=True, text=True, timeout=10)
print(r.stdout[:300])

# ─── 2. Check if we can start it ────────────────────────────────────────────────────
print("\n2. Starting vmcompute service:")
time.sleep(3)
r = subprocess.run(["sc", "start", "vmcompute"], capture_output=True, text=True, timeout=10)
print(f"   exit={r.returncode}")
print(f"   {r.stdout[:200]}")

time.sleep(5)
r = subprocess.run(["sc", "query", "vmcompute"], capture_output=True, text=True, timeout=10)
print(f"\n   After start: {r.stdout[:200]}")

# ─── 3. Check Hyper-V service ───────────────────────────────────────────────────────
print("\n3. Hyper-V services:")
for svc in ["vmms", "vmcompute", "docker", "com.docker.service"]:
    time.sleep(2)
    r = subprocess.run(["sc", "query", svc], capture_output=True, text=True, timeout=5)
    state = "UNKNOWN"
    for line in r.stdout.split("\n"):
        if "STATE" in line:
            state = line.strip()
    status = "✅" if "RUNNING" in state else "❌"
    print(f"   {svc}: {status} ({state[:50] if state else 'not found'})")

# ─── 4. Check if Hyper-V is enabled at boot ─────────────────────────────────────────
print("\n4. Hyper-V feature status:")
time.sleep(2)
r = subprocess.run(["bcdedit", "/enum", "{current}"], capture_output=True, text=True, timeout=5)
for line in r.stdout.split("\n"):
    if "hypervisor" in line.lower() or "hyper-v" in line.lower():
        print(f"   {line.strip()}")

# ─── 5. Restore WSL2 backend + try again ────────────────────────────────────────────
print("\n5. Restoring WSL2 backend:")
settings_path = os.path.expanduser(r"~\AppData\Roaming\Docker\settings.json")
if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    settings["wsl2BasedEngine"] = True
    settings["useWsl2"] = True
    settings["backend"] = "wsl-2"
    
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    print("   ✅ Restored WSL2 backend settings")

# ─── 6. Kill + restart Docker ──────────────────────────────────────────────────────
print("\n6. Restarting Docker Desktop:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
print("   All Docker processes killed")
time.sleep(5)

# Shutdown WSL2
subprocess.run(["wsl", "--shutdown"], capture_output=True, text=True, timeout=30)
print("   WSL2 shut down")
time.sleep(10)

# Launch Docker Desktop
docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
if os.path.exists(docker_exe):
    subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("   Docker Desktop relaunched")
    print("   Waiting 90s...")
    
    for i in range(18):
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
            print(f"   Waiting... ({i+1}/18)")

# ─── 7. Final check ────────────────────────────────────────────────────────────────
print("\n7. Final check:")
time.sleep(5)
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe", "vmcompute.exe"]:
    r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {proc}", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    print(f"   {proc}: {'✅' if r.stdout.count(proc) > 1 else '❌'}")

time.sleep(3)
r = subprocess.run(["docker", "version"], capture_output=True, text=True, timeout=8)
if r.returncode == 0:
    print(f"\n   ✅ docker version OK")
else:
    print(f"\n   ❌ docker version: {r.stderr[:150]}")

print(f"\n{'='*60}")
os.remove(__file__)
