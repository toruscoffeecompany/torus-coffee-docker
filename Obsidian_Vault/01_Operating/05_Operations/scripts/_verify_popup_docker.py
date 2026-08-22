#!/usr/bin/env python3
"""Post status comments on Trello cards for completed OODA work."""
import json, sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key = creds["api_key"]
token = creds["token"]

# Card: "P0: Eliminate all cmd popup sources permanently"
CARD_ID_POPUP = "6a76a0dc49915bc5db8a2acb"

comment_popup = """[2026-08-08T21:30:00Z] OODA status: ✅ CMD POPUP SOURCES ELIMINATED.
Evidence:
- references/cmd_popup_elimination_audit_2026-08-08.md created
- 4 VBS wrappers fixed: run_vault_audit_hidden.vbs, run_ooda_hidden.vbs, start_watchers.vbs, Torus_Dashboard_Launcher.vbs (Startup folder)
- Root cause: cmd.exe /c wrapper pattern + C:\\Python314\\python.exe (not pythonw.exe)
- All 10 remaining VBS wrappers verified clean (already use pythonw.exe directly)
- All 26 scheduled tasks verified using pythonw.exe (no cmd.exe /c)
- 400+ stale master_ooda_loop processes killed (from crashed loop)
Remaining: Monitor for any new popup sources in startup folder."""

resp = requests.post(
    f"https://api.trello.com/1/cards/{CARD_ID_POPUP}/actions/comments",
    params={"key": key, "token": token},
    json={"text": comment_popup},
    timeout=20
)
print(f"Popup card comment: {resp.status_code}")

# Card: "P0: Fix Docker fleet healthchecks — remove curl/wget deps"
CARD_ID_DOCKER = "6a76a0dd49915bc5db8a2be4"
comment_docker = f"""[2026-08-08T21:30:00Z] OODA status: P0 — Fix Docker fleet healthchecks.
Action: Audit all compose healthcheck definitions against actual app routes.
Evidence will be posted as fixes are applied.
Next: Read docker-compose files in 06_Docker and 06_Website, check healthcheck paths against FastAPI routes."""

resp2 = requests.post(
    f"https://api.trello.com/1/cards/{CARD_ID_DOCKER}/actions/comments",
    params={"key": key, "token": token},
    json={"text": comment_docker},
    timeout=20
)
print(f"Docker card comment: {resp2.status_code}")
