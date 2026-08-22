#!/usr/bin/env python3
"""Process Webhook Event card through OODA action phase."""
import requests, time
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
cid = "6a7115f7e256159bc959b02b"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# 1. Post status comment
comment = (
    "**Miss Pink OODA — " + now + " **\n\n"
    "**Observing:** Webhook Event — automation fired but smart ticket system returned 'no matching handler' (Aug 7 12:30 UTC). "
    "Related to void_discord_webhook_connection_request_20260807T1915Z.msg.md sent Aug 7 19:15Z to Sir Green/Sir Azure.\n\n"
    "**Orienting:** Vault cross-ref: Discord webhook connection request needs guild/channel IDs + webhook tokens to wire automation hooks.\n\n"
    "**Decision:** Moving to Sir Azure's Queue (systems/auth task). Card stays P0 — needs webhook credentials to unblock.\n\n"
    "**Action needed from Sir Green/Sir Azure:**\n"
    "1. Respond with VOID Discord guild ID + channel IDs (crew alerts, ops status, bot commands)\n"
    "2. Provide webhook URLs or bot token mapping (partial token confirmation OK)\n"
    "3. Confirm preferred auth: webhook-only or bot token with read+write\n\n"
    "**Miss Pink:** Awaiting Discord webhook credentials. Will escalate to demote-to-P1 after 24h if no response ("
    "Aug 9 05:59 UTC)."
)
r = requests.post(f"{BASE}/cards/{cid}/actions/comments", params=AUTH, data={"text": comment}, timeout=15)
print(f"Comment posted: HTTP {r.status_code}")

# 2. Update desc
desc = (
    "Auto-indexed: Webhook Event\n\n"
    "Priority: P0\nBoard: Torus_Ops | List: P0 - Alert / Critical / Do Now\n"
    "Source: automation\nTrello Card ID: 6a7115f7e256159bc959b02b\n"
    "Indexed: 2026-08-06T15:27:41.339236\nDue: 2026-08-07T15:27:40.995631\n\n"
    "---\n"
    "[OODA_OBSERVED] Webhook Event — automation fired with 'no matching handler'. "
    "Related to discord webhook connection request 20260807T1915Z. Needs Discord webhook credentials. "
    "Moved to Sir Azure Queue. Awaiting crew response. Demote-to-P1 if unresolved by 2026-08-09T05:59:00Z.\n"
)
r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": desc}, timeout=15)
print(f"Desc updated: HTTP {r.status_code}")

# 3. Move to Sir Azure's Queue
lists = requests.get(f"{BASE}/boards/6a70a3157d0db4214ac3f9a3/lists", params=AUTH, timeout=15).json()
sir_azure_list = next((l["id"] for l in lists if "Sir Azure" in l.get("name", "")), None)
if sir_azure_list:
    r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"idList": sir_azure_list}, timeout=15)
    print(f"Moved to Sir Azure queue: HTTP {r.status_code}")

print(f"\nActions complete for Webhook Event card ({cid[:8]})")
