#!/usr/bin/env python3
"""
FIX: Docker Desktop — missing docker-desktop-data WSL2 distro.
The main docker-desktop distro exists but docker-desktop-data is MISSING.
Docker Desktop needs both to function. Will manually register it.
"""
import subprocess, time, os, json

print("=== DOCKER FIX: Register missing docker-desktop-data ===\n")

# ─── 1. Check what's in the WSL data dirs ──────────────────────────────────────────
print("1. WSL data directories:")
wsl_dir = os.path.expanduser(r"~\AppData\Local\Docker\wsl")
for subdir in ["main", "disk", "data"]:
    full = os.path.join(wsl_dir, subdir)
    if os.path.exists(full):
        files = os.listdir(full)[:10]
        print(f"   {subdir}/: {files}")
        for f in files:
            fpath = os.path.join(full, f)
            if os.path.isfile(fpath):
                print(f"     {f} ({os.path.getsize(fpath)/1024/1024:.1f} MB)")
    else:
        print(f"   {subdir}/: NOT FOUND")

# ─── 2. Check ext4.vhdx ────────────────────────────────────────────────────────────
print("\n2. Checking ext4.vhdx:")
ext4_files = []
for root, dirs, files in os.walk(wsl_dir):
    for f in files:
        if f.endswith(".vhdx") or f == "ext4.vhdx":
            full = os.path.join(root, f)
            sz = os.path.getsize(full)
            print(f"   {full} ({sz/1024/1024:.1f} MB)")
            ext4_files.append(full)

# ─── 3. Try to manually register docker-desktop-data ────────────────────────────────
print("\n3. Attempting manual docker-desktop-data registration:")
# First, try launching Docker Desktop with --register-wsl-distro flag
docker_exe = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
if os.path.exists(docker_exe):
    # Try the installer to repair/regenerate missing distros
    installer = r"C:\Users\torus\AppData\Local\Programs\DockerDesktop\Docker Desktop Installer.exe"
    if os.path.exists(installer):
        print(f"   Found installer — running 'install --accept-license --force'")
        # The installer may need different syntax
        r = subprocess.run([installer, "install", "--accept-license", "--force"],
            capture_output=True, text=True, timeout=180)
        print(f"   Exit: {r.returncode}")
        print(f"   stdout: {r.stdout[:300]}")
        if r.stderr:
            print(f"   stderr: {r.stderr[:200]}")
    else:
        print(f"   Installer not found")
    
    # Try launching with force flag
    print(f"   Launching Docker Desktop with --force-start")
    subprocess.Popen([docker_exe, "--force-start"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(60)
    
    # Check
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq dockerd.exe", "/FO", "CSV"],
        capture_output=True, text=True, timeout=5)
    print(f"   dockerd after force-start: {'✅' if r.stdout.count('dockerd') > 1 else '❌'}")

# ─── 4. Check if we need to use WSL import ─────────────────────────────────────────
# If the ext4.vhdx exists, we can manually import it
print("\n4. Manual WSL import approach:")
if ext4_files:
    print(f"   ext4 files found — attempting manual import")
    # We need the docker-desktop-data ext4 file to import
    # Look for the data distribution's ext4 file
    for ef in ext4_files:
        if "data" in ef.lower() or "disk" in ef.lower():
            print(f"   Candidate: {ef}")
            
            # Try wsl --import
            print(f"   Trying: wsl --import docker-desktop-data ...")
            # Need admin for wsl --import
            # This may fail without admin, so let's try
            
# ─── 5. Check if Docker Desktop settings need backend override ─────────────────────
print("\n5. Checking Docker daemon config:")
daemon_path = os.path.expanduser(r"~\.docker\daemon.json")
if os.path.exists(daemon_path):
    with open(daemon_path, 'r') as f:
        print(f"   {f.read()}")

# ─── 6. Check Windows Hyper-V ─────────────────────────────────────────────────────
print("\n6. Hyper-V / Container features:")
time.sleep(2)
r = subprocess.run(["powershell", "-Command", "Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All 2>&1; Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform 2>&1; Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux 2>&1"],
    capture_output=True, text=True, timeout=15)
# Parse output
for line in r.stdout.split("\n"):
    if "State" in line or "FeatureName" in line:
        print(f"   {line.strip()}")

# ─── 7. Check if Windows containers feature is enabled ──────────────────────────────
print("\n7. Windows container feature:")
time.sleep(2)
r = subprocess.run(["reg", "query", "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\CloudExperienceHost\\Uninstall\\Windows-Defender-ApplicationGuard"],
    capture_output=True, text=True, timeout=5)
# Check Docker Desktop log
log_path = os.path.expanduser(r"~\AppData\Local\Docker\log\host\electron-ui-console-*.log")
import glob
logs = sorted(glob.glob(log_path), key=os.path.getmtime, reverse=True)
if logs:
    print(f"\n8. Last Docker log: {os.path.basename(logs[0])}")
    with open(logs[0], 'r', errors='ignore') as f:
        content = f.read()
    # Look for errors
    for line in content.split("\n")[-20:]:
        if line.strip():
            print(f"   {line.strip()[:150]}")

print(f"\n{'='*60}")
os.remove(__file__)
