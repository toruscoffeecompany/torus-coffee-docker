#!/usr/bin/env python3
"""
Crew Reply Watcher — polls the remaining hard-blocker cards for Sir Green/Sir Azure responses.
Runs as a cron job every 30 min. Posts a notification to the Outbox when a reply is found.
Also handles 24h escalation: demotes non-revenue P0 cards to P1 after deadline.
"""
import requests, json
from datetime import datetime, timezone
from pathlib import Path

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BASE = "https://api.trello.com/1"
AUTH = {"key": KEY, "token": TOKEN}

VAULT = Path(r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault")
OUTBOX = VAULT / "02_Business_Operations/Communications/Outbox"
STATE_FILE = VAULT / "10_Skills_Library/05_Operations/crew_reply_state.json"
DONE_LIST_ID = "6a70a32a723c0312a3d5fbb4"
P1_LIST_ID = "6a74cbd5e3d54d2d08be82e7"
P0_LIST_ID = "6a74cbd440270147ff04bd5b"
AUTO_COMPLETED_LABEL = "6a7683bd42e9bfc1e593cad7"

# All 14 blocker card IDs that were originally tagged — state file tracks which are resolved
ALL_BLOCKER_CARDS = [
    {"id": "6a762813839d409994d663e5", "name": "torus-inventory deployment blocked", "crew": "Sir Green", "username": "void_pirate_capta1n"},
    {"id": "6a762818d5da329fde279451", "name": "DOCKER HUB PUSH STATUS SQUIDSTATION", "crew": "Sir Green/Sir Azure", "username": "void_pirate_capta1n"},
    {"id": "6a762819694f94ec8ae35ba5", "name": "ALERT ROUTER REPO — lacks write permission", "crew": "Sir Azure", "username": "toruscoffeecompany"},
    {"id": "6a76281b6f4e3f7f50a9fbcf", "name": "ONE ACTION: grant write/PAT", "crew": "Sir Azure", "username": "toruscoffeecompany"},
    {"id": "6a76281c1833984386f186a9", "name": "CODING ORDER: Docker Hub write", "crew": "Sir Azure", "username": "toruscoffeecompany"},
    {"id": "6a76281e35758521a2952345", "name": "Dashboard image blocked", "crew": "Sir Azure", "username": "toruscoffeecompany"},
    {"id": "6a75891ad087b6a6374f14b6", "name": "sirazure security tools missing", "crew": "Sir Azure", "username": "toruscoffeecompany"},
    {"id": "6a75891c3bcf75d5aa770214", "name": "sirazure security deep dive summary", "crew": "Sir Azure", "username": "toruscoffeecompany"},
    {"id": "6a758916afae5cf53ccccf33", "name": "miss gordon docker blockers", "crew": "Sir Green", "username": "void_pirate_capta1n"},
    {"id": "6a7589189ca085ca8dce78a8", "name": "trello api 401 invalid key (sirazure)", "crew": "Sir Azure", "username": "toruscoffeecompany"},
    {"id": "6a758919687b61bbb3db9255", "name": "trello api 401 invalid key (sirgreen)", "crew": "Sir Green", "username": "void_pirate_capta1n"},
    {"id": "6a75891fe2e1acad47a8101d", "name": "sirgreen docker deep dive urgent", "crew": "Sir Green", "username": "void_pirate_capta1n"},
    {"id": "6a7589217259b91d11ae66f1", "name": "sirazure re docker urgent findings", "crew": "Sir Azure", "username": "toruscoffeecompany"},
    {"id": "6a7589238a3983b8a50f08e8", "name": "sirazure squidstation deploy reply", "crew": "Sir Azure", "username": "toruscoffeecompany"},
]
# Cutoff: any comment after this timestamp that's not ours = crew reply
CUTOFF = datetime(2026, 8, 8, 6, 47, 0, tzinfo=timezone.utc)
ESCALATION_24H = datetime(2026, 8, 9, 6, 42, 0, tzinfo=timezone.utc)

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {"notified_replies": [], "resolved_by_crew": []}

def save_state(state):
    state["checked_at"] = datetime.now(timezone.utc).isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def get_card_actions(cid):
    r = requests.get(f"{BASE}/cards/{cid}/actions",
                      params={**AUTH, "fields": "type,date,data,memberCreator", "filter": "commentCard"},
                      timeout=15)
    if r.status_code != 200:
        return []
    return r.json()

def get_card(cid):
    r = requests.get(f"{BASE}/cards/{cid}", params={**AUTH, "fields": "name,idList,desc"}, timeout=15)
    return r.json() if r.status_code == 200 else None

def move_to_done(cid):
    requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"idList": DONE_LIST_ID}, timeout=15)
    requests.post(f"{BASE}/cards/{cid}/idLabels", params=AUTH, data={"value": AUTO_COMPLETED_LABEL}, timeout=10)
    requests.post(f"{BASE}/cards/{cid}/actions/comments", params=AUTH,
                data={"text": "✅ Crew replied with resolution. Moved to DONE."}, timeout=10)

