#!/usr/bin/env python3
"""
Torus Ops Deep Audit — continuous Trello board audit loop.

Runs every hour (or configurable interval via --interval).
Each pass:
  1. Fetch ALL live cards from Torus_Ops board (no stale index dependency)
  2. Dedupe: archive all but newest duplicate-name card (keep newest by dateLastActivity)
  3. Enforce Top 10 hard cap (archive/remove excess to P1)
  4. Rebalance priority labels: clean multi-priority labels, reclassify by content
  5. Route crew inbox spam: consolidate duplicate message cards
  6. Clean P4/P5/P6: archive stale, move actionable up
  7. Update TRELLO_CARD_INDEX.json to match live state
  8. Post one timestamped audit summary comment on the board's audit tracking card
  9. Repeat until board is clean (NO_ACTIONABLE_CARDS or --once flag)

State tracking: torus_ops_audit_state.json
  - last_run, cards_before, cards_after, archived, moved, relabeled, iterations
  - stops when no changes made in a full pass
"""
import json
import os
import re
import time
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import Counter, defaultdict
import requests

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
TRELLO_CREDS = VAULT / "01_Operating/Operating Paperwork/Trello_API_Credentials.md"
LOG_PATH = VAULT / "10_Skills_Library/05_Operations/logs/torus_ops_audit.log"
STATE_PATH = VAULT / "10_Skills_Library/05_Operations/torus_ops_audit_state.json"
INDEX_PATH = VAULT / "10_Skills_Library/05_Operations/TRELLO_CARD_INDEX.json"

BOARD_ID = "6a70a3157d0db4214ac3f9a3"
TOP10_MAX = 10
STALE_P5_P6_DAYS = 30
BATCH_PAUSE = 1

# Import list/label IDs from trello_final_automation
LIST_IDS = {
    'Top 10': '6a74cbd3aa052ed2b30c5644',
    'P0': '6a74cbd440270147ff04bd5b',
    'P1': '6a74cbd5e3d54d2d08be82e7',
    'P2': '6a74cbd4148f814483a64589',
    'P3': '6a70a32923622d3e00107d70',
    'P4': '6a74cbd573259cffe8a23cc0',
    'P5': '6a70a3282e405a2460afc170',
    'P6': '6a74cbd67bbe3ef35a634495',
    'Done': '6a70a32a723c0312a3d5fbb4',
    "Sir Azure's Queue": '6a74cbd51b2662f6cdc37cce',
    "Sir Green's Queue": '6a74cbd679972be49ea46dae',
    'Future Ideas': '6a74cbd56a538340582a8897',
}
LIST_NAMES = {v: k for k, v in LIST_IDS.items()}

PRIORITY_LABEL_IDS = {
    'P0': '6a74cc10430afd9940c72bae',
    'P1': '6a70acc569135c796d8eba5d',
    'P2': '6a70acc56f143597877f576e',
    'P3': '6a70acc6fddcac79f411267f',
    'P4': '6a74f1246d3c910c8d7c8ef3',
    'P5': '6a74f124364b0cbd6b9c7117',
    'P6': '6a74f1253664a10a9e17bb57',
    'Top 10': '6a74c9ad1518ad0f9e645fc5',
}


def log(msg):
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n"
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line)
        print(line, end="")
    except Exception:
        pass


def load_creds():
    text = TRELLO_CREDS.read_text(encoding="utf-8")
    api_key = token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Missing Trello API key/token")
    return api_key, token


def trello_get(key, token, url, params=None, timeout=30):
    p = {"key": key, "token": token}
    if params:
        p.update(params)
    r = requests.get(url, params=p, timeout=timeout)
    r.raise_for_status()
    return r.json()


def trello_put(key, token, url, data, timeout=20):
    r = requests.put(url, params={"key": key, "token": token}, data=data, timeout=timeout)
    return r.status_code, r.text[:200] if r.status_code != 200 else ""


def trello_post(key, token, url, data, timeout=20):
    r = requests.post(url, params={"key": key, "token": token}, data=data, timeout=timeout)
    return r.status_code, r.text[:200] if r.status_code != 200 else ""


def trello_del(key, token, url, params=None, timeout=20):
    p = {"key": key, "token": token}
    if params:
        p.update(params)
    r = requests.delete(url, params=p, timeout=timeout)
    return r.status_code


