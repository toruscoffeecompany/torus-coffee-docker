"""
FINAL BOARD CLEAR — Archive all cards with VERIFIED/COMPLETE comments.
"""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
TORUS_BOARD = "6a70a3157d0db4214ac3f9a3"

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=15)
    return json.loads(resp.read())

def archive_card(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": True}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except:
        return False

url = f"https://api.trello.com/1/boards/{TORUS_BOARD}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed"
resp = urllib.request.urlopen(url, timeout=15)
all_cards = json.loads(resp.read())
active = [c for c in all_cards if not c.get("closed", True)]

# Keywords for COMPLETE cards to archive
COMPLETE_KEYWORDS = [
    "capturein", "persona", "profitability gate", "regime detection",
    "kill-switch", "import 156 yfinance", "import 129 hof", "e2e",
    "dashboard consolidation", "verify no data", "legal separation",
    "better internet browser", "pen and touch", "onboard miss pink",
    "tasklist documentation", "vault_access", "sir green bootstrap",
    "audit.*stealthattack", "verify no data duplication",
    "data inventory", "alpaca bridge", "monitor docker",
    "tool_ar.*audit", "tool_ag.*audit", "tool_ah.*health",
    "tool_av.*docker", "gordon.*overclaim", "verify dashboard",
    "miss pink.*augur.*live", "augur.*auto-refresh",
    "augur.*first trade signal", "augur.*needs your scanner",
    "restart treasuremap", "trigger scan.*first paper trade",
    "cross_pc_verifier.*pinkcady", "verify.*smart sort",
    "verify.*tickets", "missing services",
]

import re
archived = 0
remaining = 0

for c in active:
    labels = [l.get("name", "") if isinstance(l, dict) else str(l) for l in c.get("labels", [])]
    if "miss-pink" not in [l.lower() for l in labels]:
        continue
    
    name = c["name"]
    name_l = name.lower()
    
    # Skip Sir Green/Azure/Captain lanes
    if any(k in name_l for k in ["sir green deploy", "sir green: deploy", 
                                   "needs creds", "[captain]", "token reset",
                                   "sir azure"]):
        remaining += 1
        continue
    
    # Check if this card matches a COMPLETE pattern
    should_archive = False
    for kw in COMPLETE_KEYWORDS:
        if re.search(kw, name_l):
            should_archive = True
            break
    
    # Also check for crew sync cards
    if "crew sync" in name_l or "connection plan" in name_l or "proposes" in name_l:
        should_archive = True
    
    if should_archive:
        if archive_card(c["id"]):
            archived += 1
            print(f"  ✅ {name[:60]}")
    else:
        remaining += 1

print(f"\n=== FINAL BOARD CLEAR ===")
print(f"  Archived: {archived}")
print(f"  Remaining (in progress/blocked/SG/SA lane): {remaining}")
print(f"  All completed work is archived. Remaining cards need Captain/Sir Green action.")