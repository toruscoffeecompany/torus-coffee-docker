#!/usr/bin/env python3
"""
VOID_OPS auto-verification monitor — FAST version for cron.
Checks for newly completed cards → tests → posts comments.
"""
import json, subprocess, time, os
from pathlib import Path

def load_creds():
    creds_path = Path(r"D:\Work\Torus Coffee Company LLC\Obsidian_Vault\01_Operating\Operating Paperwork\Trello_API_Credentials.md")
    for val in creds_path.read_text(encoding="utf-8").replace("`", " ").split():
        if val.startswith("d6ee"):
            key = val
        elif val.startswith("ATTA"):
            token = val
    return key, token

KEY, TOKEN = load_creds()
VOID = "6a595669b8f8f99c93392f4f"
STATE_FILE = r"D:\Work\.pirate_automation\scripts\_void_verification_state.json"

def curl_json(url, sleep=3):
    time.sleep(sleep)
    r = subprocess.run(["curl", "-s", "--connect-timeout", "8", "--max-time", "10", url],
        capture_output=True, text=True, timeout=12)
    try:
        return json.loads(r.stdout)
    except:
        return None

def curl_code(url, sleep=2):
    time.sleep(sleep)
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
            "--connect-timeout", "5", "--max-time", "8", url], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except:
        return "TIMEOUT"

def post_comment(cid, text):
    time.sleep(2)
    r = subprocess.run(["curl", "-s", "--connect-timeout", "8", "-X", "POST",
        f"https://api.trello.com/1/cards/{cid}/actions/comments?key={KEY}&token={TOKEN}",
        "-H", "Content-Type: application/json", "-d", json.dumps({"text": text})],
        capture_output=True, text=True, timeout=12)
    return "id" in r.stdout

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_done": [], "last_check": ""}

def save_state(s):
    with open(STATE_FILE, "w") as f:
        json.dump(s, f)

# ─── Main ───────────────────────────────────────────────────────────────────────
now = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
print(f"=== VoidOps Monitor — {now} ===")

state = load_state()
print(f"Last check: {state.get('last_check')}")

# Get lists
lists = curl_json(f"https://api.trello.com/1/boards/{VOID}/lists?fields=id,name&key={KEY}&token={TOKEN}", sleep=4)
if not lists:
    print("❌ API error")
    exit()

list_map = {l["id"]: l["name"] for l in lists}
done_list = [l for l in lists if l["name"].strip().lower() == "done"]
todo_list = [l for l in lists if l["name"].strip().lower() in ("to do", "to-do", "backlog")]

if not done_list:
    print("❌ Done list not found")
    exit()

# Get done cards
done_cards = curl_json(f"https://api.trello.com/1/lists/{done_list[0]['id']}/cards?fields=id,name,dateLastActivity&key={KEY}&token={TOKEN}", sleep=4)
if not done_cards:
    print("❌ No done cards")
    exit()

prev_done = set(state.get("last_done", []))
current_done = set(c["id"] for c in done_cards)
new_done = current_done - prev_done

print(f"Done cards: {len(done_cards)} | New since last: {len(new_done)}")

