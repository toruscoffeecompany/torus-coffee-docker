#!/usr/bin/env python3
"""
Discovery script: fetch Torus_Ops board lists, find P0 and Top 10 lists,
fetch all cards in those lists, and save card details + comments to JSON.
"""
import requests
import json
import time
import os
from datetime import datetime, timezone

BOARD_ID = "6a70a3157d0db4214ac3f9a3"
KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

BASE = "https://api.trello.com/1"
AUTH = {"key": KEY, "token": TOKEN}

LOG_DIR = r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    with open(os.path.join(LOG_DIR, "subagent_blocker.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")

log("=== DISCOVERY START ===")

# Step 1: Fetch board lists
log("Fetching board lists...")
resp = requests.get(f"{BASE}/boards/{BOARD_ID}/lists", params=AUTH)
lists = resp.json()
log(f"Found {len(lists)} lists on board")

p0_list_id = None
top10_list_id = None
done_list_id = None
sir_azure_q = None
sir_green_q = None

for lst in lists:
    name = lst["name"]
    lid = lst["id"]
    log(f"  List: '{name}' -> id={lid}")
    if "P0" in name and "Alert" in name:
        p0_list_id = lid
    elif "Top 10" in name:
        top10_list_id = lid
    elif name.lower() == "done":
        done_list_id = lid
    elif "Sir Azure" in name:
        sir_azure_q = lid
    elif "Sir Green" in name:
        sir_green_q = lid

log(f"P0 list id: {p0_list_id}")
log(f"Top 10 list id: {top10_list_id}")
log(f"Done list id: {done_list_id}")
log(f"Sir Azure's Queue id: {sir_azure_q}")
log(f"Sir Green's Queue id: {sir_green_q}")

# Step 2: Fetch cards in P0 list
log(f"\nFetching cards in P0 list ({p0_list_id})...")
p0_cards = requests.get(f"{BASE}/lists/{p0_list_id}/cards", params={**AUTH, "customFieldItems": "true"}).json()
log(f"P0 list has {len(p0_cards)} cards")
for c in p0_cards:
    log(f"  P0 Card: shortLink={c.get('shortLink')[:8]} name='{c.get('name')}'")

# Step 3: Fetch cards in Top 10 list
log(f"\nFetching cards in Top 10 list ({top10_list_id})...")
top10_cards = requests.get(f"{BASE}/lists/{top10_list_id}/cards", params={**AUTH, "customFieldItems": "true"}).json()
log(f"Top 10 list has {len(top10_cards)} cards")
for c in top10_cards:
    log(f"  Top10 Card: shortLink={c.get('shortLink')[:8]} name='{c.get('name')}'")

# Step 4: For each card, fetch details + comments
all_cards = {}
for c in p0_cards + top10_cards:
    cid = c["id"]
    short = c.get("shortLink", "")[:8]
    # Fetch card details with more fields
    detail = requests.get(f"{BASE}/cards/{cid}", params={**AUTH, "fields": "name,desc,dateLastActivity,due,labels,shortLink,idMembers", "members": "true"}).json()
    # Fetch actions (comments)
    actions = requests.get(f"{BASE}/cards/{cid}/actions", params={**AUTH, "fields": "date,memberCreator,memberRequestor,text", "filter": "commentCard"}).json()
    comments = []
    for a in actions:
        creator = a.get("memberCreator", {})
        comments.append({
            "date": a.get("date"),
            "creator": creator.get("fullName", creator.get("username", "unknown")),
            "text": a.get("text", "")
        })
    all_cards[cid] = {
        "short_link": short,
        "name": detail.get("name"),
        "desc": detail.get("desc"),
        "dateLastActivity": detail.get("dateLastActivity"),
        "due": detail.get("due"),
        "labels": [{"id": l["id"], "name": l.get("name"), "color": l.get("color")} for l in detail.get("labels", [])],
        "members": [{"id": m.get("id"), "fullName": m.get("fullName"), "username": m.get("username")} for m in detail.get("members", [])],
        "comments": comments,
        "list_id": p0_list_id if c in p0_cards else top10_list_id,
        "list_name": "P0" if c in p0_cards else "Top 10"
    }
    log(f"\nCard {short} '{detail.get('name')}':")
    log(f"  desc length: {len(detail.get('desc',''))}")
    log(f"  dateLastActivity: {detail.get('dateLastActivity')}")
    log(f"  labels: {[l['name'] for l in detail.get('labels',[])]}")
    log(f"  members: {[m.get('fullName','?') for m in detail.get('members',[])]}")
    log(f"  comments: {len(comments)}")

# Save to JSON for analysis
out_path = os.path.join(LOG_DIR, "subagent_blocker_discovery.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(all_cards, f, indent=2, ensure_ascii=False)
log(f"\nDiscovery data saved to {out_path}")
log(f"Total cards discovered: P0={len(p0_cards)}, Top10={len(top10_cards)}")
log("=== DISCOVERY END ===")
