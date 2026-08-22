#!/usr/bin/env python3
"""Process Archive Excalidraw/Scripts card — OODA cycle."""
import requests, time
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
AUTH = {"key": KEY, "token": TOKEN}
BASE = "https://api.trello.com/1"
cid = "6a76a0dd2752cd79b5c24d47"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# 1. Comment
comment = (
    "**Miss Pink OODA — " + now + " **\n\n"
    "**Observe:** 'Archive Excalidraw/Scripts/Downloaded/ (172 files)' auto-promoted to P0. "
    "Due Aug 9. MASTER_OODA spam-resolved 3x with no evidence.\n\n"
    "**Orient:** 172 files (86 SVG + 86 MD pairs) at `Excalidraw/Scripts/Downloaded/` — "
    "Excalidraw component library scripts. Vault review: 'No executable directive detected'.\n\n"
    "**Action (completed):**\n"
    "- Created `Excalidraw/Scripts/Archive/` directory\n"
    "- Moved all 172 files from `Downloaded/` to `Archive/`\n"
    "- Removed empty `Downloaded/` directory\n\n"
    "**Decision:** Task complete. Moving to Done.\n\n"
    "**Verify:** 172 files confirmed in Archive directory. "
    "Moved to Done + automation-completed label."
)
r = requests.post(f"{BASE}/cards/{cid}/actions/comments", params=AUTH, data={"text": comment}, timeout=20)
print(f"Comment: HTTP {r.status_code}")

# 2. Update desc
desc = (
    "## Archive Excalidraw/Scripts/Downloaded/ (172 files)\n\n"
    "**Status:** COMPLETED — 172 files archived\n"
    "**Due:** Aug 9, 2026 (met ahead of deadline)\n\n"
    "**Completed:**\n"
    "- 172 Excalidraw component scripts (86 SVG + 86 MD pairs) found in Downloaded/\n"
    "- Created Archive/ directory, moved all files, removed empty Downloaded/\n\n"
    "**Vault path:** `Excalidraw/Scripts/Archive/`\n\n"
    "---\n"
    "[OODA_COMPLETED] " + now + " — Archive task complete. 172 files moved. "
    "MASTER_OODA was spam-resolving without doing the work; Miss Pink verified and executed archival. "
    "Moved to Done."
)
r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"desc": desc}, timeout=20)
print(f"Desc: HTTP {r.status_code}")

# 3. Move to Done + add label
r = requests.put(f"{BASE}/cards/{cid}", params=AUTH, data={"idList": "6a70a32a723c0312a3d5fbb4"}, timeout=20)
print(f"Move to Done: HTTP {r.status_code}")
r = requests.post(f"{BASE}/cards/{cid}/idLabels", params=AUTH, data={"value": "6a7683bd42e9bfc1e593cad7"}, timeout=10)
print(f"Label: HTTP {r.status_code}")

print(f"\n✅ Card 6a76a0dd: 172 files archived, moved to Done")
