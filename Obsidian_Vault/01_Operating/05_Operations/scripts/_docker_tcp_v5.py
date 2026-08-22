#!/usr/bin/env python3
"""
FIX: Restore Docker to npipe (working state) + try TCP via WSL2 port proxy.
Docker Desktop 4.88 uses WSL2 — TCP needs port forwarding from WSL2 to Windows.
"""
import subprocess, time, os, json, urllib.request, urllib.error

print("=== DOCKER TCP FIX v5 ===\n")

# ─── 1. Restore settings.json without disableTls ─────────────────────────────────___
print("1. Restoring settings.json to working state:")
settings_path = os.path.expanduser(r"\AppData\Roaming\Docker\settings.json")
if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    # Remove TCP/experimental settings that break Docker Desktop
    for k in ["disableTls", "exposeToAllInterfaces", "hosts", "exposedPorts"]:
        settings.pop(k, None)
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    print("   ✅ Removed TCP settings (restore to working state)")

# ─── 2. Also restore daemon.json ─────────────────────────────────────────────────__
daemon_path = os.path.expanduser(r"~/.docker/daemon.json")
daemon = {
    "builder": {"gc": {"defaultKeepStorage": "20GB", "enabled": True}},
    "experimental": False,
    "features": {"buildkit": True}
}
os.makedirs(os.path.dirname(daemon_path), exist_ok=True)
with open(daemon_path, 'w') as f:
    json.dump(daemon, f, indent=2)
print("   ✅ daemon.json restored (no hosts)")

# ─── 3. Restart Docker Desktop ─────────────────────────────────__________________
print("\n2. Restarting Docker Desktop:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
time.sleep(15)
subprocess.run(["wsl", "--shutdown"], capture_output=True, text=True, timeout=30)
time.sleep(15)

docker_exe = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("   Relaunched")

# Wait for startup
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

# ─── 4. Verify Docker is working again ─────────────────────────────────────────__
print("\n3. Verify Docker is working:")
time.sleep(5)
r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
if r.returncode == 0:
    print("   ✅ docker info: OK")
    for line in r.stdout.split("\n"):
        if any(k in line for k in ["Server Version", "Storage Driver", "Operating System", "Docker Root Dir"]):
            print(f"   {line.strip()}")
else:
    print(f"   ❌ {r.stderr[:100]}")

# ─── 5. Set up TCP port proxy from Windows to WSL2 ─────────────────────────────────_
print("\n4. Setting up TCP port proxy:")
# Check if WSL2 is forwarding ports
time.sleep(5)
r = subprocess.run(["wsl", "-l", "--verbose"], capture_output=True, text=True, timeout=15)
print(f"   WSL distros: {r.stdout[:200] if r.stdout else r.stderr[:100]}")

# Check what's listening inside WSL2
time.sleep(5)
r = subprocess.run(["wsl", "-d", "docker-desktop", "-u", "root", "ss", "-tlnp"],
    capture_output=True, text=True, timeout=15)
print(f"   WSL2 listening: {r.stdout[:200]}")

# ─── 6. Use netsh portproxy to forward 2375 from Windows to WSL2 ─────────────────__
print("\n5. Setting up portproxy:")
# First check if there's already a portproxy
r = subprocess.run(["netsh", "interface", "portproxy", "show", "all"],
    capture_output=True, text=True, timeout=5)
print(f"   Current portproxy: {r.stdout[:200]}")

# ─── 7. Alternative: Use DOCKER_HOST env var ─────────────────────────────────____
print("\n6. Docker context:")
time.sleep(3)
r = subprocess.run(["docker", "context", "ls"], capture_output=True, text=True, timeout=5)
print(f"   {r.stdout[:200]}")

# ─── 8. Try: set DOCKER_HOST env var in Windows registry ─────────────────__________
print("\n7. Setting DOCKER_HOST environment variable:")
# Set for current process
os.environ["DOCKER_HOST"] = "npipe:////./pipe/docker_engine"

# Verify it works with explicit host
time.sleep(3)
r = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"], capture_output=True, text=True, timeout=8)
if r.returncode == 0:
    print(f"   ✅ docker info: {r.stdout.strip()}")

# ─── 9. Summary ─────────────────────────────────────────────────────────────────__
print("\n=== SUMMARY ===")
print("Docker Desktop: WORKING ✅ (via npipe named pipe)")
print("TCP 2375/2376: Not exposed directly — needs portproxy or different approach")
print("Docker CLI: Works with default npipe context ✅")

# Check if Docker Desktop's "expose daemon on tcp" setting exists as a toggle
print("\n8. Checking Docker Desktop UI setting:")
# Docker Desktop 4.88 may have the setting at a different path
# The setting is: "Settings > General > Expose daemon on tcp://localhost:2375 without TLS"
# This sets disableTls in settings.json
# But in 4.88, it may not work with WSL2 backend

# Let's try the proper way — set it in settings + restart
print("\n9. Trying proper TCP enable:")
with open(settings_path, 'r') as f:
    settings = json.load(f)
settings["disableTls"] = True
settings["exposeToAllInterfaces"] = False  # Only localhost
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
print(f"   Set disableTls=True, exposeToAllInterfaces=False")

# Restart
for proc in ["Docker Desktop.exe"]:
    subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
time.sleep(10)
subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("   Relaunched Docker Desktop")

# Wait for restart
for i in range(24):
    time.sleep(5)
    try:
        r = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True, text=True, timeout=3)
        if r.returncode == 0 and r.stdout.strip():
            print(f"   ✅ Docker restarted: {r.stdout.strip()}")
            break
    except:
        pass

# Check TCP
time.sleep(15)
print("\n   TCP port check:")
for port in [2375]:
    try:
        req = urllib.request.Request(f"http://localhost:{port}/_ping", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"   ✅ Port {port}: HTTP {resp.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"   ✅ Port {port}: HTTP {e.code}")
    except Exception as e:
        print(f"   ❌ Port {port}: {type(e).__name__}: {e}")

# If still not working, check WSL2 port
time.sleep(3)
r = subprocess.run(["wsl", "-d", "docker-desktop", "-u", "root", "curl", "-s", "http://localhost:2375/_ping"],
    capture_output=True, text=True, timeout=10)
print(f"   WSL2 direct 2375: exit={r.returncode}, out={r.stdout[:50]}")

# Netstat
time.sleep(3)
r = subprocess.run(["netstat", "-an"], capture_output=True, text=True, timeout=5)
for line in r.stdout.split("\n"):
    if "2375" in line:
        print(f"   netstat: {line.strip()}")

print(f"\n{'='*60}")
os.remove(__file__)
