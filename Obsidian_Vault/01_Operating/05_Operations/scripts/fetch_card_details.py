#!/usr/bin/env python3
"""
Fetch detailed card info + ALL raw actions (comments) for the 8 P0 + 6 Top10 inbox target cards.
Uses short links which Trello API accepts.
"""
import requests
import json
import os
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BASE = "https://api.trello.com/1"
AUTH = {"key": KEY, "token": TOKEN}

LOG_DIR = r"D:\Work\Torus Coffee Company LLC\10_Skills_Library\05_Operations\logs"

# 8 P0 hard blocker cards (by short link)
P0_TARGETS = {
    "j78qCBv7": {"name": "torus-inventory deployment blocked", "crew": "Sir Green"},
    "AxIrRTvk": {"name": "DOCKER HUB PUSH RESULTS Alert Router blocked", "crew": "Sir Azure"},
    "XHMIZE7Z": {"name": "SQUIDSTATION images push blocked by auth", "crew": "Sir Azure"},
    "PA0cXfnz": {"name": "Alert Router repo lacks write permission", "crew": "Sir Azure"},
    "Y4ZukTiV": {"name": "ONE ACTION GRANT WRITE ACCESS OR PROVIDE PAT", "crew": "Sir Azure"},
    "BhiiSMda": {"name": "Dashboard image blocked - need Docker Hub auth", "crew": "Sir Azure"},
    "C62H03IE": {"name": "sirazure security tools missing", "crew": "Sir Azure"},
    "NqP799aw": {"name": "sirazure security deep dive summary", "crew": "Sir Azure"},
}

# Also related Docker Hub PAT card (potentially the 8th P0)
EXTRA_P0 = {
    "ZKN2PLUL": {"name": "CODING ORDER DOCKER HUB WRITE ACCESS FOR ALERT ROUTER", "crew": "Sir Azure"},
}

# 6 Top 10 inbox cards
TOP10_INBOX = {
    "DBt9Lo9F": {"name": "miss gordon docker blockers sirgreen", "crew": "Sir Green"},
    "wBjiNiQX": {"name": "trello api 401 invalid key blocker sirazure", "crew": "Sir Azure"},
    "eki12c7i": {"name": "trello api 401 invalid key blocker sirgreen", "crew": "Sir Green"},
    "da6AVCGc": {"name": "sirgreen docker deep dive urgent sirgreen", "crew": "Sir Green"},
    "QOsSORTv": {"name": "sirazure re docker urgent findings sirazure", "crew": "Sir Azure"},
    "pRdpRKKE": {"name": "sirazure squidstation deploy reply sirazure", "crew": "Sir Azure"},
}

ALL_TARGETS = {**P0_TARGETS, **EXTRA_P0, **TOP10_INBOX}

results = {}
for short, meta in ALL_TARGETS.items():
    print(f"\n{'='*70}")
    print(f"SHORT: {short} | {meta['name']} | Crew: {meta['crew']}")
    print(f"{'='*70}")

    # Fetch card details
    card_resp = requests.get(f"{BASE}/cards/{short}", params={**AUTH,
        "fields": "name,desc,dateLastActivity,due,idList,idLabels,labels,shortLink,idMembers",
        "members": "true"})
    if card_resp.status_code != 200:
        print(f"  ERROR fetching card: {card_resp.status_code} {card_resp.text}")
        continue
    card = card_resp.json()
    print(f"  CARD ID: {card['id']}")
    print(f"  Name: {card['name']}")
    print(f"  List ID: {card.get('idList')}")
    print(f"  dateLastActivity: {card.get('dateLastActivity')}")
    print(f"  Due: {card.get('due')}")
    print(f"  Labels: {[l.get('name') for l in card.get('labels',[])]}")
    print(f"  Members: {[m.get('fullName','?') for m in card.get('members',[])]}")
    print(f"\n  DESC ({len(card.get('desc',''))} chars):")
    print(f"  {card.get('desc','')[:2000]}")

    # Fetch ALL actions (not just comments) to see full history
    actions_resp = requests.get(f"{BASE}/cards/{short}/actions", params={**AUTH,
        "fields": "id,date,memberCreator,memberRequestor,text,type,data"})
    if actions_resp.status_code != 200:
        print(f"  ERROR fetching actions: {actions_resp.status_code}")
        actions = []
    else:
        actions = actions_resp.json()
    print(f"\n  ACTIONS ({len(actions)} total):")
    for a in actions:
        atype = a.get("type", "")
        creator = a.get("memberCreator", {}) or {}
        creator_name = creator.get("fullName", creator.get("username", "?"))
        text = (a.get("text") or "").strip()[:300]
        adate = a.get("date", "")
        print(f"    [{atype}] {adate} {creator_name}: {text[:200]}")
        if atype.startswith("comment"):
            print(f"      FULL TEXT: {text}")

    results[short] = {
        "card_id": card["id"],
        "short_link": short,
        "name": card.get("name"),
        "desc": card.get("desc"),
        "dateLastActivity": card.get("dateLastActivity"),
        "due": card.get("due"),
        "idList": card.get("idList"),
        "labels": [l.get("name") for l in card.get("labels",[])],
        "members": [m.get("fullName","?") for m in card.get("members",[])],
        "crew": meta["crew"],
        "actions": [{"type": a.get("type"), "date": a.get("date"),
                      "creator": (a.get("memberCreator") or {}).get("fullName", "?"),
                      "text": a.get("text","")} for a in actions]
    }

out_path = os.path.join(LOG_DIR, "subagent_blocker_details.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n\nDetails saved to {out_path}")
