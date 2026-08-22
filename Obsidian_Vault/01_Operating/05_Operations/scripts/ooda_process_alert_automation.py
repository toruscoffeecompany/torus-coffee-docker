#!/usr/bin/env python3
"""Process Alert automation card 6a75890c"""
import requests, time
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
cid = "6a75890c6c69623853472e9e"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Post OODA comment
comment = (
    "**Miss Pink OODA — " + now + " **\n\n"
    "**Observe:** MASTER_OODA marked this card 'Completed: Executed card directive' at 02:48 UTC, "
    "but it's still in P0. Vault review note at "
    "`ops_notes/review/alert_automation_confirm_sir_green_sir_azure_read_and_act_on_inbox_messages_review.md` "
    "**says 'No executable directive detected. Owner: Miss Pink.'**\n\n"
    "**Orient:** The alert automation system itself (auto-promoting to Top 10, routing to inboxes, "
    "smart classification) is a Sir Green task. MASTER_OODA's 'completion' only created a review note — "
    "it hasn't verified Sir Green/Sir Azure are actually reading and acting on inbox messages.\n\n"
    "**Decision:** This cannot be closed as 'done' until Sir Green confirms the alert automation is "
    "working end-to-end. Keeping in P0 pending crew verification.\n\n"
    "**Action needed @void_pirate_capta1n (Sir Green):**\n"
    "Please confirm: Is the alert automation (inbox routing → smart classification → crew queues) "
    "working correctly? Specifically, are Sir Green and Sir Azure receiving and acting on inbox alerts?\n\n"
    "**Miss Pink:** If this automation is verified working, I'll move to Done. If it needs fixes, "
    "I'll assist with the automation script. Standing by for Sir Green's reply."
)
r = requests.post(f"{BASE}/cards/{cid}/actions/comments", params=AUTH, data={"text": comment}, timeout=20)
print(f"Comment: HTTP {r.status_code}")

# Update desc with clarification
desc = (
    "## Alert automation: confirm Sir Green/Sir Azure read and act on inbox messages\n\n"
    "**Priority:** P0\n"
    "**Status:** AWAITING CREW VERIFICATION — MASTER_OODA marked 'completed' at 02:48 UTC but this "
    "only created a review note, not verified end-to-end.\n\n"
    "**What needs confirmation:**\n"
    "- Alert automation routing inbox → smart classification → crew queues\n"
    "- Sir Green and Sir Azure receiving and acting on alerts\n"
    "- Auto-promotion to Top 10 working correctly\n\n"
    "**Owner:** Sir Green (VOID)\n\n"
    "---\n"
    "[OODA_OBSERVED] " + now + " — MASTER_OODA 'completed' marker was premature (only created review note). "
    "Awaiting Sir Green confirmation that alert automation works end-to-end. Card remains P0.\n"
)
r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": desc}, timeout=20)
print(f"Desc: HTTP {r.status_code}")
print(f"\n✅ Card 6a75890c processed: status comment + desc updated, remains P0 awaiting crew")