def parse_iso(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def classify_card(name, labels, desc=""):
    """Classify a card into the correct list based on content."""
    name_lower = name.lower()
    desc_lower = (desc or "").lower()
    label_names = [l.get('name', '').lower() for l in labels]

    # Already explicitly classified by label? Respect it for priority cards
    for prio in ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'Top 10', 'Future Ideas']:
        if prio.lower() in label_names and prio in LIST_IDS:
            return prio

    # Crew queues
    for qname in ["Sir Azure's Queue", "Sir Green's Queue"]:
        if qname.lower() in label_names:
            return qname

    # Content-based classification
    p0_signals = ['🚨', 'alert', 'blocked', '403', '502', 'critical', 'emergency',
                  'security', 'breach', 'down', 'outage', 'production down',
                  'revenue stopped', 'payment failure', 'data loss',
                  'dashboard 502', 'dashboard down', 'website down', 'pos down',
                  'inventory down', 'square payment failure']
    if any(k in name_lower for k in p0_signals):
        return 'P0'

    top10_signals = ['freeze-dried production', 'square developer', 'payments live',
                     'pos deployment', 'inventory deployment', 'website launch',
                     'production sop', 'revenue stream plan', 'first sale',
                     'confirm pat works', 'github auth for toruscoffeecompany',
                     'first dollar', 'first paid', 'launch payment', 'go live',
                     'torus-inventory deployment', 'launch freeze-dried']
    if any(k in name_lower for k in top10_signals):
        return 'Top 10'

    p1_signals = ['critical', 'urgent', 'emergency', 'blocker', 'p0', 'alert',
                  'do now', 'dashboard 502', 'dashboard down', 'website down',
                  'website offline', 'auth broken', 'github connection broken',
                  'data loss', 'docker build failed', 'docker push failed',
                  'docker down', 'production down', 'revenue stopped',
                  'payment failure', 'pos down', 'inventory down',
                  'squidstation', 'void pirate github blocked']
    if any(k in name_lower for k in p1_signals):
        return 'P1'

    # Sir Azure / Sir Green crew routing
    sir_azure_keywords = ['sir azure', 'sirazure', 'security tools', 'stealthattack',
                          'pinkcady security', 'windows spy', 'autohotkey', 'ahkv2',
                          'nikto', 'tshark', 'yara', 'comfyui', 'minio', 'postgres', 'nginx']
    if any(k in name_lower for k in sir_azure_keywords) or any(k in desc_lower for k in sir_azure_keywords):
        return "Sir Azure's Queue"

    sir_green_keywords = ['sir green', 'sirgreen', 'fleet', 'swarm', 'compose',
                          'api route', 'missing route', 'dashboard_server',
                          'prometheus', 'grafana', 'redis secured', 'docker hub']
    if any(k in name_lower for k in sir_green_keywords) or any(k in desc_lower for k in sir_green_keywords):
        return "Sir Green's Queue"

    p2_signals = ['implement discord', 'integrate buffer', 'connect zapier',
                  'deploy torus', 'deploy dashboard', 'fix dashboard', 'fix docker',
                  'setup square', 'square payments', 'pos live', 'inventory live',
                  'website launch', 'launch payment', 'go live', 'production sop',
                  'freeze-dried production', 'first sale', 'first dollar', 'revenue stream']
    if any(k in name_lower for k in p2_signals):
        return 'P2'

    # Inbox spam detection: cards with "📨" or "[INBOX]" or message-style names
    inbox_patterns = ['📨', '[inbox]', 'sirazure', 'sirgreen', 'misspink', '.msg']
    is_inbox = any(k in name_lower for k in ['📨', '[inbox]']) or '.msg' in name_lower

    p3_signals = ['setup', 'install', 'run', 'deploy', 'launch', 'research', 'investigate',
                  'review', 'audit', 'plan', 'analyze', 'social post', 'schedule',
                  'track ', 'monitor', 'report', 'update doc', 'document',
                  'discord bot', 'bot script', 'maintenance', 'weekly', 'monthly']
    if any(k in name_lower for k in p3_signals):
        return 'P3'

    p4_signals = ['backlog', 'later', 'maybe', 'park', 'hold', 'someday',
                  'polish', 'cleanup', 'refactor', 'renovate', 'redesign',
                  'enhancement', 'nice to have', 'optional', 'future improvement',
                  'branding', 'template design']
    if any(k in name_lower for k in p4_signals):
        return 'P4'

    p6_signals = ['blocked', 'waiting', 'dependency', 'external', 'waiting on',
                  'blocked by', 'seasonal', 'event', 'campaign', 'holiday',
                  '2027', '2028', 'halloween', 'christmas', 'thanksgiving',
                  'easter', 'valentine', 'mothers day', 'fathers day',
                  'black friday', 'cyber monday']
    if any(k in name_lower for k in p6_signals):
        return 'P6'

    future_signals = ['future', 'ai answering', 'phone number', 'sms', 'text automation',
                      'google voice', 'research free', 'evaluate ai', 'voice ai',
                      'ar menu', 'paid upgrade', 'after revenue proof', 'someday',
                      'next year', 'future campaign']
    if any(k in name_lower for k in future_signals):
        return 'Future Ideas'

    # Default: inbox spam -> archive, everything else -> P3
    if is_inbox:
        return 'ARCHIVE'
    return 'P3'


