#!/usr/bin/env python3
"""Miss Pink OODA — Final P2 batch processing."""
import sys, os, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']
OODA = "\U0001f9f2"

cards = [
    ("6a77c8c3833558f5d31c03b6",
     "Prometheus+Grafana: Deployed (port 9090/3001). Alert-router image blocked by Docker Hub auth. Issue #4 tracked. Captain action.",
     False,  "Captain"),
    ("6a77c8c226418135d2eacad5",
     "Alert-router: Deployed on port 4000. 5/6 images pushed. Alert-router needs Docker Hub PAT. Issue #5 closed.",
     False,  "Captain"),
    ("6a7536aed2f2574acffb1de4",
     "Vercel deploy: vercel.json at 06_Website/next-storefront/vercel.json. Build passes. Needs Captain to connect Vercel account.",
     False,  "Captain"),
    ("6a70dc38b1d094fb7520c275",
     "Winter 2026 Venue Research: Venue research documented in 13_Team/. Free options evaluated. Awaiting Captain decision.",
     False,  "Captain"),
    ("6a7536bd5b78413b00a7abd8",
     "YouTube automation: buffer_automation.py schedules weekly posts. AI thumbnails via ComfyUI on STEALTHATTACK (port 8188). Awaiting Sir Azure render activation.",
     False,  "Sir Azure"),
    ("6a75368c84748f2cf7ae1822",
     "Google Analytics: GA4 configured in 06_Website/next-storefront/app/layout.tsx. Needs Captain to provide real GA4 measurement ID.",
     False,  "Captain"),
    ("6a70fd6168484eac3e8f306a",
     "Meta Business Suite: Not connected. No Meta credentials in vault. Needs Captain to set up FB page access token.",
     False,  "Captain"),
    ("6a70fd6215d81dccfafc6721",
     "Cloudflare DNS/CDN: Not configured. No Cloudflare config in repo. Needs Captain to set up Cloudflare account + DNS records.",
     False,  "Captain"),
    ("6a7536b45dd1e1e814ebe554",
     "Build website to Vercel: Same as Deploy website to Vercel. vercel.json ready at 06_Website/next-storefront/. Captain action.",
     False,  "Captain"),
    ("6a7536c965440023ee45a025",
     "Discord bot: Bot scripts ready at scripts/discord_bot*. Requires Discord tokens from Captain. crew_map.json at Crew/Torus_Discord/. Captain action.",
     False,  "Captain"),
    ("6a77a2c4f6de79b4b0f4faab",
     "VOIDPirateTrade collab: Requires Captain to add Miss Pink as collaborator on VOIDPirateTrade org. GitHub issue #19. Captain action.",
     False,  "Captain"),
    ("6a753737a134f0acb0e200c5",
     "Docker Hub auth failure: 5/6 images pushed. Alert-router blocked by auth. Needs Captain Docker Hub PAT for remaining pushes.",
     False,  "Captain"),
    ("6a7596c53c416fac2a2424b2",
     "VirtualBox + Docker sandbox networking: VBox + Docker on PINKCADY documented. Sir Azure to configure host-only bridge for Crownless Fortune sandbox.",
     False,  "Sir Azure"),
    ("6a77abd6e8e95f73c46ce6f0",
     "Browser recommendation: Firefox + uBlock Origin or LibreWolf recommended for low resource usage. Captain action — install on PINKCADY.",
     False,  "Captain"),
    ("6a77c0b6716ee7bd29dcb571",
     "Ollama service on SQUIDSTATION Kubernetes: Requires Sir Green to deploy on K8s cluster. Ollama llama3.2 already vault-bound on PINKCADY. Sir Green action.",
     False,  "Sir Green"),
    ("6a789d47",
     f"cross_pc_verifier missing on PINKCADY: No cross_pc_verifier.py script found in vault. Need to create at scripts/cross_pc_verifier.py. TORUS sorting template documented.",
     False,  "To-do"),
    ("6a789d4d",
     f"cross_pc_verifier missing on STEALTHATTACK: No cross_pc_verifier.py or ticket_processor.py found. Need Sir Azure to deploy on STEALTHATTACK. Sir Azure action.",
     False,  "Sir Azure"),
]

for cid, comment, archive, owner in cards:
    try:
        full = f"{OODA} OODA: {comment}"
        r = requests.post(f"https://api.trello.com/1/cards/{cid}/actions/comments",
            params={"key": key, "token": token},
            data={"text": full}, timeout=10)
        if archive:
            requests.put(f"https://api.trello.com/1/cards/{cid}",
                params={"key": key, "token": token, "closed": "true"}, timeout=10)
        print(f"  {cid[:8]}: {r.status_code} ({'archived' if archive else 'left open'})")
        time.sleep(0.1)
    except Exception as e:
        print(f"  ERROR {cid[:8]}: {e}")

print(f"\nProcessed {len(cards)} cards")
