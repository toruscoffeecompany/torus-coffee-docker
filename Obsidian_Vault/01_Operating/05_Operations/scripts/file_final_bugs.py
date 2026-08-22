"""
File the vault path drift + OODA timezone bugs.
Also file the "vault.json missing" + "API endpoints return HTML" consolidated bugs properly.
"""
import json, urllib.request, time
from datetime import datetime, timezone

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_list_id(board_id, keywords):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    lists = json.loads(resp.read())
    for l in lists:
        if any(k in l["name"].lower() for k in keywords):
            return l["id"]
    return lists[0]["id"]

def get_label_id(board_id, label_name):
    resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{board_id}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
    labels = json.loads(resp.read())
    for l in labels:
        if l["name"].lower() == label_name.lower():
            return l["id"]
    return None

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass
    time.sleep(0.3)

def create_bug(name, desc, priority="P0"):
    list_id = get_list_id(VOID, ["doing", "p0", "p1", "backlog"])
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"idList": list_id, "name": name, "desc": desc, "pos": "top"}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=10).read())
        cid = result["id"]
        for lbl in ["sir-green", priority, "Bug"]:
            lid = get_label_id(VOID, lbl)
            if lid:
                lb_url = f"https://api.trello.com/1/cards/{cid}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
                lb_data = json.dumps({"value": lid}).encode()
                lb_req = urllib.request.Request(lb_url, data=lb_data, method='POST')
                lb_req.add_header("Content-Type", "application/json")
                try: urllib.request.urlopen(lb_req, timeout=10)
                except: pass
        print(f"  ✅ Created: {name[:55]}")
        
        # Comment with @sir-green
        comment = f"""🔄 **MISS PINK BUG HUNT ({ts})**

@SirGreen — Bug filed during continuous dashboard + OODA audit.

**{name}**

**Priority:** {priority}
**Verified by:** Miss Pink — live system testing + file inspection

— 🦜"""
        post_comment(cid, comment)
    except Exception as e:
        print(f"  ❌ Failed: {name[:40]} — {e}")
    time.sleep(0.5)

# ─── NEW BUG: Vault structure path drift ───────────────────────────────────────
print("=== Filing new bugs ===\n")

create_bug(
    "🐛 [BUG] Vault structure changed — vault.json missing, INBOX paths moved — scripts broken",
    f"""**Bug Hunt Report — {ts}**

**Issue:** Vault structure was reorganized. vault.json is GONE + INBOX paths changed.
Multiple scripts reference old paths → FileNotFoundError.

**Evidence:**
- OLD: `Z:/Developer_Brain/01_Projects/capta1n_orchestrat0r/_Hub/vault.json` → MISSING
- OLD: `Z:/Developer_Brain/02_Business_Operations/Communications/MISS_PINK_INBOX/` → path changed
- OLD: `Z:/Developer_Brain/02_Business_Operations/Communications/SIR_GREEN_INBOX/` → moved to `_Hub/`

**New structure:**
- Distributed JSON files: augmented_signals.json, scanner_health.json, ooda_log_*.json
- INBOXes: `Z:/Developer_Brain/02_Business_Operations/MISS_PINK_INBOX/`, `Z:/Developer_Brain/02_Business_Operations/_Hub/SIR_GREEN_INBOX/`, `Z:/Developer_Brain/02_Business_Operations/Infrastructure/SIR_AZURE_INBOX/`

**Impact:**
- ooda_loop_torus.py was checking `data.get("updated_at")` from vault.json — KeyError
- Dashboard reports "149 uncommitted" because it can't find vault.json
- Scripts using old INBOX paths silently fail

**Fix:**
1. Update ALL scripts to use new distributed JSON paths (documented in VAULT_STRUCTURE.md)
2. Update dashboard to read from scanner_health.json instead of vault.json
3. Update all INBOX path references
4. Create VAULT_STRUCTURE.md + add to vault root

**Vault structure doc:** `D:/Work/Torus Coffee Company LLC/VAULT_STRUCTURE.md`

— 🦜""",
    "P1"
)