def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"last_run": None, "cards_before": 0, "cards_after": 0,
            "archived": 0, "moved": 0, "relabeled": 0, "iterations": 0,
            "last_summary": None}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def fetch_all_cards(key, token):
    """Fetch all cards from the board."""
    params = {"fields": "id,name,desc,idList,dateLastActivity,labels,closed,due,url"}
    cards = trello_get(key, token, f"https://api.trello.com/1/boards/{BOARD_ID}/cards",
                       params, timeout=60)
    open_cards = [c for c in cards if not c.get("closed")]
    return open_cards, cards


def fetch_label_map(key, token):
    labels = trello_get(key, token, f"https://api.trello.com/1/boards/{BOARD_ID}/labels",
                        {"fields": "id,name"}, timeout=15)
    return {l['id']: l['name'] for l in labels}, {l['name']: l['id'] for l in labels}


def fetch_list_map(key, token):
    lists = trello_get(key, token, f"https://api.trello.com/1/boards/{BOARD_ID}/lists",
                       {"fields": "id,name"}, timeout=15)
    return {l['id']: l['name'] for l in lists}, {l['name']: l['id'] for l in lists}


def archive_card(key, token, card_id):
    """Soft-delete (archive) a card."""
    code, _ = trello_put(key, token, f"https://api.trello.com/1/cards/{card_id}",
                         {"closed": "true"}, timeout=15)
    return code == 200


def move_card(key, token, card_id, list_id):
    code, _ = trello_put(key, token, f"https://api.trello.com/1/cards/{card_id}",
                         {"idList": list_id}, timeout=15)
    return code == 200


def set_labels(key, token, card_id, new_label_ids, existing_labels):
    """Replace all priority labels with exactly one."""
    # Remove all priority labels
    priority_ids = set()
    for name, lid in PRIORITY_LABEL_IDS.items():
        priority_ids.add(lid)

    for lbl in existing_labels:
        lid = lbl.get('id', '')
        if lid in priority_ids and lid not in new_label_ids:
            trello_del(key, token, f"https://api.trello.com/1/cards/{card_id}/idLabels/{lid}", timeout=10)

    # Add the correct priority label
    for lid in new_label_ids:
        if lid not in priority_ids:
            continue
        if lid not in [l.get('id', '') for l in existing_labels]:
            trello_post(key, token, f"https://api.trello.com/1/cards/{card_id}/idLabels",
                        {"value": lid}, timeout=10)


