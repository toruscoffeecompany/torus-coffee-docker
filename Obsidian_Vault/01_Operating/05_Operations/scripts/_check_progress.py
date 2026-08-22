#!/usr/bin/env python3
"""
Check how many cards were already processed + continue the batch 2.
"""
import json, subprocess, time

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "ATTA5fa83ac8bb79f4f0431b2753c87cb04fe898aa700ff84d1f1c1648f180648f180034d2dC1621D9C"
VOID = "6a595669b8f8f99c93392f4f"

time.sleep(6)
r = subprocess.run(["curl", "-s", "--connect-timeout", "15",
    f"https://api.trello.com/1/boards/{VOID}/lists?fields=id,name&key={KEY}&token={TOKEN}"],
    capture_output=True, text=True, timeout=20)
lists = json.loads(r.stdout)
list_map = {l["name"]: l["id"] for l in lists}

# Count cards in each list
time.sleep(6)
for name, lid in list_map.items():
    r = subprocess.run(["curl", "-s", "--connect-timeout", "15",
        f"https://api.trello.com/1/lists/{lid}/cards?fields=name&key={KEY}&token={TOKEN}"],
        capture_output=True, text=True, timeout=20)
    try:
        cards = json.loads(r.stdout)
        print(f"  {name}: {len(cards)} cards")
    except:
        print(f"  {name}: ERROR")

# Check recent To Do cards for "Miss Pink verification" comments (our reopen markers)
time.sleep(6)
r = subprocess.run(["curl", "-s", "--connect-timeout", "15",
    f"https://api.trello.com/1/lists/{list_map.get('To Do', '')}/cards?fields=name,actions&key={KEY}&token={TOKEN}"],
    capture_output=True, text=True, timeout=30)
todo_cards = json.loads(r.stdout)
reopened = [c for c in todo_cards if any(a.get("data", {}).get("text", "") for a in c.get("actions", []) if "Miss Pink verification FAILED" in a.get("data", {}).get("text", ""))]
print(f"\n  Cards with 'Miss Pink verification FAILED' comments: {len(reopened)}")

for c in reopened[:10]:
    print(f"    {c['name'][:60]}")

print(f"\n{'='*60}")

os.remove(__file__)
