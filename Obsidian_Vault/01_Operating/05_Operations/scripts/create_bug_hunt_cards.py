#!/usr/bin/env python3
"""Create Trello cards for Miss Pink OODA bug hunt findings."""
import json, urllib.request, urllib.error

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
API = "https://api.trello.com/1"

# CORRECT list IDs from Torus_Ops board
P0_LIST = "6a74cbd440270147ff04bd5b"   # P0 - Alert / Critical / Do Now
P1_LIST = "6a74cbd5e3d54d2d08be82e7"   # P1 - High / Doing Now
P2_LIST = "6a74cbd4148f814483a64589"   # P2 - Med High / This Week
INBOX_LIST = "6a75869a95f875e18db6c081"  # Miss Pink's Inbox

# Label IDs
P0_LABEL = "6a74cc10430afd9940c72bae"
P1_LABEL = "6a70acc569135c796d8eba5d"
P2_LABEL = "6a77a9680f3bc16bb419f4d2"
SIR_GREEN_LABEL = "6a74dd62bbb2ecab3909e29f"
MISS_PINK_LABEL = "6a74dd623356f01be75f7d0c"

def post(path, body):
    url = f"{API}/{path}?key={KEY}&token={TOKEN}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  ERROR: {e.code} - {e.read().decode()}")
        return None

# ─── BUG #1: Dashboard server not running (P0, Sir Green) ────────────────────────
print("Creating Card #1: Dashboard server P0...")
card1 = post("cards", {
    "name": "BUG: Captain's Dashboard server (port 8080) NOT running on PINKCADY",
    "desc": """## BUG: Captain's Dashboard server not running
PC: PINKCADY (100.106.235.103) | Port: 8080 | Priority: P0 | Owner: Sir Green (SQUIDSTATION)

### What's broken:
- Port 8080 is CLOSED on PINKCADY
- dashboard_server.py exists at: D:\\Work\\Void Pirate Trading Co, (Backup)\\Captain_Dashboard\\dashboard\\dashboard_server.py (177KB)
- augur_autonomous_trainer.py line 39: CD_BASE = "http://100.106.235.103:8080"
- analyze_dashboard.py + analyze_augur_tab.py point to SQUIDSTATION:8080 (WRONG)

### Fix needed:
1. Sir Green: Start dashboard_server.py on PINKCADY:8080
2. Sir Green: Fix analyze_dashboard.py + analyze_augur_tab.py -> 100.106.235.103:8080

### Verified by:
Miss Pink OODA 2026-08-13T00:42Z""",
    "idList": P0_LIST,
    "idLabels": [P0_LABEL, SIR_GREEN_LABEL]
})
if card1: print(f"  Card #1: {card1['shortUrl']}")

# ─── BUG #2: Dashboard analysis scripts wrong IP (P1) ───────────────────────────
print("Creating Card #2: Wrong IP P1...")
card2 = post("cards", {
    "name": "BUG: analyze_dashboard.py + analyze_augur_tab.py point to SQUIDSTATION not PINKCADY:8080",
    "desc": """## BUG: Dashboard analysis scripts wrong IP
PC: PINKCADY | Priority: P1 | Owner: Miss Pink

### What's broken:
analyze_dashboard.py line 3: url = "http://100.83.247.14:8080/"  (SQUIDSTATION - WRONG)
analyze_augur_tab.py line 3: url = "http://100.83.247.14:8080/"  (SQUIDSTATION - WRONG)

Captain's dashboard runs on PINKCADY: http://100.106.235.103:8080/

### Fix:
Change url to http://100.106.235.103:8080/ in both scripts:
- /d/Work/.pirate_automation/scripts/analyze_dashboard.py
- /d/Work/.pirate_automation/scripts/analyze_augur_tab.py

### Verified by:
Miss Pink OODA 2026-08-13T00:42Z""",
    "idList": P1_LIST,
    "idLabels": [P1_LABEL, MISS_PINK_LABEL]
})
if card2: print(f"  Card #2: {card2['shortUrl']}")

# ─── BUG #3: run_scanner.sh path fix (record, P2) ───────────────────────────────
print("Creating Card #3: Scanner path fix record...")
card3 = post("cards", {
    "name": "BUG FIX (done): run_scanner.sh + run_ooda.sh path mangling fixed",
    "desc": """## BUG FIX (already patched)
PC: PINKCADY | Priority: P2 | Owner: Miss Pink

### What was broken:
run_scanner.sh: cd /d/Work/... && cmd /c "python script.py"
  - Bash cd changes bash cwd, cmd /c spawns new process
  - Path became D:\\d\\Work\\... (double drive letter)
  - Scanner cron failed: can't open file 'D:\\d\\Work\\...'

### Fix applied:
cmd /c "python.exe D:\\Work\\tr3asure_mAp\\augmented_signal_generator.py"  (absolute Windows path)

### Verified:
scanner wrote MSFT signal + health JSON at 23:41 UTC. OODA 9/9 ALL SYSTEMS GO.

### Card for record only. No further action needed.

Verified by: Miss Pink OODA 2026-08-13T00:42Z""",
    "idList": P2_LIST,
    "idLabels": [P2_LABEL]
})
if card3: print(f"  Card #3: {card3['shortUrl']}")

# ─── BUG #4: Deploy signal integration to SQUIDSTATION (P2) ────────────────────
print("Creating Card #4: Deploy signal integration P2...")
card4 = post("cards", {
    "name": "TODO: Deploy augmented signal integration (4-layer scoring) to SQUIDSTATION TM API",
    "desc": """## TODO: Deploy 4-layer signal integration to SQUIDSTATION
PC: PINKCADY (ready) / SQUIDSTATION (deploy) | Priority: P2 | Owner: Sir Green

### Ready (PINKCADY side):
- signal_augmentation.py in D:/Work/tr3asure_mAp/
- 4-layer scoring: 0.4*tech + 0.3*fundamental + 0.2*sector + 0.1*macro
- AAPL verified: combined_score=0.39 -> ENTRY signal
- deploy_patches_to_vault.py copies patches to Z:/Developer_Brain/Deploy/Patches/

### Sir Green needs:
1. Apply signal_augmentation.py to SQUIDSTATION TM API (patches/app.py)
2. Serve /api/augur/augmented_signals with 4-layer scores
3. Deploy AugurTab.jsx update to dashboard (port 8080)
4. Verify scanner_health.json -> TM status sync

### Verified by:
Miss Pink OODA 2026-08-13T00:42Z""",
    "idList": P2_LIST,
    "idLabels": [P2_LABEL, SIR_GREEN_LABEL]
})
if card4: print(f"  Card #4: {card4['shortUrl']}")

print("\n=== ALL CARDS CREATED ===")
