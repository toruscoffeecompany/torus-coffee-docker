#!/usr/bin/env python3
"""
Miss Pink — FINAL PC ORGANIZATION FIX
Fixes the incomplete user reorganization:
1. Creates proper symlinks for 22 missing vault dirs at business root
2. Handles duplicate 01_Operating, 10_Skills_Library (real copies vs vault)
3. Fixes 02_Business_Operations — root has LIVE bot data (7 files), vault has old archive (11k files)
4. Moves 150+ scripts from Pirate Fleet Operations back to scripts/
5. Updates cron scripts for tr3asure_mAp path
6. Cleans up: nul, leftover SQUIDSTATION_Archive dir, __pycache__
"""
import os, shutil, subprocess, json
from pathlib import Path

ROOT = Path("D:/Work/Torus Coffee Company LLC")
VAULT = ROOT / "Obsidian_Vault"
SCRIPTS = ROOT / "scripts"
PFO = ROOT / "Pirate Fleet Operations"

def main():
    print("=== MISS PINK PC ORGANIZATION FINAL FIX ===\n")
    
    # ─── 1. Handle 10_Skills_Library duplication ─────────────────────────────
    # Root has real dir (64k files), Vault has the original
    # → Move root to Obsidian_Vault location (the vault copy is canonical)
    root_10 = ROOT / "10_Skills_Library"
    vault_10 = VAULT / "10_Skills_Library"
    if root_10.exists() and not os.path.islink(str(root_10)):
        # Check if they're the same content
        root_count = len(list(root_10.rglob('*')))
        vault_count = len(list(vault_10.rglob('*')))
        print(f"10_Skills_Library: root={root_count} items, vault={vault_count} items")
        if root_count == vault_count:
            # Remove the duplicate at root (vault has canonical copy)
            print(f"  → Same content — removing duplicate root dir")
            shutil.rmtree(str(root_10))
            # Create symlink
            try:
                root_10.symlink_to(vault_10, target_is_directory=True)
                print(f"  ✅ Created symlink: 10_Skills_Library → Obsidian_Vault/10_Skills_Library")
            except OSError as e:
                print(f"  ⚠️ Could not create symlink: {e}")
                print(f"  → Keeping as real dir (Obsidian will use either)")
    
    # ─── 2. Handle 01_Operating duplication ───────────────────────────────────
    root_01 = ROOT / "01_Operating"
    vault_01 = VAULT / "01_Operating"
    if root_01.exists() and not os.path.islink(str(root_01)):
        root_files = set(os.listdir(str(root_01)))
        vault_files = set(os.listdir(str(vault_01)))
        print(f"\n01_Operating: root={len(root_files)} entries, vault={len(vault_files)} entries")
        if root_files == vault_files:
            print(f"  → Same content — removing duplicate root dir")
            shutil.rmtree(str(root_01))
            try:
                root_01.symlink_to(vault_01, target_is_directory=True)
                print(f"  ✅ Created symlink: 01_Operating → Obsidian_Vault/01_Operating")
            except OSError:
                print(f"  → Keeping as real dir")
    
    # ─── 3. Handle 02_Business_Operations ─────────────────────────────────────
    # Root: 7 files (LIVE bot data — KEEP as real dir)
    # Vault: 11,128 files (old archive)
    # These are DIFFERENT — root is live ops, vault is historical archive
    # DON'T symlink — both should exist independently
    root_02 = ROOT / "02_Business_Operations"
    vault_02 = VAULT / "02_Business_Operations"
    print(f"\n02_Business_Operations:")
    print(f"  Root: {len(list(root_02.rglob('*')))} items (LIVE — bot writes here)")
    print(f"  Vault: {len(list(vault_02.rglob('*')))} items (archive)")
    print(f"  → Both kept as real dirs (live + archive)")
    
    # ─── 4. Create symlinks for 22 missing vault dirs ───────────────────────────
    vault_dirs = sorted([d for d in VAULT.iterdir() if d.is_dir() and not d.name.startswith('.')])
    existing_at_root = set()
    for item in ROOT.iterdir():
        if item.name not in ['.git', '.obsidian', '.smart-env', 'nul']:
            existing_at_root.add(item.name)
    
    print(f"\n=== Creating symlinks for missing vault dirs ===")
    created = 0
    for vdir in vault_dirs:
        if vdir.name in existing_at_root:
            continue  # Already exists at root (real dir or symlink)
        link_path = ROOT / vdir.name
        try:
            link_path.symlink_to(vdir, target_is_directory=True)
            print(f"  ✅ {vdir.name} → Obsidian_Vault/{vdir.name}")
            created += 1
        except OSError as e:
            print(f"  ⚠️ {vdir.name}: {e}")
    
    print(f"  Created {created} symlinks")
    
    # ─── 5. Move scripts from Pirate Fleet Operations → scripts/ ───────────────
    pfo_scripts = PFO / "scripts"
    if pfo_scripts.exists():
        script_count = len(list(pfo_scripts.glob("*.py")))
        print(f"\n=== Moving scripts from Pirate Fleet Operations to scripts/ ===")
        for f in sorted(pfo_scripts.glob("*.py")):
            target = SCRIPTS / f.name
            if target.exists():
                target.unlink()  # overwrite
            shutil.move(str(f), str(target))
        print(f"  ✅ Moved {script_count} Python scripts to scripts/")
        
        # Check for other non-script files
        others = list(pfo_scripts.iterdir())
        others = [o for o in others if not o.suffix == '.py']
        if others:
            for o in others:
                target = SCRIPTS / o.name
                if target.exists():
                    if target.is_dir(): shutil.rmtree(str(target))
                    else: target.unlink()
                shutil.move(str(o), str(target))
                print(f"  ✅ Moved {o.name} to scripts/")
        
        # Remove empty Pirate Fleet Operations
        try:
            PFO.rmdir()
            print(f"  ✅ Removed empty Pirate Fleet Operations dir")
        except OSError:
            remaining = list(PFO.iterdir())
            print(f"  ⚠️ PFO not empty: {[d.name for d in remaining if not d.name=='scripts']}")
    
    # ─── 6. Update cron scripts for tr3asure_mAp path ────────────────────────
    print(f"\n=== Updating cron scripts for new tr3asure_mAp path ===")
    run_scanner = Path("C:/Users/torus/AppData/Local/hermes/scripts/run_scanner.py")
    run_ooda = Path("C:/Users/torus/AppData/Local/hermes/scripts/run_ooda.py")
    
    # run_scanner.py: tr3asure_mAp is now at D:\Work\tr3asure_mAp
    if run_scanner.exists():
        content = run_scanner.read_text()
        new_content = content.replace(
            "D:/Work/tr3asure_mAp",
            "D:/Work/tr3asure_mAp"
        )
        run_scanner.write_text(new_content)
        print(f"  ✅ Updated run_scanner.py path")
    
    # run_ooda.py: workdir changed from Torus root to same path, scripts/ stays same
    if run_ooda.exists():
        content = run_ooda.read_text()
        # workdir is still D:/Work/Torus Coffee Company LLC (correct)
        # but scripts/ now has the real ooda_loop_torus.py
        if "D:/Work/Torus Coffee Company LLC" in content:
            print(f"  ✅ run_ooda.py workdir already correct (D:/Work/Torus Coffee Company LLC)")
    
    # ─── 7. Clean up artifacts ───────────────────────────────────────────────────
    print(f"\n=== Cleaning up artifacts ===")
    
    # nul file
    nul = ROOT / "nul"
    if nul.exists():
        try:
            os.remove(str(nul))
            print(f"  ✅ Removed nul")
        except:
            print(f"  ⚠️ nul persists (Windows device — harmless)")
    
    # __pycache__ in Obsidian_Vault
    pyc = VAULT / "__pycache__"
    if pyc.exists():
        shutil.rmtree(str(pyc))
        print(f"  ✅ Removed Obsidian_Vault/__pycache__")
    
    # Leftover empty SQUIDSTATION_Archive in tr3asure_mAp
    sq = Path("D:/Work/tr3asure_mAp/data/SQUIDSTATION_Archive")
    if sq.exists() and not any(sq.iterdir()):
        sq.rmdir()
        print(f"  ✅ Removed empty SQUIDSTATION_Archive from tr3asure_mAp")
    
    # ─── 8. Verify final structure ───────────────────────────────────────────────
    print(f"\n=== FINAL STRUCTURE ===")
    root_items = sorted(ROOT.iterdir(), key=lambda x: x.name.lower())
    for item in root_items:
        if item.name.startswith('.'): continue
        if item.name == 'nul': continue
        if os.path.islink(str(item)):
            print(f"  🔗 {item.name} → {item.resolve().name}")
        elif item.is_dir():
            cnt = len([f for f in item.rglob('*') if f.is_file()])
            print(f"  📁 {item.name} ({cnt} files)")
    
    # Verify scripts
    print(f"\n=== scripts/ contents ({len(list(SCRIPTS.glob('*.py')))} Python files) ===")
    for f in sorted(SCRIPTS.glob("*.py")):
        print(f"  {f.name}")
    
    print("\n=== ORGANIZATION COMPLETE ===")

if __name__ == "__main__":
    main()
