#!/usr/bin/env python3
"""
crew_queue_automation.py
Sync Sir Green's and Sir Azure's queue cards from Torus Ops to VOID Ops,
auto-assign crew members, and send notifications via outbox.
"""
import json
import urllib.request
import urllib.parse
import os
import time
from datetime import datetime, timezone
from pathlib import Path

# Trello credentials loaded from vault credential file (scrubbed from source 2026-08-22)
import re as _re

def _load_trello_creds():
    cred_file = Path(r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault\01_Operating\Operating Paperwork\Trello_API_Credentials.md")
    text = cred_file.read_text(encoding="utf-8")
    blocks = dict(zip(_re.findall(r"## (API Key|Secret|Token)", text),
                      _re.findall(r"`([^`]+)`", text)))
    return blocks["API Key"], blocks["Token"]

TRELLO_KEY, TRELLO_TOKEN = _load_trello_creds()

TORUS_BOARD_ID = "6a70a3157d0db4214ac3f9a3"
VOID_BOARD_ID = "6a595669b8f8f99c93392f4f"

VAULT = Path(r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault")
OUTBOX = VAULT / "02_Business_Operations/Communications/Outbox"

# Crew mapping
CREW = {
    "sir-green": {"name": "Sir Green", "discord": "sir green", "color": "green"},
    "sir-azure": {"name": "Sir Azure", "discord": "sir azure", "color": "blue"},
    "miss-pink": {"name": "Miss Pink", "discord": "misspink", "color": "pink"},
}

def trello_get(path, params=None):
    url = f"https://api.trello.com/1{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    if params:
        url += "&" + "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ⚠️ GET {path} failed: {e}")
        return None

def trello_put(path, data_dict):
    url = f"https://api.trello.com/1{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps(data_dict).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ⚠️ PUT {path} failed: {e}")
        return None

def trello_post(path, data_dict):
    url = f"https://api.trello.com/1{path}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = urllib.parse.urlencode(data_dict).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ⚠️ POST {path} failed: {e}")
        return None

def post_trello_comment(card_id, text):
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15):
            pass
    except Exception:
        pass
    time.sleep(0.4)

def get_board_lists(board_id):
    return trello_get(f"/boards/{board_id}/lists", {"fields": "id,name", "filter": "all"}) or []

def get_list_cards(list_id):
    return trello_get(f"/lists/{list_id}/cards", {"fields": "id,name,labels,desc,closed"}) or []

def get_board_cards(board_id):
    return trello_get(f"/boards/{board_id}/cards", {
        "fields": "id,name,labels,closed,desc", "filter": "open"
    }) or []

def auto_assign_crew(card, default_crew=None):
    """Determine crew owner based on queue membership, labels, and content.
    
    Args:
        card: Trello card dict
        default_crew: Crew key from queue membership (highest priority)
    """
    labels = [l.get("name", "").lower() for l in card.get("labels", []) if isinstance(l, dict)]
    name_l = card.get("name", "").lower()
    desc_l = card.get("desc", "").lower()

    # 1. Queue membership takes precedence (if provided)
    if default_crew:
        return default_crew

    # 2. Check explicit labels
    for crew_key in ["sir-green", "sir-azure", "miss-pink"]:
        if crew_key in labels:
            return crew_key

    # 3. Check queue context via card name/content patterns
    if "sir green" in name_l or "sg " in name_l:
        return "sir-green"
    if "sir azure" in name_l or "sa " in name_l:
        return "sir-azure"
    if "miss pink" in name_l or "misspink" in name_l or "mp " in name_l:
        return "miss-pink"

    # Content-based routing heuristics
    deploy_keywords = ["deploy", "docker", "kubernetes", "k8s", "helm", "server", "infra", "void", "squidstation", "stealthattack"]
    ai_keywords = ["ai", "llm", "model", "agent", "augur", "inference", "training", "dataset", "embedding"]
    website_keywords = ["website", "web", "frontend", "react", "nextjs", "css", "html", "landing"]

    if any(kw in name_l or kw in desc_l for kw in deploy_keywords + ["tencentdb", "agent memory", "offline"]):
        return "sir-green"
    if any(kw in name_l or kw in desc_l for kw in ai_keywords):
        return "sir-azure"
    if any(kw in name_l or kw in desc_l for kw in website_keywords + ["qa", "report", "lane"]):
        return "miss-pink"

    # Default: miss-pink (owner of automation)
    return "miss-pink"

