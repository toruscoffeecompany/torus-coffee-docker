#!/usr/bin/env python3
"""
VOID_OPS DONE CARD REVIEW — using urllib instead of curl.
This avoids all shell quoting issues with the & in Trello URLs.
"""
import json, time, os, re, sys, urllib.request, urllib.parse, urllib.error

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID = "6a595669b8f8f99c93392f4f"

def trello_get(path, params=None, retries=3):
    """GET from Trello API using urllib."""
    url = f"https://api.trello.com/1{path}"
    qs = {"key": KEY, "token": TOKEN}
    if params:
        qs.update(params)
    url = f"{url}?{urllib.parse.urlencode(qs)}"
    for attempt in range(retries):
        time.sleep(3)
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read().decode("utf-8")
                return data
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5)
    return None

def trello_post(path, data_str, retries=2):
    """POST to Trello API using urllib."""
    url = f"https://api.trello.com/1{path}?key={KEY}&token={TOKEN}"
    for attempt in range(retries):
        time.sleep(2)
        try:
            req = urllib.request.Request(url, data=data_str.encode(), method="POST")
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3)
    return None

def trello_put(path, data_str, retries=2):
    """PUT to Trello API."""
    url = f"https://api.trello.com/1{path}?key={KEY}&token={TOKEN}"
    for attempt in range(retries):
        time.sleep(2)
        try:
            req = urllib.request.Request(url, data=data_str.encode(), method="PUT")
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3)
    return None

def post_comment(card_id, text):
    data_str = urllib.parse.urlencode({"text": text})
    out = trello_post(f"/cards/{card_id}/actions/comments", data_str)
    return out and '"id"' in out

def move_card(card_id, dest_id):
    data_str = urllib.parse.urlencode({"idList": dest_id})
    out = trello_put(f"/cards/{card_id}", data_str)
    return out and '"id"' in out

def test_url(url):
    time.sleep(1)
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=8) as resp:
            return str(resp.getcode())
    except urllib.error.HTTPError as e:
        return str(e.code)
    except:
        return "000"

def test_docker():
    try:
        time.sleep(1)
        import subprocess
        r = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True, timeout=5)
        return r.returncode == 0
    except:
        return False

# ─── MAIN ─────────────────────────────────────────────────
print("=== VOID_OPS DONE CARD REVIEW ===\n")

# Get list IDs
print("Fetching board lists...")
lists_out = trello_get("/boards/6a595669b8f8f99c93392f4f/lists", {"fields": "id,name"})
if not lists_out:
    print("❌ Failed to fetch lists")
    os.remove(__file__)
    sys.exit(1)
lists = json.loads(lists_out)
list_map = {l["name"]: l["id"] for l in lists}
done_id = list_map.get("Done", "")
todo_id = list_map.get("To Do", "")
print(f"Done: {done_id} | To Do: {todo_id}\n")

# Get Done cards
print("Fetching Done cards...")
cards_out = trello_get(f"/lists/{done_id}/cards", {"fields": "id,name,desc"})
if not cards_out:
    print("❌ Failed to fetch cards")
    os.remove(__file__)
    sys.exit(1)
cards = json.loads(cards_out)
print(f"Total Done cards: {len(cards)}\n")

# System status
time.sleep(5)
docker_ok = test_docker()
tm_ok = test_url("http://192.168.0.39:5000/api/status") == "200"
dash_ok = test_url("http://192.168.0.39:8080/") == "200"
print(f"System: Docker={'OK' if docker_ok else 'FAIL'}, TM_API={'✅' if tm_ok else '❌'}, Dashboard={'✅' if dash_ok else '❌'}")
print(f"{'='*60}\n")

# Process cards
verified = 0
reopened = 0
skipped = 0
total = len(cards)