def run_pass(key, token):
    """Run one full audit pass. Returns (changes_made, summary)."""
    changes_made = 0
    summary = {"archived": 0, "moved": 0, "relabeled": 0, "duplicates_archived": 0,
               "top10_enforced": 0, "stale_archived": 0}

    log("=== Starting Torus Ops deep audit pass ===")

    # 1. Fetch everything
    open_cards, all_cards = fetch_all_cards(key, token)
    label_id_to_name, label_name_to_id = fetch_label_map(key, token)
    list_id_to_name, list_name_to_id = fetch_list_map(key, token)

    log(f"Live open cards: {len(open_cards)}, total: {len(all_cards)}")

    # 2. Dedupe: archive all but newest duplicate-name card
    name_groups = defaultdict(list)
    for c in open_cards:
        name = c.get('name', '').strip().lower()
        if name:
            name_groups[name].append(c)

    archived_dups = 0
    for name, group in name_groups.items():
        if len(group) > 1:
            # Sort by dateLastActivity, keep newest
            sorted_group = sorted(group, key=lambda x: x.get('dateLastActivity', '') or '')
            for dup in sorted_group[:-1]:  # archive all but newest
                if archive_card(key, token, dup['id']):
                    archived_dups += 1
                    changes_made += 1
                    summary["duplicates_archived"] += 1
                time.sleep(BATCH_PAUSE * 0.1)  # small pause to avoid rate limits

    log(f"Dedupe: archived {archived_dups} duplicate cards")

    # 3. Re-fetch cards after dedupe (archived cards disappear from open)
    open_cards, _ = fetch_all_cards(key, token)

    # 4. Classify and rebalance each card
    moved_count = 0
    relabeled_count = 0
    for card in open_cards:
        cid = card.get('id', '')
        name = card.get('name', '')
        desc = card.get('desc', '')
        current_list_id = card.get('idList', '')
        current_labels = card.get('labels', [])

        # Skip cards in Done list (already resolved — don't reclassify)
        # Skip cards with automation-completed label (already resolved by crew)
        completed_labels = [l.get('name','') for l in current_labels if l.get('name','') == 'automation-completed']
        if current_list_id == LIST_IDS.get('Done') or completed_labels:
            continue

        # Classify
        classification = classify_card(name, current_labels, desc)

        # Handle ARCHIVE classification
        if classification == 'ARCHIVE':
            if archive_card(key, token, cid):
                summary["stale_archived"] += 1
                changes_made += 1
            continue

        target_list_id = LIST_IDS.get(classification)
        if not target_list_id:
            continue

        # Move if needed
        if current_list_id != target_list_id:
            if move_card(key, token, cid, target_list_id):
                moved_count += 1
                changes_made += 1
                summary["moved"] += 1
            time.sleep(BATCH_PAUSE * 0.1)

        # Fix labels: ensure exactly one priority label
        target_label_id = PRIORITY_LABEL_IDS.get(classification)
        if target_label_id:
            # Check if card already has the correct label and no conflicting priority labels
            label_ids_on_card = {l.get('id', '') for l in current_labels}
            priority_ids_on_card = {l.get('id', '') for l in current_labels
                                    if l.get('id', '') in set(PRIORITY_LABEL_IDS.values())}

            has_correct = target_label_id in label_ids_on_card
            has_conflicting = len(priority_ids_on_card - {target_label_id}) > 0

            if has_conflicting or not has_correct:
                set_labels(key, token, cid, [target_label_id], current_labels)
                relabeled_count += 1
                changes_made += 1
                summary["relabeled"] += 1
                time.sleep(BATCH_PAUSE * 0.1)

    log(f"Rebalance: moved {moved_count}, relabeled {relabeled_count}")

    # 5. Enforce Top 10 hard cap
    top10_list_id = LIST_IDS.get('Top 10')
    if top10_list_id:
        top10_cards = [c for c in open_cards if c.get('idList') == top10_list_id]
        if len(top10_cards) > TOP10_MAX:
            # Sort by dateLastActivity, demote oldest to P1
            sorted_top10 = sorted(top10_cards, key=lambda x: x.get('dateLastActivity', '') or '')
            excess = sorted_top10[TOP10_MAX:]
            top10_label_id = label_name_to_id.get('Top 10')
            p1_list_id = LIST_IDS.get('P1')
            for card in excess:
                # Remove Top 10 label
                if top10_label_id:
                    trello_del(key, token, f"https://api.trello.com/1/cards/{card['id']}/idLabels/{top10_label_id}", timeout=10)
                # Move to P1
                if p1_list_id:
                    move_card(key, token, card['id'], p1_list_id)
                summary["top10_enforced"] += 1
                changes_made += 1
            log(f"Top 10 enforcement: demoted {len(excess)} to P1")

    # 6. Archive stale P5/P6 cards older than STALE_P5_P6_DAYS
    stale_ids = []
    now = datetime.now(timezone.utc)
    for c in open_cards:
        lid = c.get('idList', '')
        list_name = list_id_to_name.get(lid, '')
        if list_name in ('P5', 'P6'):
            last = parse_iso(c.get('dateLastActivity', ''))
            if last and (now - last) > timedelta(days=STALE_P5_P6_DAYS):
                stale_ids.append(c['id'])
    for sid in stale_ids:
        if archive_card(key, token, sid):
            summary["stale_archived"] += 1
            changes_made += 1
        time.sleep(BATCH_PAUSE * 0.1)

    log(f"Stale P5/P6 archived: {len(stale_ids)}")

    # 7. Post summary comment on a tracking card (find or skip)
    now_iso = now.isoformat()
    comment = (f"[{now_iso}] TORUS_OPS_DEEP_AUDIT pass complete.\n"
               f"Changes: archived_dups={summary['duplicates_archived']}, "
               f"moved={summary['moved']}, relabeled={summary['relabeled']}, "
               f"top10_enforced={summary['top10_enforced']}, "
               f"stale_archived={summary['stale_archived']}\n"
               f"Total open cards: {len(open_cards)}")

    # Find the audit tracking card or pick the oldest P0 card
    audit_cards = [c for c in open_cards if 'audit' in c.get('name', '').lower()]
    target_card = audit_cards[0] if audit_cards else None
    if target_card:
        trello_post(key, token, f"https://api.trello.com/1/cards/{target_card['id']}/actions/comments",
                    {"text": comment}, timeout=15)

    return changes_made, summary, len(open_cards)


