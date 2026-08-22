#!/usr/bin/env python3
"""Post status comments on hard blocker cards — version 2.
Checks live board, posts on existing cards, handles 200/201 as success."""
import requests, time, json
from datetime import datetime, timezone
from collections import defaultdict

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BASE = "https://api.trello.com/1"
AUTH = {"key": KEY, "token": TOKEN}
BOARD_ID = "6a70a3157d0db4214ac3f9a3"

# Target card names to find (fuzzy match since board has been reclassified)
TARGET_NAMES = {
    # P0 hard blockers
    "torus-inventory deployment blocked": ("Sir Green", "Sir Azure: confirm deploy status. Is this still blocked? If yes, what's the blocker?"),
    "DOCKER HUB PUSH STATUS SQUIDSTATION IMAGES PUSH BLOCKED BY AUTH": ("Sir Green", "Sir Azure: SQUIDSTATION Docker Hub push blocked by auth. Confirm if PAT needed or host login issue."),
    "ALERT ROUTER REPO EXISTS BUT SQUIDSTATION LACKS WRITE PERMISSION": ("Sir Azure", "SQUIDSTATION lacks write to alert-router repo. Confirm filesystem perm fix or PAT grant."),
    "📨 [INBOX] sirazure security tools missing sirazure 20260806": ("Sir Azure", "Security tools (nikto/tshark/yara) not installed on PINKCADY. Confirm ETA or blocker."),
    "One Action Grant Write Access OR Provide PAT For Alert Router": ("Sir Azure", "Consolidated: alert-router Docker Hub push needs write access or PAT. Pick one and confirm."),
    "Coding Order Docker Hub Write Access For Alert Router": ("Sir Azure", "Docker Hub write access coding order. Confirm exact repo name + which PAT to use."),
    "🚨 [P1] Dashboard image blocked — Need Docker Hub Auth": ("Sir Azure", "Dashboard image push blocked. Same Docker Hub auth issue as alert-router? Confirm."),
    # Top 10 inbox cards
    "📨 [INBOX] miss gordon docker blockers sirgreen 20260806": ("Sir Green", "Docker blockers from Miss Gordon. Confirm resolution status (resolved/in-progress/blocked)."),
    "📨 [INBOX] trello api 401 invalid key blocker sirazure 20260806": ("Sir Azure", "Trello API 401 invalid key. Is this a credential rotation issue or code bug? Confirm resolution."),
    "📨 [INBOX] trello api 401 invalid key blocker sirgreen 20260806": ("Sir Green", "Trello API 401 invalid key. Same issue? Confirm if key needs rotation."),
    "📨 [INBOX] sirgreen docker deep dive urgent sirgreen 20260806": ("Sir Green", "Docker deep dive findings. 1-line status: resolved/in-progress/blocked?"),
    "📨 [INBOX] sirazure re docker urgent findings sirazure 20260806": ("Sir Azure", "Docker urgent findings. Confirm resolution status or ETA."),
    "📨 [INBOX] sirazure squidstation deploy reply sirazure 20260806": ("Sir Azure", "SquidStation deploy reply. Confirm deploy status — deployed/blocked/needs Sir Green coordination."),
}

def get_all_cards():
    """Fetch all open cards from the board."""
    resp = requests.get(f"{BASE}/boards/{BOARD_ID}/cards",
                        params={**AUTH, "fields": "id,name,idList,dateLastActivity,labels"},
                        timeout=60)
    return resp.json()

def post_comment(card_id, text):
    r = requests.post(f"{BASE}/cards/{card_id}/actions/comments",
                      params=AUTH, data={"text": text}, timeout=20)
    return r.status_code

def update_desc(card_id, old_desc, audit_tag):
    if "OOO_AUDIT" not in old_desc:
        requests.put(f"{BASE}/cards/{card_id}", params=AUTH,
                     data={"desc": old_desc + audit_tag}, timeout=20)

def main():
    print("=== Fetching live board state ===")
    cards = get_all_cards()
    print(f"Total live open cards: {len(cards)}")

    # Build normalized name index
    name_index = {}
    for c in cards:
        name = c.get('name', '').strip()
        name_lower = name.lower()
        # Try exact match first, then partial
        if name_lower not in name_index:
            name_index[name_lower] = c

    found_cards = []
    not_found = []

    for target_name, (crew, action) in TARGET_NAMES.items():
        target_lower = target_name.lower()
        matched = None

        # Check exact match
        if target_lower in name_index:
            matched = name_index[target_lower]
        else:
            # Check if any card name starts with target_lower
            for nl, card in name_index.items():
                if nl.startswith(target_lower[:30]) or target_lower[:30] in nl:
                    matched = card
                    break
                # Also check substring
                if target_lower[:15] in nl and ('sir' in nl or 'inbox' in nl or 'docker' in nl or 'alert' in nl or 'security' in nl or 'trello' in nl):
                    matched = card
                    break

        if matched:
            found_cards.append((matched, crew, action))
        else:
            not_found.append((target_name, crew, action))

    print(f"\nFound {len(found_cards)} target cards on live board")
    print(f"Not found: {len(not_found)}")

    posted = 0
    for card, crew, action in found_cards:
        cid = card['id']
        name = card['name']
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        comment = (
            f"🔔 OODA AUDIT — {now}\n\n"
            f"**Status check requested by Miss Pink** — this card is in P0/Top 10 and requires crew confirmation.\n\n"
            f"@{crew.split(',')[0].strip()}: **{action}**\n\n"
            f"_Please reply with explicit confirmation (✅ resolved / ⏸️ blocked / 🚧 in-progress) "
            f"so Miss Pink can update the board accordingly._\n\n"
            f"_Tag: #P0_BLOCKER #OODA_AUDIT_"
        )

        code = post_comment(cid, comment)
        if code in (200, 201):
            posted += 1
            print(f"  ✅ [{cid[:8]}] {name[:55]} -> {crew}")
        else:
            print(f"  ❌ [{cid[:8]}] {name[:55]} -> HTTP {code}")

        # Update desc
        old_desc = card.get('desc', '') or ''
        audit_tag = f"\n\n---\n[OOO_AUDIT: {now}] Status comment posted for {crew} confirmation. Awaits explicit confirmation before board state can be updated. Review note: no executable directive detected.\n"
        update_desc(cid, old_desc, audit_tag)

        time.sleep(0.5)

    print(f"\n=== Done: {posted}/{len(found_cards)} comments posted ===")

    if not_found:
        print(f"\n=== Cards not found (may have been archived/reclassified) ===")
        for name, crew, _ in not_found:
            print(f"  - [{crew}] {name[:60]}")

    return 0 if posted == len(found_cards) else 1

if __name__ == "__main__":
    raise SystemExit(main())
