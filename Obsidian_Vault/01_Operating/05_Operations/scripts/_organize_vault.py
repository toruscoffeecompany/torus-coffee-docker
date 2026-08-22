#!/usr/bin/env python3
"""
ORGANIZE: Move all files inside Obsidian vault (D:/Work/Torus Coffee Company LLC/Obsidian_Vault/).
Files outside vault but inside business dir need relocation:
1. D:/Work/Torus Coffee Company LLC/Obsidian_Vault/01_Operating/ -> Vault/01_Operating/
2. D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/ -> Vault/10_Skills_Library/
3. credential_loader.py -> Vault/10_Skills_Library/05_Operations/scripts/
4. smart_ticket_cycle.py -> Vault/10_Skills_Library/05_Operations/scripts/
5. D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ -> Vault/10_Skills_Library/05_Operations/scripts/
6. D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ -> Vault/10_Skills_Library/05_Operations/scripts/
"""
import os, shutil, json, glob

BUSINESS_DIR = r"D:\Work\Torus Coffee Company LLC"
VAULT_DIR = r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault"
SCRIPTS_TARGET = os.path.join(VAULT_DIR, "10_Skills_Library", "05_Operations", "scripts")
OPS_SCRIPTS_EXIST = os.path.join(VAULT_DIR, "10_Skills_Library", "05_Operations", "scripts")

os.makedirs(SCRIPTS_TARGET, exist_ok=True)
os.makedirs(os.path.join(VAULT_DIR, "01_Operating"), exist_ok=True)
os.makedirs(os.path.join(VAULT_DIR, "10_Skills_Library"), exist_ok=True)

moved = []
errors = []

# ─── 1. Move 01_Operating → Vault/01_Operating ─────────────────────___
src = os.path.join(BUSINESS_DIR, "01_Operating")
dst = os.path.join(VAULT_DIR, "01_Operating")
if os.path.exists(src):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d):
            # Merge
            if os.path.isdir(d):
                shutil.copytree(s, d, dirs_exist_ok=True)
                moved.append(f"[MERGE] {s} -> {d}")
            else:
                # Compare + only copy if different
                try:
                    with open(s, 'rb') as f1, open(d, 'rb') as f2:
                        if f1.read() != f2.read():
                            shutil.move(s, d)
                            moved.append(f"[REPLACE] {s} -> {d}")
                except:
                    moved.append(f"[SKIP] {s} — existing file")
        else:
            shutil.move(s, d)
            moved.append(f"{s} -> {d}")

# ─── 2. Move 10_Skills_Library → Vault/10_Skills_Library ─────────────
src = os.path.join(BUSINESS_DIR, "10_Skills_Library")
dst = os.path.join(VAULT_DIR, "10_Skills_Library")
if os.path.exists(src):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d):
            if os.path.isdir(d):
                shutil.copytree(s, d, dirs_exist_ok=True)
                moved.append(f"[MERGE] {s} -> {d}")
            else:
                try:
                    with open(s, 'rb') as f1, open(d, 'rb') as f2:
                        if f1.read() != f2.read():
                            shutil.move(s, d)
                            moved.append(f"[REPLACE] {s} -> {d}")
                except:
                    moved.append(f"[SKIP] {s}")
        else:
            shutil.move(s, d)
            moved.append(f"{s} -> {d}")

# ─── 3. Move credential_loader.py ─────────────────────────────────_
src = os.path.join(BUSINESS_DIR, "credential_loader.py")
dst = os.path.join(SCRIPTS_TARGET, "credential_loader.py")
if os.path.exists(src):
    shutil.move(src, dst)
    moved.append(f"{src} -> {dst}")

# ─── 4. Move smart_ticket_cycle.py ──────────────────────────────────
src = os.path.join(BUSINESS_DIR, "smart_ticket_cycle.py")
dst = os.path.join(SCRIPTS_TARGET, "smart_ticket_cycle.py")
if os.path.exists(src):
    shutil.move(src, dst)
    moved.append(f"{src} -> {dst}")

# ─── 5. Move scripts/ directory ─────────────────────────────────────
src = os.path.join(BUSINESS_DIR, "scripts")
dst = SCRIPTS_TARGET
if os.path.exists(src):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d):
            try:
                with open(s, 'rb') as f1, open(d, 'rb') as f2:
                    if f1.read() != f2.read():
                        shutil.move(s, d)
                        moved.append(f"[REPLACE] {s} -> {d}")
                    else:
                        os.remove(s)
                        moved.append(f"[SKIP-DUP] {s}")
            except:
                moved.append(f"[SKIP] {s}")
        else:
            shutil.move(s, d)
            moved.append(f"{s} -> {d}")
    os.rmdir(src)
    moved.append(f"Removed empty dir: {src}")

# ─── 6. Move .pirate_automation scripts → Vault scripts ─────────────
src = r"D:\Work\.pirate_automation\scripts"
if os.path.exists(src):
    print(f"Found {len(os.listdir(src))} pirate_automation scripts")
    count = 0
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(SCRIPTS_TARGET, item)
        if os.path.exists(d):
            try:
                with open(s, 'rb') as f1, open(d, 'rb') as f2:
                    if f1.read() != f2.read():
                        shutil.move(s, d)
                        count += 1
                    else:
                        os.remove(s)
            except:
                pass
        else:
            shutil.move(s, d)
            count += 1
    moved.append(f"Moved {count} scripts from .pirate_automation -> Vault scripts")
    # Keep the .pirate_automation dir but mark as cleaned
    with open(r"D:\Work\.pirate_automation\ARCHIVED.txt", "w") as f:
        f.write("Scripts moved to Obsidian_Vault/10_Skills_Library/05_Operations/scripts/\n")

# ─── 7. Clean up empty top-level dirs ─────────────────────────────────
for cleanup in ["01_Operating", "10_Skills_Library", "scripts"]:
    path = os.path.join(BUSINESS_DIR, cleanup)
    if os.path.exists(path) and not os.listdir(path):
        os.rmdir(path)
        moved.append(f"Removed empty dir: {path}")

# Print results
print("=== MOVED FILES ===")
for m in moved:
    print(f"  ✅ {m}")

print(f"\n=== ERRORS: {len(errors)} ===")
for e in errors:
    print(f"  ❌ {e}")

# ─── Verify final state ─────────────────────────────────────────────
print(f"\n{'='*60}")
print("FINAL DIRECTORY STATE — D:/Work/Torus Coffee Company LLC:")
print(f"{'='*60}")
for item in sorted(os.listdir(BUSINESS_DIR)):
    full = os.path.join(BUSINESS_DIR, item)
    if os.path.isdir(full):
        count = sum(len(files) for _, _, files in os.walk(full))
        print(f"  📁 {item}/ ({count} files)")
    else:
        print(f"  📄 {item} ({os.path.getsize(full)} bytes)")

print(f"\n{'='*60}")
print("Vault structure (key dirs):")
print(f"{'='*60}")
for root, dirs, files in os.walk(VAULT_DIR):
    level = root.replace(VAULT_DIR, '').count(os.sep)
    if level <= 2:
        indent = "  " * level
        print(f"{indent}📁 {os.path.basename(root)}/")
        if level <= 1 and files:
            for f in files[:5]:
                print(f"{indent}  📄 {f}")

print(f"\n{len(moved)} files moved, {len(errors)} errors.")

# Clean up this script
try:
    os.remove(__file__)
except:
    pass
