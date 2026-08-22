#!/usr/bin/env python3
"""OODA Bug Hunt: Scan VOID_OPS board + check dashboard connectivity."""
import json, urllib.request, socket

KEY = "TRELLO_KEY_REMOVED_SEE_CREDENTIAL_FILE"
TOKEN = "TRELLO_TOKEN_REMOVED_SEE_CREDENTIAL_FILE"
VOID_OPS_BOARD = "6a595669b8f8f99c93392f4f"
API = "https://api.trello.com/1"

# ─── 1. VOID_OPS board lists ─────────────────────────────────────────────────────
url = f"{API}/boards/{VOID_OPS_BOARD}/lists?key={KEY}&token={TOKEN}"
resp = urllib.request.urlopen(url, timeout=30)
lists = json.loads(resp.read())

print("=== VOID_OPS BOARD — LIST IDs ===")
for l in lists:
    status = "CLOSED" if l.get("closed") else "open"
    print(f"  id={l['id']} | {status} | {l['name']}")

# ─── 2. Dashboard connectivity check (192.168.0.39:8080) ────────────────────────
print("\n=== Dashboard connectivity (192.168.0.39:8080) ===")

# Test port 8080
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
result = sock.connect_ex(("192.168.0.39", 8080))
if result == 0:
    print("  Port 8080: OPEN ✅")
    # Try HTTP
    try:
        url2 = "http://192.168.0.39:8080/api/status"
        req = urllib.request.Request(url2, headers={"X-API-Key": "***"})
        resp2 = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp2.read())
        print(f"  /api/status: {data.get('status', '?')} ✅")
        print(f"  kill_trading: {data.get('kill_trading', '?')}")
        print(f"  paper_mode: {data.get('paper_mode', '?')}")
    except Exception as e:
        print(f"  HTTP error: {e}")
else:
    print(f"  Port 8080: CLOSED (code {result}) ⚠️")

sock.close()

# ─── 3. Find ALL PINKCADY scripts connecting to dashboard/localhost:8080 ─────────
import os, re

print("\n=== Scripts on PINKCADY that connect to dashboard (localhost/192.168.0.39/100.106.235.103 + port 8080) ===")
search_dirs = [
    r"D:\Work\.pirate_automation\scripts",
    r"D:\Work\tr3asure_mAp",
]

dashboard_url_pattern = re.compile(
    r'(100\.106\.235\.103|192\.168\.0\.39|localhost|127\.0\.0\.1)[^\d]*:8080|'
    r'CD_BASE|dashboard_server|analyze_dashboard|analyze_augur_tab',
    re.IGNORECASE
)

found_files = []
for d in search_dirs:
    if not os.path.exists(d):
        continue
    for root, dirs, files in os.walk(d):
        # skip venv + pycache
        dirs[:] = [x for x in dirs if "venv" not in x and "__pycache__" not in x]
        for f in files:
            if not f.endswith((".py", ".pyw", ".sh", ".vbs", ".js")):
                continue
            fpath = os.path.join(root, f)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                if dashboard_url_pattern.search(content):
                    # Find the specific lines
                    lines = []
                    for i, line in enumerate(content.split("\n"), 1):
                        if dashboard_url_pattern.search(line):
                            lines.append(f"  line {i}: {line.strip()[:120]}")
                    found_files.append((fpath, lines))
            except Exception:
                pass

print(f"  Found {len(found_files)} files with dashboard references:")
for fpath, lines in found_files:
    rel = fpath.replace("D:\\Work\\", "")
    print(f"\n  📄 {rel}")
    for l in lines[:3]:
        print(f"    {l}")
    if len(lines) > 3:
        print(f"    ... ({len(lines)} total matches)")
