"""
trello_full_audit.py — Build comprehensive tasklist from ALL Torus Ops Trello cards.
Categorizes by priority, owner, and Augur relevance.
"""
import json, urllib.request, sys

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

# Get all lists
lists = trello_get(f"boards/{BOARD_ID}/lists")
list_map = {l["id"]: l["name"] for l in lists}

# Get all members on the board
members = trello_get(f"boards/{BOARD_ID}/members")
member_map = {m["id"]: m.get("fullName", m.get("username", "?")) for m in members}

# Get ALL cards with full details
cards = trello_get(f"boards/{BOARD_ID}/cards")

print(f"{'='*70}")
print(f"TORUS OPS BOARD — FULL TASK LIST AUDIT")
print(f"Total cards: {len(cards)} | Total members: {len(members)}")
print(f"{'='*70}")

# Categorize all cards
tasks = []
for c in cards:
    name = c.get("name", "")[:100]
    desc = c.get("desc", "")[:200]
    labels = [l.get("name", "") for l in c.get("labels", [])]
    list_id = c.get("idList", "")
    list_name = list_map.get(list_id, "?")
    due = c.get("due", "None")
    members_on_card = [m.get("id", "") for m in c.get("members", [])]
    member_names = [member_map.get(m, "?") for m in members_on_card]
    
    # Determine priority
    priority = "P3"
    for p in ["P0", "P1", "P2"]:
        if p in labels:
            priority = p
            break
    
    # Determine if assigned to sir_green, miss_pink, or sir_azure
    assigned_to = "unassigned"
    for m in member_names:
        if "Green" in m or "Sir Green" in m:
            assigned_to = "sir_green"
        elif "Azure" in m or "Sir Azure" in m:
            assigned_to = "sir_azure"
        elif "Pink" in m or "Brewbeard" in m:
            assigned_to = "miss_pink"
    
    # Check if miss-pink is in labels
    if "miss-pink" in labels and assigned_to == "unassigned":
        assigned_to = "miss_pink_label"
    if "sir-green" in labels and assigned_to == "unassigned":
        assigned_to = "sir_green_label"
    if "sir-azure" in labels and assigned_to == "unassigned":
        assigned_to = "sir_azure_label"
    
    # Check if Done
    is_done = "Done" in list_name or "Done" in labels or "automation-completed" in labels
    
    # Check relevance to Augur trading
    augur_keywords = ["augur", "yfinance", "price_history", "hof", "genome", "scan",
                      "paper trade", "regime", "kill-switch", "kill switch", "signal",
                      "alapca", "alpaca", "trading", "data import", "import csv",
                      "backfill", "data_downloader", "market_regime"]
    is_augur_related = any(kw in name.lower() or kw in desc.lower() for kw in augur_keywords)
    
    tasks.append({
        "id": c.get("id", "")[:12],
        "name": name,
        "priority": priority,
        "assigned": assigned_to,
        "list": list_name,
        "due": due[:10] if due and due != "None" else None,
        "labels": labels,
        "members": member_names,
        "done": is_done,
        "augur_related": is_augur_related,
        "url": c.get("url", ""),
        "desc_preview": desc[:100] if desc else ""
    })

# Print summary by priority
for priority in ["P0", "P1", "P2"]:
    p_tasks = [t for t in tasks if t["priority"] == priority and not t["done"]]
    print(f"\n{'='*70}")
    print(f"{priority} — {len(p_tasks)} active cards")
    print(f"{'='*70}")
    for t in p_tasks:
        augur_tag = " [AUGUR]" if t["augur_related"] else ""
        owner_tag = f" ({t['assigned']})" if t["assigned"] != "unassigned" else ""
        due_str = f" | 📅 {t['due']}" if t["due"] else ""
        print(f"  {t['priority']}{augur_tag}{owner_tag} | {t['name'][:55]}")
        if due_str:
            print(f"    due: {t['due']}")
        if t["desc_preview"]:
            print(f"    desc: {t['desc_preview'][:50]}...")

# Summary stats
done_count = len([t for t in tasks if t["done"]])
p0_active = len([t for t in tasks if t["priority"] == "P0" and not t["done"]])
p1_active = len([t for t in tasks if t["priority"] == "P1" and not t["done"]])
p2_active = len([t for t in tasks if t["priority"] == "P2" and not t["done"]])
augur_active = len([t for t in tasks if t["augur_related"] and not t["done"]])

print(f"\n{'='*70}")
print(f"SUMMARY")
print(f"{'='*70}")
print(f"  Total cards: {len(tasks)}")
print(f"  Done: {done_count} | Active: {len(tasks)-done_count}")
print(f"  P0 active: {p0_active} | P1 active: {p1_active} | P2 active: {p2_active}")
print(f"  Augur-related active: {augur_active}")

# Augur-specific cards
print(f"\n{'='*70}")
print(f"AUGUR-RELATED ACTIVE CARDS (not done)")
print(f"{'='*70}")
augur_cards = [t for t in tasks if t["augur_related"] and not t["done"]]
for t in augur_cards:
    print(f"  [{t['priority']}] [{t['assigned']}] {t['name'][:60]}")
    if t["due"]:
        print(f"    Due: {t['due']}")
    print(f"    URL: {t['url']}")
    print()

# Write full tasklist to file
with open("D:/Work/Torus Coffee Company LLC/Obsidian_Vault/02_Business_Operations/Communications/Outbox/TORUS_OPS_TASKLIST_20260810T2330Z.md", "w") as f:
    f.write(f"# Torus Ops Trello — Full Tasklist Audit\n\n")
    f.write(f"**Date:** 2026-08-10T23:30Z\n")
    f.write(f"**Board:** Torus_Ops (6a70a3157d0db4214ac3f9a3)\n\n")
    f.write(f"## Summary\n")
    f.write(f"- Total cards: {len(tasks)}\n")
    f.write(f"- Done: {done_count} | Active: {len(tasks)-done_count}\n")
    f.write(f"- P0 active: {p0_active} | P1 active: {p1_active} | P2 active: {p2_active}\n")
    f.write(f"- Augur-related active: {augur_active}\n\n")
    
    for t in augur_cards:
        f.write(f"## [{t['priority']}] {t['name']}\n")
        f.write(f"- **List:** {t['list']}\n")
        f.write(f"- **Assigned:** {t['assigned']}\n")
        if t["due"]:
            f.write(f"- **Due:** {t['due']}\n")
        f.write(f"- **URL:** {t['url']}\n\n")

print("Full tasklist written to Outbox/TORUS_OPS_TASKLIST_20260810T2330Z.md")