def update_index(key, token):
    """Refresh TRELLO_CARD_INDEX.json from live board state."""
    open_cards, all_cards = fetch_all_cards(key, token)
    label_id_to_name, label_name_to_id = fetch_label_map(key, token)
    list_id_to_name, list_name_to_id = fetch_list_map(key, token)

    index = {"cards": [], "last_checked": datetime.now(timezone.utc).isoformat()}
    for c in open_cards:
        list_name = list_id_to_name.get(c.get('idList', ''), '')
        labels = [label_id_to_name.get(l.get('id', ''), l.get('name', '')) for l in c.get('labels', [])]
        index["cards"].append({
            "id": c.get('id', ''),
            "name": c.get('name', ''),
            "board": "Torus_Ops",
            "list": list_name,
            "labels": labels,
            "dateLastActivity": c.get('dateLastActivity', ''),
            "due": c.get('due'),
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        })
    INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8", errors="replace")
    log(f"Index refreshed: {len(index['cards'])} cards")


def main():
    args = sys.argv[1:]
    once = '--once' in args
    interval = 60  # minutes
    for a in args:
        if a.startswith('--interval='):
            interval = int(a.split('=')[1])

    key, token = load_creds()
    state = load_state()
    iteration = 0

    log(f"TORUS_OPS_DEEP_AUDIT_START interval={interval}m")

    while True:
        iteration += 1
        iteration_start = datetime.now(timezone.utc)
        log(f"\n{'='*60}")
        log(f"AUDIT PASS #{iteration}")

        changes, summary, card_count = run_pass(key, token)

        # Update index
        update_index(key, token)

        state["last_run"] = iteration_start.isoformat()
        state["cards_before"] = state.get("cards_after", 0)
        state["cards_after"] = card_count
        state["archived"] += summary["duplicates_archived"] + summary["stale_archived"]
        state["moved"] += summary["moved"]
        state["relabeled"] += summary["relabeled"]
        state["iterations"] = iteration
        state["last_summary"] = summary

        save_state(state)

        log(f"PASS #{iteration} COMPLETE: {changes} changes, {card_count} open cards")
        log(f"  Summary: {json.dumps(summary)}")

        if changes == 0:
            log("NO_CHANGES_MADE — board is in stable state. Audit complete.")
            # Post final completion comment
            break

        if once:
            log("--once flag set, exiting after single pass")
            break

        log(f"Sleeping {interval} minutes until next pass...")
        time.sleep(interval * 60)

    log("TORUS_OPS_DEEP_AUDIT_DONE")
    return 0 if changes == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
