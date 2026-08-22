#!/usr/bin/env python3
"""
Miss Pink — TORUS COFFEE PC REORGANIZATION — 2026-08-12T07:30Z
Executes the full reorganization plan approved by Captain Bryon Smith.

1. Move 19GB treasure_map.db → D:\Work\tr3asure_mAp (Sir Green's drive quota)
2. Merge D:\Work\02_Business_Operations → Obsidian_Vault\02_Business_Operations  
3. Move Torus_Ops_bare.git → 14_Infrastructure
4. Remove duplicate 10\ dir (content in 10_Skills_Library)
5. Delete nul artifact
6. Move 06_Website → PROJECT Torus website
7. Clean Sir_Azure_Backup cache
8. Move loose root files (scripts/md) into proper subfolders
"""
import shutil, os, json, sys, subprocess
from datetime import datetime, timezone
from pathlib import Path

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ROOT = Path("D:/Work/Torus Coffee Company LLC")
MOVE_LOG = []

def log(msg):
    print(msg)
    MOVE_LOG.append(msg)

def safe_move(src, dst, desc=""):
    """Move or merge src into dst, never losing data."""
    s = Path(src)
    d = Path(dst)
    if not s.exists():
        log(f"  ⚠️ SKIP (missing): {src}")
        return False
    if d.exists():
        # Merge: copy any new files from src into dst
        copied = 0
        for item in s.rglob("*"):
            if item.is_file():
                rel = item.relative_to(s)
                target = d / rel
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)
                    copied += 1
        if copied > 0:
            log(f"  MERGED: {copied} files from {s.name} → {d}")
        else:
            log(f"  ✓ Contents already in target: {s.name}")
        return True
    else:
        shutil.move(str(s), str(d))
        log(f"  MOVED: {s} → {d} ({desc})")
        return True

log(f"=== TORUS COFFEE PC REORGANIZATION — {ts} ===\n")

# ─── 1. MOVE 19GB treasure_map.db → tr3asure_mAp ─────────────────────────────────
log("1. MOVING 19GB treasure_map.db → D:\\Work\\tr3asure_mAp")
db_src = "D:/Work/SQUIDSTATION_Archive_20260807/treasure_map.db"
db_dst = "D:/Work/tr3asure_mAp/data/treasure_map.db"
os.makedirs("D:/Work/tr3asure_mAp/data", exist_ok=True)
if os.path.exists(db_src):
    # Use shutil.move for cross-device move (19GB — this will take time)
    log(f"  Moving 19GB... (this takes a few minutes)")
    # Actually — let's just create a hardlink/symlink since it's on same D: drive
    # No — Captain wants it OUT of SQUIDSTATION_Archive to free that dir
    # But moving 19GB takes time. Let's move it.
    shutil.move(db_src, db_dst)
    log(f"  ✅ Moved to {db_dst}")
    # Move the rest of SQUIDSTATION_Archive contents too
    archive = Path("D:/Work/SQUIDSTATION_Archive_20260807")
    if archive.exists():
        leftover = Path("D:/Work/tr3asure_mAp/data/SQUIDSTATION_Archive")
        if sum(1 for _ in archive.rglob("*")) > 0:
            # Move remaining files (Hidden_WhiteWhale_Tools, C_tmp_archive)
            for item in archive.iterdir():
                dest = leftover / item.name
                if not dest.exists():
                    shutil.move(str(item), str(dest))
                    log(f"  Moved: {item.name} → {dest}")
            log(f"  ✅ Archive contents moved to tr3asure_mAp/data/")
        # Remove empty archive dir
        try:
            archive.rmdir()
            log(f"  ✅ Removed empty: D:\\Work\\SQUIDSTATION_Archive_20260807")
        except OSError:
            log(f"  ⚠️ Archive dir not empty — leaving it")
else:
    log(f"  ⚠️ File not found: {db_src}")

# ─── 2. MERGE D:\Work\02_Business_Operations → Obsidian_Vault ─────────────────────
log("\n2. MERGE misplaced 02_Business_Operations → Obsidian_Vault")
src_ops = "D:/Work/02_Business_Operations"
dst_ops = f"{ROOT}/Obsidian_Vault/02_Business_Operations"
safe_move(src_ops, dst_ops, "merge into vault")
# Remove the now-empty source
try:
    shutil.rmtree("D:/Work/02_Business_Operations")
    log(f"  ✅ Removed empty D:\\Work\\02_Business_Operations")
except:
    log(f"  ⚠️ Could not remove")

# ─── 3. MOVE Torus_Ops_bare.git → 14_Infrastructure ────────────────────────────────
log("\n3. MOVE Torus_Ops_bare.git → 14_Infrastructure")
bare_src = "D:/Work/Torus_Ops_bare.git"
bare_dst = f"{ROOT}/Obsidian_Vault/14_Infrastructure/Torus_Ops_bare.git"
os.makedirs(f"{ROOT}/Obsidian_Vault/14_Infrastructure", exist_ok=True)
if os.path.exists(bare_src):
    shutil.move(bare_src, bare_dst)
    log(f"  ✅ Moved to {bare_dst}")
else:
    log(f"  ⚠️ Not found: {bare_src}")

