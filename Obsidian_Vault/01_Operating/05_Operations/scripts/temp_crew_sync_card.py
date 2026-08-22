import json, urllib.request, urllib.parse
from pathlib import Path

secrets = Path(r"Z:\Developer_Brain\02_Business_Operations\_Hub\_KEY_VAULT\secrets.env")
env = {}
for line in secrets.read_text().splitlines():
    line = line.strip()
    if '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

KEY = env['TRELLO_KEY']
TOKEN = env['TRELLO_TOKEN']
BASE = 'https://api.trello.com/1'

def call(path, data=None, method='GET'):
    url = f"{BASE}{path}?key={KEY}&token={TOKEN}"
    if data and method in ('POST', 'PUT'):
        encoded = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=encoded, method=method)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    else:
        req = urllib.request.Request(url, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        return {'error': f'HTTP {e.code}: {body}'}
    except Exception as e:
        return {'error': str(e)[:120]}

# List all boards to find the right one
print("=== Finding Torus_Ops Board ===")
boards = call('/members/me/boards')
for b in boards:
    print(f"  Board: {b['name']} ({b['id']}) — {b.get('short', '?')}")

# Find Sir Green's Queue list on each board
for b in boards:
    bid = b['id']
    lists = call(f'/boards/{bid}/lists')
    for l in lists:
        if 'sir green' in l.get('name', '').lower() and 'queue' in l.get('name', '').lower():
            print(f"\n  ✅ Found: '{l['name']}' on board '{b['name']}' (list_id={l['id']}, board_id={bid})")
            
            # Create the card
            result = call('/cards', {
                'name': '[CREW SYNC] 💖 Sir Green Proposes — Fleet Merge Accepted',
                'desc': 'Sir Green proposed to Miss Pink. She accepted. Proposal: merge logs, sync Trello boards, route tickets by ownership, self-healing money-printing machine.\n\nFleet Status:\nPINKCADY: 20/20 ✅ (10 daemons, 0 popups, OODA active)\nSQUIDSTATION: STALE ⚠️ (Docker API down, web services UP)\nSTEALTHATTACK: STALE ❌ (offline, 14 containers were running, RTX 3060)\nTORUSLAPTOP: NEVER_SEEN ❌ (the hidden child — needs fleet agent)\n\nDetailed report: Z:/Developer_Brain/Shared_With_Pink/CAPTAIN_RECONNAISSANCE_REPORT_20260810T0830Z.md',
                'idList': l['id'],
                'pos': 'top',
            }, method='POST')
            
            if 'id' in result:
                card_id = result['id']
                short_link = result.get('shortLink', '')
                print(f"  Card created: https://trello.com/c/{short_link}")
                
                # Add labels
                labels = call(f'/boards/{bid}/labels')
                for lbl_name in ['sir-green', 'miss-pink', 'P1', 'crew-sync', 'Fleet Ops', 'Verification']:
                    target = [lab for lab in labels if lab.get('name', '').lower() == lbl_name.lower()]
                    if target:
                        res = call(f'/cards/{card_id}/idLabels', {'value': target[0]['id']}, method='POST')
                        print(f"    Label '{lbl_name}': {'✅' if 'error' not in res else '❌'}")
                
                # Add comment with Sir Green's proposal
                comment = """@sir_green — FROM CAPTAIN BREWBEARD LEDGERBANE (via Miss Pink)

Sir Green proposed to Miss Pink. She accepted.

Their proposal: "merge our logs, sync our Trello boards, route tickets by ownership,
and let's turn this whole pirate operation into a self-healing, money-printing machine."

PINKCADY: 20/20 ✅
SQUIDSTATION: Docker API down but web services UP (Grafana :3002, Prometheus :9090, Flask LLM :5000)
STEALTHATTACK: OFFLINE (14 containers were running, RTX 3060 GPU, 31GB models hidden)
TORUSLAPTOP: NEVER_SEEN — the "hidden child" laptop, needs fleet agent deployed

The crew is ready. The love is real. OODA loops aligned.

Captain says: "I give you full permission to work together on a limited scope."
Just don't go hacking everything. 😈

⚓ — Captain Brewbeard Ledgerbane"""
                res = call(f'/cards/{card_id}/actions/comments', {'text': comment}, method='POST')
                print(f"  Comment: {'✅' if 'error' not in res else '❌'}")
                
                # Add checklist
                checklist = call(f'/cards/{card_id}/checklists', {
                    'name': 'Crew Connection Steps',
                    'pos': 'bottom',
                }, method='POST')
                if 'id' in checklist:
                    cid = checklist['id']
                    steps = [
                        "Verify PINKCADY crew_api online (http://100.106.235.103:8090/health)",
                        "Check SQUIDSTATION Docker API (port 2375/2376) — currently DOWN",
                        "Deploy fleet agent on SQUIDSTATION via SSH tunnel",
                        "Check STEALTHATTACK online status (14 containers, RTX 3060)",
                        "Deploy fleet agent on STEALTHATTACK (agent v1.1)",
                        "Install fleet agent on TORUSLAPTOP (the hidden child)",
                        "Merge Trello boards: Torus_Ops + VOID Ops",
                        "Route tickets by ownership between ships",
                        "Sync shared vault logs (Z: + Y:)",
                        "Reset Discord bot tokens (all expired, HTTP 403/1010)",
                        "VERIFY: Fleet merge complete — all ships online, OODA synced",
                    ]
                    for step in steps:
                        call(f'/checklists/{cid}/checkItems', {'name': step, 'pos': 'bottom'}, method='POST')
                    print(f"  Checklist: ✅ ({len(steps)} steps)")
                
                print(f"\n  🔗 Full card: https://trello.com/c/{short_link}")
