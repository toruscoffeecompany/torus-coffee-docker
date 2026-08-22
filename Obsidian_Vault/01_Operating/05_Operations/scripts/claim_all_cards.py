"""
MISS PINK — CLAIM ALL UNASSIGNED TORUS_OPS CARDS + VERIFY EVERYTHING.
Step 1: Get ALL unassigned cards on Torus_Ops board
Step 2: Assign them to Miss Pink
Step 3: Categorize + work each one
Step 4: Verify end-to-end
"""
import json, urllib.request, sqlite3, os, sys, time
from datetime import datetime

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

TORUS_BOARD = "6a70a3157d0db4214ac3f9a3"

def trello_get(path, params=None):
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}&{query}"
    else:
        url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

def trello_put(path, data):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), method='PUT')
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except:
        return False

def post_comment(card_id, text):
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except:
        return False

# ─── 1. Get my member ID ─────────────────────────────────────────────────────
me = trello_get("members/me")
my_id = me["id"]
print(f"Miss Pink ID: {my_id}")

# ─── 2. Get ALL Torus_Ops cards ────────────────────────────────────────────────
print(f"\n=== FETCHING ALL TORUS_OPS CARDS ===")
all_cards = trello_get(f"boards/{TORUS_BOARD}/cards")
active_cards = [c for c in all_cards if not c.get("closed", True)]
print(f"Total active cards on Torus_Ops: {len(active_cards)}")

# ─── 3. Get board labels + lists ───────────────────────────────────────────────
labels = trello_get(f"boards/{TORUS_BOARD}/labels")
lists = trello_get(f"boards/{TORUS_BOARD}/lists")
label_map = {l["id"]: l["name"] for l in labels}
list_map = {l["id"]: l["name"] for l in lists}

# ─── 4. Find unassigned cards + assign to me ───────────────────────────────────
print(f"\n=== CLAIMING UNASSIGNED CARDS ===")
unassigned = []
for c in active_cards:
    members = c.get("idMembers", [])
    # If idMembers isn't in the response, try to get it
    if not members:
        # Try getting card details
        try:
            card_detail = trello_get(f"cards/{c['id']}")
            members = card_detail.get("idMembers", [])
        except:
            pass
    if not members:
        unassigned.append(c)

print(f"Unassigned cards: {len(unassigned)}")

claimed = 0
for c in unassigned:
    # Only claim if not already miss-pink labeled (those we already processed)
    card_labels = [label_map.get(l["id"], "") for l in c.get("labels", [])]
    # Check if card is in Sir Green's or Sir Azure's lane
    label_lower = " ".join(card_labels).lower()
    
    should_skip = False
    # Skip Sir Green's deploy cards
    if any(k in c["name"].lower() or k in c.get("desc", "").lower() for k in [
        "sir green deploy", "deploy signal_augmentation", "populate ticker",
        "wire augmented", "docker exec", "docker-side", "deploy to squidstation",
        "docker container",
    ]):
        should_skip = True
    
    # Skip Captain-only blocks
    if any(k in c["name"].lower() for k in [
        "[captain]", "needs creds", "needs manual", "token reset",
    ]):
        should_skip = True
    
    if should_skip:
        print(f"  ⏭️ SKIP (not my lane): {c['name'][:50]}")
        continue
    
    # Assign to me
    result = trello_put(f"cards/{c['id']}", {"idMembers": [my_id]})
    if result:
        claim_msg = ""
        if "miss-pink" not in [l.lower() for l in card_labels]:
            # Add miss-pink label
            mp_label = None
            for l in labels:
                if l["name"].lower() in ["miss-pink", "misspink", "miss_pink"]:
                    mp_label = l["id"]
                    break
            if mp_label:
                trello_put(f"cards/{c['id']}", {"idLabels": [mp_label]})
                claim_msg = " (label added)"
        print(f"  ✅ CLAIMED: {c['name'][:50]}{claim_msg}")
        claimed += 1
    else:
        print(f"  ❌ Failed to claim: {c['name'][:50]}")

print(f"\nTotal claimed: {claimed}")

# ─── 5. Now get ALL miss-pink cards on Torus_Ops ────────────────────────────────
print(f"\n=== ALL MISS-PINK CARDS ON TORUS_OPS ===")
my_cards = []
for c in active_cards:
    members = c.get("idMembers", [])
    # Get card detail for members + labels if needed
    if not members or not c.get("labels"):
        try:
            cd = trello_get(f"cards/{c['id']}")
            members = cd.get("idMembers", members)
            card_label_objs = cd.get("labels", c.get("labels", []))
        except:
            card_label_objs = c.get("labels", [])
    else:
        card_label_objs = c.get("labels", [])
    
    # Resolve label IDs to names
    card_labels = []
    for l in card_label_objs:
        if isinstance(l, dict):
            lid = l.get("id")
            lname = l.get("name")
            if lname:
                card_labels.append(lname)
            elif lid:
                card_labels.append(label_map.get(lid, ""))
        else:
            card_labels.append(str(l))
    
    card_labels = [l for l in card_labels if l]
    label_lower = [l.lower() for l in card_labels]
    
    if my_id in members or "miss-pink" in label_lower:
        priority = "P0" if "P0" in card_labels else "P1" if "P1" in card_labels else "P2" if "P2" in card_labels else "P3" if "P3" in card_labels else "OTHER"
        done = "DONE" if any(l in card_labels for l in ["Done", "done", "COMPLETE", "Complete"]) else "TODO"
        slist = list_map.get(c.get("idList", ""), "?")
        my_cards.append({
            "id": c["id"],
            "name": c["name"],
            "priority": priority,
            "status": done,
            "list": slist,
            "labels": card_labels,
            "url": c.get("shortUrl", ""),
            "desc": c.get("desc", "")[:150],
        })

print(f"Total miss-pink cards on Torus_Ops: {len(my_cards)}")

# Categorize
by_status = {}
for c in my_cards:
    key = f"{c['priority']}-{c['status']}"
    by_status.setdefault(key, []).append(c)

for key in sorted(by_status.keys()):
    cards = by_status[key]
    print(f"\n  [{key}] ({len(cards)} cards):")
    for c in cards[:5]:
        print(f"    • {c['name'][:60]} [{c['list'][:20]}]")

print(f"\n{'='*70}")
print(f"READY TO WORK: {len(my_cards)} cards")
print(f"{'='*70}")