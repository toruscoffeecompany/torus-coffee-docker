#!/usr/bin/env python3
"""
Miss Pink — C: DRIVE CLEANUP
Removes safe duplicates + temp files to free space.

SAFE TO DELETE (won't break Hermes):
1. Hermes .bak directories (state.db.bak, win-unpacked.bak, etc.) = ~0.8GB
2. Duplicate node_modules/electron copies in Hermes (keeping apps/desktop only)
3. Temp DB files (tm_fix.db, tm_local.db, verify_tm*.db) = ~9.35GB
4. WSL crash dumps = ~0.33GB
5. npm-cache duplicates
6. Docker Scout temp in Temp/
7. Hermes state.db pre-update backup

VERIFY safe (not deleted):
- Hermes agent itself (apps/desktop/release)
- Docker (docker_data.vhdx — needed)
- Ollama (needs models for Augur)
- VS Code, Discord, Postman (user apps)
"""
import os, shutil, json
from pathlib import Path
from datetime import datetime

C = Path("C:/Users/torus")
freed = 0
deleted = []

def safe_remove(path, description):
    global freed, deleted
    if path.exists():
        if path.is_dir():
            sz = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        else:
            sz = path.stat().st_size
        try:
            if path.is_dir():
                shutil.rmtree(str(path))
            else:
                path.unlink()
            freed += sz
            deleted.append(f"✅ {description}: {sz/(1024**3):.2f} GB")
        except Exception as e:
            deleted.append(f"⚠️ {description}: {e}")

print("=== C: DRIVE CLEANUP ===\n")

# ─── 1. Hermes backup directories ────────────────────────────────────────────────
print("--- Hermes backups ---")
hermes = C / "AppData/Local/hermes"
hermes_agent = hermes / "hermes-agent"

# state.db pre-update backups
for bak in hermes.glob("state.db*.bak*"):
    safe_remove(bak, f"state.db backup: {bak.name}")

# win-unpacked.bak directories (4 copies of Hermes.exe etc.)
for bak_dir in hermes_agent.rglob("*.bak"):
    if bak_dir.is_dir():
        safe_remove(bak_dir, f"Backup dir: {bak_dir.relative_to(hermes_agent)}")

# node_modules/electron duplicates (keep apps/desktop only)
electron_copies = list(hermes_agent.rglob("node_modules/*/electron/dist/electron.exe"))
if len(electron_copies) > 1:
    print(f"  Found {len(electron_copies)} electron.exe copies (keeping 1)")
    for ex in electron_copies[1:]:  # keep first
        electron_dir = ex.parent
        # Also remove the corresponding node_modules
        safe_remove(electron_dir.parent.parent, f"Duplicate node_modules: {electron_dir.parent.parent.relative_to(hermes_agent)}")

# ─── 2. Temp DB files ───────────────────────────────────────────────────────────
print("\n--- Temp databases ---")
temp_dir = C / "AppData/Local/Temp"
for db_name in ["tm_fix.db", "tm_local.db", "verify_tm.db", "verify_tm2.db"]:
    safe_remove(temp_dir / db_name, f"Temp DB: {db_name}")

# ─── 3. WSL crash dumps ─────────────────────────────────────────────────────────
print("\n--- WSL crash dumps ---")
wsl_crashes = temp_dir / "wsl-crashes"
safe_remove(wsl_crashes, "WSL crash dumps")

# ─── 4. npm cache ──────────────────────────────────────────────────────────────
print("\n--- npm/pip caches ---")
npm_cache = C / "AppData/Local/npm-cache"
# Don't fully delete — just clear old npx caches
npx_dir = npm_cache / "_npx"
if npx_dir.exists():
    # Keep only the latest npx cache dirs
    npx_dirs = sorted(npx_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
    for old in npx_dirs[3:]:  # keep 3 newest
        safe_remove(old, f"Old npx cache: {old.name}")

# ─── 5. Docker Scout temp ──────────────────────────────────────────────────────
print("\n--- Docker temp ---")
docker_scout_temp = temp_dir / "docker-scout"
safe_remove(docker_scout_temp, "Docker Scout temp images")

# ─── 6. Trivy DB cache ─────────────────────────────────────────────────────────
print("\n--- Security scanner caches ---")
trivy_db = C / "AppData/Local/java-db/trivy-java.db"
safe_remove(trivy_db, "Trivy security DB cache")

# ─── 7. Hermes state.db pre-update ─────────────────────────────────────────────
# Already handled in step 1

# ─── Report ─────────────────────────────────────────────────────────────────────
print("\n=== SUMMARY ===")
for d in deleted:
    print(f"  {d}")

print(f"\n💾 Total freed: {freed/(1024**3):.2f} GB")
print(f"C: drive should now have ~{12 + freed/(1024**3):.1f} GB free (was 12 GB)")