if new_done:
    print(f"\n=== {len(new_done)} NEW completed cards — verifying ===")
    for cid in new_done:
        card = next((c for c in done_cards if c["id"] == cid), None)
        if not card:
            continue
        name = card["name"]
        
        # Only verify bug cards
        is_bug = any(k in name.lower() for k in ["bug", "🐛", "404", "502", "augur", "tm api", "dashboard", "signal", "position", "gzip", "cache", "docker", "http/2", "gap_check", "container", "download_status", "genome", "optimizer", "running"])
        
        if not is_bug:
            print(f"  ↓ {name[:50]} — not a bug card, skipping")
            continue
        
        print(f"\n  🔍 {name[:55]}")
        now_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        # Run verification
        nl = name.lower()
        tests = []
        passed = 0
        failed = 0
        
        if "502" in nl or "/api/services" in nl or "/api/containers" in nl or "/api/vault" in nl or "/api/opsec" in nl or "/api/comms" in nl or "/api/scanner" in nl or "/api/sir-azure" in nl or "/api/captain" in nl or "/api/white-whale" in nl:
            if "/api/" in name:
                ep = "/api/" + name.split("/api/")[1].split()[0].split("(")[0].strip().rstrip("'")
            else:
                ep = "/api/"
            for kw in ["/api/services", "/api/containers", "/api/vault", "/api/opsec", "/api/comms", "/api/scanner", "/api/sir-azure", "/api/captain", "/api/white-whale", "/api/alerts"]:
                if kw in nl:
                    ep = kw
                    break
            code = curl_code(f"http://192.168.0.39:8080{ep}")
            if code == "200":
                tests.append(f"✅ {ep} returns HTTP 200")
                passed += 1
            else:
                tests.append(f"❌ {ep} returns HTTP {code}")
                failed += 1
        
        elif "404" in nl and "tm api" in nl:
            for ep in ["/api/account", "/api/orders", "/api/balance", "/api/performance", "/api/backtest", "/api/trade", "/api/execute", "/api/risk"]:
                if ep.replace("/api/", "") in nl:
                    code = curl_code(f"http://192.168.0.39:5000{ep}")
                    if code == "200":
                        tests.append(f"✅ {ep} returns HTTP 200")
                        passed += 1
                    else:
                        tests.append(f"❌ {ep} returns HTTP {code}")
                        failed += 1
                    break
        
        elif "augur" in nl and ("not running" in nl or "genome" in nl or "optimizer" in nl):
            code, body = curl_code(f"http://192.168.0.39:8080/api/augur"), None
            # Get body separately
            time.sleep(2)
            r = subprocess.run(["curl", "-s", "--connect-timeout", "8", "--max-time", "10", "http://192.168.0.39:8080/api/augur"],
                capture_output=True, text=True, timeout=12)
            try:
                d = json.loads(r.stdout)
                aug_data = d.get("live_backend", {}).get("augur_status", {}).get("data", {})
                running = aug_data.get("running")
                genome = aug_data.get("genome_id")
                opt = aug_data.get("optimizer")
                
                running_str = "✅" if running == True else "❌"
                tests.append(f"running: {running_str} {running}")
                passed += 1 if running == True else 0
                failed += 1 if running != True else 0
                
                tests.append(f"genome_id: {genome}")
                passed += 1 if genome is not None else 0
                failed += 1 if genome is None else 0
                
                tests.append(f"optimizer: {opt}")
                passed += 1 if opt == "nsga2" else 0
                failed += 1 if opt != "nsga2" else 0
            except:
                tests.append("⚠️ Could not parse")
                failed += 1
        
        elif "gzip" in nl or "cache" in nl:
            r = subprocess.run(["curl", "-s", "-D", "-", "-o", "/dev/null", "--connect-timeout", "8",
                "http://192.168.0.39:8080/api/status"], capture_output=True, text=True, timeout=12)
            h = r.stdout.lower()
            if "content-encoding: gzip" in h and "cache-control" in h:
                tests.append("✅ GZIP + Cache-Control present")
                passed += 2
            elif "content-encoding: gzip" in h:
                tests.append("✅ GZIP present, Cache-Control still missing")
                passed += 1
                failed += 1
            elif "cache-control" in h:
                tests.append("✅ Cache-Control present, GZIP still missing")
                passed += 1
                failed += 1
            else:
                tests.append("❌ GZIP + Cache-Control still missing")
                failed += 2
        
        elif "signals" in nl:
            code, body = curl_code(f"http://192.168.0.39:5000/api/signals"), None
            time.sleep(2)
            r = subprocess.run(["curl", "-s", "--connect-timeout", "8", "--max-time", "10", "http://192.168.0.39:5000/api/signals"],
                capture_output=True, text=True, timeout=12)
            try:
                d = json.loads(r.stdout)
                cnt = d.get("count", 0)
                if cnt > 0:
                    tests.append(f"✅ {cnt} signals")
                    passed += 1
                else:
                    tests.append("❌ Still 0 signals")
                    failed += 1
            except:
                tests.append(f"returns {r.stdout[:50]}")
                failed += 1
        
        elif "positions" in nl:
            r = subprocess.run(["curl", "-s", "--connect-timeout", "8", "--max-time", "10", "http://192.168.0.39:5000/api/positions"],
                capture_output=True, text=True, timeout=12)
            try:
                d = json.loads(r.stdout)
                pos = d.get("positions", [])
                if pos:
                    tests.append(f"✅ {len(pos)} positions")
                    passed += 1
                else:
                    tests.append("❌ Still empty")
                    failed += 1
            except:
                tests.append("❌ non-JSON")
                failed += 1
        
        elif "gap_check" in nl:
            r = subprocess.run(["curl", "-s", "--connect-timeout", "8", "--max-time", "10", "http://192.168.0.39:8080/api/augur"],
                capture_output=True, text=True, timeout=12)
            try:
                d = json.loads(r.stdout)
                gap = d.get("live_backend", {}).get("alpaca_status", {}).get("data", {}).get("last_gap_check")
                if gap is not None:
                    tests.append(f"✅ gap_check = {gap}")
                    passed += 1
                else:
                    tests.append("❌ Still None")
                    failed += 1
            except:
                failed += 1
        
        elif "download_status" in nl:
            r = subprocess.run(["curl", "-s", "--connect-timeout", "8", "--max-time", "10", "http://192.168.0.39:5000/api/status"],
                capture_output=True, text=True, timeout=12)
            try:
                d = json.loads(r.stdout)
                dl = d.get("download_status")
                if dl is not None:
                    tests.append(f"✅ download_status = {dl}")
                    passed += 1
                else:
                    tests.append("❌ Still null")
                    failed += 1
            except:
                failed += 1
        
        elif "docker" in nl or "port 2376" in nl:
            code = curl_code("http://192.168.0.39:2376/containers/json")
            if code == "200":
                tests.append("✅ Docker API reachable")
                passed += 1
            else:
                tests.append(f"❌ Still unreachable ({code})")
                failed += 1
        
        elif "http/2" in nl or "1.1" in nl:
            r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_version}", "--http2",
                "--connect-timeout", "8", "http://192.168.0.39:8080/api/status"],
                capture_output=True, text=True, timeout=12)
            if r.stdout.strip() == "2":
                tests.append("✅ HTTP/2 enabled")
                passed += 1
            else:
                tests.append("❌ Still HTTP/1.1")
                failed += 1
        
        elif "container" in nl and "treasuremap" in nl:
            r = subprocess.run(["curl", "-s", "--connect-timeout", "8", "--max-time", "10", "http://192.168.0.39:8080/api/augur"],
                capture_output=True, text=True, timeout=12)
            try:
                d = json.loads(r.stdout)
                tm = d.get("live_backend", {}).get("treasuremap_stack", {})
                containers = tm.get("containers_up", [])
                if containers:
                    tests.append(f"✅ {len(containers)} containers running")
                    passed += 1
                else:
                    tests.append("❌ Still empty")
                    failed += 1
            except:
                failed += 1
        
        else:
            tests.append("ℹ️ Manual review needed")
        
        verdict = "✅ VERIFIED FIXED" if failed == 0 and passed > 0 else ("⚠️ PARTIAL" if failed < passed else "❌ STILL BROKEN")
        
        comment = f"🤖 **Auto-Verification** — {now_ts}\n\n"
        comment += "Tests:\n" + "\n".join(f"  {t}" for t in tests) + "\n"
        comment += f"\nResult: {passed} passed, {failed} failed\n"
        comment += f"Verdict: **{verdict}**\n\n_Checked by Miss Pink's auto-verification bot on PINKCADY._"
        
        print(f"    Tests: {passed} passed, {failed} failed → {verdict}")
        print(f"    Posting comment...")
        success = post_comment(cid, comment)
        print(f"    ✅ Comment posted: {success}")
        
        # If verified FIXED → archive (closed=true)
        if "VERIFIED FIXED" in verdict:
            time.sleep(2)
            r = subprocess.run(["curl", "-s", "--connect-timeout", "8",
                f"https://api.trello.com/1/cards/{cid}?closed=true&key={KEY}&token={TOKEN}"],
                capture_output=True, text=True, timeout=10)
            print(f"    📦 Archived (verified fixed)")
        # If still broken, reopen
        elif "STILL BROKEN" in verdict and todo_list:
            time.sleep(2)
            subprocess.run(["curl", "-s", "-X", "PUT", "--connect-timeout", "8",
                f"https://api.trello.com/1/cards/{cid}?closed=false&idList={todo_list[0]['id']}&key={KEY}&token={TOKEN}"],
                capture_output=True, text=True, timeout=12)
            post_comment(cid, "⚠️ **Auto-Reopened**: Verification test failed. Fix incomplete.")
            print(f"    🔁 Reopened card")
else:
    print("No new completed cards since last check.")

# Save state
state["last_done"] = list(current_done)
state["last_check"] = now
save_state(state)
print(f"\n✅ State saved. Next run in 5 min.")
