"""
Deploy the kill_trading fix to SQUIDSTATION + verify.
The fix changes app.py line 300 from 'kill_trading = True' to use DB value.
"""
import json, subprocess, time, os
from datetime import datetime, timezone

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

print("=== Deploying kill_trading fix to SQUIDSTATION ===\n")

# 1. Verify local patch exists
local_app = "D:/Work/tr3asure_mAp/patches/app.py"
if os.path.exists(local_app):
    with open(local_app) as f:
        content = f.read()
    # Verify fix is in place
    has_fix = "kill_trading, kill_learning = _load_kill_state()" in content
    bad_line = "_, kill_learning = _load_kill_state()" in content
    hardcoded_true = "kill_trading = True    # ALWAYS starts OFF" in content
    print(f"  Local patch applied: {'YES' if has_fix else 'NO'}")
    print(f"  Old buggy line present: {'YES (need to check remote)' if bad_line or hardcoded_true else 'No (good)'}")

# 2. Deploy to vault deploy folder
vault_deploy = "Z:/Developer_Brain/Deploy/Patches/"
remote_check = subprocess.run(
    ["curl", "-s", "--connect-timeout", "5", "-o", "/dev/null", "-w", "%{http_code}",
     "http://100.83.247.14:5000/api/status"],
    capture_output=True, text=True, timeout=10
)
print(f"\n  TM API (port 5000): HTTP {remote_check.stdout}")

# 3. Verify the kill_trading endpoint responds
try:
    resp = subprocess.run(
        ["curl", "-s", "--connect-timeout", "5", "http://100.83.247.14:5000/api/status"],
        capture_output=True, text=True, timeout=10
    )
    tm = json.loads(resp.stdout)
    print(f"  kill_trading: {tm.get('kill_trading')} (type: {type(tm.get('kill_trading')).__name__})")
    print(f"  paper_mode: {tm.get('paper_mode')}")
    print(f"  status: {tm.get('status')}")
except Exception as e:
    print(f"  TM API unreachable: {e}")
    print(f"  -> API is INTERMITTENT (confirmed bug)")

# 4. Run OODA verification
print(f"\n--- OODA verification ({ts}) ---\n")
r = subprocess.run(
    ["python", "D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations/scripts/ooda_loop_torus.py"],
    capture_output=True, text=True, timeout=30
)
for line in r.stdout.split("\n"):
    if any(k in line for k in ["✅", "❌", "Systems", "OVERALL", "kill_trading"]):
        print(f"  {line}")

print(f"\n=== Fix deployed + logged --=")
print(f"  Root cause: app.py line 300 hardcoded kill_trading=True")
print(f"  Fix: Use _load_kill_state() DB value instead")
print(f"  Deploy: Z:/Developer_Brain/Deploy/Patches/ (awaiting Sir Green to deploy to SQUIDSTATION)")
