#!/usr/bin/env python3
"""Miss Pink OODA — Process remaining P2 actionable cards (batch 2)."""
import sys, os, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credential_loader import load_trello_credentials

creds = load_trello_credentials()
key, token = creds['api_key'], creds['token']
OODA = "\U0001f9f2"

cards = [
    # (card_id, comment, archive, note)
    ("6a77c8c38433558f5d31c03b6",
     "Prometheus+Grafana: Deployed. Prometheus port 9090, Grafana port 3001. Fleet metrics scraping at /fleet. Dashboard panel at /api/fleet. VERIFIED operational.",
     True,
     "Already documented"),
    ("6a77c8c226418135d2eacad5",
     "Alert-router: Deployed on port 4000. Webhook retry with 3 attempts backoff. Crew routing to Discord/SMTP. 5/6 Docker images pushed (alert-router image blocked by auth).",
     False,
     "Auth blocked"),
    ("6a7536aed2f2574acffb1de4",
     "Vercel deploy: vercel.json at 06_Website/next-storefront/vercel.json. Next.js build passes (npm run build exits 0). Ready for Captain to connect Vercel account.",
     False,
     "Captain action"),
    ("6a70dc38b1d094fb7520c275",
     "Winter 2026 Venue Research: Documented in 13_Team/Winter_2026_Venue_Research.md. Free options evaluated. Needs Captain decision on venue.",
     False,
     "Captain action"),
    ("6a7536b95c7790534a275f08",
     "Content pipeline: buffer_automation.py schedules social posts to 3 channels (LinkedIn, YouTube, Twitter). Zapier webhook live. HubSpot CRM connected with Service Key.",
     True,
     "Verified"),
    ("6a7536bd5b78413b00a7abd8",
     "YouTube automation: buffer_automation.py schedules weekly posts. AI thumbnails via ComfyUI on STEALTHATTACK (port 8188). Ready for Sir Azure activation.",
     False,
     "Sir Azure action"),
    ("6a7536beca690ffaf30a82e5",
     "AI image/video generation: ComfyUI on STEALTHATTACK (port 8188, GPU-accelerated). Ollama llama3.2 on PINKCADY (port 11434, GT 1030 GPU). Smart bridge spec ready.",
     False,
     "Sir Azure action"),
    ("6a75368c84748f2cf7ae1822",
     "Google Analytics: GA4 configured in 06_Website/next-storefront/app/layout.tsx. GA_MEASUREMENT_ID placeholder — needs Captain to provide real GA4 ID.",
     False,
     "Captain action"),
    ("6a70fd6168484eac3e8f306a",
     "Meta Business Suite: Not connected. No Meta credentials in vault. Needs Captain to provide Facebook page access token.",
     False,
     "Captain action"),
    ("6a70fd6215d81dccfafc6721",
     "Cloudflare DNS/CDN: No Cloudflare config in repo. Needs Captain to set up Cloudflare account + DNS records for toruscoffeecompany.com.",
     False,
     "Captain action"),
]

for cid, comment, archive, note in cards:
    try:
        full = f"{OODA} OODA: {comment}"
        r = requests.post(f"https://api.trello.com/1/cards/{cid}/actions/comments",
            params={"key": key, "token": token},
            data={"text": full}, timeout=10)
        if archive:
            requests.put(f"https://api.trello.com/1/cards/{cid}",
                params={"key": key, "token": token, "closed": "true"}, timeout=10)
        print(f"  {cid[:8]}: comment={r.status_code} archive={archive}")
        time.sleep(0.1)
    except Exception as e:
        print(f"  ERROR {cid[:8]}: {e}")

print(f"\nProcessed {len(cards)} cards")
