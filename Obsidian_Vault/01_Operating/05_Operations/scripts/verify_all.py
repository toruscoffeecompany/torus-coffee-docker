"""
FINAL VERIFICATION + IDS SETUP + CONTINUE OODA LOOP.
1. Verify all previous work (rules, dashboard, bridge, cron, etc.)
2. Help Sir Green build IDS stack (Suricata/Zeek/CrowdSec)
3. Continue working remaining cards on both boards
"""
import json, urllib.request, subprocess, os, time, py_compile
from datetime import datetime, timezone

TRELLO_KEY = "d6ee11ff17..."
TRELLO_TOKEN = "ATTA..."
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ─── Helper functions ────────────────────────────────────────────────────────
def post_comment(cid, text):
    url = f"https://api.trello.com/1/cards/{cid}/actions/comments?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except Exception as e: print(f"  ⚠️ Comment: {e}")
    time.sleep(0.3)

def archive_card(cid):
    url = f"https://api.trello.com/1/cards/{cid}?key={TRELLO_KEY}&token={TRELLO_TOKEN}"
    data = json.dumps({"closed": True}).encode()
    req = urllib.request.Request(url, data=data, method='PUT')
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except Exception as e: print(f"  ⚠️ Archive: {e}")
    time.sleep(0.3)

def get_labels(c):
    return [l.get("name", "") for l in c.get("labels", []) if isinstance(l, dict)]

# ─── 1. COMPREHENSIVE VERIFICATION ────────────────────────────────────────────
print("=" * 70)
print("  COMPREHENSIVE END-TO-END VERIFICATION")
print("=" * 70)

verification_results = []
errors = []

# 1a. TreasureMap API
print("\n1a. TreasureMap API (SQUIDSTATION:5000)...")
checks += 1
try:
    r = urllib.request.urlopen("http://100.83.247.14:5000/api/status", timeout=10)
    tm = json.loads(r.read())
    kt = tm.get("kill_trading")
    pm = tm.get("paper_mode")
    kl = tm.get("kill_learning")
    running = tm.get("system", {}).get("running")
    print(f"   kill_trading: {kt}")
    print(f"   paper_mode: {pm}")
    print(f"   kill_learning: {kl}")
    print(f"   system.running: {running}")
    if kt is False and pm is True:
        verification_results.append(("TM API", "✅"))
    else:
        verification_results.append(("TM API", "❌"))
        errors.append("TM API state wrong")
except Exception as e:
    verification_results.append(("TM API", "❌"))
    errors.append(f"TM API: {e}")

# 1b. Scanner vault JSON
print("\n1b. Scanner vault JSON...")
sig_path = r"Z:/Developer_Brain/Shared_With_Pink/augmented_signals.json"
if os.path.exists(sig_path):
    with open(sig_path) as f:
        sig = json.load(f)
    signals = sig.get("signals", [])
    updated = sig.get("updated_at", "?")
    age = datetime.now(timezone.utc).timestamp() - datetime.fromisoformat(updated).timestamp() if updated else 0
    print(f"   Signals: {len(signals)} (age: {int(age)}s)")
    verification_results.append(("Scanner JSON", "✅" if age < 300 else "⚠️"))  # 5 min old
else:
    verification_results.append(("Scanner JSON", "❌"))
    errors.append("Scanner JSON missing")

# 1c. Database
print("\n1c. Database (tm_hof.db)...")
db_path = r"D:/Work/tr3asure_mAp/data/tm_hof.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    tables = {
        "price_history": "SELECT COUNT(*) FROM price_history",
        "hall_of_fame": "SELECT COUNT(*) FROM hall_of_fame",
        "bot_signals": "SELECT COUNT(*) FROM bot_signals",
    }
    for name, q in tables.items():
        count = conn.execute(q).fetchone()[0]
        print(f"   {name}: {count}")
    conn.close()
    verification_results.append(("Database", "✅"))
else:
    verification_results.append(("Database", "❌"))
    errors.append("DB missing")

# 1d. UPSERT fix
print("\n1d. UPSERT fix...")
script_path = r"Z:/Developer_Brain/02_Business_Operations/Infrastructure/scripts/void_torus_queue_bridge.py"
if os.path.exists(script_path):
    with open(script_path) as f:
        content = f.read()
    has_upsert = "card_exists_on_board" in content
    has_update = "create_or_update_card" in content
    compiles = True
    try:
        py_compile.compile(script_path, doraise=True)
    except:
        compiles = False
    print(f"   card_exists_on_board: {has_upsert}")
    print(f"   create_or_update_card: {has_update}")
    print(f"   Compiles: {compiles}")
    verification_results.append(("UPSERT fix", "✅" if has_upsert and has_update and compiles else "❌"))
else:
    verification_results.append(("UPSERT fix", "❌"))

# ... (truncated for brevity — the full script would continue)
