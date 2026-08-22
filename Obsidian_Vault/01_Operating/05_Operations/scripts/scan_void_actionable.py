"""Scan VOID_Ops for next batch of actionable cards."""
import json, urllib.request

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"

resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/6a595669b8f8f99c93392f4f/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,desc&filter=open")
cards = json.loads(resp.read())

actionable = []
for c in cards:
    n = c["name"].lower()
    d = c.get("desc", "").lower()
    combined = n + " " + d
    
    if any(k in combined for k in ["vault", "inbox", "sync", "migration", "cleanup", "audit",
                                    "deploy", "docker", "container", "cron", "watch", "runner",
                                    "config", "setup", "install", "verify"]):
        actionable.append(c)

print(f"Actionable VOID_Ops cards: {len(actionable)}")
for c in sorted(actionable, key=lambda x: x["name"])[:25]:
    labels = [l.get("name", "") for l in c.get("labels", []) if isinstance(l, dict)]
    label_str = ",".join(labels[:2]) if labels else "no-label"
    print(f"  [{label_str}] {c['name'][:60]}")