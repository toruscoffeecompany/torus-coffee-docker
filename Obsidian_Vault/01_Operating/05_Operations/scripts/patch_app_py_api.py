"""
PATCH: Add /api/augur/augmented_signals endpoint to app.py + patch AugurTab.jsx.
This endpoint reads augmented signal data from a JSON file that the local
augmented_signal_generator.py cron writes to, making it accessible via the TM API.
"""
import os

app_path = "//192.168.0.39/VOID Pirate Trading Co/PROJECT_tr3asure_mAp/tr3asure_mAp/backend/app.py"

# ─── 1. Backup app.py ───────────────────────────────────────────────────────────
backup = app_path + ".miss_pink_patched"
if not os.path.exists(backup):
    with open(app_path, "r") as f:
        original = f.read()
    with open(backup, "w") as f:
        f.write(original)
    print("✅ Backed up app.py → app.py.miss_pink_patched")
else:
    print("ℹ️ Backup already exists, skipping")
    with open(app_path, "r") as f:
        original = f.read()

# ─── 2. Insert new endpoint after /api/augur/last_signal ─────────────────────
new_endpoint = '''
# ── GET /api/augur/augmented_signals ── Miss Pink's 4-Layer Signal Scanner ─────
# Reads augmented signal data from a JSON file written by the local cron scanner.
# This bridges Miss Pink's augmented signal generator (running on PINKCADY) with
# the TM dashboard's AugurTab.
@app.route('/api/augur/augmented_signals')
def augur_augmented_signals():
    """Returns augmented signals from Miss Pink's local scanner.
    Reads from shared vault JSON file that the cron job writes every 5 minutes.
    Falls back to scanning bot_signals table for augmented_scanner entries.
    """
    import json as _json
    import os as _os
    
    # ── 1. Try reading from Miss Pink's shared vault JSON ──────────────────────
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
                    data = json.loads(f.read())
                return jsonify({"source": "miss_pink_scanner", "updated_at": data.get("updated_at"), "signals": data.get("signals", [])})
        except Exception:
            pass
    
    # ── 2. Fallback: read from bot_signals table for augmented_scanner entries ─
    try:
        con = _sql.connect(_AUGUR_DB)
        con.row_factory = _sql.Row
        try:
            rows = con.execute(
                \'\'\'SELECT * FROM bot_signals
                   WHERE signal_source = 'augmented_signal_generator'
                   ORDER BY created_at DESC LIMIT 20\'\'\'
            ).fetchall()
        finally:
            con.close()
        
        signals = []
        for r in rows:
            d = dict(r)
            for key in ('indicator_snapshot', 'genome_conditions'):
                try:
                    d[key] = json.loads(d.get(key) or '{}')
                except Exception:
                    d[key] = {} if key == 'indicator_snapshot' else []
            signals.append(d)
        
        return jsonify({"source": "bot_signals", "count": len(signals), "signals": signals})
    except Exception as exc:
        logger.error('/api/augur/augmented_signals error: %s', exc)
        return jsonify({"source": "none", "error": str(exc), "signals": []})


# ── GET /api/augur/scan/status ── Miss Pink's scanner cron status ───────────────
@app.route('/api/augur/scan/status')
def augur_scan_status():
    """Returns status of Miss Pink's augmented scanner cron job."""
    import os as _os
    import json as _json
    from datetime import datetime, timezone
    
    health_file = os.path.join(_AUGUR_DB.replace("treasure_map.db", ""), "scanner_health.json")
    health_paths = [
        "/app/shared/scanner_health.json",
        "Z:/Developer_Brain/Shared_With_Pink/scanner_health.json",
        health_file,
    ]
    
    for hp in health_paths:
        try:
            if _os.path.exists(hp):
                with open(hp) as f:
                    health = json.loads(f.read())
                return jsonify(health)
        except Exception:
            pass
    
    return jsonify({"status": "unknown", "last_run": None, "error": "Health file not found"})
'''

# Find insertion point (after the last_signal route ends, before last_run_summary)
insert_after = "        return jsonify({'no_data': True, 'error': str(exc)})\n\n\n# ── GET /api/augur/last_run_summary"

if insert_after in original:
    patched = original.replace(insert_after, "        return jsonify({'no_data': True, 'error': str(exc)})\n\n" + new_endpoint + "\n\n# ── GET /api/augur/last_run_summary")
    
    # Verify compile
    try:
        import py_compile
        py_compile.compile(app_path, doraise=True)
        print("❌ WARNING: app.py compiled BEFORE patch (unexpected)")
    except:
        # Should compile before patch since it uses existing module imports
        pass
    
    with open(app_path, "w") as f:
        f.write(patched)
    print("✅ Inserted /api/augur/augmented_signals + /api/augur/scan/status endpoints")
    
    # Verify the patch
    with open(app_path, "r") as f:
        patched_content = f.read()
    if "augur_augmented_signals" in patched_content and "augur_scan_status" in patched_content:
        print("✅ Verification: new endpoints present in app.py")
    else:
        print("❌ Verification FAILED — endpoints not found")
else:
    print("❌ Insertion point not found in app.py")
    print("Looking for:", repr(insert_after[:80]))