def create_outbox_message(crew_key, card_name, card_url, action, card_id=None, details=None):
    """Create an outbox .msg.md file for the assigned crew member."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    crew = CREW.get(crew_key, CREW["miss-pink"])
    to_name = crew["discord"]

    msg_id = f"crew_queue_sync_{crew_key.replace('-','')}-{ts}"
    if card_id:
        msg_id = f"crew_queue_sync_{crew_key.replace('-','')}_{card_id[:8]}-{ts}"

    body_lines = []
    if action == "sync":
        body_lines = [
            f"Crew queue sync complete.",
            f"",
            f"Torus Ops -> VOID Ops:",
            f"- {crew['name']}'s Queue: 1 card processed",
            f"  - [{card_name}]({card_url})",
        ]
        if details:
            body_lines.append(f"")
            for k, v in details.items():
                body_lines.append(f"- {k}: {v}")
        body_lines.extend([
            f"",
            f"Status: ⛢ SYNCED",
            f"— Miss Pink 🦜",
        ])
    elif action == "noop":
        body_lines = [
            f"Crew queue sync check.",
            f"",
            f"Torus Ops -> VOID Ops:",
            f"- {crew['name']}'s Queue: already synced, no action needed",
            f"  - [{card_name}]({card_url})",
            f"",
            f"Status: ⛢ NOOP",
            f"— Miss Pink 🦜",
        ]
    elif action == "missing_list":
        body_lines = [
            f"Queue sync blocked.",
            f"",
            f"Torus Ops -> VOID Ops:",
            f"- {crew['name']}'s Queue: target list missing on VOID Ops",
            f"  - [{card_name}]({card_url})",
            f"",
            f"Status: ⛢ BLOCKED — create queue list on VOID Ops manually.",
            f"— Miss Pink 🦜",
        ]
    else:
        body_lines = [
            f"Crew queue sync: {action}",
            f"",
            f"- [{card_name}]({card_url})",
            f"",
            f"Status: ⛢ {action.upper()}",
            f"— Miss Pink 🦜",
        ]

    body = "\n".join(body_lines)

    filename = f"{msg_id}.msg.md"
    filepath = OUTBOX / filename

    content = f"""---
from: misspink
to: {to_name}
topic: queue-sync
id: {msg_id}
requires_response: false
action_required: false
ts: {ts}
---

{body}
"""

    filepath.write_text(content, encoding="utf-8")
    return filepath, msg_id

def ensure_void_green_queue(void_lists):
    """Ensure Sir Green's Queue exists on VOID Ops. Create if missing."""
    green_list = next((l for l in void_lists if l["name"] == "Sir Green's Queue"), None)
    if green_list:
        return green_list["id"]

    # Create the list in VOID Backlog (first available list as parent context)
    url = f"https://api.trello.com/1/boards/{VOID_BOARD_ID}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = urllib.parse.urlencode({"name": "Sir Green's Queue", "idBoard": VOID_BOARD_ID}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            new_list = json.loads(resp.read().decode("utf-8"))
            print(f"  ✅ Created 'Sir Green's Queue' on VOID Ops")
            return new_list["id"]
    except Exception as e:
        print(f"  ⚠️ Failed to create Sir Green's Queue: {e}")
        return None