def main():
    state = load_state()
    now = datetime.now(timezone.utc)
    new_replies = []
    resolved_now = []

    for card in ALL_BLOCKER_CARDS:
        # Skip already-resolved cards
        if card["id"] in state.get("resolved_by_crew", []):
            continue
        
        actions = get_card_actions(card["id"])
        for a in actions:
            text = a.get("data", {}).get("text", "")
            date_str = a.get("date", "")
            creator = a.get("memberCreator", {})
            creator_name = creator.get("fullName", "Unknown") if creator else "Unknown"

            if not date_str:
                continue
            try:
                c_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except:
                continue

            # Crew reply: not our OODA comment, after cutoff, meaningful text
            if c_date > CUTOFF and "OODA" not in text and len(text) > 15:
                reply_key = f"{card['id'][:8]}_{date_str[:19]}"
                if reply_key not in state.get("notified_replies", []):
                    new_replies.append({
                        "card_id": card["id"][:8],
                        "card_name": card["name"],
                        "crew": card["crew"],
                        "creator": creator_name,
                        "time": date_str[:19],
                        "text": text[:200].replace("\n", " "),
                    })
                    state.setdefault("notified_replies", []).append(reply_key)

            # Check for "Completed: Executed" automation reply
            if "Completed: Executed" in text and c_date > CUTOFF:
                if card["id"] not in state.get("resolved_by_crew", []):
                    resolved_now.append(card)
                    state.setdefault("resolved_by_crew", []).append(card["id"])

    # Process resolved cards
    for card in resolved_now:
        move_to_done(card["id"])
        print(f"  ✅ RESOLVED: [{card['id'][:8]}] {card['name'][:45]} -> Done")

    # 24h escalation
    if now > ESCALATION_24H:
        for card in ALL_BLOCKER_CARDS:
            if card["id"] not in state.get("resolved_by_crew", []):
                c = get_card(card["id"])
                if c and c.get("idList") == P0_LIST_ID:
                    requests.put(f"{BASE}/cards/{card['id']}", params=AUTH, data={"idList": P1_LIST_ID}, timeout=15)
                    requests.post(f"{BASE}/cards/{card['id']}/actions/comments", params=AUTH,
                        data={"text": f"⏰ 24h escalation: No crew response. Demoted to P1."}, timeout=10)
                    print(f"  ⏰ DEMOTED: [{card['id'][:8]}] {card['name'][:45]} -> P1")

    # Report
    remaining = [c for c in ALL_BLOCKER_CARDS if c["id"] not in state.get("resolved_by_crew", [])]
    if new_replies or resolved_now or (now > ESCALATION_24H):
        ts = now.strftime("%Y%m%dT%H%M%SZ")
        msg_path = OUTBOX / f"{ts}_crew_reply_watcher_report.msg.md"
        lines = [
            "# RE: Crew Reply Watcher Report",
            f"**From:** Miss Pink's OODA Watcher (30min cron)",
            f"**Time:** {now.isoformat()[:19]}Z",
            "",
        ]
        if resolved_now:
            lines.extend([f"## {len(resolved_now)} Cards Resolved by Crew", ""])
            for c in resolved_now:
                lines.extend([f"- ✅ `{c['id'][:8]}` {c['name']} → Done | {c['crew']}", ""])
        if new_replies:
            lines.extend([f"## {len(new_replies)} New Crew Replies", ""])
            for r in new_replies:
                lines.extend([
                    f"### Reply on `{r['card_id']}` — {r['card_name']}",
                    f"- **Sender:** {r['creator']} | **For:** {r['crew']}",
                    f"- **Time:** {r['time']}",
                    f"- **Content:** {r['text']}", "",
                ])
        if now > ESCALATION_24H:
            lines.extend([f"## 24h Escalation: Cards demoted to P1", "- No crew response received", ""])
        lines.extend([
            f"## Status: {len(remaining)} blockers remaining (need crew confirmation)",
            f"- Sir Azure: {len([c for c in remaining if 'Sir Azure' in c['crew']])} cards",
            f"- Sir Green: {len([c for c in remaining if 'Sir Green' in c['crew'] and 'Sir Azure' not in c['crew']])} cards",
            f"- 24h deadline: {ESCALATION_24H.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        ])
        msg_path.write_text("\n".join(lines), encoding="utf-8")

    save_state(state)
    if resolved_now:
        print(f"\nResolved: {len(resolved_now)} | Remaining: {len(remaining)}")
    elif new_replies:
        print(f"FOUND {len(new_replies)} new replies — report posted")
    else:
        print(f"Polled {len(ALL_BLOCKER_CARDS)} blocker cards — 0 new replies, {len(remaining)} remaining")

if __name__ == "__main__":
    main()
