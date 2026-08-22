"""
PATCH app.py + AugurTab.jsx — copy to local, patch, document deploy steps.
Vault share is read-only. Patches need to be applied via Sir Green's Docker exec.
"""
import os, shutil

# Source paths (read-only vault mount)
SRC_APP = "//192.168.0.39/VOID Pirate Trading Co/PROJECT_tr3asure_mAp/tr3asure_mAp/backend/app.py"
SRC_TAB = "//192.168.0.39/VOID Pirate Trading Co/PROJECT_tr3asure_mAp/tr3asure_mAp/frontend/src/tabs/AugurTab.jsx"

# Local working copies
WORK_DIR = "D:/Work/tr3asure_mAp/patches"
os.makedirs(WORK_DIR, exist_ok=True)
LOCAL_APP = f"{WORK_DIR}/app.py"
LOCAL_TAB = f"{WORK_DIR}/AugurTab.jsx"

# ─── 1. Copy files locally ──────────────────────────────────────────────────────
print("=== Copying files to local working directory ===")
shutil.copy2(SRC_APP, LOCAL_APP)
print(f"✅ Copied app.py → {LOCAL_APP}")

shutil.copy2(SRC_TAB, LOCAL_TAB)
print(f"✅ Copied AugurTab.jsx → {LOCAL_TAB}")

# ─── 2. Patch app.py ────────────────────────────────────────────────────────────
print("\n=== Patching app.py ===")
with open(LOCAL_APP, "r") as f:
    content = f.read()

insert_after = "        return jsonify({'no_data': True, 'error': str(exc)})\n\n\n# ── GET /api/augur/last_run_summary"

if insert_after in content:
    new_endpoint = '''
# ── GET /api/augur/augmented_signals ── Miss Pink's 4-Layer Signal Scanner ─────
# Reads augmented signal data from shared vault JSON file written by local cron.
@app.route('/api/augur/augmented_signals')
def augur_augmented_signals():
    """Returns augmented signals from Miss Pink's local scanner.
    Reads from shared vault JSON file that the cron writes every 5 minutes.
    Falls back to bot_signals table for augmented_scanner entries.
    """
    import json as _json
    import os as _os
    
    vault_paths = [
        "/app/shared/augmented_signals.json",
        "//192.168.0.39/VOID Pirate Trading Co/data/augmented_signals.json",
        "Z:/Developer_Brain/Shared_With_Pink/augmented_signals.json",
        os.path.join(_AUGUR_DB.replace("treasure_map.db", ""), "augmented_signals.json"),
    ]
    
    for vp in vault_paths:
        try:
            if _os.path.exists(vp):
                with open(vp) as f:
                    data = _json.loads(f.read())
                return jsonify({"source": "miss_pink_scanner", "updated_at": data.get("updated_at"), "signals": data.get("signals", [])})
        except Exception:
            pass
    
    # ── Fallback: read from bot_signals table ─────────────────────────────────
    try:
        con = _sql.connect(_AUGUR_DB)
        con.row_factory = _sql.Row
        try:
            rows = con.execute(
                """SELECT * FROM bot_signals
                   WHERE signal_source = 'augmented_signal_generator'
                   ORDER BY created_at DESC LIMIT 20"""
            ).fetchall()
        finally:
            con.close()
        
        signals = []
        for r in rows:
            d = dict(r)
            for key in ('indicator_snapshot', 'genome_conditions'):
                try:
                    d[key] = _json.loads(d.get(key) or '{}')
                except Exception:
                    d[key] = {} if key == 'indicator_snapshot' else []
            signals.append(d)
        
        return jsonify({"source": "bot_signals", "count": len(signals), "signals": signals})
    except Exception as exc:
        logger.error('/api/augur/augmented_signals error: %s', exc)
        return jsonify({"source": "none", "error": str(exc), "signals": []})


# ── GET /api/augur/scan/status ── Miss Pink's augmented scanner cron status ─────
@app.route('/api/augur/scan/status')
def augur_scan_status():
    """Returns status of Miss Pink's augmented scanner cron job."""
    import os as _os
    import json as _json
    
    health_paths = [
        "/app/shared/scanner_health.json",
        "Z:/Developer_Brain/Shared_With_Pink/scanner_health.json",
        os.path.join(_AUGUR_DB.replace("treasure_map.db", ""), "scanner_health.json"),
    ]
    
    for hp in health_paths:
        try:
            if _os.path.exists(hp):
                with open(hp) as f:
                    health = _json.loads(f.read())
                return jsonify(health)
        except Exception:
            pass
    
    return jsonify({"status": "unknown", "last_run": None, "error": "Health file not found"})
'''
    
    patched = content.replace(insert_after, "        return jsonify({'no_data': True, 'error': str(exc)})\n\n" + new_endpoint + "\n\n# ── GET /api/augur/last_run_summary")
    
    with open(LOCAL_APP, "w") as f:
        f.write(patched)
    
    # Verify
    with open(LOCAL_APP, "r") as f:
        verify = f.read()
    if "augur_augmented_signals" in verify and "augur_scan_status" in verify:
        print("✅ app.py patched: /api/augur/augmented_signals + /api/augur/scan/status added")
    else:
        print("❌ Patch verification FAILED")
    
    # Compile check
    import py_compile
    try:
        py_compile.compile(LOCAL_APP, doraise=True)
        print("✅ Compile check: PASS")
    except Exception as e:
        print(f"❌ Compile check FAILED: {e}")
else:
    print("❌ Insertion point not found")
    # Show context around line 15823
    lines = content.split('\n')
    for i in range(15815, min(15830, len(lines))):
        print(f"  {i+1}: {lines[i][:80]}")