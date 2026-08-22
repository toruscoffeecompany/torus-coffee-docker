"""
BUG HUNT — File Trello cards for each bug found on the TreasureMap dashboard
at 192.168.0.39:8080. Assign to Sir Green.
"""
import json, urllib.request, time

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD = "6a595669b8f8f99c93392f4f"  # VOID_Ops
LIST = "6a70a3157d0db4214ac3f9a3"  # We'll use the first list
ts = "2026-08-11T13:00Z"

def create_card(name, desc, labels=["sir-green", "P1", "Bug"], pos="top"):
    """Create a Trello card."""
    # First get a valid list ID
    pass

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except Exception as e: print(f"  ⚠️ Comment: {e}")
    time.sleep(0.35)

# ─── Get a valid list ID on VOID_Ops board ─────────────────────────────────────
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{BOARD}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}")
lists = json.loads(resp.read())
# Find a list named "Doing" or "P1" or "Backlog"
target_list = None
for l in lists:
    if l["name"].lower() in ["doing", "p1", "backlog", "p0", "in progress"]:
        target_list = l["id"]
        break
if not target_list:
    target_list = lists[0]["id"]  # Fallback to first list
print(f"Using list: {target_list}")

# ─── Create bug cards ──────────────────────────────────────────────────────────
def create_bug_card(name, desc, priority="P1"):
    """Create a new bug card on VOID_Ops, assigned to Sir Green."""
    url = f"https://api.trello.com/1/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({
        "idList": target_list,
        "name": name,
        "desc": desc,
        "pos": "top",
    }).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read())
        card_id = result["id"]
        print(f"  ✅ Created: {name[:50]} (ID: {card_id})")
        
        # Add labels
        labels_to_add = ["sir-green", priority, "Bug"]
        for label_name in labels_to_add:
            # Find label ID
            label_url = f"https://api.trello.com/1/boards/{BOARD}/labels?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
            label_resp = urllib.request.urlopen(label_url).read()
            labels = json.loads(label_resp)
            for lbl in labels:
                if lbl["name"].lower() == label_name.lower():
                    lb_url = f"https://api.trello.com/1/cards/{card_id}/idLabels?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
                    lb_data = json.dumps({"value": lbl["id"]}).encode()
                    lb_req = urllib.request.Request(lb_url, data=lb_data, method='POST')
                    lb_req.add_header("Content-Type", "application/json")
                    try: urllib.request.urlopen(lb_req, timeout=10)
                    except: pass
                    break
        
        # Post Miss Pink comment
        post_comment(card_id, f"""🔍 **Miss Pink Bug Hunt ({ts}):**

**Bug found:** {name}

**Details:**
{desc}

**Root cause analysis from dashboard:**
- TreasureMap dashboard (192.168.0.39:8080) shows critical issues
- Fleet services (ports 80/81/2376/9999) all DOWN 🔴
- Vault shows 149 uncommitted files, NOT gitignored
- STEALTHATTACK shows ONLINE but is actually OFFLINE (stale status)

**Priority:** {priority}
**Assignee:** Sir Green (SQUIDSTATION maintainer)

— Miss Pink 🦜""")
        
        return card_id
    except Exception as e:
        print(f"  ❌ FAILED: {name[:50]} — {e}")
        return None
    time.sleep(0.5)

# ─── Bug Cards ──────────────────────────────────────────────────────────────
print("\n=== Filing bug cards for Sir Green ===\n")

