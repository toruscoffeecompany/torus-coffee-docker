import requests, os, re

TRELLO_KEY = os.environ.get("TRELLO_KEY") or "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = os.environ.get("TRELLO_TOKEN") or "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

DEST_QUEUES = {
    "sir-green": "6a777169cd5feec20ef26ede",
    "sir-azure": "6a776abeeb95769f264a0bda",
}

for crew, list_id in DEST_QUEUES.items():
    params = {"key": TRELLO_KEY, "token": TRELLO_TOKEN, "fields": "name,id,shortUrl,desc"}
    r = requests.get(f"https://api.trello.com/1/lists/{list_id}/cards", params=params, timeout=30)
    cards = r.json()
    print(f"{crew}: {len(cards)} cards")
    for c in cards:
        src = ""
        m = re.search(r"Synced from Torus_Ops: (https://trello\.com/c/[^\s]+)", c.get("desc", ""))
        if m:
            src = m.group(1)
        print(f"  - {c['name']} | {c.get('shortUrl','')} | src={src}")
