#!/usr/bin/env python3
"""
Check TORUS_OPS board for MISSING cards related to:
- PINKCADY infrastructure
- Miss Pink's Hermes app
- Torus Coffee Company systems

Don't verify Done cards — just audit + create missing tracking cards.
"""
import json, time, urllib.request, urllib.parse

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "ATTA5fa83ac8abb79f4f0431b2753c87cb04fe898aa700ff84d1f1c1648f180034d2dC1621D9C"
TORUS_OPS = "6a70a3157d0db4214ac3f9a3"

def trello_get(path, params=None):
    url = f"https://api.trello.com/1{path}?key={KEY}&token={TOKEN}"
    if params:
        url += "&" + "&".join(f"{k}={v}" for k, v in params.items())
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8")
    except:
        return None

def trello_post(path, data_dict):
    url = f"https://api.trello.com/1{path}?key={KEY}&token={TOKEN}"
    data = urllib.parse.urlencode(data_dict).encode()
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        return f"ERROR: {e}"

time.sleep(5)

# ─── Get ALL lists ─────────────────────────────────────────────────────
print("=== TORUS_OPS: Auditing for missing PINKCADY/Hermes cards ===\n")
lists_out = trello_get(f"/boards/{TORUS_OPS}/lists", {"fields": "id,name"})
lists = json.loads(lists_out)
list_map = {l["name"]: l["id"] for l in lists}

print("Lists:")
for l in lists:
    print(f"  {l['name']} ({l['id']})")

# ─── Get ALL open cards ────────────────────────────────────────────────
all_open_cards = []
for l in lists:
    time.sleep(3)
    name = l["name"]
    if any(kw in name.lower() for kw in ["done", "completed", "archive"]):
        continue
    cards_out = trello_get(f"/lists/{l['id']}/cards", {"fields": "id,name,desc,labels"})
    if cards_out:
        cards = json.loads(cards_out)
        for c in cards:
            tags = [t.get("name","") for t in c.get("labels",[])]
            all_open_cards.append({"name": c["name"], "list": name, "labels": tags, "desc": c.get("desc","")[:100]})

# ─── Search for PINKCADY/Hermes-related cards ──────────────────────────
print(f"\n{'='*60}")
print("EXISTING PINKCADY/HERMES cards:")
print(f"{'='*60}")

keywords = ["pinkcady", "pinksady", "pinkcady", "hermes", "docker", "wsl", "terminal",
            "credential", "docker-credential", "settings.json", "daemon.json",
            "vault sync", "obsidian", "crew comms", "discord bot",
            "monitoring", "free tier", "budget", "cost"]

found = []
for c in all_open_cards:
    name_lower = c["name"].lower()
    desc_lower = c.get("desc","").lower() if "desc" in c else ""
    for kw in keywords:
        if kw in name_lower or kw in desc_lower:
            found.append(c)
            print(f"  [{c['list']}] {c['name'][:70]} (labels: {', '.join(c['labels'])})")
            break

if not found:
    print("  No PINKCADY/Hermes-specific cards found!")

# ─── Check for missing cards ─────────────────────────────────────────__
print(f"\n{'='*60}")
print("MISSING CARDS TO CREATE:")
print(f"{'='*60}")
missing = []

# Check what exists vs what should exist
existing_topics = set()
for c in all_open_cards:
    existing_topics.add(c["name"].lower())

# 1. Docker Desktop rebuild card
has_docker = any("docker" in c["name"].lower() for c in all_open_cards)
if not has_docker:
    missing.append({
        "name": "P0: Docker Desktop 4.88 — Fix WSL2 backend + enable TCP 2375/2376",
        "list": "P1 - High / Doing Now",
        "desc": "Docker Desktop 4.88 on PINKCADY with WSL2 backend. Installer crash fixed. TCP 2375/2376 not exposed by Docker Desktop 4.88 — need alternative approach (npipe or socat). 182GB old data backed up at wsl_backup_20260817. All 10 Torus containers rebuilt from source and running healthy.",
        "labels": ["P0", "miss-pink", "infra", "docker"],
    })

# 2. Hermes automation scripts card
has_hermes_scripts = any("hermes" in c["name"].lower() and "script" in c["name"].lower() for c in all_open_cards)
if not has_hermes_scripts:
    missing.append({
        "name": "P1: Document + maintain Miss Pink's Hermes automation scripts",
        "list": "P3 - Medium / Follow Up",
        "desc": "All automation scripts live at D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/. After Docker rebuild, verify all scripts still work with new container versions (toruscoffee/torus-*:20260817-v4). Scripts include _docker_fix_settings.py, _docker_register_data.py, _done_review_batch*.py, etc.",
        "labels": ["miss-pink", "automation", "docs"],
    })

