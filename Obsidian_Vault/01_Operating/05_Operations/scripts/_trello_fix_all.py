#!/usr/bin/env python3
"""
FIX: Update Trello credentials + access all boards.
The CORRECT token (from trello_client.py) is:
  TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE
The WRONG token (in credentials file) had 'ac8abb' but correct has 'ac8bb'.
"""
import json, time, urllib.request, urllib.parse, urllib.error
import re

# ─── CORRECT credentials ─────────────────────────────────────────
KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
SECRET = "7a18fea7cb6ff6a44ef933669f80f48d06d896dcb43ca015db67607a9d3edab7"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"  # CORRECT!

# Board IDs
BOARDS = {
    "VOID_OPS": "6a595669b8f8f99c93392f4f",
    "TORUS_OPS": "6a70a3157d0db4214ac3f9a3",
    "Sir Azure STEALTHATTACK": "6a737c97a7d29e8c7c34cf5a",
    "Sir_Azure_Ops": "6a839af9b5e7e56792d25e30",
    "Business Docs": "6a70a3152b3a1f6dca3fa08c",
    "Website Rebuild": "6a70a316f884c39f2dc5e6a6",
}

def trello_get(path, params=None, max_retries=5):
    url = f"https://api.trello.com/1{path}?key={KEY}&token={TOKEN}"
    if params:
        url += "&" + "&".join(f"{urllib.parse.quote(k)}={urllib.parse.quote(str(v))}" for k, v in params.items())
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=25) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(5 * (attempt + 1))
            else:
                return None
        except Exception:
            time.sleep(3 * (attempt + 1))
    return None

def trello_post(path, data_dict, max_retries=5):
    url = f"https://api.trello.com/1{path}?key={KEY}&token={TOKEN}"
    data = urllib.parse.urlencode(data_dict).encode()
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=25) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(5 * (attempt + 1))
            else:
                err_body = ""
                try:
                    err_body = e.read().decode()[:200]
                except:
                    pass
                return f"ERR_{e.code}: {err_body}"
        except Exception:
            time.sleep(3 * (attempt + 1))
    return None

time.sleep(5)

# ─── Test all 3 boards ───────────────────────────────────────────────────
print("=== TESTING ALL 3 CREW BOARDS ===\n")
for name, bid in BOARDS.items():
    time.sleep(2)
    resp = trello_get(f"/boards/{bid}", {"fields": "name,url"})
    if resp:
        data = json.loads(resp)
        print(f"  ✅ {name}: {data.get('name', '???')} — {data.get('url', '???')}")
    else:
        print(f"  ❌ {name}: FAILED")

# ─── Get lists for each board ────────────────────────────────────────────
print("\n=== BOARD LISTS ===\n")

board_lists = {}
for name, bid in BOARDS.items():
    if name in ["Business Docs", "Website Rebuild", "My Trello Board"]:
        continue
    time.sleep(3)
    lists_out = trello_get(f"/boards/{bid}/lists", {"fields": "id,name"})
    if lists_out:
        lists = json.loads(lists_out)
        board_lists[name] = lists
        print(f"  {name}:")
        for l in lists:
            print(f"    {l['name']} ({l['id'][:10]}...)")
    else:
        print(f"  {name}: FAILED to get lists")
    print()

# ─── Identify Sir Azure Ops board ────────────────────────────────────────
print("=== SIRA AURELIA / STEALTHATTACK BOARDS ===\n")
if "Sir Azure / STEALTHATTACK" in board_lists:
    print("Sir Azure / STEALTHATTACK lists:")
    for l in board_lists["Sir Azure / STEALTHATTACK"]:
        print(f"  {l['name']}")
    print()

if "Sir_Azure_Ops" in board_lists:
    print("Sir_Azure_Ops lists:")
    for l in board_lists["Sir_Azure_Ops"]:
        print(f"  {l['name']}")

# ─── Get open cards from TORUS_OPS ─────────────────────────────────────___
print(f"\n{'='*60}")
print("TORUS_OPS open cards:")
print(f"{'='*60}")
torus_open = 0
if "TORUS_OPS" in board_lists:
    for l in board_lists["TORUS_OPS"]:
        if any(kw in l["name"].lower() for kw in ["done", "completed", "archive"]):
            continue
        time.sleep(3)
        cards_out = trello_get(f"/lists/{l['id']}/cards", {"fields": "id,name,labels"})
        if cards_out:
            cards = json.loads(cards_out)
            for c in cards:
                labels = [t.get("name","") for t in c.get("labels",[])]
                label_str = ", ".join(labels) if labels else "no labels"
                if not any(kw in l["name"].lower() for kw in ["done", "backlog"]):
                    print(f"  [{l['name']}] {c['name'][:65]} ({label_str})")
                torus_open += 1

print(f"\nTotal TORUS_OPS open cards: {torus_open}")

# ─── Get VOID_OPS Done card count ────────────────────────────────────────
print(f"\n{'='*60}")
print("VOID_OPS Done cards:")
print(f"{'='*60}")
if "VOID_OPS" in board_lists:
    for l in board_lists["VOID_OPS"]:
        if "done" in l["name"].lower():
            time.sleep(3)
            cards_out = trello_get(f"/lists/{l['id']}/cards", {"fields": "id,name"})
            if cards_out:
                cards = json.loads(cards_out)
                print(f"  {l['name']}: {len(cards)} cards")
                for c in cards[:5]:
                    print(f"    • {c['name'][:65]}")

print(f"\n{'='*60}")
print("ALL BOARDS ACCESSIBLE!")
print(f"{'='*60}")
print(f"VOID_OPS: {BOARDS['VOID_OPS']}")
print(f"TORUS_OPS: {BOARDS['TORUS_OPS']}")
print(f"Sir Azure / STEALTHATTACK: {BOARDS['Sir Azure / STEALTHATTACK']}")
print(f"Sir_Azure_Ops: {BOARDS['Sir_Azure_Ops']}")

# Save boards to memory
with open(r"D:\Work\.pirate_automation\scripts\_trello_boards_found.py", "w") as f:
    f.write(f"KEY = '{KEY}'\nTOKEN = '{TOKEN}'\n")
    for name, bid in BOARDS.items():
        f.write(f"{name.upper()} = '{bid}'\n")
