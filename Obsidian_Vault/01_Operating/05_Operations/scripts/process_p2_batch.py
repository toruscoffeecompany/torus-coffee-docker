#!/usr/bin/env python3
"""Miss Pink OODA — Process remaining P2 actionable cards."""
import sys, os, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']

OODA_TAG = "\U0001f9f2"  # robot face emoji

cards = [
    ("6a77c8c3945f3bd361b99f1d", "Docker Deploy torus-website: Image toruscoffee/torus-website:20260806-v1 in compose, pushed to Docker Hub, deployed with healthcheck at /health (port 3000).", True),
    ("6a77c8c38433558f5d31c03b6", "Prometheus+Grafana: Deployed. Prometheus port 9090, Grafana port 3001. Fleet metrics scraping at /fleet. Dashboard panel active.", True),
    ("6a77c8c226418135d2eacad5", "Alert-router: Deployed on port 4000. 5/6 Docker images pushed (alert-router blocked by auth). Webhook retry + crew routing functional.", False),
    ("6a77c8be1ef8982c02048c50", "Actionable alerts from dashboard: alert_router.py routes to Discord/SMTP. Status endpoint at /status. Alerts verified functional.", True),
    ("6a76281735fbe026273b3460", "Docker Hub push: 5 of 6 images pushed (torus-website, torus-pos, torus-inventory, redis, nginx). Alert-router blocked by auth - Sir Green action.", False),
    ("6a73a7c5c961b274fc935140", "[miss_pink] github_access_setup: Git remote authenticated. gh CLI working. Token in secrets.local.json.", True),
    ("6a73a7c8c15e8b17f35dbd92", "[miss_pink] github_team_setup: GitHub team structure verified. 3 repos accessible. Permissions confirmed.", True),
    ("6a73a7cbcf811fd5997c24ed", "[miss_pink] dashboard_reporting: TOOL_AE dashboard reports at /status, /vault-sync, /trello, /github. All verified.", True),
    ("6a73a7cd89e17f7ac03a289b", "[miss_pink] connectivity_monitor: crew_connectivity_monitor.py running on PINKCADY. Monitors 3 fleet hosts. Queue relay active.", True),
    ("6a73a7dc5e7fcc6f226c9bfd", "[sir_azure] github_token_setup: Requires Sir Azure GitHub token. Awaiting Sir Azure action.", False),
    ("6a73b459fa6409e91a66c985", "[sir_green] vault_access: Requires Sir Green to grant permanent vault access for PINKCADY automation. Sir Green action.", False),
    ("6a75329603a4a871edf307c6", "Self-healing/self-correcting mesh: miss_pink_self_heal.py operational. check_file_integrity() + git_restore_file(). Self-healing active.", True),
    ("6a7536973c45b35fbcd19b87", "credentials.ts path fixed: File at 06_Website/dashboard/lib/credentials.ts. Import path corrected.", True),
    ("6a7536acd75ae91c3c6a38cd", "dashboard_launcher.py: Created at scripts/dashboard_launcher.py. Startup shortcut configured. Verified operational.", True),
    ("6a7536b12176b10e925a88d5", "torus-pos: Deployed on port 3000. Healthcheck at /health. Healthy and serving.", True),
]

for cid, comment, archive in cards:
    try:
        r = requests.post(f"https://api.trello.com/1/cards/{cid}/actions/comments",
            params={"key": key, "token": token},
            data={"text": f"{OODA_TAG} OODA: {comment}"}, timeout=10)
        if archive:
            requests.put(f"https://api.trello.com/1/cards/{cid}",
                params={"key": key, "token": token, "closed": "true"}, timeout=10)
        status = "archived" if archive else "left open"
        print(f"  {cid[:8]}: {r.status_code} ({status})")
        time.sleep(0.1)
    except Exception as e:
        print(f"  ERROR {cid[:8]}: {e}")

print(f"\nProcessed {len(cards)} cards")
