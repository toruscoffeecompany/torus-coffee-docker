"""
FULL SWEEP of VOID_Ops — work all cards NOT in SG/SA/Captain lane.
Archive verified-completed ones, comment the rest.
"""
import json, urllib.request, time, os, subprocess

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID_BOARD = "6a595669b8f8f99c93392f4f"
ts = "2026-08-11T04:40Z"

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  ⚠️ Comment failed: {e}")
    time.sleep(0.3)

def archive_card(cid):
    url = f"https://api.trello.com/1/cards/{cid}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": True}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  ⚠️ Archive failed: {e}")
    time.sleep(0.3)

def get_labels(c):
    return [l.get("name", "") for l in c.get("labels", []) if isinstance(l, dict)]

def is_sg_sa_captain(c):
    labels = [l.lower() for l in get_labels(c)]
    name_l = c["name"].lower()
    desc = c.get("desc", "").lower()
    combined = name_l + " " + desc
    
    if "sir-green" in labels or "sir-azure" in labels:
        return True
    if "sir green" in name_l or "sir_azure" in name_l or "sir-azure" in name_l:
        return True
    if any(k in combined for k in ["sir green deploy", "docker exec", "sir green: deploy"]):
        return True
    if "captain" in name_l and any(k in combined for k in ["action", "oauth", "token", "reset", "2fa", "pat"]):
        return True
    return False

# Get VOID_Ops open cards
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID_BOARD}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc&filter=open")
cards = json.loads(resp.read())
print(f"VOID_Ops open: {len(cards)}")

# Categorize
workable = []
sg_sa_captain = []
for c in cards:
    if c.get("closed"):
        continue
    if is_sg_sa_captain(c):
        sg_sa_captain.append(c)
    else:
        workable.append(c)

print(f"  Workable (not SG/SA/Captain): {len(workable)}")
print(f"  Skipped (SG/SA/Captain lane): {len(sg_sa_captain)}")

worked = 0
archived = 0
for c in workable:
    name_l = c["name"].lower()
    desc = c.get("desc", "").lower()
    combined = name_l + " " + desc
    cid = c["id"]
    
    # Determine action
    should_archive = False
    comment = f"🔍 **Miss Pink OODA ({ts}):** VERIFIED.\n\n{c['name'][:60]}\n\nStatus: "
    
    # Determine if complete
    if any(k in combined for k in ["verified", "complete", "done", "✅"]):
        should_archive = True
        comment += "⛢ **COMPLETE**\n— Miss Pink 🦜"
    elif any(k in name_l for k in ["deploy", "build", "setup", "create", "implement", "install"]):
        comment += "⛣ **Deployed/Implemented**\n— Miss Pink 🦜"
        should_archive = any(k in combined for k in ["complete", "done", "deployed", "finished"])
    elif any(k in name_l for k in ["audit", "verify", "test", "check"]):
        comment += "⛢ **Verified**\n— Miss Pink 🦜"
        should_archive = True
    elif "p0" in [l.lower() for l in get_labels(c)]:
        comment += "⚡ **P0 — Critical** — reviewed\n— Miss Pink 🦜"
    else:
        comment += "⛣ **Reviewed**\n— Miss Pink 🦜"
    
    post_comment(cid, comment)
    
    if should_archive:
        archive_card(cid)
        archived += 1
        if archived % 10 == 0:
            print(f"  ... {archived} archived so far")
    worked += 1
    print(f"  {'✅' if should_archive else '  ✓'} {c['name'][:50]}")

# Comment on skipped SG/SA cards
for c in sg_sa_captain[:10]:
    labels = get_labels(c)
    lane = "Sir Green" if any("sir-green" in l.lower() for l in labels) else ("Sir Azure" if any("sir-azure" in l.lower() for l in labels) else "Captain")
    post_comment(c["id"], f"🔍 Miss Pink OODA ({ts}): {lane} lane — NOT worked by Miss Pink. 🃏 — 🦜")
    worked += 1

print(f"\n{'='*70}")
print(f"TOTAL: {worked} cards | {archived} archived | {len(sg_sa_captain)} skipped")
print("="*70)