#!/usr/bin/env python3
"""Process Card 6a712bc7 — Deploy website to free hosting"""
import requests, time
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
cid = "6a712bc79bc50687e977187a"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Get list IDs
lists = requests.get(f"{BASE}/boards/6a70a3157d0db4214ac3f9a3/lists", params=AUTH, timeout=15).json()
p2_id = next((l["id"] for l in lists if "P2" in l.get("name", "")), None)
p0_id = next((l["id"] for l in lists if "P0" in l.get("name", "")), None)

# 1. Post OODA comment
comment = (
    "**Miss Pink OODA — " + now + " **\n\n"
    "**Observe:** MASTER_OODA loop is spamming 'advancing by priority' every ~1s on this card. "
    "Card desc says 'No executable directive found' — no specific hosting instructions.\n\n"
    "**Orient:** Vault cross-ref: `PROJECT WEBSITE R3DEPLOY/index.md` — project is in **Design Phase, "
    "Ready to Start**. Scaffold built at `06_Website/next-storefront/`, GitHub repo `torus_website_rebuild` "
    "has initial commit. Tailscale pending (Sir Green). GitHub push paused until vault locked down.\n\n"
    "**Decision:** This is NOT a P0 blocker. Website is in design phase — hosting deployment is weeks out "
    "per the 8-week timeline (Week 8 milestone). Premature escalation.\n\n"
    "**Actions:**\n"
    "1. ↓ Moving P0 → P2 (This Week — design phase)\n"
    "2. ← Updating desc to reference vault docs instead of auto-index stub\n"
    "3. 🔇 Noting MASTER_OODA spam loop needs intervention\n"
    "4. ✅ This card will remain P2 until Week 8 (deployment milestone) or Sir Green provides hosting access\n\n"
    "**Miss Pink:** Card correctly reclassified. Hosting deployment will trigger when design phase completes "
    "and Tailscale is available. Not blocking current ops."
)
r = requests.post(f"{BASE}/cards/{cid}/actions/comments", params=AUTH, data={"text": comment}, timeout=20)
print(f"Comment: HTTP {r.status_code}")

# 2. Update desc with vault redirect
desc = (
    "## Deploy website to free hosting\n\n"
    "**Status:** P2 — Design Phase (Week 1). Not currently blocking.\n\n"
    "**Vault docs:** `06_Website/PROJECT WEBSITE R3DEPLOY/index.md`\n"
    "- Stack: Next.js + TypeScript + Tailwind\n"
    "- Repo: https://github.com/toruscoffeecompany/Torus_website_rebuild\n"
    "- Scaffold: `06_Website/next-storefront/`\n"
    "- Tailscale pending (Sir Green)\n\n"
    "**Timeline:** Week 8 — Deployment & Hosting\n\n"
    "---\n"
    "[OODA_OBSERVED] " + now + " — MASTER_OODA was spam-posting 'advancing by priority' every ~1s. "
    "Root cause: no executable directive, auto-indexed stub. Card reclassified P0→P2, "
    "desc updated with vault docs. Will deploy to free hosting when design phase completes.\n"
)
r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": desc}, timeout=20)
print(f"Desc: HTTP {r.status_code}")

# 3. Move to P2
r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"idList": p2_id}, timeout=20)
print(f"Move P0→P2: HTTP {r.status_code}")

print(f"\n✅ Card 6a712bc7 processed: reclassified P0→P2, desc updated, OODA comment posted")
print(f"MASTER_OODA spam note: alerted in comment — needs loop intervention")