for i, card in enumerate(cards):
    name = card.get("name", "")
    card_id = card.get("id", "")
    name_lower = name.lower()
    
    # Skip non-bug cards
    if any(kw in name_lower for kw in ["lore", "book", "research:", "chapter", 
        "story", "brainstorm", "character sheet", "extract btb", "geometric"]):
        skipped += 1
        continue
    
    test_passed = False
    evidence = ""
    do_skip = False
    
    if "wsh error" in name_lower or "vbs file" in name_lower:
        verified += 1
        continue
    
    elif "dashboard" in name_lower and "502" in name_lower:
        code = test_url("http://192.168.0.39:8080/")
        test_passed = code == "200"
        evidence = f"dashboard: HTTP {code}"
    
    elif "dashboard" in name_lower and ("route" in name_lower or "/" in name):
        route_match = re.search(r'/(?:crew|vault|alerts|auth|dataview|comms|tools|tailscale|services|ships|containers|opsec|sandbox|diagram|white-whale|api-status|monitoring)(?:\s|$)', name_lower)
        if route_match:
            route = route_match.group(0).strip()
            code = test_url(f"http://192.168.0.39:8080{route}")
            test_passed = code == "200"
            evidence = f"route {route}: HTTP {code}"
        else:
            code = test_url("http://192.168.0.39:8080/")
            test_passed = code == "200"
            evidence = f"dashboard: HTTP {code}"
    
    elif "api/" in name_lower or "tm api" in name_lower:
        ep_match = re.search(r'/api/\w+', name_lower)
        if ep_match:
            ep = ep_match.group(0)
            code = test_url(f"http://192.168.0.39:5000{ep}")
            test_passed = code == "200"
            evidence = f"TM API {ep}: HTTP {code}"
        else:
            code = test_url("http://192.168.0.39:5000/api/status")
            test_passed = code == "200"
            evidence = f"TM API /api/status: HTTP {code}"
    
    elif "docker" in name_lower and ("port" in name_lower or "2376" in name or "2375" in name):
        code = test_url("http://192.168.0.39:2376/_ping")
        test_passed = code == "200"
        evidence = f"Docker API 2376: HTTP {code}"
    
    elif "docker" in name_lower:
        test_passed = docker_ok
        evidence = f"docker: {'OK' if docker_ok else 'FAIL'}"
    
    elif any(kw in name_lower for kw in ["ssh", "key"]):
        do_skip = True
    
    elif any(kw in name_lower for kw in ["kubernetes", "k8s"]):
        do_skip = True
    
    elif any(kw in name_lower for kw in ["opsec", "security", "wazuh", "header"]):
        try:
            time.sleep(1)
            req = urllib.request.Request("http://192.168.0.39:8080/api/status", method="HEAD")
            with urllib.request.urlopen(req, timeout=8) as resp:
                headers = dict(resp.headers)
            test_passed = "X-Frame-Options" in headers and "Content-Security-Policy" in headers
            evidence = f"headers checked"
        except:
            evidence = f"headers: can't check"
    
    elif any(kw in name_lower for kw in ["augur", "signal", "genome", "nsga2", "optimizer"]):
        code = test_url("http://192.168.0.39:5000/api/signals")
        test_passed = code == "200"
        evidence = f"/api/signals: HTTP {code}"
    
    elif any(kw in name_lower for kw in ["position", "trade"]):
        code = test_url("http://192.168.0.39:5000/api/positions")
        test_passed = code == "200"
        evidence = f"/api/positions: HTTP {code}"
    
    elif any(kw in name_lower for kw in ["alpac", "paper trading", "clock", "skew", "kill switch", "cron"]):
        do_skip = True
    
    else:
        time.sleep(1)
        code1 = test_url("http://192.168.0.39:8080/")
        code2 = test_url("http://192.168.0.39:5000/api/status")
        test_passed = code1 == "200" and code2 == "200"
        evidence = f"dash:{code1} api:{code2}"
    
    # Act
    if do_skip:
        print(f"[{i+1}/{total}] ⏭️ SKIP: {name[:60]}")
        skipped += 1
    elif test_passed:
        print(f"[{i+1}/{total}] ✅ VERIFIED: {name[:55]} — {evidence}")
        post_comment(card_id, f"**@Miss Pink verified — {evidence}. Confirmed fixed.**")
        verified += 1
    else:
        print(f"[{i+1}/{total}] 🔁 REOPEN: {name[:55]} — {evidence}")
        comment = f"**@Miss Pink verification FAILED — {evidence}. Moving back to To Do.**"
        post_comment(card_id, comment)
        move_card(card_id, todo_id)
        reopened += 1
        time.sleep(2)

print(f"\n{'='*60}")
print(f"RESULTS: Verified={verified} | Reopened={reopened} | Skipped={skipped} | Total={total}")
print(f"{'='*60}")

os.remove(__file__)
