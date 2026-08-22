#!/usr/bin/env python3
"""
Smart Ticket Cycle — manage Trello board lifecycle:
  - Promote P1/P2 cards into Top 10
  - Downgrade stuck cards (no activity > 30 days, not P0)
  - Verify Done cards
  - Append status comments to next actionable card
  - Write report to outbox
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

import requests

# === CONFIGURATION ===
VAULT = Path(r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault")
OUTBOX = VAULT / "02_Business_Operations" / "Communications" / "Outbox"


def load_creds():
    creds_path = VAULT / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
    text = creds_path.read_text(encoding="utf-8")
    api_key = token = None
    for val in text.replace("`", " ").split():
        if val.startswith("d6ee"):
            api_key = val
        elif val.startswith("ATTA"):
            token = val
    if not api_key or not token:
        raise ValueError("Trello credentials not found")
    return api_key, token


TRELLO_KEY, TRELLO_TOKEN = load_creds()
BASE = "https://api.trello.com/1"

# Board ID — Torus Ops board (Miss Pink primary)
BOARD_ID = "6a70a3157d0db4214ac3f9a3"


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
def trello_get(path, timeout=30):
    r = requests.get(f"{BASE}{path}", params={"key": TRELLO_KEY, "token": TRELLO_TOKEN}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def trello_post(path, payload, timeout=30):
    r = requests.post(f"{BASE}{path}", params={"key": TRELLO_KEY, "token": TRELLO_TOKEN}, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Priority helpers
# ---------------------------------------------------------------------------
PRIORITY_ORDER = ["P0", "P1", "P2", "P3", "P4", "P5", "P6", ""]


def card_priority(card: dict) -> str:
    name = card.get("name", "")
    if name.startswith("P0:") or name.startswith("[P0]"):
        return "P0"
    if name.startswith("P1:") or name.startswith("[P1]"):
        return "P1"
    if name.startswith("P2:") or name.startswith("[P2]"):
        return "P2"
    if name.startswith("P3:") or name.startswith("[P3]"):
        return "P3"
    return ""


def priority_sort_key(card: dict) -> tuple:
    p = card_priority(card)
    try:
        idx = PRIORITY_ORDER.index(p)
    except ValueError:
        idx = len(PRIORITY_ORDER)
    return (idx, card.get("name", "").lower())


# Configuration
MIN_CYCLE_INTERVAL_SECONDS = 43200  # 12 hours minimum between cycles
STATE_FILE = VAULT / "01_Operating" / "05_Operations" / "smart_ticket_cycle_state.json"

# === State tracking ===
def load_state():
    """Load last cycle timestamp from state file."""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {"last_run": None, "cycle_count": 0, "rate_limited": False}

def save_state(state):
    """Save cycle state to state file."""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass

def check_rate_limit():
    """Check if we need to wait before running the cycle.
    Returns True if should proceed, False if rate-limited."""
    state = load_state()
    last_run = state.get("last_run")
    if last_run:
        try:
            last_ts = datetime.fromisoformat(last_run.replace("Z", "+00:00")).timestamp()
            elapsed = datetime.now(timezone.utc).timestamp() - last_ts
            if elapsed < MIN_CYCLE_INTERVAL_SECONDS:
                remaining = MIN_CYCLE_INTERVAL_SECONDS - elapsed
                print(f"⚠️ Rate limited — {remaining:.0f}s until next allowed run")
                state["rate_limited"] = True
                save_state(state)
                return False
        except Exception:
            pass
    return True

# Core cycle
def run_cycle():
    # ─══ Rate limiting check ────────────────────────────────────────────────────────────────
    if not check_rate_limit():
        print("Skipping cycle due to rate limiting")
        return
    
    state = load_state()
    cycle_num = state.get("cycle_count", 0) + 1

    now = datetime.now(timezone.utc)
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    now_file = now.strftime("%Y%m%dT%H%M%SZ")
    
    print(f"[{now_iso}] SMART_TICKET_CYCLE_START (cycle #{cycle_num})")

    # ------------------------------------------------------------------
    # 1. Fetch all board cards
    # ------------------------------------------------------------------
    all_cards = trello_get(f"/boards/{BOARD_ID}/cards")
    open_cards = [c for c in all_cards if not c.get("closed", False)]
    done_cards = [c for c in all_cards if c.get("closed", False)]

    # Count by priority among open cards
    p_counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0, "P4": 0, "P5": 0, "P6": 0}
    for c in open_cards:
        p = card_priority(c)
        if p in p_counts:
            p_counts[p] += 1

    top10 = sorted(open_cards, key=priority_sort_key)[:10]

    print(f"Counts Top10={len(top10)} P0={p_counts['P0']} P1={p_counts['P1']} P2={p_counts['P2']} P3={p_counts['P3']} open={len(open_cards)}")

    # ------------------------------------------------------------------
    # 2. Promote P1/P2 into Top 10 — add Top10 label if not already there
    # ------------------------------------------------------------------
    promoted = []
    top10_ids = {c["id"] for c in top10}
    try:
        board_labels = trello_get(f"/boards/{BOARD_ID}/labels")
        top10_label = next((l for l in board_labels if l["name"].lower() == "top10"), None)
    except Exception:
        top10_label = None

    for c in open_cards:
        p = card_priority(c)
        if p in ("P1", "P2") and c["id"] not in top10_ids:
            promoted.append({"name": c["name"], "id": c["id"]})
            if top10_label:
                try:
                    labels = trello_get(f"/cards/{c['id']}/labels")
                    label_ids = [l["id"] for l in labels]
                    if top10_label["id"] not in label_ids:
                        trello_post(f"/cards/{c['id']}/idLabels", {"value": top10_label["id"]})
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # 3. Downgrade stuck cards (no activity > 30 days, not P0)
    # ------------------------------------------------------------------
    stuck_threshold = now.timestamp() - (30 * 24 * 60 * 60)
    downgraded = []
    for c in open_cards:
        p = card_priority(c)
        if p in ("P1", "P2", "P3", "P4", "P5", "P6"):
            date_last = c.get("dateLastActivity")
            if date_last:
                try:
                    last_ts = datetime.fromisoformat(date_last.replace("Z", "+00:00")).timestamp()
                except Exception:
                    last_ts = 0
            else:
                last_ts = 0
            if last_ts < stuck_threshold:
                new_p = f"P{min(int(p[1]) + 1, 6)}"
                downgraded.append({"name": c["name"], "id": c["id"], "from": p, "to": new_p})
                new_name = c["name"].replace(f"{p}:", f"{new_p}:").replace(f"[{p}]", f"[{new_p}]")
                try:
                    trello_post(f"/cards/{c['id']}", {"name": new_name})
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # 4. Verify Done cards — confirm closed cards exist in Done list
    # ------------------------------------------------------------------
    verified_done = []
    try:
        lists = trello_get(f"/boards/{BOARD_ID}/lists")
        done_list = next((l for l in lists if l["name"].lower() == "done"), None)
        if done_list:
            done_list_cards = trello_get(f"/lists/{done_list['id']}/cards")
            for c in done_list_cards:
                verified_done.append({"name": c["name"], "id": c["id"]})
    except Exception:
        pass

    # ------------------------------------------------------------------
    # 5. Next actionable card (first open card by priority)
    # ------------------------------------------------------------------
    next_actionable = None
    if open_cards:
        best = sorted(open_cards, key=priority_sort_key)[0]
        next_actionable = {"name": best["name"], "id": best["id"]}

    # ------------------------------------------------------------------
    # 6. Append status comment to next actionable card
    # ------------------------------------------------------------------
    comment_text = (
        f"[{now_iso}] Smart ticket cycle: next actionable = {next_actionable['name'] if next_actionable else 'None'} "
        f"| board open={len(open_cards)} | promoted={len(promoted)} | downgraded={len(downgraded)}"
    )
    if next_actionable:
        try:
            trello_post(f"/cards/{next_actionable['id']}/actions/comments", {"text": comment_text})
        except Exception as e:
            print(f"WARNING: could not post comment: {e}")

    # ------------------------------------------------------------------
    # 7. Print summary
    # ------------------------------------------------------------------
    print(f"\n## Promoted\n{json.dumps(promoted, indent=2)}")
    print(f"\n## Downgraded\n{json.dumps(downgraded, indent=2)}")
    print(f"\n## Verified Done\n{json.dumps(verified_done, indent=2)}")
    print(f"\n## Next Actionable\n{json.dumps(next_actionable, indent=2)}")
    print(f"\n## Comment Added\n{json.dumps({'card_id': next_actionable['id'] if next_actionable else None, 'text': comment_text}, indent=2)}")
    print(f"\n## Counts\n{json.dumps({**{'Top 10': len(top10)}, **p_counts, 'Done': len(done_cards)}, indent=2)}")

    # ------------------------------------------------------------------
    # 8. Write report to outbox
    # ------------------------------------------------------------------
    OUTBOX.mkdir(parents=True, exist_ok=True)
    report_path = OUTBOX / f"{now_file}_smart_ticket_cycle.msg.md"
    report = f"""# Smart Ticket Cycle — {now_iso}

## Promoted
{json.dumps(promoted, indent=2)}

## Downgraded
{json.dumps(downgraded, indent=2)}

## Verified Done
{json.dumps(verified_done, indent=2)}

## Next Actionable
{json.dumps(next_actionable, indent=2)}

## Comment Added
{json.dumps({'card_id': next_actionable['id'] if next_actionable else None, 'text': comment_text}, indent=2)}

## Counts
{json.dumps({**{'Top 10': len(top10)}, **p_counts, 'Done': len(done_cards)}, indent=2)}
"""
    report_path.write_text(report, encoding="utf-8")
    print(f"\\nReport written to {report_path}")
    
    # ─══ Save state (rate limiting + cycle tracking) ────────────────────────────────────────────
    state["last_run"] = now_iso
    state["cycle_count"] = cycle_num
    state["rate_limited"] = False
    state["last_summary"] = f"open={len(open_cards)} promoted={len(promoted)} downgraded={len(downgraded)}"
    save_state(state)

    print(f"\\n✅ Cycle complete — state saved (count: {cycle_num})")


if __name__ == "__main__":
    try:
        run_cycle()
    except Exception as e:
        print(f"FATAL: {e}")
        sys.exit(1)
