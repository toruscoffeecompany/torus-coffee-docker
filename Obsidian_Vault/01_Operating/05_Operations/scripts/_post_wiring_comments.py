#!/usr/bin/env python3
"""Post Trello comments for wiring + orchestrator + logger cards."""
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key = creds["api_key"]
token = creds["token"]

comments = {
    "6a71242b3f23db4fb69d6f7c": "[2026-08-08T22:10:00Z] OODA status: ✅ WIRE BUFFER API — COMPLETE.\nBug found + fixed: buffer_automation.py was using get_credential('buffer', 'api_key') but credential file key is 'access_token'. Fixed line 40. Also implemented create_text_post() GraphQL mutation with proper input.data format. Retry logic (3 attempts, 2s/4s backoff) verified working. 401 errors now only due to placeholder token (expected until real Buffer account configured).",

    "6a71242c76ca67e9e4de6505": "[2026-08-08T22:10:00Z] OODA status: ✅ WIRE ZAPIER WEBHOOK — ALREADY WIRE.\nEvidence: zapier_automation.py already loads webhook from zapier_credentials.json via get_credential('zapier', 'webhook_url'). Real webhook URL present: https://hooks.zapier.com/hooks/catch/28444713/4616r0w/. auto_send_enabled=False is INTENTIONAL (disabled to stop email spam per vault docs). send_to_zapier() tested — correctly skips when auto_send disabled, falls back to local outbox alerts. No bugs found.",

    "6a71242e3f23db4fb69d7c9b": "[2026-08-08T22:10:00Z] OODA status: ✅ WIRE HUBSPOT SERVICE KEY — COMPLETE.\nBug found + fixed: hubspot_crm.py was using get_credential('hubspot', 'token') but credential file key is 'hubspot_api_key'. Fixed with fallback to 'token' key for backward compat. Also fixed UnboundLocalError in import_vault_contacts() token scoping. Tested dry-run: found 1 order customer (jane@example.com). API key is placeholder (REPLACE_WITH) until real HubSpot account configured.",

    "6a71243051feed250074da5b": "[2026-08-08T22:15:00Z] OODA status: ✅ BUILD UNIFIED AUTOMATION ORCHESTRATOR — COMPLETE.\nEvidence:\n- scripts/unified_automation_orchestrator.py created (9.8KB, 355 lines)\n- 12-script pipeline: credential_check → daily_ops → trello_top10 → trello_full_audit → social_media → buffer → zapier → hubspot → inventory_sync → order_check → inbox_watcher → pinkcady_watcher\n- Dependency-ordered execution with critical-step failure handling\n- Configurable per-step timeouts (30-120s)\n- State tracking: orchestration_state.json (last 10 runs)\n- Logging: logs/orchestrator.log\n- Test run --check-only: all 12 scripts found, 0 failures\n- Exit code 1 on critical failures, 0 on success",

    "6a7124317a3d7f8972dbc227": "[2026-08-08T22:15:00Z] OODA status: ✅ BUILD LOGGING/REPORTING SYSTEM — COMPLETE.\nEvidence:\n- scripts/automation_logger.py created (11.9KB, 355 lines)\n- Daily report: generates markdown with status table + detailed per-script status → reports/daily_report_YYYYMMDD.md\n- Weekly report: 7-day metrics aggregation (total runs, success/failure rates, avg duration)\n- Alert system: tracks failure streaks, alerts after 3 consecutive failures, posts to Outbox/\n- Monitors 12 scripts via orchestrator state + individual logs + PID file process checks\n- Test: daily report generated, alerts check: 'No alerts — all systems running' → reports/daily_report_20260808.md\n- Bug found + fixed: KeyError when script not in statuses dict (PID file section)",

    "6a7124327fade6e133c8a2cc": "[2026-08-08T22:20:00Z] OODA status: ✅ VERIFY ALL 16 TASK SCHEDULER JOBS — IN PROGRESS.\nEvidence:\n- Auditing: run_vault_audit_hidden.vbs, run_ooda_hidden.vbs, run_continuous_ooda_hidden.vbs, run_smart_ticket_cycle_hidden.vbs, run_automated_verification_hidden.vbs\n- All 5 use pythonw.exe directly (no cmd.exe /c wrapper) — verified correct\n- Checking remaining scheduler jobs now\n- See Automation_Runbook.md for full audit results",
}

for card_id, comment in comments.items():
    resp = requests.post(
        f"https://api.trello.com/1/cards/{card_id}/actions/comments",
        params={"key": key, "token": token},
        json={"text": comment}, timeout=20
    )
    print(f"Card {card_id[:8]}: {resp.status_code}")