# 3. TORUS_OPS Done card verification
has_done_audit = any("verify" in c["name"].lower() and "done" in c["name"].lower() for c in all_open_cards)
if not has_done_audit:
    missing.append({
        "name": "P1: Audit TORUS_OPS Done cards — verify completed work",
        "list": "P3 - Medium / Follow Up",
        "desc": "Review completed TORUS_OPS cards (small batches of 5) — verify each task was actually completed. Archive verified cards. Reopen broken ones. First batch verified: CRON scheduler, dashboard race condition, redundant fetches, SQUIDSTATION clone, sync scripts.",
        "labels": ["miss-pink", "audit", "verification"],
    })

# 4. VOID_OPS Done card verification continuation
has_void_audit = any("void" in c["name"].lower() and "done" in c["name"].lower() for c in all_open_cards)
if not has_void_audit:
    missing.append({
        "name": "P1: Continue VOID_OPS Done card verification (batches 3+)",
        "list": "P3 - Medium / Follow Up",
        "desc": "VOID_OPS board has ~40 Done cards. Batch 1 (5 cards) all verified. Batch 2 (10 cards) completed with 8 verified, 2 reopened. Continue with batches of 5-10. Current system status: Docker ✅, TM API ✅, Dashboard ✅.",
        "labels": ["miss-pink", "audit", "verification", "void-ops"],
    })

# 5. Docker credential helper fix
has_cred = any("credential" in c["name"].lower() for c in all_open_cards)
if not has_cred:
    missing.append({
        "name": "P1: Fix Docker credential helper (docker-credential-desktop) PATH issue",
        "list": "P1 - High / Doing Now",
        "desc": "docker-credential-desktop.exe was at C:/Program Files/Docker/Docker/resources/bin/ but not in PATH. Fixes applied via setx + clean config.json. Docker builds now work. Need to verify PATH persists across reboots + Docker Desktop updates.",
        "labels": ["P1", "miss-pink", "docker", "windows"],
    })

# 6. Docker data backup verification
has_backup = any("backup" in c["name"].lower() and "docker" in c["name"].lower() for c in all_open_cards)
if not has_backup:
    missing.append({
        "name": "P2: Verify Docker data backup (182GB wsl_backup_20260817)",
        "list": "P3 - Medium / Follow Up",
        "desc": "182GB Docker data backed up at C:/Users/torus/AppData/Local/Docker/wsl_backup_20260817/ during fresh Docker reinstall. Need to verify backup integrity + document recovery procedure. Old containers not needed — all rebuilt from source at 20260817-v4.",
        "labels": ["P2", "miss-pink", "docker", "backup"],
    })

# 7. Hermes profile cleanup
has_profile = any("profile" in c["name"].lower() and "hermes" in c["name"].lower() for c in all_open_cards)
if not has_profile:
    missing.append({
        "name": "P3: Verify Hermes profiles + skills state after Docker rebuild",
        "list": "P3 - Medium / Follow Up",
        "desc": "Docker Desktop reinstall may have affected Hermes profiles at C:/Users/torus/AppData/Local/hermes/profiles/. Verify default profile skills, plugins, cron jobs intact. Check ~/.docker/config.json is clean.",
        "labels": ["P3", "miss-pink", "hermes", "maintenance"],
    })

# ─── Create missing cards ──────────────────────────────────────────────
if missing:
    print(f"\n{'='*60}")
    print(f"CREATING {len(missing)} CARDS:")
    print(f"{'='*60}")
    
    for card in missing:
        target_list = list_map.get(card["list"], "")
        if not target_list:
            # Find first non-Done list
            for l in lists:
                if "done" not in l["name"].lower() and "completed" not in l["name"].lower():
                    target_list = l["id"]
                    break
        
        # Post the card
        result = trello_post("/cards", {
            "idList": target_list,
            "name": card["name"],
            "desc": card["desc"],
            "pos": "top",
        })
        if result and "id" in result:
            print(f"   ✅ Created: {card['name'][:70]}")
        else:
            print(f"   ❌ Failed: {card['name'][:70]} — {result}")
        time.sleep(2)
else:
    print("   No missing cards found!")

# ─── Summary ─────────────────────────────────────────────────────────__
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Total open TORUS_OPS cards: {len(all_open_cards)}")
print(f"PINKCADY/Hermes/automation cards found: {len(found)}")
print(f"Missing cards created: {len(missing)}")

print(f"\n{'='*60}")
import os
os.remove(__file__)
