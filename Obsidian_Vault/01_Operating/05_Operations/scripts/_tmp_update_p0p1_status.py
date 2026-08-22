#!/usr/bin/env python3
"""Create missing supporting docs for P0/P1/Top 10 cards and update descriptions."""
import requests
from pathlib import Path
from datetime import datetime, timezone

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
CRED_FILE = VAULT / "01_Operating" / "Operating Paperwork" / "Trello_API_Credentials.md"
DOCS = VAULT / "10_Skills_Library" / "05_Operations"

def load_trello_creds():
    text = CRED_FILE.read_text(errors="ignore")
    api_key = token = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "API Key" in line and i + 1 < len(lines):
            api_key = lines[i + 1].strip().strip("`")
        elif "Token" in line and "OAuth" not in line and i + 1 < len(lines):
            token = lines[i + 1].strip().strip("`")
    if not api_key or not token:
        raise RuntimeError("Trello credentials missing")
    return api_key, token

def write_doc(rel, content):
    p = DOCS / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p

def update_card(api_key, token, card_id, desc):
    r = requests.put(
        f"https://api.trello.com/1/cards/{card_id}",
        data={"key": api_key, "token": token, "desc": desc},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()

def run():
    api_key, token = load_trello_creds()
    updates = {}
    # Security tools install plan
    p = write_doc(
        "Crew/SECURITY_TOOLS_INSTALL_PLAN.md",
        """# Security Tools Install Plan on PINKCADY

Free-tier tools to install on PINKCADY:
- nikto: web server scanner
- tshark: network packet capture/analysis
- yara: pattern-based malware/artifact scanning
- crowdsec: free IPS/WAF
- suricata: free NIDS (already present per inbox)

Next actions:
1. Install via `choco` or `winget` on Windows.
2. Verify each tool with `--version`.
3. Add scan results to vault under `10_Skills_Library/05_Operations/Security/`.
4. Update this card with completion evidence.

Blocker:
- Execution requires Sir Azure availability on PINKCADY.
""",
    )
    updates["6a73bd43a4ef3f072e63a664"] = p.read_text(encoding="utf-8")

    # Tools/Security tabs plan
    p = write_doc(
        "Docker/DASHBOARD_TOOLS_SECURITY_PLAN.md",
        """# Tools/Security Tabs for Unified Dashboard on 8089

Add two new tabs to the unified dashboard:
- `/tools`: local inventory of installed tools, versions, and health
- `/security`: security findings from nikto/tshark/yara/suricata

Implementation notes:
- Frontend: reuse existing dashboard layout
- Backend: expose endpoints `GET /api/tools` and `GET /api/security-docs`
- Data source: `10_Skills_Library/05_Operations/Security/*`

Blockers:
- Requires Sir Green to add `/api/tools`, `/api/security-docs`, `/api/hw`, `/api/rig-report` routes
- Requires Sir Azure to populate security scan artifacts
""",
    )
    updates["6a73bd44be602ed2ba5a0158"] = p.read_text(encoding="utf-8")

    # Alert router blocker doc
    p = write_doc(
        "Docker/ALERT_ROUTER_DOCKER_HUB_BLOCKER.md",
        """# Alert Router Docker Hub Push Blocker

Status: BLOCKED

Symptom:
- `toruscoffee/torus-alert-router:latest` push blocked
- SQUIDSTATION images blocked by auth

Required actions:
1. Provide SQUIDSTATION with Docker Hub PAT or org write access
2. Re-run push from SQUIDSTATION or PINKCADY
3. Verify image exists on shared Docker Hub
4. Deploy `torus-alert-router` via `docker-compose.torus.fleet.yml`

Workaround:
- Use local image tag until Hub auth resolved
""",
    )
    updates["6a73f9d0d73587c596609d61"] = p.read_text(encoding="utf-8")

    # Suricata investigation doc
    p = write_doc(
        "Crew/SURICATA_EMPTY_MESSAGE_INVESTIGATION.md",
        """# Suricata Alert Investigation: Empty Message

Observed:
- Suricata alert fired with empty message payload

Investigation steps:
1. Review `/var/log/suricata/eve.json` for surrounding events
2. Check rule ID and signature
3. Correlate with dashboard/Prometheus alerts
4. If benign, add suppression rule
5. If real, escalate to Sir Green/Sir Azure

Current finding:
- Likely benign or instrumentation artifact; no immediate action required.
""",
    )
    updates["6a74226b70c09f9232cbdbac"] = p.read_text(encoding="utf-8")

    # Dashboard 502 regression status
    p = write_doc(
        "Docker/DASHBOARD_502_REGRESSION_STATUS.md",
        """# Dashboard 502 Regression Status

Current state:
- Dashboard container build succeeded: `toruscoffee/torus-dashboard:20260806-v2`
- Redeployment blocked by name conflict with existing `torus-dashboard`/`torus-redis` containers on SQUIDSTATION Docker API

Required actions:
1. Remove/rename conflicting containers on SQUIDSTATION
2. Re-run `docker compose -f docker-compose.torus.fleet.yml up -d torus-dashboard`
3. Verify `/api/fleet`, `/api/tools`, `/api/security-docs`, `/api/hw`, `/api/rig-report` routes

Blockers:
- Missing dashboard routes owned by Sir Green
- `/api/status` timeout on large payload (Sir Green fix pending)
""",
    )
    updates["6a74b23152f49229cdbf9e8f"] = p.read_text(encoding="utf-8")

    # GitHub auth setup doc
    p = write_doc(
        "Crew/GITHUB_AUTH_SETUP.md",
        """# PINKCADY GitHub Auth Setup for toruscoffeecompany Repos

Goal: enable Git operations from PINKCADY without password prompts.

Options:
1. SSH key: add PINKCADY public key to toruscoffeecompany GitHub account
2. PAT: store in Windows Credential Manager or `~/.git-credentials`
3. Git Credential Manager Core: use OAuth flow

Recommended free path:
- Use Git Credential Manager Core (`gcm`)
- Run `gh auth login` on PINKCADY for GitHub CLI access

Next actions:
1. Generate or reuse existing SSH key on PINKCADY
2. Add to GitHub account under toruscoffeecompany
3. Test `git clone git@github.com:toruscoffeecompany/Torus_Ops.git`
""",
    )
    updates["6a738887a9af207d20987848"] = p.read_text(encoding="utf-8")

    # Square setup doc
    p = write_doc(
        "Crew/SQUARE_DEVELOPER_SETUP.md",
        """# Square Developer Account Setup Walkthrough

Free-tier path:
1. Sign up at https://developer.squareup.com/
2. Create application in Square Developer Dashboard
3. Retrieve `SANDBOX_APPLICATION_ID`, `SANDBOX_ACCESS_TOKEN`
4. Configure payment links in Square Dashboard
5. Add links to website (`Deploy website to free hosting` card)

Next actions:
1. Create Square Developer account
2. Configure application settings
3. Store credentials in vault under `01_Operating/Operating Paperwork/Square_API_Credentials.md`
""",
    )
    updates["6a70c2e7c2bff8d0aac51714"] = p.read_text(encoding="utf-8")

    # SQUIDSTATION dashboard deploy doc
    p = write_doc(
        "Docker/DASHBOARD_SQUIDSTATION_DEPLOY.md",
        """# Deploy dashboard_server.py on SQUIDSTATION

Current blocker:
- Container name conflict on SQUIDSTATION Docker API

Deployment steps once blocker resolved:
1. Ensure `docker-compose.torus.fleet.yml` project name is unique
2. Run `docker compose -f docker-compose.torus.fleet.yml up -d torus-dashboard`
3. Verify dashboard reachable on host port 8089
4. Confirm `/api/fleet`, `/api/tools`, `/api/security-docs`, `/api/hw`, `/api/rig-report` respond

Required crew actions:
- Sir Green: remove conflicting containers or rename compose project
- Sir Green: implement missing routes in `dashboard_server.py`
""",
    )
    updates["6a714aec2a9827e94b0c2bbd"] = p.read_text(encoding="utf-8")

    # ComfyUI SQUIDSTATION deploy doc
    p = write_doc(
        "Docker/COMFYUI_SQUIDSTATION_DEPLOY.md",
        """# Sir Azure: ComfyUI/Redis/MinIO/Postgres/Nginx on SQUIDSTATION

Stack:
- ComfyUI: AI image generation
- Redis: job queue/cache
- MinIO: local object storage
- Postgres: metadata persistence
- Nginx: reverse proxy

Free-tier path:
1. Use existing SQUIDSTATION Docker engine
2. Create compose override or new compose file
3. Bind-mount models to existing storage
4. Expose only local network ports

Next actions:
1. Sir Azure to create `docker-compose.sir-azure.yml` on SQUIDSTATION
2. Test ComfyUI UI on local port
3. Add health checks and restart policies
""",
    )
    updates["6a73c1df44ddb17b0142b8c9"] = p.read_text(encoding="utf-8")

    # torus-inventory SQUIDSTATION deploy doc
    p = write_doc(
        "Docker/INVENTORY_SQUIDSTATION_DEPLOY.md",
        """# torus-inventory: Deploy Fixed FastAPI Image on SQUIDSTATION

Current state:
- Image built and tagged locally
- Deployment pending SQUIDSTATION container restart

Steps:
1. Push fixed image to shared Docker Hub or load locally on SQUIDSTATION
2. Run inventory service on SQUIDSTATION with volume mounts for `inventory.json`
3. Verify `/health` and `/items` endpoints
4. Update Trello card with deployment evidence

Blocker:
- SQUIDSTATION Docker context and auth
""",
    )
    updates["6a74213f952e3bf93da19ac0"] = p.read_text(encoding="utf-8")

    for card_id, desc in updates.items():
        try:
            update_card(api_key, token, card_id, desc)
            print(f"updated {card_id}")
        except Exception as e:
            print(f"failed {card_id}: {e}")

if __name__ == "__main__":
    run()
