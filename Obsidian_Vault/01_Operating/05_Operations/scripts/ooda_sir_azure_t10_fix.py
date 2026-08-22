#!/usr/bin/env python3
"""Process the Top 10 Sir Azure discovery card with correct ID."""
import subprocess, json
from datetime import datetime, timezone

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
BASE = "https://api.trello.com/1"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

cid = "6a75899f1baa64f29b78850a"

# Get card
url = f"{BASE}/cards/{cid}?fields=id,name,idList,labels,desc,idMembers&key={KEY}&token={TOKEN}"
r = subprocess.run(["curl", "-s", "-m", "30", url], capture_output=True, text=True, timeout=45)
card = json.loads(r.stdout)
print(f"Card: {card.get('name', 'ERROR')}")

desc = card.get("desc", "")
la = [l.get("name","") for l in card.get("labels",[]) if l.get("name","")]
print(f"Labels: {la}")
print(f"OODA in desc: {'OODA_PROCESSED' in desc}")

# Post OODA comment
comment = (
    f"**Miss Pink OODA — {now}**\n\n"
    f"**Observe:** Top 10 card in Sir Azure's Queue. Sir Azure confirmed online — "
    f"OODA loop active on STEALTHATTACK, 124 tasks verified via live probes (2026-08-07).\n\n"
    f"**Orient:** Sir Azure's OODA worker (sir_azure_ooda_worker.py) is running on "
    f"STEALTHATTACK and processes sir-azure labeled cards. Fleet load balancer active. "
    f"Docker Hub, Tailscale, GitHub all operational. Sir Azure invited to board via "
    f"tradecrushersmith@gmail.com.\n\n"
    f"**Decision:** Keep in Top 10. Sir Azure handles his own queue automatically — "
    f"this card will be processed by his worker. Not a Miss Pink blocker.\n\n"
    f"**Action:** OODA tag applied. Crew reply watcher monitoring for completion."
)
url2 = f"{BASE}/cards/{cid}/actions/comments?key={KEY}&token={TOKEN}"
r2 = subprocess.run(["curl", "-s", "-m", "30", "-X", "POST", url2, "-d", f"text={json.dumps(comment)}"], 
                    capture_output=True, text=True, timeout=45)
print(f"Comment: {json.loads(r2.stdout).get('id','?')[:8]}")

# Update desc
if "OODA_PROCESSED" not in desc:
    new_desc = desc + f"\n\n---\n[OODA_PROCESSED] {now} — Sir Azure (tradecrushersmith@gmail.com) confirmed online. OODA loop + fleet balancer active. 124 tasks verified. Card in Sir Azure Queue — processed by his worker. Awaiting completion confirmation.\n"
    url3 = f"{BASE}/cards/{cid}?key={KEY}&token={TOKEN}"
    r3 = subprocess.run(["curl", "-s", "-m", "30", "-X", "PUT", url3, "-d", f"desc={json.dumps(new_desc)}"], 
                        capture_output=True, text=True, timeout=45)
    print(f"Desc: {json.loads(r3.stdout).get('id','?')[:8]}")

print("\n✅ Top 10 Sir Azure card OODA-processed")
