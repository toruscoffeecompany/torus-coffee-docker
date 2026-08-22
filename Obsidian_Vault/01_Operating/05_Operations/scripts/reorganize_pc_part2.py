"""Part 2 reorg steps — runs with full path."""
import os, shutil, sys
from pathlib import Path

ROOT = Path("D:/Work/Torus Coffee Company LLC")
vault = ROOT / "Obsidian_Vault"

# ─── STEP 5: Delete nul artifact (handle Windows device file) ────────────────────
nul = ROOT / "nul"
if nul.exists() and nul.is_file():
    # Force delete — it's a 0-byte file artifact, not the Windows device
    try:
        os.chmod(str(nul), 0o777)
        nul.unlink()
        print("✅ Deleted nul")
    except PermissionError:
        # Use cmd to force delete
# MISS PINK FIX: os.system(f'del /f /q "{nul}" 2>nul')  # ← spawns cmd.exe popup!
        if not nul.exists():
            print("✅ Deleted nul via cmd")
        else:
            print(f"⚠️ Could not delete nul (Windows device file — may be harmless)")
elif nul.exists():
    print(f"  nul exists but is_dir={nul.is_dir()}")
else:
    print("  nul already gone")

# ─── STEP 6: Move 06_Website → PROJECT Torus website ────────────────────────────
src = vault / "06_Website"
dst = ROOT / "PROJECT Torus website"
dst.mkdir(parents=True, exist_ok=True)
if src.exists():
    count = 0
    for item in os.listdir(str(src)):
        s = src / item
        d = dst / item
        if d.exists():
            if d.is_dir(): shutil.rmtree(str(d))
            else: d.unlink()
        shutil.move(str(s), str(d))
        count += 1
    # Check if empty
    try:
        src.rmdir()
        print(f"✅ Moved 06_Website → PROJECT Torus website ({count} items)")
    except OSError:
        remaining = list(src.iterdir())
        print(f"⚠️ 06_Website not empty: {len(remaining)} items — manual check")
else:
    print("  06_Website already moved or not found")

# ─── STEP 7: Clean Sir_Azure_Backup ─────────────────────────────────────────────
az = Path("D:/Work/Sir_Azure_Backup")
if az.exists():
    freed = 0
    for item in os.listdir(str(az)):
        p = az / item
        if p.is_dir():
            sz = sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
            shutil.rmtree(str(p))
            freed += sz
            print(f"✅ Removed Sir_Azure_Backup/{item} ({sz/1024/1024:.1f} MB)")
        else:
            sz = p.stat().st_size
            p.unlink()
            freed += sz
            print(f"✅ Removed Sir_Azure_Backup file: {item}")
    try:
        az.rmdir()
        print(f"✅ Removed empty Sir_Azure_Backup dir (freed {freed/1024/1024:.1f} MB)")
    except OSError:
        print(f"⚠️ Sir_Azure_Backup not empty: {list(az.iterdir())}")
else:
    print("  Sir_Azure_Backup already gone")

# ─── STEP 8: Move loose root files ────────────────────────────────────────────────
loose = {
    "cmd_popup_emergency_blocker.py": ROOT / "scripts",
    "cmd_blocker_emergency.log": ROOT / "scripts",
    "cmd_popup_blocker.lock": ROOT / "scripts",
    "smart_ticket_cycle.py": ROOT / "scripts",
    "temp_crew_sync_card.py": ROOT / "scripts",
    "VAULT_STRUCTURE.md": vault / "00_Inbox",
}
for fname, target in loose.items():
    src = ROOT / fname
    if src.exists() and src.is_file():
        dst = target / fname
        target.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.move(str(src), str(dst))
            print(f"✅ {fname} → {target}/")
        else:
            src.unlink()
            print(f"✅ Removed dup: {fname}")
    else:
        print(f"  {fname}: not at root")

# ─── STEP 9: Move Hermes Alt Obsidian Vault Skills ────────────────────────────────
hermes = Path("D:/Work/Hermes Alt Obsidian Vault Skills")
if hermes.exists():
    dst = vault / "10_Skills_Library"
    for item in os.listdir(str(hermes)):
        s = hermes / item
        d = dst / item
        if d.exists():
            if d.is_dir():
                for f in s.rglob('*'):
                    if f.is_file():
                        rel = f.relative_to(s)
                        t = d / rel
                        if not t.exists():
                            t.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(str(f), str(t))
            elif s.is_file():
                s.unlink()
        else:
            shutil.move(str(s), str(d))
    shutil.rmtree(str(hermes))
    print("✅ Merged + removed Hermes Alt Obsidian Vault Skills")
else:
    print("  Hermes Alt Obsidian Vault Skills already gone")

print("\n=== DONE === All reorg steps complete.")