def ensure_void_azure_queue(void_lists):
    """Ensure Sir Azure's Queue exists on VOID Ops. Create if missing."""
    azure_list = next((l for l in void_lists if l["name"] == "Sir Azure's Queue"), None)
    if azure_list:
        return azure_list["id"]

    # Create the list in VOID Backlog (first available list as parent context)
    # Trello API: create a list in a board
    url = f"https://api.trello.com/1/boards/{VOID_BOARD_ID}/lists?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = urllib.parse.urlencode({"name": "Sir Azure's Queue", "idBoard": VOID_BOARD_ID}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            new_list = json.loads(resp.read().decode("utf-8"))
            print(f"  ✅ Created 'Sir Azure's Queue' on VOID Ops")
            return new_list["id"]
    except Exception as e:
        print(f"  ⚠️ Failed to create Sir Azure's Queue: {e}")
        return None

def move_card_to_void(card, void_list_id, crew_key):
    """Move (or copy) a card from Torus Ops to VOID Ops."""
    card_id = card["id"]
    card_name = card["name"]

    # Check if already synced: look for a card with same name on VOID board
    void_cards = get_board_cards(VOID_BOARD_ID)
    existing = [c for c in void_cards if c.get("name") == card_name]
    if existing:
        print(f"  ⏭️  Already on VOID Ops: {card_name[:50]}")
        return existing[0]["id"], "noop"

    # Move card to VOID board in the target list
    result = trello_put(f"/cards/{card_id}", {
        "idList": void_list_id,
        "idBoard": VOID_BOARD_ID
    })

    if result and result.get("id"):
        print(f"  ✅ Moved to VOID Ops: {card_name[:50]}")
        # Post comment on the card
        post_trello_comment(result["id"], f"""🔁 **Miss Pink crew queue sync ({datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}):** SYNCED to VOID Ops.

**Card:** {card_name}
**Source:** Torus Ops ({card_id})
**Target:** VOID Ops ({result['id']})
**Assigned to:** {CREW[crew_key]['name']}

Auto-synced by crew_queue_automation.py.
— Miss Pink 🦜""")
        return result["id"], "sync"
    else:
        print(f"  ❌ Failed to move: {card_name[:50]}")
        return None, "failed"