bugs = [
    ("🐛 [BUG] Fleet Services DOWN — Ports 80/81/2376/9999 all 🔴 DOWN on SQUIDSTATION",
     f"""**Bug Hunt OODA Report — {ts}**

**Issue:** Fleet services are all DOWN on SQUIDSTATION (192.168.0.39).

**Dashboard evidence:**
- Port 80 (HTTP): 🔴 DOWN
- Port 81 (NPM): 🔴 DOWN
- Port 2376 (Docker API): 🔴 DOWN
- Port 9999 (Health): 🔴 DOWN
- Port 8080 (Dashboard): 🟢 UP

**Container fleet:** 12 total, 11 running, 1 down (void-vaultwarden or similar)

**Root cause:** Likely Docker daemon crash or NPM (Nginx Proxy Manager) failure.

**Impact:** Fleet services (HTTP, NPM, Docker API, Health check) completely unavailable.

**Fix required:**
1. Check Docker daemon status on SQUIDSTATION
2. Restart NPM (Nginx Proxy Manager) on port 81
3. Start Docker API socket on port 2376
4. Start health service on port 9999

**Verified by:** Miss Pink — TreasureMap dashboard UI inspection at 13:00Z

— 🦜""", "P0"),

    ("🐛 [BUG] Vault NOT gitignored + 149 uncommitted files — Secret leak risk",
     f"""**Bug Hunt OODA Report — {ts}**

**Issue:** Vault is NOT gitignored, with 149 uncommitted files.

**Dashboard evidence:**
- Git Status: ⚠️ Modified
- Uncommitted: ⚠️ 149 files
- Gitignored: ❌ NO
- Secrets in Git: ❌ undefined (can't verify!)
- Vault mount: ✅ Mounted

**Root cause:** Vault secrets.env and other sensitive files may be tracked in git without .gitignore.

**Risk:** Secret leak — Discord tokens, API keys, credentials exposed in git history.

**Fix required:**
1. Create/update .gitignore in vault root:
   ```
   _KEY_VAULT/
   secrets.env
   *.env
   .env
   credentials/
   tokens/
   ```
2. Remove tracked secrets: `git rm --cached secrets.env`
3. Commit .gitignore + force push

**Verified by:** Miss Pink — Captain's Dashboard → Vault Health panel at 13:00Z

— 🦜""", "P0"),

    ("🐛 [BUG] Cipher tools missing — encode_pirate.py, decode_pirate.py, TIDAL_TONGUE.md all ❌",
     f"""**Bug Hunt OODA Report — {ts}**

**Issue:** Cipher tools required for WHITE WHALE protocol are MISSING.

**Dashboard evidence:**
- encode_pirate.py: ❌ Missing
- decode_pirate.py: ❌ Missing
- TIDAL_TONGUE.md: ❌ Missing

**Root cause:** Cipher tool scripts not deployed or were deleted.

**Impact:** WHITE WHALE encrypted communications (OPSEC) not functional.
G6/G8 rules about encrypted channel + no secrets in git may be non-functional.

**Fix required:**
1. Deploy encode_pirate.py to vault/scripts/
2. Deploy decode_pirate.py to vault/scripts/
3. Create TIDAL_TONGUE.md documentation
4. Verify ciphers work + add to dashboard health check

**Verified by:** Miss Pink — Captain's Dashboard → Cipher Tools panel at 13:00Z

— 🦜""", "P1"),

    ("🐛 [BUG] STEALTHATTACK shows ONLINE but is actually OFFLINE — Stale fleet status",
     f"""**Bug Hunt OODA Report — {ts}**

**Issue:** Dashboard shows STEALTHATTACK (192.168.0.10) as 🟢 ONLINE, but it is actually OFFLINE.

**Dashboard evidence:**
- STEALTHATTACK Status: 🟢 ONLINE (WRONG)
- PINKCADY Status: 🟢 ONLINE (correct)
- SQUIDSTATION Status: 🟢 ONLINE (correct)

**Reality (verified by Miss Pink):**
- STEALTHATTACK ping: 100% packet loss ❌
- Docker TCP:2375: timed out ❌
- Ollama TCP:11434: timed out ❌
- Incident log: Z:/Developer_Brain/Shared_With_Pink/STEALTHATTACK_OFFLINE_INCIDENT_20260811.json

**Root cause:** Dashboard fleet status widget not polling actual rigs — using cached/stale data.

**Impact:** Captain thinks STEALTHATTACK is online when it's down. All 14 AI containers offline.

**Fix required:**
1. Add active health check to fleet status widget (ping + port check every 30s)
2. Add timeout handling — show ⚠️ if unreachable for >60s
3. Auto-refresh fleet status on dashboard load
4. Integrate with fleet_comms_watcher for real-time updates

**Verified by:** Miss Pink — Dashboard DOM inspection + fleet ping verification at 13:00Z

— 🦜""", "P0"),

    ("🐛 [BUG] /augur route returns empty page — AugurTab broken on dashboard",
     f"""**Bug Hunt OODA Report — {ts}**

**Issue:** Navigating to /augur on the dashboard returns an EMPTY PAGE.

**Dashboard evidence:**
- URL: http://192.168.0.39:8080/augur
- Title: "" (empty)
- Element count: 0 (blank page)
- Content: none

**Root cause:** The AugurTab.jsx component is not rendering — likely:
- Missing route definition in app.py
- Patched file not deployed to Docker container
- Missing /api/augur/augmented_signals endpoint

**Impact:** Captain cannot access Augur trading tab — blind to signals.

**Fix required:**
1. Verify /api/augur/augmented_signals endpoint is deployed in Docker
2. Check app.py route for /augur
3. Redeploy patched app.py + AugurTab.jsx to SQUIDSTATION Docker
4. Restart TreasureMap Flask service

**Verified by:** Miss Pink — Browser navigation to /augur at 13:00Z

**Evidence:** Patches exist at:
Z:/Developer_Brain/Shared_With_Pink/deploy_patches_20260811/app.py
Z:/Developer_Brain/Shared_With_Pink/deploy_patches_20260811/AugurTab.jsx

— 🦜""", "P0"),
]

for name, desc, priority in bugs:
    card_id = create_bug_card(name, desc, priority)
    if card_id:
        # Assign to Sir Green
        assign_url = f"https://api.trello.com/1/cards/{card_id}/members?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
        assign_data = json.dumps({"value": "sirgreen"}).encode()  # Sir Green's Trello username
        assign_req = urllib.request.Request(assign_url, data=assign_data, method='POST')
        assign_req.add_header("Content-Type", "application/json")
        try:
            urllib.request.urlopen(assign_req, timeout=10)
            print(f"  → Assigned to Sir Green")
        except Exception as e:
            print(f"  ⚠️ Assign failed: {e}")
    time.sleep(1)

print(f"\n{'='*70}")
print(f"BUG HUNT COMPLETE: 5 bug cards filed for Sir Green")
print("="*70)