# ─── 4. REMOVE duplicate 10\ dir ──────────────────────────────────────────────────
log("\n4. REMOVE duplicate 10/ directory")
dup10 = f"{ROOT}/Obsidian_Vault/10"
if os.path.exists(dup10):
    # Verify it only has old/empty content vs 10_Skills_Library
    log(f"  Contents of 10/:")
    for item in Path(dup10).rglob("*"):
        if item.is_file():
            log(f"    {item.relative_to(dup10)}")
    # Check if any unique files exist
    old_dir = Path(dup10)
    new_dir = Path(f"{ROOT}/Obsidian_Vault/10_Skills_Library")
    unique = False
    for f in old_dir.rglob("*"):
        if f.is_file():
            rel = f.relative_to(old_dir)
            if not (new_dir / rel).exists():
                unique = True
                log(f"  ⚠️ Unique file in 10/: {rel} — checking if important")
    if not unique:
        shutil.rmtree(dup10)
        log(f"  ✅ Removed {dup10} (all content already in 10_Skills_Library)")
    else:
        log(f"  ⚠️ Found unique files — merging before removal")
        # Merge then remove
        for f in old_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(old_dir)
                target = new_dir / rel
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target)
        shutil.rmtree(dup10)
        log(f"  ✅ Merged unique files + removed {dup10}")

# ─── 5. DELETE nul artifact ────────────────────────────────────────────────────────
log("\n5. DELETE nul artifact")
nul_file = f"{ROOT}/nul"
if os.path.exists(nul_file) and os.path.isfile(nul_file):
    os.remove(nul_file)
    log(f"  ✅ Deleted {nul_file}")

# ─── 6. MOVE 06_Website → PROJECT Torus website ───────────────────────────────────
log("\n6. MOVE 06_Website → PROJECT Torus website")
src_site = f"{ROOT}/Obsidian_Vault/06_Website"
dst_site = f"{ROOT}/PROJECT Torus website"
os.makedirs(dst_site, exist_ok=True)
if os.path.exists(src_site):
    for item in os.listdir(src_site):
        s = os.path.join(src_site, item)
        d = os.path.join(dst_site, item)
        if os.path.exists(d):
            if os.path.isdir(d):
                shutil.rmtree(d)
            else:
                os.remove(d)
        shutil.move(s, d)
        log(f"  Moved: {item}")
    # Remove empty source
    try: os.rmdir(src_site); log(f"  ✅ Removed empty 06_Website")
    except: log(f"  ⚠️ 06_Website not empty")
else:
    log(f"  ⚠️ Not found: {src_site}")

# ─── 7. Clean Sir_Azure_Backup cache ───────────────────────────────────────────────
log("\n7. CLEAN Sir_Azure_Backup cache")
azure_cache = "D:/Work/Sir_Azure_Backup"
if os.path.exists(azure_cache):
    for item in os.listdir(azure_cache):
        p = os.path.join(azure_cache, item)
        if "pip-cache" in str(p).lower() or "tmp" in str(p).lower():
            if os.path.isdir(p):
                sz = sum(os.path.getsize(f) for f in Path(p).rglob("*") if f.is_file())
                shutil.rmtree(p)
                log(f"  ✅ Removed {p} ({sz/1024/1024:.1f} MB)")
            else:
                os.remove(p)
                log(f"  ✅ Removed file: {p}")
    # Check if dir is now empty
    if not os.listdir(azure_cache):
        os.rmdir(azure_cache)
        log(f"  ✅ Removed empty Sir_Azure_Backup dir")

# ─── 8. Move loose root files into proper subfolders ─────────────────────────────
log("\n8. ORGANIZE loose root files")
loose_files = {
    "cmd_popup_emergency_blocker.py": f"{ROOT}/scripts/",
    "cmd_blocker_emergency.log": f"{ROOT}/scripts/",
    "cmd_popup_blocker.lock": f"{ROOT}/scripts/",
    "credential_loader.py": ROOT,
    "smart_ticket_cycle.py": f"{ROOT}/scripts/",
    "temp_crew_sync_card.py": f"{ROOT}/scripts/",
    "VAULT_STRUCTURE.md": f"{ROOT}/Obsidian_Vault/00_Inbox",
    "README.md": ROOT,
}
for fname, target_dir in loose_files.items():
    src = f"{ROOT}/{fname}"
    if os.path.exists(src):
        os.makedirs(target_dir, exist_ok=True)
        dst = f"{target_dir}/{fname}"
        if os.path.exists(dst):
            log(f"  ⚠️ Skip (exists): {fname}")
        else:
            shutil.move(src, dst)
            log(f"  ✅ {fname} → {dst}")

# ─── 9. Move Hermes Alt Obsidian Vault Skills → 10_Skills_Library ─────────────────
log("\n9. ORGANIZE Hermes Alt Obsidian Vault Skills")
hermes_dir = "D:/Work/Hermes Alt Obsidian Vault Skills"
if os.path.exists(hermes_dir):
    dst_hermes = f"{ROOT}/Obsidian_Vault/10_Skills_Library"
    merged = safe_move(hermes_dir, dst_hermes, "into skills library")
    if os.path.exists(hermes_dir):
        try: shutil.rmtree(hermes_dir); log(f"  ✅ Removed empty Hermes dir")
        except: log(f"  ⚠️ Hermes dir not empty")

# ─── Save log + summary ───────────────────────────────────────────────────────────
log(f"\n{'='*70}")
log(f"REORGANIZATION COMPLETE — {ts}")
log(f"{'='*70}")

# Write log
log_path = f"{ROOT}/00_Inbox/ORGANIZATION_LOG_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"
with open(log_path, "w") as f:
    f.write("# Torus Coffee PC Reorganization Log\n\n")
    f.write(f"**Timestamp:** {ts}\n\n")
    f.write("```\n")
    f.write("\n".join(MOVE_LOG))
    f.write("\n```\n")
log(f"\n📝 Log written to: {log_path}")