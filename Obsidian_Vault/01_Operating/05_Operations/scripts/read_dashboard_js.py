import urllib.request, re

url = "http://100.83.247.14:8080/"
resp = urllib.request.urlopen(url, timeout=10)
html = resp.read().decode()

# Find the JS that handles tab navigation
js_match = re.search(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
if js_match:
    js = js_match.group(1)
    print("=== Dashboard JavaScript (tab handling) ===")
    # Print in chunks to see the full JS
    for i in range(0, len(js), 1000):
        chunk = js[i:i+1000]
        print(f"\n--- JS chunk {i//1000 + 1} ---")
        print(chunk)

# Also look for how tabs are rendered
print("\n=== Looking for tab rendering logic ===")
# Find all occurrences of 'tab' in context
for match in re.finditer(r'tab', html):
    pos = match.start()
    context = html[max(0,pos-50):pos+100]
    if 'function' in context or 'click' in context or 'show' in context or 'load' in context:
        print(f"\nAt {pos}: {context}")

# Look for the dashboard server-side code
print("\n=== Looking for dashboard launcher ===")
import os
for root, dirs, files in os.walk("D:/Work/Torus Coffee Company LLC/Obsidian_Vault/10_Skills_Library/05_Operations"):
    for f in files:
        if "dashboard" in f.lower() or "hud" in f.lower():
            full = os.path.join(root, f)
            print(f"  {full}")
        if root.count(os.sep) > 6:
            dirs.clear()