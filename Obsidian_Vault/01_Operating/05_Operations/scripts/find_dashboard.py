import urllib.request, json

# The dashboard is on PINKCADY:8080 but might need a different approach
endpoints = [
    ("127.0.0.1:8080", "http://127.0.0.1:8080/"),
    ("127.0.0.1:3000", "http://127.0.0.1:3000/"),
    ("127.0.0.1:3003", "http://127.0.0.1:3003/"),
    ("10.0.0.3:8080", "http://100.106.235.103:8080/"),
    ("treasuremap 8080", "http://100.83.247.14:8080/"),
    ("treasuremap 3003", "http://100.83.247.14:3003/"),
    ("treasuremap 5000", "http://100.83.247.14:5000/api/dashboard/full"),
]

for name, url in endpoints:
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        content = resp.read().decode()
        print(f"✅ {name} ({len(content)} chars)")
        if "html" in content[:200].lower() or "<!DOCTYPE" in content[:20]:
            # Show title
            import re
            title = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
            if title:
                print(f"  Title: {title.group(1)[:60]}")
            # Look for tab structure
            tabs = re.findall(r'data-[a-z]+="([^"]*)"', content[:3000])
            if tabs:
                print(f"  Tabs/attrs: {tabs[:5]}")
            # Look for iframe or tab references
            iframes = re.findall(r'<iframe[^>]+src="([^"]*)"', content[:3000])
            if iframes:
                print(f"  iframes: {iframes[:5]}")
            # Look for nav/tab links
            tabs2 = re.findall(r'(tab-[a-z_]+|[a-z_]+-tab)', content[:3000])
            if tabs2:
                print(f"  Tab refs: {list(set(tabs2))[:5]}")
        elif content.startswith('{') or content.startswith('['):
            print(f"  JSON (first 200): {content[:200]}")
        else:
            print(f"  First 200: {content[:200]}")
    except Exception as e:
        print(f"❌ {name} — {e}")

# Also check for the dashboard server file
print("\n=== Looking for dashboard server files ===")
import os
search_paths = [
    "D:/Work/Torus Coffee Company LLC",
    "//192.168.0.39/VOID Pirate Trading Co/PROJECT_tr3asure_mAp",
]
for base in search_paths:
    for root, dirs, files in os.walk(base):
        for f in files:
            if "dashboard" in f.lower() and f.endswith(".py"):
                full = os.path.join(root, f)
                print(f"  {full}")
        # Don't recurse too deep
        if root.count(os.sep) > 5:
            dirs.clear()