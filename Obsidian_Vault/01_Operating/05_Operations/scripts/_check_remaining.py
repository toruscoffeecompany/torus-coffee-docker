#!/usr/bin/env python3
"""
Check remaining TORUS_OPS open cards after Batch 4.
"""
import json, time, urllib.request, urllib.parse, os

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "ATTA5fa83ac8abb79f4f0431b2753c87cb04fe898aa700ff84d1f1c1648f180034d2dC1621D9C"
TORUS_OPS = "6a70a3157d0db4214ac3f9a3"

def t_get(path, params=None):
    url = f"https://api.trello.com/1{path}?key={KEY}&token={TOKEN}"
    if params:
        url += "&" + "&".join(f"{urllib.parse.quote(k)}={urllib.parse.quote(str(v))}" for k, v in params.items())
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=25) as resp:
            return resp.read().decode("utf-8")
    except:
        return None

time.sleep(5)

lists_out = t_get(f"/boards/{TORUS_OPS}/lists", {"fields": "id,name"})
lists = json.loads(lists_out)
print("=== TORUS_OPS Lists ===\n")
for l in lists:
    time.sleep(2)
    cards_out = t_get(f"/lists/{l['id']}/cards", {"fields": "id,name"})
    cards = json.loads(cards_out) if cards_out else []
    print(f"{l['name']}: {len(cards)} cards")
    for c in cards:
        print(f"  • {c['name'][:70]}")

remaining = sum(
    len(json.loads(t_get(f"/lists/{l['id']}/cards", {"fields": "id,name"}) or "[]"))
    for l in lists if not any(kw in l["name"].lower() for kw in ["done", "complete", "archive"])
)
print(f"\nTotal remaining open cards: {remaining}")
os.remove(__file__)
