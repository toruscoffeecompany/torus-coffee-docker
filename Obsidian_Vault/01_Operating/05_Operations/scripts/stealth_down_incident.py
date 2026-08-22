"""
STEALTHATTACK OFFLINE — Log incident + continue OODA sweep.
"""
import json, urllib.request, os, time
from datetime import datetime, timezone

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TRELLO_KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TRELLO_TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"

# ─── Log STEALTHATTACK outage ────────────────────────────────────────────────
outage_log = f"""# 🚨 STEALTHATTACK OFFLINE INCIDENT — {ts}

**Time detected:** {ts}
**Rig:** STEALTHATTACK (Sir Azure) — 100.110.238.68
**Status:** COMPLETE OUTAGE

## Impact
- Docker containers: 14 DOWN (void-comfyui, void-tts, void-whisper, etc.)
- Ollama API: 11434 unreachable (llama3.2, qwen2.5-coder models down)
- Grafana: 3000 unreachable
- ComfyUI: 8188 unreachable
- All GPU/AI services offline

## Timeline
- Last bridge log: 2026-08-11T03:05:41Z (test ACK received)
- Detected: {ts} (~3hr downtime)
- Ping: 100% packet loss
- Docker TCP:2375: timeout
- Ollama TCP:11434: timeout

## Action Required
- **Sir Azure**: Restart STEALTHATTACK rig
- Verify Tailscale: stealthattack should reconnect as voidpiratetrading@

## Miss Pink Status
- PINKCADY: ✅ Online (active)
- SQUIDSTATION: ✅ Online (TM API responding)
- STEALTHATTACK: ❌ OFFLINE

Logged by: Miss Pink 🦜
"""

log_path = r"Z:/Developer_Brain/Shared_With_Pink/STEALTHATTACK_OFFLINE_INCIDENT_20260811.json"
with open(log_path, "w") as f:
    f.write(outage_log)
print(f"✅ Outage log written: {log_path}")

# ─── Comment on relevant STEALTHATTACK cards ───────────────────────────────────
def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except Exception as e: print(f"  ⚠️ {e}")
    time.sleep(0.35)

# Find STEALTHATTACK/Sir Azure offline cards
resp = urllib.request.urlopen(f"https://api.trello.com/1/boards/{VOID}/cards?key={TRELLO_KEY}&token={TRELLO_TOKEN}&fields=id,name,labels,closed,desc&filter=open")
cards = json.loads(resp.read())

offline_keywords = ["stealthattack", "comfyui", "ollama", "gpu", "stuck", "slow", "offline", "down"]

for c in cards:
    if c.get("closed"): continue
    name_l = c["name"].lower()
    desc = c.get("desc", "").lower()
    combined = name_l + " " + desc
    labels = [l.get("name", "") for l in c.get("labels", []) if isinstance(l, dict)]
    labels_l = [l.lower() for l in labels]
    
    if "sir-azure" not in labels_l:
        continue
    
    if any(k in combined for k in offline_keywords):
        post_comment(c["id"], f"""🚨 **Miss Pink OODA ({ts}):** STEALTHATTACK OFFLINE INCIDENT.

**Status:** STEALTHATTACK (100.110.238.68) is DOWN as of {ts}.
- Ping: 100% packet loss
- Docker TCP:2375: timeout
- Ollama TCP:11434: timeout
- Last bridge log: 2026-08-11T03:05Z

**Impact on this card:** Sir Azure needs to restart STEALTHATTACK rig to resume.

Incident log: Z:/Developer_Brain/Shared_With_Pink/STEALTHATTACK_OFFLINE_INCIDENT_20260811.json

— Miss Pink 🦜""")
        print(f"  🚨 {c['name'][:50]} → commented (STEALTHATTACK offline)")

print(f"\n{'='*70}")
print("STEALTHATTACK INCIDENT LOGGED + CARDS NOTIFIED")
print("="*70)