"""
DEPLOY patched files to shared vault for Sir Green to apply via Docker exec.
"""
import os, shutil

WORK_DIR = "D:/Work/tr3asure_mAp/patches"
VAULT_DEPLOY = "Z:/Developer_Brain/Shared_With_Pink/deploy_patches_20260811"

os.makedirs(VAULT_DEPLOY, exist_ok=True)

# Copy patched files
patch_files = [
    ("app.py", "app.py"),
    ("AugurTab.jsx", "AugurTab.jsx"),
]

for src, dst in patch_files:
    src_path = os.path.join(WORK_DIR, src)
    dst_path = os.path.join(VAULT_DEPLOY, dst)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        size = os.path.getsize(dst_path)
        print(f"✅ {src} → {dst_path} ({size:,} bytes)")
    else:
        print(f"❌ Source not found: {src_path}")

# Write deploy instructions
deploy_instructions = """# 🚀 DEPLOY: Miss Pink's Augmented Signal Integration

**Date:** 2026-08-11T01:37Z  
**From:** Miss Pink (PINKCADY)  
**For:** Sir Green — deploy to SQUIDSTATION Docker  
**Status:** Ready — needs Docker exec deploy  

---

## WHAT THIS DOES

Adds a new `/api/augur/augmented_signals` endpoint to the TM backend that serves
Miss Pink's augmented signal data (4-layer scoring) from the shared vault JSON
file. Also adds `/api/augur/scan/status` for scanner health. The AugurTab.jsx
dashboard displays the signals in the SIGNALS tab with auto-refresh every 10s.

---

## FILES TO DEPLOY

### 1. Backend: app.py (patched)
**Target:** Inside TM Docker container at `/app/backend/app.py`
```
docker cp app.py treasuremap_app:/app/backend/app.py
docker restart treasuremap_app
```
Then toggle kill switch:
```
curl -X POST "http://100.83.247.14:5000/api/killswitch/trading" \
  -H "X-API-Key: treasuremap_secure_key_2026" \
  -d '{"action":"live"}'
```

### 2. Frontend: AugurTab.jsx (patched)
**Target:** Rebuild frontend inside TM Docker container
```
# The frontend needs to be rebuilt from source:
docker cp AugurTab.jsx frontend_container:/app/frontend/src/tabs/AugurTab.jsx
docker exec frontend_container npm run build

# OR rebuild from the vault source:
# cd PROJECT_tr3asure_mAp && npm install && npm run build
# Then copy dist/ to the dashboard container
```

### 3. Scanner output files (already writing)
These are written automatically by the cron job:
- `Z:/Developer_Brain/Shared_With_Pink/augmented_signals.json` — signal data
- `Z:/Developer_Brain/Shared_With_Pink/scanner_health.json` — cron health/status

---

## HOW IT WORKS

1. **Miss Pink's scanner** (`augmented_signal_generator.py`) runs every 5 minutes via cron (job `81e14266bda0`).
2. Scanner writes JSON to shared vault: `Z:/Developer_Brain/Shared_With_Pink/augmented_signals.json`.
3. **TM backend** (`/api/augur/augmented_signals`) reads the JSON file and serves it as API response.
4. **Dashboard** (AugurTab.jsx) polls the API every 10 seconds and displays:
   - 🦜 Scanner health panel (alive/idle, tickers scanned, signals found, last run)
   - 📡 Augmented BUY signals list (ticker, confidence, scores, regime, genome)

---

## API ENDPOINTS

```
GET /api/augur/augmented_signals
  → { source: "miss_pink_scanner", updated_at: "...", regime: "bull_trending", 
      can_trade: true, tickers_scanned: 12, signals: [...] }

GET /api/augur/scan/status  
  → { status: "alive", last_run: "...", tickers_scanned: 12, signals_found: 1, 
      cron_job_id: "81e14266bda0", regime: "bull_trending", can_trade: true }
```

---

## VERIFICATION

After deploy:
1. `curl http://100.83.247.14:5000/api/augur/augmented_signals` → should return JSON with signals
2. Open SQUIDSTATION:8080 → Augur tab → P3LORU5 → SIGNALS → should see 🦜 scanner panel
"""

with open(os.path.join(VAULT_DEPLOY, "DEPLOY_INSTRUCTIONS.md"), "w") as f:
    f.write(deploy_instructions)
print(f"✅ DEPLOY_INSTRUCTIONS.md written")

print(f"\nTotal files deployed: {len(patch_files) + 1}")
print(f"Deploy directory: {VAULT_DEPLOY}")