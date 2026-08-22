#!/usr/bin/env python3
"""
FIX: Docker Desktop WSL2 backend not starting because the docker-desktop
WSL2 distros are not registered. Need to either:
1. Re-register the distros via Docker Desktop (first-run)
2. Manually create WSL2 distribution registration
3. Force Docker Desktop to re-register
"""
import subprocess, time, os, json

print("=== DOCKER WSL2 REGISTRATION FIX ===\n")

# ─── 1. Check if Docker Desktop data exists ──────────────────────────────────────
print("1. Docker Desktop WSL2 data:")
wsl_data = os.path.expanduser(r"~\AppData\Local\Docker\wsl")
if os.path.exists(wsl_data):
    for item in os.listdir(wsl_data)[:20]:
        full = os.path.join(wsl_data, item)
        if os.path.isdir(full):
            sz = sum(os.path.getsize(os.path.join(r,f)) for r,d,fs in os.walk(full) for f in fs)
            print(f"   {item}/ ({sz/1024/1024:.1f} MB)")
        else:
            print(f"   {item} ({os.path.getsize(full)/1024/1024:.1f} MB)")

# ─── 2. Check Lxss registry for docker-desktop ─────────────────────────────────────
print("\n2. Lxss registry check:")
time.sleep(2)
r = subprocess.run(["reg", "query", "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Lxss\\Distributions", "/s", "/f", "docker"],
    capture_output=True, text=True, timeout=10)
print(f"   Lxss docker: {r.stdout[:200] if r.stdout else r.stderr[:100]}")

# ─── 3. Check HKCU Lxss ──────────────────────────────────────────────────────────
time.sleep(2)
r = subprocess.run(["reg", "query", "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Lxss", "/s", "/f", "docker"],
    capture_output=True, text=True, timeout=10)
print(f"   HKCU Lxss docker: {r.stdout[:200] if r.stdout else r.stderr[:100]}")

# ─── 4. Check if Docker Desktop has data for distributions ─────────────────────────
print("\n3. Docker distribution data:")
dist_data = os.path.join(wsl_data, "data")
if os.path.exists(dist_data):
    print(f"   data/ exists")
    for f in os.listdir(dist_data)[:10]:
        print(f"   {f}")
else:
    print(f"   data/ NOT found")

# ─── 5. Create settings.json with proper WSL2 config ──────────────────────────────
print("\n4. Creating Docker settings.json with WSL2 backend:")
settings_dir = os.path.expanduser(r"~\AppData\Roaming\Docker")
if not os.path.exists(settings_dir):
    os.makedirs(settings_dir)

settings = {
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
    "wsl2BasedEngine": True,
    "useWsl2": True,
    "backend": "wsl-2",
    "showSystemContainers": False,
    "showInlineVolumeNavigation": False,
    "dataRoot": "",
    "source": "",
    "windowsFeatures": {
        "Wsl2": True,
        "HyperV": False,
        "ContainerD": False,
        "DockerVsShim": False,
        "ClientGuarded": False
    },
    "fileShares": [
        "D:\\Work",
        "C:\\Users"
    ],
    "dockerDaemon": {
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
    },
    "kubernetes": {
        "enabled": False
    },
    "shell": "powershell",
    "stackOrchestrator": "swarm",
    "lastLoginDate": 1760000000.0,
    "sendMetrics": False,
    "sendMetricsTitleBar": False,
    "analytics": False,
    "autoupdate": True,
    "checkForUpdates": True,
    "language": "en-US",
    "openUIOnStartup": False,
    "showMenus": True,
    "showActions": True,
    "showStartNav": True,
    "showTaskbarIcon": True,
    "theme": "dark",
    "virtualMachine": {
        " WSL2.enabled": True,
        "Wsl2.enabled": True,
        "wsl2.enabled": True
    }
}

settings_path = os.path.join(settings_dir, "settings.json")
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
print(f"   ✅ Created: {settings_path}")

# Also write daemon.json
daemon_path = os.path.expanduser(r"~\.docker\daemon.json")
daemon_dir = os.path.dirname(daemon_path)
if not os.path.exists(daemon_dir):
    os.makedirs(daemon_dir)

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
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}

with open(daemon_path, 'w') as f:
    json.dump(daemon, f, indent=2)
print(f"   ✅ Updated: {daemon_path}")

# ─── 6. Check WSL version + capabilities ─────────────────────────────────────────-
print("\n5. WSL version:")
time.sleep(2)
r = subprocess.run(["wsl", "--version"], capture_output=True, text=True, timeout=10)
print(f"   {r.stdout[:300] if r.stdout else r.stderr[:200]}")

# ─── 7. Restart Docker Desktop ─────────────────────────────────────────────────────
print("\n6. Restarting Docker Desktop after config fix:")
for proc in ["Docker Desktop.exe", "dockerd.exe", "com.docker.proxy.exe", "vmmem.exe"]:
    subprocess.run(["taskkill", "/IM", proc, "/F", "/T"], capture_output=True, text=True, timeout=5)
time.sleep(5)

docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
if os.path.exists(docker_exe):
    subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"   Launched Docker Desktop — waiting 120s...")
    
    for i in range(24):
        time.sleep(5)
        r = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            print(f"   ✅ Docker Server: {r.stdout.strip()}")
            break
        if i % 6 == 5:
            print(f"   Waiting... ({i+1}/24)")
else:
    print(f"   ❌ Docker Desktop.exe not found")

# ─── 8. Final check ────────────────────────────────────────────────────────────────
print("\n7. Final check:")
time.sleep(10)
try:
    r = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=8)
    if r.returncode == 0:
        print("   ✅ docker info: OK")
        for line in r.stdout.split("\n"):
            if any(k in line for k in ["Server Version", "Storage Driver", "Operating System", "Docker Root Dir"]):
                print(f"   {line.strip()}")
    else:
        print(f"   ❌ docker info: {r.stderr[:120]}")
except:
    print("   ❌ docker info timeout")

# Port check
time.sleep(3)
r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--connect-timeout", "3", "http://localhost:2375/_ping"],
    capture_output=True, text=True, timeout=5)
print(f"   Port 2375: HTTP {r.stdout.strip()}")

print(f"\n{'='*60}")
os.remove(__file__)
