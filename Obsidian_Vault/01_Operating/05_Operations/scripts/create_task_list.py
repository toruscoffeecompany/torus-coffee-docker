"""
OODA Loop #2 — Work Sir Green cards that overlap with Miss Pink's verified work.
Focus on: connectivity, dashboard, vault, automation, fleet — areas where
Miss Pink has already verified the infrastructure.
Create task list → work → verify → close.
"""
import json, urllib.request, os, subprocess, time

TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"
ts = "2026-08-11T05:45Z"

def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except Exception as e: print(f"  ⚠️ Comment: {e}")
    time.sleep(0.3)

def archive_card(cid):
    url = f"https://api.trello.com/1/cards/{cid}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": True}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except Exception as e: print(f"  ⚠️ Archive: {e}")
    time.sleep(0.3)

def get_labels(c):
    return [l.get("name", "") for l in c.get("labels", []) if isinstance(l, dict)]

# ─── Get all VOID_Ops open cards ──────────────────────────────────────────────
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc&filter=open")
cards = json.loads(resp.read())

# ─── Create task list of actionable Sir Green cards I can help verify ─────────
# Focus on cards where Miss Pink has ALREADY verified the infrastructure
task_list = []

for c in cards:
    if c.get("closed"): continue
    name_l = c["name"].lower()
    desc = c.get("desc", "").lower()
    combined = name_l + " " + desc
    labels = get_labels(c)
    labels_l = [l.lower() for l in labels]
    
    # Sir Green cards that Miss Pink can coordinate/verify
    if "sir-green" in labels_l or "sir green" in name_l:
        # Cards where Miss Pink has verified related infrastructure
        if any(k in combined for k in [
            "connectivity monitor", "fleet mesh", "tailscale", "docker context",
            "vault", "inbox", "inbox path", "cross_pc_verifier",
            "dashboard", "hive-mind", "ship status", "fleet status",
            "alert router", "prometheus", "grafana", "monitoring",
            "email", "gmail reader", "email digest",
            "self-healing", "watchdog", "cron",
            "kubernetes", "k8s", "deploy",
            "gordon", "api_server",
            "ollama", "gpu", "comfyui",
        ]):
            task_list.append(c)

print(f"=== ACTIONABLE TASK LIST ===")
print(f"Total Sir Green cards I can help verify: {len(task_list)}\n")

# Categorize the task list
verified_categories = {
    "Fleet/Connectivity": [],
    "Dashboard": [],
    "Vault/Comms": [],
    "Automation": [],
    "Deploy/Container": [],
    "Monitoring": [],
    "Other": [],
}

for c in task_list:
    name_l = c["name"].lower()
    desc = c.get("desc", "").lower()
    combined = name_l + " " + desc
    
    if any(k in combined for k in ["connectivity", "fleet mesh", "tailscale", "cross_pc"]):
        verified_categories["Fleet/Connectivity"].append(c)
    elif any(k in combined for k in ["dashboard", "hive-mind", "ship", "grafana", "kuma", "prometheus"]):
        verified_categories["Dashboard"].append(c)
    elif any(k in combined for k in ["vault", "inbox", "email", "gmail", "digest"]):
        verified_categories["Vault/Comms"].append(c)
    elif any(k in combined for k in ["self-healing", "watchdog", "automation", "auto-respond", "sort email"]):
        verified_categories["Automation"].append(c)
    elif any(k in combined for k in ["deploy", "k8s", "kubernetes", "gordon", "api_server", "ollama", "gpu", "comfyui"]):
        verified_categories["Deploy/Container"].append(c)
    elif any(k in combined for k in ["monitor", "alert"]):
        verified_categories["Monitoring"].append(c)
    else:
        verified_categories["Other"].append(c)

for cat, items in verified_categories.items():
    if items:
        print(f"\n{cat} ({len(items)}):")
        for c in sorted(items, key=lambda x: x["name"])[:8]:
            print(f"  • {c['name'][:58]}")
        if len(items) > 8:
            print(f"  ... ({len(items) - 8} more)")

print(f"\n{'='*70}")
print(f"TOTAL ACTIONABLE TASKS: {len(task_list)}")
print("="*70)