def main():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"=== crew_queue_automation.py — {ts} ===\n")

    # ─── 1. Load Torus Ops queues ───────────────────────────────────────────
    torus_lists = get_board_lists(TORUS_BOARD_ID)
    torus_queues = {}
    for l in torus_lists:
        name_l = l["name"].lower()
        if "sir green" in name_l or "sir-azure" in name_l or "sir azure" in name_l:
            torus_queues[l["name"]] = l["id"]

    print(f"Torus Ops queues found: {list(torus_queues.keys())}")

    torus_queue_cards = {}
    for qname, qid in torus_queues.items():
        cards = get_list_cards(qid)
        # Filter open cards only
        open_cards = [c for c in cards if not c.get("closed")]
        torus_queue_cards[qname] = open_cards
        print(f"  {qname}: {len(open_cards)} open cards")

    # ─── 2. Load VOID Ops queues ─────────────────────────────────────────────
    void_lists = get_board_lists(VOID_BOARD_ID)
    void_queues = {}
    for l in void_lists:
        name_l = l["name"].lower()
        if "sir green" in name_l or "sir-azure" in name_l or "sir azure" in name_l:
            void_queues[l["name"]] = l["id"]

    print(f"\nVOID Ops queues found: {list(void_queues.keys())}")

    # Ensure Sir Green's Queue exists on VOID Ops
    void_queues.setdefault("Sir Green's Queue", None)
    if void_queues.get("Sir Green's Queue") is None:
        void_queues["Sir Green's Queue"] = ensure_void_green_queue(void_lists)

    # Ensure Sir Azure's Queue exists on VOID Ops
    void_queues.setdefault("Sir Azure's Queue", None)
    if void_queues.get("Sir Azure's Queue") is None:
        void_queues["Sir Azure's Queue"] = ensure_void_azure_queue(void_lists)

    # ─── 3. Process each Torus queue ────────────────────────────────────────
    results = {
        "timestamp": ts,
        "notifications": 0,
        "processed": 0,
        "failed": 0,
        "failed_details": [],
        "queue_snapshot": {},
    }

    # Track which cards we've moved to avoid duplicates
    moved_card_ids = set()

    for qname, qid in torus_queues.items():
        cards = torus_queue_cards.get(qname, [])
        if not cards:
            continue

        # Determine target crew and VOID list
        if "Sir Green" in qname:
            crew_key = "sir-green"
            target_list_name = "Sir Green's Queue"
        elif "Sir Azure" in qname:
            crew_key = "sir-azure"
            target_list_name = "Sir Azure's Queue"
        else:
            continue

        target_list_id = void_queues.get(target_list_name)
        if not target_list_id:
            print(f"  ❌ Target list '{target_list_name}' not found on VOID Ops")
            results["failed"] += len(cards)
            for c in cards:
                results["failed_details"].append({
                    "card_id": c["id"],
                    "name": c["name"],
                    "reason": f"missing target list: {target_list_name}"
                })
                results["queue_snapshot"][c["id"]] = c["name"]
                create_outbox_message(crew_key, c["name"], f"https://trello.com/c/{c['id']}", "missing_list", c["id"])
            continue

        print(f"\nProcessing {qname} -> {target_list_name} (crew: {CREW[crew_key]['name']})")
        for card in cards:
            cid = card["id"]
            cname = card["name"]

            if cid in moved_card_ids:
                print(f"  ⏭️  Already processed: {cname[:50]}")
                continue
            moved_card_ids.add(cid)

            results["queue_snapshot"][cid] = cname

            # Auto-assign (refine based on card metadata if needed)
            assigned_crew = auto_assign_crew(card, default_crew=crew_key)

            # Only sync if the assigned crew matches the queue owner
            if assigned_crew != crew_key:
                print(f"  🔄 Re-route: {cname[:50]} -> {CREW[assigned_crew]['name']}")
                # For now, still move to the queue's VOID list but note the assignment
                # In a more advanced flow, we'd route to a different queue

            void_card_id, action = move_card_to_void(card, target_list_id, assigned_crew)

            if action == "sync":
                results["processed"] += 1
                results["notifications"] += 1
                filepath, msg_id = create_outbox_message(
                    assigned_crew, cname,
                    f"https://trello.com/c/{void_card_id}",
                    "sync",
                    void_card_id,
                    details={"source_card": cid, "auto_assigned": CREW[assigned_crew]["name"]}
                )
                print(f"  📨 Outbox: {filepath.name}")
            elif action == "noop":
                results["notifications"] += 1
                filepath, msg_id = create_outbox_message(
                    assigned_crew, cname,
                    f"https://trello.com/c/{void_card_id}",
                    "noop",
                    void_card_id
                )
                print(f"  📨 Outbox (noop): {filepath.name}")
            else:
                results["failed"] += 1
                results["failed_details"].append({
                    "card_id": cid,
                    "name": cname,
                    "reason": "move failed"
                })
                create_outbox_message(
                    assigned_crew, cname,
                    f"https://trello.com/c/{cid}",
                    "failed",
                    cid
                )

    # ─── 4. Summary ─────────────────────────────────────────────────────────
    print(f"\n=== SUMMARY ===")
    print(f"Processed: {results['processed']}")
    print(f"Failed: {results['failed']}")
    print(f"Notifications sent: {results['notifications']}")
    if results["failed_details"]:
        print(f"Failed details: {json.dumps(results['failed_details'], indent=2)}")

    # Write results to stdout as JSON
    print("\n=== JSON_RESULT ===")
    print(json.dumps(results, indent=2))

    return results

if __name__ == "__main__":
    main()