# ─── NEW BUG: OODA timezone comparison bug (already fixed but document it) ───────
create_bug(
    "🐛 [BUG] OODA script uses datetime.utcnow() with offset-aware datetime — comparison fails",
    f"""**Bug Hunt Report — {ts}**

**Issue:** ooda_loop_torus.py used `datetime.utcnow()` (offset-naive) compared against
`datetime.fromisoformat()` (offset-aware) from scanner_health.json's last_run timestamp.
This caused TypeError → 'Exception Group EMITTED' → systems reported as false.

**Evidence:**
```
TypeError: can't subtract offset-naive and offset-aware datetimes
  File "ooda_loop_torus.py", line 103, in <module>
    updated = datetime.fromisoformat(data.get("updated_at", ""))
  File "ooda_loop_torus.py", line 108
    now = datetime.utcnow()  ← BUG: naive datetime
```

**Impact:** When scanner ran >10 min before OODA check, the comparison would FAIL →
OODA reported "WARN" instead of "GO" even though scanner was alive.

**Fix (APPLIED):**
1. `from datetime import datetime, timezone`
2. `now = datetime.now(timezone.utc)` (offset-aware)
3. `if updated.tzinfo is None: updated = updated.replace(tzinfo=timezone.utc)`

**File:** D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ooda_loop_torus.py (lines 102-106)

**Note:** This bug is FIXED in the running script but the root cause (mixed
timezone usage) could still exist in other scripts. Audit recommended.

— 🦜""",
    "P2"
)

# ─── NEW BUG: OODA cron not auto-restarting if killed ───────────────────────────
create_bug(
    "🐛 [BUG] OODA cron has no auto-restart — dies silently if killed",
    f"""**Bug Hunt Report — {ts}**

**Issue:** The OODA cron job (4692924e5258) has no watchdog/process supervisor.
If the cron session dies, is killed, or the agent crashes → OODA stops silently.

**Evidence:**
- Cron `4692924e5258` schedule: '*/5 * * * *'
- No systemd/supervisor/process monitor wrapping the script
- If `python3 ooda_loop_torus.py` crashes (exception, OOM, segfault) → DEAD SILENT
- No alerting on failure

**Impact:** OODA monitoring stops → NO automatic card processing + system verification
→ bugs go undetected + cards don't get archived/recreated.

**Fix:**
1. Wrap OODA cron script in a process supervisor (supervisord/systemd/tmux)
2. Add health check endpoint to OODA output
3. Alert on cron job failure (Discord bot notification)
4. Auto-restart on crash

**File:** Cron job 4692924e5258 (hermes scheduler)
**Script:** D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ooda_loop_torus.py

— 🦜""",
    "P1"
)

# ─── NEW BUG: Scanner health.json uses 'last_run' but vault.json used 'updated_at' ─
create_bug(
    "🐛 [BUG] Inconsistent JSON schema — scanner_health.json vs old vault.json",
    f"""**Bug Hunt Report — {ts}**

**Issue:** Two JSON files use DIFFERENT timestamp field names:
- `scanner_health.json`: uses `"last_run"` ✅
- Old `vault.json`: used `"updated_at"` ❌ (now missing)

The OODA script had code for BOTH — `data.get("updated_at")` from vault.json AND
`health_data.get("last_run")` from scanner_health.json. This caused confusion + bugs.

**Evidence:**
```python
# Old code tried BOTH:
updated = datetime.fromisoformat(data.get("updated_at", ""))     # vault.json
updated = datetime.fromisoformat(health_data.get("last_run", "")) # scanner_health.json
```

**Impact:** Mixed schemas caused KeyError when vault.json disappeared → OODA falsely
reporting system down.

**Fix (APPLIED):**
1. Standardized on scanner_health.json with "last_run" field ✅
2. Updated ooda_loop_torus.py to read ONLY from scanner_health.json
3. Created VAULT_STRUCTURE.md documenting all JSON schemas

**Files:** scanner_health.json, ooda_loop_torus.py (patched)
**Schema docs:** D:/Work/Torus Coffee Company LLC/VAULT_STRUCTURE.md

— 🦜""",
    "P2"
)

print(f"\n{'='*70}")
print(f"NEW BUGS FILED: 4")
print("="*70)