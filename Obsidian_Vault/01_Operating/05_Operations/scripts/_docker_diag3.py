#!/usr/bin/env python3
"""
Diagnose Docker Desktop startup — GUI running but engine not starting.
Check WSL2, logs, and try to manually start the backend.
"""
import subprocess, time, os, json

print("=== DOCKER DESKTOP DIAGNOSTIC ===\n")

# ─── 1. Check WSL2 distro status ────────────────────────────────────────────────
print("1. WSL2 distro status:")
time.sleep(2)
r = subprocess.run(["wsl", "list", "--verbose"], capture_output=True, text=True, timeout=10)
print(f"   {r.stdout[:400] if r.stdout else f'stderr: {r.stderr[:200]}'}")

# ─── 2. Check docker-desktop WSL distro ───────────────────────────────────────────
print("\n2. Docker Desktop WSL2 distro:")
time.sleep(2)
r = subprocess.run(["wsl", "list", "--verbose"], capture_output=True, text=True, timeout=10)
if "docker-desktop" in r.stdout.lower():
    print("   ✅ docker-desktop distro registered")
    for line in r.stdout.split("\n"):
        if "docker-desktop" in line.lower():
            print(f"   {line.strip()}")
else:
    print("   ❌ docker-desktop distro NOT registered")
    # Try to register it
    print("   Trying to register docker-desktop via Docker Desktop...")

# ─── 3. Check Docker log files ────────────────────────────────────────────────────
print("\n3. Docker log files:")
log_dirs = [
    os.path.expanduser(r"~\AppData\Local\Docker\log"),
    os.path.expanduser(r"~\AppData\Local\Docker\log\host"),
]
for d in log_dirs:
    if os.path.exists(d):
        for f in sorted(os.listdir(d), key=lambda x: os.path.getmtime(os.path.join(d, x)), reverse=True):
            fpath = os.path.join(d, f)
            if os.path.isfile(fpath) and f.endswith(".log"):
                mtime = os.path.getmtime(fpath)
                age = time.time() - mtime
                if age < 3600:  # Last hour
                    size = os.path.getsize(fpath)
                    print(f"   {f} ({size/1024:.0f} KB, {age:.0f}s ago)")
                    # Read last 500 chars
                    try:
                        with open(fpath, 'r', errors='ignore') as fh:
                            content = fh.read()
                        tail = content[-500:] if len(content) > 500 else content
                        print(f"     ...{tail}")
                    except:
                        pass

# ─── 4. Check if Docker Desktop settings.json exists ──────────────────────────────
print("\n4. Docker settings:")
settings_paths = [
    os.path.expanduser(r"~\AppData\Roaming\Docker\settings.json"),
    os.path.expanduser(r"~\AppData\Local\Docker\settings.json"),
]
for p in settings_paths:
    if os.path.exists(p):
        print(f"   ✅ Found: {p}")
        try:
            with open(p, 'r') as f:
                settings = json.load(f)
            # Check key settings
            for k in ["wsl2BasedEngine", "useWsl2", "backend", "showSystemContainers", "dataRoot"]:
                if k in settings:
                    print(f"   {k}: {settings[k]}")
        except json.JSONDecodeError:
            print(f"   ⚠️ Invalid JSON: {p}")
    else:
        print(f"   ❌ Not found: {p}")

# ─── 5. Check WSL feature status ──────────────────────────────────────────────────
print("\n5. WSL features:")
time.sleep(2)
r = subprocess.run(["wsl", "list"], capture_output=True, text=True, timeout=10)
print(f"   wsl list: {r.stdout[:300] if r.stdout else r.stderr[:200]}")

# ─── 6. Check Docker process tree ─────────────────────────────────────────────────
print("\n6. Docker process tree:")
time.sleep(2)
r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Docker Desktop.exe", "/V", "/FO", "CSV"],
    capture_output=True, text=True, timeout=5)
if r.stdout.count("Docker Desktop") > 1:
    print("   ✅ Docker Desktop.exe running")
else:
    print("   ❌ Docker Desktop.exe NOT running")
    
    # Relaunch it
    docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
    if os.path.exists(docker_exe):
        print(f"   Launching: {docker_exe}")
        subprocess.Popen([docker_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("   Launched — waiting 60s...")
        time.sleep(60)

# ─── 7. Wait + retry docker commands ──────────────────────────────────────────────
print("\n7. Retrying Docker commands (30s wait):")
for i in range(6):
    time.sleep(5)
    # Use shorter timeout for each check
    try:
        r = subprocess.run(["docker", "version"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            print(f"   ✅ docker version OK: {r.stdout[:80]}")
            break
    except subprocess.TimeoutExpired:
        print(f"   Timeout ({i+1}/6)")
    except:
        print(f"   Error ({i+1}/6)")

# ─── 8. Check named pipe ──────────────────────────────────────────────────────────
print("\n8. Docker named pipe:")
time.sleep(2)
r = subprocess.run(["curl", "-s", "--connect-timeout", "5", "http://localhost:2375/version"],
    capture_output=True, text=True, timeout=8)
if r.returncode == 0 and r.stdout:
    print(f"   Port 2375: ✅ responding")
    print(f"   {r.stdout[:150]}")
else:
    print(f"   Port 2375: ❌ not responding")

print(f"\n{'='*60}")
os.remove(__file__)
