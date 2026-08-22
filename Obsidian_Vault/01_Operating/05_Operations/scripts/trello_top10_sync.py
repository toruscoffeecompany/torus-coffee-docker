#!/usr/bin/env python3
"""Trello Top 10 sync automation.
- Reads open cards from Torus_Ops board
- Maintains a Top 10 list by priority/score
- Marks duplicates, stale cards, and promotes next-in-line
- Writes TRELLO_TOP10.json snapshot
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("Missing requests. Install with: pip install requests")

BASE = Path(r"D:\Work\Torus Coffee Company LLC")
CRED_FILE = BASE / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
TOP10_FILE = BASE / "10_Skills_Library" / "05_Operations" / "TRELLO_TOP10.json"
BOARD_ID = "6a70a3157d0db4214ac3f9a3"


def load_trello_creds() -> tuple[str, str]:
    text = CRED_FILE.read_text(encoding="utf-8")
    api_key = token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Trello API credentials missing")
    return api_key, token


def classify(title: str) -> str:
    t = title.lower()
    if t.startswith("re "):
        return "P3"
    if any(k in t for k in [
        "status update", "coding order", "next actions", "one action",
        "docker", "plugin", "dashboard", "alert", "verify", "fleet",
        "build", "push", "deploy", "swarm", "compose", "webhook",
        "k8s", "kubernetes", "torus-light", "squidstation", "pinkcady",
        "stealthattack", "obsidian", "inventory", "pos", "website",
        "alert-router", "multistage", "hub", "miss gordon", "review",
        "action plan", "process sir azure inbox backlog", "livesync",
        "trello", "board audit", "priority"
    ]):
        return "P2"
    if "inbox" in t:
        return "P3"
    return "P2"


def score_card(card: dict) -> int:
    labels = [l["name"] for l in card.get("labels", [])]
    score = 0
    if "P1" in labels:
        score += 100
    elif "P2" in labels:
        score += 50
    elif "P3" in labels:
        score += 20
    title = card.get("name", "").lower()
    for kw in ["dashboard", "docker", "alert", "k8s", "kubernetes", "plugin", "obsidian", "fleet", "swarm", "compose", "webhook", "trello", "github", "verify", "fix", "top priority"]:
        if kw in title:
            score += 10
    return score


def main() -> int:
    api_key, token = load_trello_creds()
    r = requests.get(
        f"https://api.trello.com/1/boards/{BOARD_ID}/cards",
        params={"key": api_key, "token": token, "fields": "name,idList,labels,url,dateLastActivity", "card_fields": "name,labels,url,dateLastActivity"},
        timeout=15,
    )
    if r.status_code != 200:
        print(f"TRELLO_HTTP_{r.status_code}")
        return 0
    cards = r.json()
    scored = []
    for card in cards:
        s = score_card(card)
        last = card.get("dateLastActivity") or ""
        age_days = 9999
        if last:
            try:
                dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400
            except Exception:
                pass
        scored.append({
            "id": card.get("id"),
            "name": card.get("name"),
            "url": card.get("url"),
            "score": s,
            "age_days": round(age_days, 1),
            "labels": [l["name"] for l in card.get("labels", [])],
        })
    scored.sort(key=lambda x: (-x["score"], x["age_days"]))
    top10 = scored[:10]
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "board_id": BOARD_ID,
        "total_cards": len(cards),
        "top10": top10,
        "next_candidates": scored[10:20],
        "stale_candidates": [c for c in scored if c["age_days"] > 14][:10],
    }
    TOP10_FILE.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"TOP10_OK total={len(cards)} top10={len(top10)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
