#!/usr/bin/env python3
"""Fix organization — proper symlink detection + cleanup."""
import os, shutil
from pathlib import Path

ROOT = Path("D:/Work/Torus Coffee Company LLC")
VAULT = ROOT / "Obsidian_Vault"
SCRIPTS = ROOT / "scripts"
PFO = ROOT / "Pirate Fleet Operations"

def remove_path(p):
    """Remove a file/symlink/dir safely."""
    st = os.lstat(str(p))
    if os.path.islink(str(p)) or (st.st_file_attributes & 0x400):  # FILE_ATTRIBUTE_REPARSE_POINT
        os.unlink(str(p))
        return "unlink"
    elif p.is_dir():
        shutil.rmtree(str(p))
        return "rmtree"
    else:
        p.unlink()
        return "unlink"

def create_symlink(target, link_name):
    """Create symlink, replacing if exists."""
    if os.path.exists(str(link_name)) or os.path.islink(str(link_name)):
        if os.path.islink(str(link_name)):
            os.unlink(str(link_name))
        elif os.path.exists(str(link_name)):
            # Real dir/file — check if it's a dup before replacing
            print(f"  ⚠️ {link_name} exists as real item")
            return False
    os.symlink(str(target), str(link_name), target_is_directory=True)
    return True

print("=== FIXING ORGANIZATION ===\n")

# ─── 1. Remove duplicate 10_Skills_Library at root (create symlink instead) ─
root_10 = ROOT / "10_Skills_Library"
vault_10 = VAULT / "10_Skills_Library"
print(f"10_Skills_Library: root exists={root_10.exists()}, islink={os.path.islink(str(root_10))}")
if root_10.exists():
    # Remove the real dir (it's a duplicate)
    result = remove_path(root_10)
    print(f"  Removed duplicate (via {result})")
    create_symlink(vault_10, root_10)
    print(f"  ✅ Created symlink: 10_Skills_Library → Obsidian_Vault/10_Skills_Library")

# ─── 2. Remove duplicate 01_Operating at root ─
root_01 = ROOT / "01_Operating"
vault_01 = VAULT / "01_Operating"
print(f"\n01_Operating: root exists={root_01.exists()}, islink={os.path.islink(str(root_01))}")
if root_01.exists():
    result = remove_path(root_01)
    print(f"  Removed duplicate (via {result})")
    create_symlink(vault_01, root_01)
    print(f"  ✅ Created symlink: 01_Operating → Obsidian_Vault/01_Operating")

# ─── 3. Create symlinks for 22 missing vault dirs ─
vault_dirs = sorted([d for d in VAULT.iterdir() if d.is_dir() and not d.name.startswith('.')])
existing = set()
for item in ROOT.iterdir():
    if item.name not in ['.git', '.obsidian', '.smart-env', 'nul', 'Obsidian_Vault', 'scripts', 'PROJECT Torus website', 'Pirate Fleet Operations']:
        existing.add(item.name)

created = 0
for vdir in vault_dirs:
    if vdir.name in existing:
        continue
    link = ROOT / vdir.name
    if create_symlink(vdir, link):
        created += 1
        print(f"  ✅ {vdir.name} → Obsidian_Vault/{vdir.name}")
    else:
        print(f"  ⚠️ {vdir.name}: skipped")
print(f"\nCreated {created} symlinks")

# ─── 4. Move scripts from Pirate Fleet Operations → scripts/ ─
pfo_scripts = PFO / "scripts"
if pfo_scripts.exists():
    script_count = len(list(pfo_scripts.glob("*.py")))
    print(f"\nMoving {script_count} scripts from PFO → scripts/")
    for f in sorted(pfo_scripts.glob("*.py")):
        target = SCRIPTS / f.name
        if target.exists():
            target.unlink()
        shutil.move(str(f), str(target))
    # Other files
    for f in sorted(pfo_scripts.iterdir()):
        if f.suffix != '.py':
            target = SCRIPTS / f.name
            if target.exists() and target.is_dir(): shutil.rmtree(str(target))
            elif target.exists(): target.unlink()
            shutil.move(str(f), str(target))
            print(f"  ✅ Moved {f.name}")
    
    # Remove PFO dirs
    try:
        PFO.rmdir()
        print(f"  ✅ Removed Pirate Fleet Operations")
    except:
        for sub in sorted(PFO.iterdir()):
            if sub.is_dir():
                shutil.rmtree(str(sub))
                print(f"  ✅ Removed PFO/{sub.name}")
            else:
                sub.unlink()
        PFO.rmdir()
        print(f"  ✅ Removed Pirate Fleet Operations")

# ─── 5. Update cron scripts for tr3asure_mAp path ─
print("\n=== Updating cron scripts ===")
for script_name, replacements in [
    ("C:/Users/torus/AppData/Local/hermes/scripts/run_scanner.py",
     [("D:/Work/tr3asure_mAp", "D:/Work/tr3asure_mAp")]),
]:
    p = Path(script_name)
    if p.exists():
        content = p.read_text()
        for old, new in replacements:
            content = content.replace(old, new)
        p.write_text(content)
        print(f"  ✅ Updated {script_name.split('/')[-1]}")

# run_ooda.py — workdir is D:/Work/Torus Coffee Company LLC, runs scripts/ooda_loop_torus.py
ooda = Path("C:/Users/torus/AppData/Local/hermes/scripts/run_ooda.py")
if ooda.exists():
    content = ooda.read_text()
    if "D:/Work/tr3asure_mAp" in content:
        content = content.replace("D:/Work/tr3asure_mAp", "D:/Work/tr3asure_mAp")
        ooda.write_text(content)
        print(f"  ✅ Updated run_ooda.py path")
    if "scripts/ooda_loop_torus.py" in content:
        print(f"  ✅ run_ooda.py workdir correct (D:/Work/Torus Coffee Company LLC)")

# ─── 6. Clean up artifacts ─
print("\n=== Cleanup ===")
nul = ROOT / "nul"
if nul.exists():
    print(f"  nul: persists (Windows device — harmless, 0 bytes)")

pyc = VAULT / "__pycache__"
if pyc.exists():
    shutil.rmtree(str(pyc))
    print(f"  ✅ Removed Obsidian_Vault/__pycache__")

sq = Path("D:/Work/tr3asure_mAp/data/SQUIDSTATION_Archive")
if sq.exists():
    if sq.is_dir() and not any(sq.iterdir()):
        sq.rmdir()
        print(f"  ✅ Removed empty SQUIDSTATION_Archive from tr3asure_mAp")

# ─── 7. Final structure ─
print("\n=== FINAL STRUCTURE ===")
for item in sorted(ROOT.iterdir(), key=lambda x: x.name.lower()):
    if item.name.startswith('.'): 
        print(f"  🔐 {item.name}/")
        continue
    if item.name == 'nul':
        print(f"  ⚠️  {item.name} (Windows device)")
        continue
    if os.path.islink(str(item)):
        print(f"  🔗 {item.name} → {Path(os.readlink(str(item))).name}")
    elif item.is_dir():
        cnt = len([f for f in item.rglob('*') if f.is_file()])
        print(f"  📁 {item.name} ({cnt} files)")
    else:
        print(f"  📄 {item.name}")

print("\n=== SCRIPTS/ ===")
for f in sorted(SCRIPTS.glob("*.py")):
    print(f"  {f.name}")
print(f"  Total: {len(list(SCRIPTS.glob('*.py')))} Python scripts")

print("\n=== DONE ===")
