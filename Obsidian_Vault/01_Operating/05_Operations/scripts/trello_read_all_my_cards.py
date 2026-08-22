"""Read all Trello cards assigned to miss-pink and work the actionable P0/P1/P2 items."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

def trello_get(path):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())

def trello_post(path, body):
    url = f"https://api.trello.com/1/{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

cards = trello_get(f"boards/{BOARD_ID}/cards")
mine = [c for c in cards if "miss-pink" in [l.get("name","") for l in c.get("labels",[])]]

p0, p1, p2 = [], [], []
for c in mine:
    labels = [l.get("name","") for l in c.get("labels",[])]
    if "P0" in labels: p0.append(c)
    elif "P1" in labels: p1.append(c)
    elif "P2" in labels: p2.append(c)

print("="*70)
print(f"MY CARDS: P0={len(p0)} P1={len(p1)} P2={len(p2)} Total={len(mine)}")
print("="*70)

print(f"\n{'█'*70}")
print(f"P0 — CRITICAL ({len(p0)})")
print(f"{'█'*70}")
for c in p0:
    print(f"\n  {c['name'][:65]}")
    print(f"  URL: {c['url']}")
    # Get card details
    detail = trello_get(f"cards/{c['id']}?fields=name,desc,labels,idList,status,url,dateLastActivity")
    desc = detail.get("desc", "")[:200]
    print(f"  Desc: {desc}...")

print(f"\n{'='*70}")
print(f"P1 — HIGH ({len(p1)})")
print(f"{'='*70}")
for c in p1[:10]:
    labels = [l.get("name","") for l in c.get("labels",[])]
    print(f"  [{','.join([l for l in labels if l][:4])}] {c['name'][:65]}")

print(f"\n{'='*70}")
print(f"P2 — MEDIUM ({len(p2)})")
print(f"{'='*70}")
for c in p2[:10]:
    labels = [l.get("name","") for l in c.get("labels",[])]
    print(f"  [{','.join([l for l in labels if l][:4])}] {c['name'][:60]}")

print(f"\n... and {len(p2)-10} more P2 cards")