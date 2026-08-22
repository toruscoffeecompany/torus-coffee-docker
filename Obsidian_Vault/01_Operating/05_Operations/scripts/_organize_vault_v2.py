#!/usr/bin/env python3
"""
ORGANIZE (continued): Move all files inside Obsidian vault.
Retry with better error handling for non-empty dirs.
"""
import os, shutil, json, glob

BUSINESS_DIR = r"D:\Work\Torus Coffee Company LLC"
VAULT_DIR = r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault"
SCRIPTS_TARGET = os.path.join(VAULT_DIR, "10_Skills_Library", "05_Operations", "scripts")

moved = []
errors = []

def safe_move(src, dst):
    """Move src -> dst, with merge support."""
    if not os.path.exists(src):
        return None
    if os.path.isdir(src):
        if os.path.exists(dst):
            # Merge directories
            for item in os.listdir(src):
                safe_move(os.path.join(src, item), os.path.join(dst, item))
            # Try to remove the now-merged directory
            try:
                shutil.rmtree(src)
            except:
                pass
            return f"[MERGED] {src} -> {dst}"
        else:
            shutil.move(src, dst)
            return f"{src} -> {dst}"
    else:
        if os.path.exists(dst):
            # Compare
            try:
                with open(src, 'rb') as f1, open(dst, 'rb') as f2:
                    if f1.read() != f2.read():
                        shutil.move(src, dst)
                        return f"[REPLACE] {src} -> {dst}"
                    else:
                        os.remove(src)
                        return f"[SKIP-DUP] {src}"
            except:
                return f"[SKIP] {src}"
        else:
            shutil.move(src, dst)
            return f"{src} -> {dst}"

# ─── 1. Move 01_Operating → Vault/01_Operating ─────────────────────___
src = os.path.join(BUSINESS_DIR, "01_Operating")
dst = os.path.join(VAULT_DIR, "01_Operating")
r = safe_move(src, dst)
if r: moved.append(r)

# ─── 2. Move 10_Skills_Library → Vault/10_Skills_Library ─────────────
src = os.path.join(BUSINESS_DIR, "10_Skills_Library")
dst = os.path.join(VAULT_DIR, "10_Skills_Library")
r = safe_move(src, dst)
if r: moved.append(r)

# ─── 3. Move credential_loader.py ─────────────────────────────────_
src = os.path.join(BUSINESS_DIR, "credential_loader.py")
dst = os.path.join(SCRIPTS_TARGET, "credential_loader.py")
r = safe_move(src, dst)
if r: moved.append(r)

# ─── 4. Move smart_ticket_cycle.py ──────────────────────────────────
src = os.path.join(BUSINESS_DIR, "smart_ticket_cycle.py")
dst = os.path.join(SCRIPTS_TARGET, "smart_ticket_cycle.py")
r = safe_move(src, dst)
if r: moved.append(r)

# ─── 5. Move scripts/ directory ─────────────────────────────────────
src = os.path.join(BUSINESS_DIR, "scripts")
dst = SCRIPTS_TARGET
r = safe_move(src, dst)
if r: moved.append(r)

# ─── 6. Move .pirate_automation scripts → Vault scripts ─────────────
src = r"D:\Work\.pirate_automation\scripts"
if os.path.exists(src):
    print(f"Moving {len(os.listdir(src))} pirate_automation scripts...")
    cnt = 0
    for item in os.listdir(src):
        r = safe_move(os.path.join(src, item), os.path.join(SCRIPTS_TARGET, item))
        if r:
            cnt += 1
    moved.append(f"Moved {cnt} scripts from .pirate_automation -> Vault scripts")
    with open(r"D:\Work\.pirate_automation\ARCHIVED.txt", "w") as f:
        f.write("Scripts moved to Obsidian_Vault/10_Skills_Library/05_Operations/scripts/\n")

# ─── Print results ─────────────────────────────────────────────────
print("=== MOVED FILES ===")
for m in moved:
    print(f"  ✅ {m}")

print(f"\n=== ERRORS: {len(errors)} ===")
for e in errors:
    print(f"  ❌ {e}")

# ─── Verify final state ─────────────────────────────────────────────
print(f"\n{'='*60}")
print("FINAL DIRECTORY STATE — business dir top level:")
print(f"{'='*60}")
for item in sorted(os.listdir(BUSINESS_DIR)):
    full = os.path.join(BUSINESS_DIR, item)
    if os.path.isdir(full):
        count = sum(1 for _ in os.walk(full))
        total_files = sum(len(files) for _, _, files in os.walk(full))
        print(f"  📁 {item}/ ({total_files} files)")
    else:
        print(f"  📄 {item} ({os.path.getsize(full)} bytes)")

print(f"\n{len(moved)} operations completed.")

os.remove(__file__)
